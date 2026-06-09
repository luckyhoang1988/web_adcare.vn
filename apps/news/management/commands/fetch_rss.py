from django.core.management.base import BaseCommand

from apps.news.models import RssSource
from apps.news.services import fetch_source


class Command(BaseCommand):
    help = 'Kéo bài từ các nguồn RSS (use_ai → AI viết lại), lưu nháp để duyệt.'

    def add_arguments(self, parser):
        parser.add_argument('--source', type=int, default=None,
                            help='ID nguồn cụ thể (mặc định: tất cả nguồn đang kích hoạt).')
        parser.add_argument('--dry-run', action='store_true',
                            help='Chỉ in kết quả, không lưu bài.')

    def handle(self, *args, **options):
        if options['source']:
            sources = RssSource.objects.filter(pk=options['source'])
        else:
            sources = RssSource.objects.filter(is_active=True)

        if not sources:
            self.stdout.write(self.style.WARNING('Không có nguồn nào để chạy.'))
            return

        total = {'created': 0, 'skipped': 0, 'errors': 0}
        for source in sources:
            self.stdout.write(f'→ {source.name} ...')
            stats = fetch_source(source, dry_run=options['dry_run'])
            for k in total:
                total[k] += stats[k]
            self.stdout.write(
                f"   tạo {stats['created']} · trùng {stats['skipped']} · lỗi {stats['errors']}"
            )

        self.stdout.write(self.style.SUCCESS(
            f"Xong. Tổng: tạo {total['created']} · trùng {total['skipped']} · lỗi {total['errors']}"
            + (' (dry-run)' if options['dry_run'] else '')
        ))
