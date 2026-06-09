"""Gán icon FontAwesome đồng nhất cho TẤT CẢ danh mục (sản phẩm, dịch vụ,
giải pháp, dự án) dựa trên tên — để menu toàn site dùng chung một bộ icon.

Cách dùng:
    python manage.py fix_category_icons            # điền icon còn trống
    python manage.py fix_category_icons --dry-run  # chỉ xem, không lưu
    python manage.py fix_category_icons --force     # ghi đè cả icon đã có (đồng bộ toàn bộ)

Match theo TOKEN trong slug ASCII (vi_slugify -> không phụ thuộc dấu) nên
hoạt động với mọi tên tiếng Việt có/không dấu, và tránh khớp nhầm
(vd "nâng cấp" không bị nhận thành "cáp").
"""
from django.core.management.base import BaseCommand

from apps.core.models import vi_slugify

# (từ-khóa-trong-slug, icon FontAwesome 6). Duyệt theo thứ tự — đặt mục
# cụ thể (vd "may-chu") TRƯỚC mục chung ("may") để ưu tiên đúng.
# Match theo ranh giới token: "cap" chỉ khớp token "cap", không khớp "capacity".
KEYWORD_ICONS = [
    # --- Camera / giám sát ---
    ('camera-ip', 'fas fa-camera'),
    ('camera-analog', 'fas fa-video'),
    ('camera-cctv', 'fas fa-video'),
    ('camera-wifi', 'fas fa-wifi'),
    ('camera', 'fas fa-video'),
    ('cctv', 'fas fa-video'),
    ('giam-sat', 'fas fa-video'),
    ('dau-ghi', 'fas fa-hard-drive'),          # đầu ghi hình
    ('nvr', 'fas fa-hard-drive'),
    ('dvr', 'fas fa-hard-drive'),
    # --- Kiểm soát ra vào / an ninh ---
    ('kiem-soat', 'fas fa-fingerprint'),       # kiểm soát ra vào
    ('cham-cong', 'fas fa-fingerprint'),       # chấm công
    ('van-tay', 'fas fa-fingerprint'),
    ('khoa', 'fas fa-lock'),                   # khóa cửa
    ('cua', 'fas fa-door-open'),               # cửa
    ('barrier', 'fas fa-car'),                 # barrier bãi xe
    ('bai-xe', 'fas fa-car'),
    ('bao-dong', 'fas fa-bell'),               # báo động
    ('bao-chay', 'fas fa-fire-extinguisher'),  # báo cháy
    ('pccc', 'fas fa-fire-extinguisher'),
    ('chuong', 'fas fa-bell'),                 # chuông cửa
    ('an-ninh', 'fas fa-shield-halved'),
    # --- Máy tính / máy chủ / lưu trữ ---
    ('may-chu', 'fas fa-server'),              # máy chủ
    ('server', 'fas fa-server'),
    ('luu-tru', 'fas fa-database'),            # lưu trữ
    ('storage', 'fas fa-database'),
    ('nas', 'fas fa-database'),
    ('laptop', 'fas fa-laptop'),
    ('may-tinh', 'fas fa-desktop'),            # máy tính (để bàn)
    ('o-cung', 'fas fa-hard-drive'),           # ổ cứng
    ('ssd', 'fas fa-hard-drive'),
    ('hdd', 'fas fa-hard-drive'),
    # --- Mạng ---
    ('thiet-bi-mang', 'fas fa-network-wired'),
    ('switch', 'fas fa-network-wired'),
    ('router', 'fas fa-network-wired'),
    ('wifi', 'fas fa-wifi'),
    ('mang', 'fas fa-network-wired'),          # mạng
    ('cap', 'fas fa-ethernet'),                # cáp
    # --- Nhà thông minh ---
    ('smart-home', 'fas fa-house-signal'),
    ('nha-thong-minh', 'fas fa-house-signal'),
    ('smart', 'fas fa-house-signal'),
    # --- Nguồn / điện ---
    ('nguon', 'fas fa-plug'),                  # nguồn
    ('ups', 'fas fa-battery-full'),
    ('pin', 'fas fa-battery-full'),
    # --- Dịch vụ ---
    ('lap-dat', 'fas fa-screwdriver-wrench'),  # lắp đặt
    ('thi-cong', 'fas fa-helmet-safety'),      # thi công
    ('bao-tri', 'fas fa-wrench'),              # bảo trì
    ('sua-chua', 'fas fa-wrench'),             # sửa chữa
    ('bao-hanh', 'fas fa-shield-halved'),      # bảo hành
    ('tu-van', 'fas fa-lightbulb'),            # tư vấn
    ('thiet-ke', 'fas fa-pen-ruler'),          # thiết kế
    ('dao-tao', 'fas fa-graduation-cap'),      # đào tạo
    ('cho-thue', 'fas fa-handshake'),          # cho thuê
    ('giai-phap', 'fas fa-lightbulb'),         # giải pháp
    # --- Phụ kiện / khác ---
    ('phu-kien', 'fas fa-plug'),               # phụ kiện
    ('cong-cu', 'fas fa-screwdriver-wrench'),
    ('man-hinh', 'fas fa-display'),            # màn hình
    ('tivi', 'fas fa-tv'),
    ('loa', 'fas fa-volume-high'),             # loa
    ('micro', 'fas fa-microphone'),
    ('amply', 'fas fa-volume-high'),
    ('the-nho', 'fas fa-sd-card'),             # thẻ nhớ
]

DEFAULT_ICON = 'fas fa-box'

# Các model danh mục có field `icon`. (import lười trong handle để tránh lỗi
# nếu app nào đó chưa cài.)
CATEGORY_MODELS = [
    ('apps.products.models', 'ProductCategory', 'Sản phẩm'),
    ('apps.services.models', 'ServiceCategory', 'Dịch vụ'),
    ('apps.solutions.models', 'SolutionCategory', 'Giải pháp'),
    ('apps.projects.models', 'ProjectCategory', 'Dự án'),
]


def pick_icon(name):
    """Trả về icon khớp đầu tiên theo ranh giới token, hoặc DEFAULT_ICON."""
    padded = f'-{vi_slugify(name)}-'
    for keyword, icon in KEYWORD_ICONS:
        if f'-{keyword}-' in padded:
            return icon
    return DEFAULT_ICON


class Command(BaseCommand):
    help = 'Gán icon FontAwesome đồng nhất cho mọi danh mục (sản phẩm/dịch vụ/giải pháp/dự án).'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true',
                            help='Chỉ in ra thay đổi, không lưu vào DB.')
        parser.add_argument('--force', action='store_true',
                            help='Ghi đè cả những danh mục đã có icon.')

    def handle(self, *args, **options):
        from importlib import import_module

        dry_run = options['dry_run']
        force = options['force']
        total_updated = 0
        total_skipped = 0

        for module_path, model_name, label in CATEGORY_MODELS:
            try:
                Model = getattr(import_module(module_path), model_name)
            except (ImportError, AttributeError):
                continue

            self.stdout.write(self.style.HTTP_INFO(f'\n=== {label} ({model_name}) ==='))
            for cat in Model.objects.all():
                new_icon = pick_icon(cat.name)
                if cat.icon == new_icon:
                    total_skipped += 1
                    continue
                if cat.icon and not force:
                    self.stdout.write(
                        f'  ~ "{cat.name}": giữ "{cat.icon}" '
                        f'(đề xuất "{new_icon}", dùng --force để ghi đè)'
                    )
                    total_skipped += 1
                    continue

                self.stdout.write(
                    self.style.SUCCESS(f'  + "{cat.name}": "{cat.icon}" -> "{new_icon}"')
                )
                if not dry_run:
                    cat.icon = new_icon
                    cat.save(update_fields=['icon'])
                total_updated += 1

        msg = f'\nHoàn tất: {total_updated} cập nhật, {total_skipped} bỏ qua.'
        if dry_run:
            msg += ' (DRY-RUN — chưa lưu)'
        self.stdout.write(self.style.WARNING(msg))
