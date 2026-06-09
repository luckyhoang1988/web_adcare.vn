"""Tự động kéo bài từ RSS + (tùy chọn) AI viết lại → lưu nháp.

Dùng chung bởi management command `fetch_rss` và admin action "Lấy bài ngay".
Mọi nội dung HTML đều được sanitize bằng bleach trước khi lưu (chống stored XSS),
vì template news/detail.html render bằng `|safe`.
"""
import json
import logging
import urllib.request
from urllib.parse import urljoin

import bleach
import feedparser
from bs4 import BeautifulSoup
from django.conf import settings
from django.core.files.base import ContentFile
from django.utils import timezone
from django.utils.html import strip_tags

from .models import Article

logger = logging.getLogger(__name__)

# Allowlist HTML — chỉ giữ các thẻ/thuộc tính an toàn cho nội dung bài viết.
ALLOWED_TAGS = [
    'p', 'br', 'a', 'strong', 'b', 'em', 'i', 'u', 'ul', 'ol', 'li',
    'h2', 'h3', 'h4', 'blockquote', 'img', 'figure', 'figcaption',
    'table', 'thead', 'tbody', 'tr', 'td', 'th',
]
ALLOWED_ATTRS = {
    'a': ['href', 'title'],
    'img': ['src', 'alt', 'title'],
}
ALLOWED_PROTOCOLS = ['http', 'https']

# Giới hạn ký tự nội dung gốc gửi cho AI — tiết kiệm token & tránh chạm rate-limit free tier.
MAX_AI_INPUT_CHARS = 8000


def clean_html(html):
    """Sanitize HTML theo allowlist, loại bỏ thẻ/script nguy hiểm."""
    return bleach.clean(
        html or '',
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRS,
        protocols=ALLOWED_PROTOCOLS,
        strip=True,
    )


def _download_image(url, filename):
    """Tải ảnh về dưới dạng ContentFile (tái dùng pattern từ fetch_images.py)."""
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = resp.read()
        return ContentFile(data, name=filename)
    except Exception as e:
        logger.warning('Không tải được ảnh %s: %s', url, e)
        return None


def _extract_image_url(entry):
    """Tìm URL ảnh đại diện theo thứ tự ưu tiên. Trả URL tuyệt đối (urljoin với link bài)."""
    base = entry.get('link', '')
    found = None
    # media_content / media_thumbnail (Media RSS)
    for key in ('media_content', 'media_thumbnail'):
        media = entry.get(key)
        if media and isinstance(media, list) and media[0].get('url'):
            found = media[0]['url']
            break
    # enclosure
    if not found:
        for link in entry.get('links', []):
            if link.get('rel') == 'enclosure' and str(link.get('type', '')).startswith('image'):
                found = link.get('href')
                break
    # <img> đầu tiên trong nội dung
    if not found:
        raw = _entry_raw_content(entry)
        if raw:
            img = BeautifulSoup(raw, 'html.parser').find('img')
            if img and img.get('src'):
                found = img['src']
    return urljoin(base, found) if found else None


SYSTEM_PROMPT = (
    'Bạn là biên tập viên tiếng Việt cho website camera an ninh ADCARE. '
    'Viết lại bài thành bài nguyên gốc, chuẩn SEO, văn phong tự nhiên, không sao chép nguyên văn. '
    'Chỉ trả về JSON đúng cấu trúc: '
    '{"title": "tiêu đề", "content_html": "nội dung HTML", "summary": "tóm tắt"}. '
    'content_html chỉ dùng các thẻ: p, h2, h3, ul, ol, li, strong, em, blockquote. '
    'summary là đoạn tóm tắt ngắn dưới 300 ký tự, không chứa HTML.'
)


def _strip_json_fence(text):
    """Bỏ ```json ... ``` nếu model bọc JSON trong code fence."""
    text = text.strip()
    if text.startswith('```'):
        text = text.split('\n', 1)[-1]          # bỏ dòng ```json
        if text.rstrip().endswith('```'):
            text = text.rstrip()[:-3]
    return text.strip()


def rewrite_with_ai(title, raw_content, instructions=''):
    """Dùng LLM (OpenAI-compatible) viết lại bài thành nội dung tiếng Việt nguyên gốc.

    Nhà cung cấp cấu hình qua .env (RSS_AI_BASE_URL / RSS_AI_API_KEY / RSS_AI_MODEL) —
    Groq / Gemini / OpenRouter / Ollama đều dùng chung code này.

    Trả về dict {title, content_html, summary}. Raise nếu API lỗi
    (để fetch_source đếm vào errors và bỏ qua entry đó).
    """
    from openai import OpenAI

    client = OpenAI(api_key=settings.RSS_AI_API_KEY, base_url=settings.RSS_AI_BASE_URL)
    resp = client.chat.completions.create(
        model=settings.RSS_AI_MODEL,
        max_tokens=4096,
        response_format={'type': 'json_object'},
        messages=[
            {'role': 'system', 'content': SYSTEM_PROMPT},
            {'role': 'user', 'content': (
                f'{instructions}\n\n'
                f'Viết lại bài sau và trả về JSON:\n\n'
                f'TIÊU ĐỀ GỐC: {title}\n\n'
                f'NỘI DUNG GỐC:\n{raw_content}'
            )},
        ],
    )
    return json.loads(_strip_json_fence(resp.choices[0].message.content))


def _entry_raw_content(entry):
    """Lấy nội dung gốc của entry: ưu tiên content[], sau đó summary."""
    if entry.get('content'):
        body = entry['content'][0].get('value', '')
        if body:
            return body
    return entry.get('summary', '')


def fetch_source(source, dry_run=False):
    """Kéo bài từ một RssSource, tạo Article nháp. Trả về thống kê dict."""
    stats = {'created': 0, 'skipped': 0, 'errors': 0}
    feed = feedparser.parse(source.feed_url)
    if feed.bozo and not feed.entries:
        logger.warning('Không đọc được feed %s: %s',
                       source.feed_url, getattr(feed, 'bozo_exception', ''))
        return stats

    for entry in feed.entries[:source.max_items]:
        guid = entry.get('id') or entry.get('link') or ''
        if not guid:
            stats['errors'] += 1
            continue
        if Article.objects.filter(source_guid=guid).exists():
            stats['skipped'] += 1
            continue

        try:
            raw_content = _entry_raw_content(entry)
            orig_title = entry.get('title', '')

            if source.use_ai:
                # Gửi văn bản thuần đã cắt ngắn cho AI (đỡ token, đỡ chạm rate-limit).
                ai_input = strip_tags(raw_content)[:MAX_AI_INPUT_CHARS]
                data = rewrite_with_ai(orig_title, ai_input, source.ai_instructions)
                title = data.get('title') or orig_title
                content_html = data.get('content_html', '')
                summary = data.get('summary', '')
            else:
                title = orig_title
                content_html = raw_content
                summary = strip_tags(raw_content)[:300]

            content_html = clean_html(content_html)
            title = (title.strip() or 'Bài viết')[:300]
            if not content_html.strip():
                logger.warning('Bỏ qua "%s": nội dung rỗng sau khi xử lý', orig_title)
                stats['errors'] += 1
                continue
            if not summary:
                summary = strip_tags(content_html)[:300]

            if dry_run:
                stats['created'] += 1
                continue

            article = Article(
                category=source.category,
                title=title,
                summary=summary[:500],
                content=content_html,
                author=source.author or entry.get('author', '') or 'ADCARE Việt Nam',
                status='draft',
                published_at=None,
                source=source,
                source_guid=guid[:500],
                source_url=(entry.get('link', '') or '')[:500],
                meta_title=title[:200],
                meta_desc=summary[:300],
            )
            article.save()  # slug tự sinh trong Article.save()

            img_url = _extract_image_url(entry)
            if img_url:
                cf = _download_image(img_url, f'rss_{article.pk}.jpg')
                if cf:
                    article.image.save(f'rss_{article.pk}.jpg', cf, save=True)

            stats['created'] += 1
        except Exception as e:
            logger.exception('Lỗi xử lý entry "%s": %s', entry.get('title', '?'), e)
            stats['errors'] += 1

    if not dry_run:
        source.last_fetched_at = timezone.now()
        source.save(update_fields=['last_fetched_at'])

    return stats
