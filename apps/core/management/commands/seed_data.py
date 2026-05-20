from io import BytesIO
from PIL import Image, ImageDraw

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.core.models import SiteConfig, Slider, StatItem, AboutSection, AboutFeature
from apps.products.models import ProductCategory, Product
from apps.services.models import ServiceCategory, Service
from apps.news.models import NewsCategory, Article
from apps.partners.models import Partner


def _placeholder(width=800, height=600, color=(46, 92, 16), filename='img.jpg'):
    img = Image.new('RGB', (width, height), color=color)
    draw = ImageDraw.Draw(img)
    m = min(width, height) // 8
    draw.rectangle([(m, m), (width - m, height - m)], outline=(255, 255, 255), width=3)
    buf = BytesIO()
    img.save(buf, format='JPEG', quality=85)
    buf.seek(0)
    return ContentFile(buf.read(), name=filename)


COLORS = {
    'green':  (46, 92, 16),
    'dark':   (30, 61, 10),
    'accent': (125, 184, 51),
    'blue':   (41, 128, 185),
    'orange': (211, 84, 0),
    'purple': (142, 68, 173),
    'teal':   (22, 160, 133),
    'gray':   (80, 80, 80),
}


class Command(BaseCommand):
    help = 'Tạo dữ liệu mẫu cho website ADCARE camera an ninh'

    def handle(self, *args, **options):
        self.stdout.write('Seeding sample data...')
        self._seed_site_config()
        self._seed_sliders()
        self._seed_stats()
        self._seed_about()
        self._seed_products()
        self._seed_services()
        self._seed_news()
        self._seed_partners()
        self.stdout.write(self.style.SUCCESS('Done! Visit http://localhost:8000'))

    # -------------------------------------------------------------------------

    def _seed_site_config(self):
        cfg, _ = SiteConfig.objects.get_or_create(pk=1)
        cfg.company_name = 'ADCARE Việt Nam'
        cfg.slogan = 'Giải pháp an ninh thông minh — Bảo vệ tài sản của bạn'
        cfg.address = '123 Nguyễn Văn Linh, Phường Tân Phong, Quận 7, TP. Hồ Chí Minh'
        cfg.phone = '0901 234 567'
        cfg.phone_2 = '028 3456 7890'
        cfg.email = 'info@adcare.vn'
        cfg.email_2 = 'support@adcare.vn'
        cfg.facebook_url = 'https://facebook.com/adcare.vn'
        cfg.youtube_url = 'https://youtube.com/@adcarevietnam'
        cfg.working_hours = 'Thứ 2 – Thứ 7: 8:00 – 17:30\nChủ nhật: 8:00 – 12:00'
        cfg.footer_description = (
            'ADCARE Việt Nam chuyên cung cấp, lắp đặt và bảo trì hệ thống '
            'camera an ninh, báo động, kiểm soát ra vào cho gia đình và doanh nghiệp.'
        )
        cfg.meta_description = (
            'ADCARE Việt Nam — Giải pháp camera an ninh toàn diện. '
            'Lắp đặt camera IP, camera Analog, hệ thống báo động tại TP.HCM.'
        )
        cfg.save()
        self.stdout.write('  [OK] SiteConfig')

    def _seed_sliders(self):
        slides = [
            {
                'title': 'Giải pháp Camera An Ninh Toàn Diện',
                'subtitle': 'Bảo vệ gia đình và doanh nghiệp của bạn 24/7 với hệ thống camera IP hiện đại nhất',
                'button_text': 'Xem sản phẩm',
                'button_url': '/san-pham/',
                'button2_text': 'Liên hệ tư vấn',
                'button2_url': '/lien-he/',
                'order': 1,
                'color': COLORS['green'],
            },
            {
                'title': 'Dịch Vụ Lắp Đặt Chuyên Nghiệp',
                'subtitle': 'Đội ngũ kỹ thuật viên giàu kinh nghiệm, lắp đặt nhanh chóng, bảo hành dài hạn',
                'button_text': 'Xem dịch vụ',
                'button_url': '/dich-vu/',
                'button2_text': 'Báo giá miễn phí',
                'button2_url': '/lien-he/',
                'order': 2,
                'color': COLORS['dark'],
            },
            {
                'title': 'Camera Hikvision & Dahua Chính Hãng',
                'subtitle': 'Phân phối độc quyền camera IP, camera Analog, đầu ghi hình từ các thương hiệu hàng đầu',
                'button_text': 'Khám phá ngay',
                'button_url': '/san-pham/',
                'button2_text': '',
                'button2_url': '',
                'order': 3,
                'color': COLORS['blue'],
            },
        ]
        for s in slides:
            obj, created = Slider.objects.get_or_create(title=s['title'])
            if created:
                obj.subtitle = s['subtitle']
                obj.button_text = s['button_text']
                obj.button_url = s['button_url']
                obj.button2_text = s['button2_text']
                obj.button2_url = s['button2_url']
                obj.order = s['order']
                obj.is_active = True
                obj.image.save(f"slider_{s['order']}.jpg", _placeholder(1920, 800, s['color']))
        self.stdout.write('  [OK] Sliders')

    def _seed_stats(self):
        items = [
            ('fas fa-project-diagram', '500+', 'Dự án hoàn thành', 'Từ nhà ở đến toà nhà văn phòng', 1),
            ('fas fa-users', '1.000+', 'Khách hàng tin tưởng', 'Trên toàn quốc', 2),
            ('fas fa-calendar-alt', '10+', 'Năm kinh nghiệm', 'Trong lĩnh vực an ninh', 3),
            ('fas fa-headset', '24/7', 'Hỗ trợ kỹ thuật', 'Hotline luôn sẵn sàng', 4),
        ]
        for icon, number, label, desc, order in items:
            StatItem.objects.get_or_create(
                label=label,
                defaults={'icon': icon, 'number': number, 'description': desc, 'order': order, 'is_active': True},
            )
        self.stdout.write('  [OK] StatItems')

    def _seed_about(self):
        about, created = AboutSection.objects.get_or_create(
            title='Về ADCARE Việt Nam',
            defaults={
                'subtitle': 'Hơn 10 năm bảo vệ tài sản và con người',
                'content': (
                    'ADCARE Việt Nam được thành lập năm 2014, là đơn vị chuyên cung cấp các giải pháp '
                    'an ninh điện tử toàn diện cho hộ gia đình, văn phòng, nhà máy và công trình xây dựng.\n\n'
                    'Với đội ngũ kỹ sư và kỹ thuật viên được đào tạo bài bản, chúng tôi tự hào đã triển khai '
                    'hơn 500 dự án lớn nhỏ trên khắp cả nước. Sản phẩm chúng tôi cung cấp đều là hàng chính '
                    'hãng từ các thương hiệu hàng đầu thế giới như Hikvision, Dahua, Axis, Bosch.\n\n'
                    'ADCARE cam kết mang đến giải pháp tối ưu nhất với chi phí hợp lý, đảm bảo an toàn '
                    'và bình yên cho khách hàng.'
                ),
                'button_text': 'Tìm hiểu thêm',
                'button_url': '/ve-chung-toi/',
                'is_active': True,
            },
        )
        if created:
            about.image.save('about_main.jpg', _placeholder(700, 500, COLORS['green']))

            features = [
                ('fas fa-shield-alt', 'Sản phẩm chính hãng 100%', 1),
                ('fas fa-tools', 'Lắp đặt nhanh — bảo hành 24 tháng', 2),
                ('fas fa-headset', 'Hỗ trợ kỹ thuật 24/7', 3),
                ('fas fa-certificate', 'Đội ngũ kỹ sư được chứng nhận', 4),
            ]
            for icon, text, order in features:
                AboutFeature.objects.create(about=about, icon=icon, text=text, order=order)
        self.stdout.write('  [OK] AboutSection')

    def _seed_products(self):
        categories = [
            ('Camera IP', 'camera-ip', 'fas fa-video', COLORS['blue'], 1),
            ('Camera Analog', 'camera-analog', 'fas fa-camera', COLORS['teal'], 2),
            ('Camera PTZ', 'camera-ptz', 'fas fa-sync-alt', COLORS['purple'], 3),
            ('Đầu ghi hình', 'dau-ghi-hinh', 'fas fa-hdd', COLORS['orange'], 4),
            ('Phụ kiện & Cáp', 'phu-kien-cap', 'fas fa-plug', COLORS['gray'], 5),
        ]

        products_data = {
            'camera-ip': [
                {
                    'name': 'Camera IP Hikvision DS-2CD2143G2-I',
                    'slug': 'camera-ip-hikvision-ds-2cd2143g2-i',
                    'short_desc': 'Camera IP 4MP AcuSense, hồng ngoại 40m, chuẩn IP67, chống ngược sáng WDR 120dB.',
                    'brand': 'Hikvision', 'model_number': 'DS-2CD2143G2-I',
                    'is_featured': True, 'order': 1, 'color': COLORS['blue'],
                    'specifications': 'Độ phân giải: 4MP (2560×1440)\nHồng ngoại: 40m\nChuẩn IP: IP67\nWDR: 120dB\nGiao thức: ONVIF',
                },
                {
                    'name': 'Camera IP Dahua IPC-HDW2831T-AS',
                    'slug': 'camera-ip-dahua-ipc-hdw2831t-as',
                    'short_desc': 'Camera IP Eyeball 8MP, hồng ngoại 30m, tích hợp mic, chuẩn IP67.',
                    'brand': 'Dahua', 'model_number': 'IPC-HDW2831T-AS',
                    'is_featured': False, 'order': 2, 'color': COLORS['blue'],
                    'specifications': 'Độ phân giải: 8MP (3840×2160)\nHồng ngoại: 30m\nMicrophone: Có\nChuẩn IP: IP67',
                },
                {
                    'name': 'Camera IP Axis P3245-V',
                    'slug': 'camera-ip-axis-p3245-v',
                    'short_desc': 'Camera IP dome cố định 2MP, Lightfinder 2.0, góc rộng 104°.',
                    'brand': 'Axis', 'model_number': 'P3245-V',
                    'is_featured': False, 'order': 3, 'color': COLORS['blue'],
                    'specifications': 'Độ phân giải: 2MP (1920×1080)\nLightfinder 2.0\nGóc nhìn: 104°\nPoE 802.3af',
                },
            ],
            'camera-analog': [
                {
                    'name': 'Camera Analog Hikvision DS-2CE16D0T-IRF',
                    'slug': 'camera-analog-hikvision-ds-2ce16d0t-irf',
                    'short_desc': 'Camera HD-TVI 2MP, hồng ngoại 25m, góc rộng 2.8mm, chống bụi nước IP66.',
                    'brand': 'Hikvision', 'model_number': 'DS-2CE16D0T-IRF',
                    'is_featured': True, 'order': 1, 'color': COLORS['teal'],
                    'specifications': 'Độ phân giải: 2MP (1920×1080)\nHồng ngoại: 25m\nTiêu cự: 2.8mm\nChuẩn IP: IP66',
                },
                {
                    'name': 'Camera Analog Dahua HAC-HDW1500TL-A',
                    'slug': 'camera-analog-dahua-hac-hdw1500tl-a',
                    'short_desc': 'Camera HDCVI 5MP, hồng ngoại 20m, tích hợp mic, lắp âm trần.',
                    'brand': 'Dahua', 'model_number': 'HAC-HDW1500TL-A',
                    'is_featured': False, 'order': 2, 'color': COLORS['teal'],
                    'specifications': 'Độ phân giải: 5MP (2592×1944)\nHồng ngoại: 20m\nMicrophone: Có\nLắp đặt: Âm trần',
                },
            ],
            'camera-ptz': [
                {
                    'name': 'Camera PTZ Hikvision DS-2DE4425IWG-E',
                    'slug': 'camera-ptz-hikvision-ds-2de4425iwg-e',
                    'short_desc': 'Camera PTZ IP 4MP, zoom quang 25x, hồng ngoại 100m, auto-tracking.',
                    'brand': 'Hikvision', 'model_number': 'DS-2DE4425IWG-E',
                    'is_featured': True, 'order': 1, 'color': COLORS['purple'],
                    'specifications': 'Độ phân giải: 4MP\nZoom quang: 25x\nHồng ngoại: 100m\nAuto-tracking: Có\nIP66+IK10',
                },
                {
                    'name': 'Camera PTZ Dahua SD49425XB-HNR',
                    'slug': 'camera-ptz-dahua-sd49425xb-hnr',
                    'short_desc': 'Camera PTZ AI 4MP, zoom quang 25x, nhận diện khuôn mặt, hồng ngoại 100m.',
                    'brand': 'Dahua', 'model_number': 'SD49425XB-HNR',
                    'is_featured': False, 'order': 2, 'color': COLORS['purple'],
                    'specifications': 'Độ phân giải: 4MP\nZoom quang: 25x\nAI: Nhận diện khuôn mặt\nHồng ngoại: 100m',
                },
            ],
            'dau-ghi-hinh': [
                {
                    'name': 'NVR Hikvision DS-7608NI-Q1',
                    'slug': 'nvr-hikvision-ds-7608ni-q1',
                    'short_desc': 'Đầu ghi IP 8 kênh, hỗ trợ camera 4K, 1 ổ cứng tối đa 10TB.',
                    'brand': 'Hikvision', 'model_number': 'DS-7608NI-Q1',
                    'is_featured': True, 'order': 1, 'color': COLORS['orange'],
                    'specifications': 'Số kênh: 8\nHỗ trợ: 4K Ultra HD\nỔ cứng: 1 x tối đa 10TB\nBăng thông: 80Mbps',
                },
                {
                    'name': 'DVR Dahua XVR5108HS-I3',
                    'slug': 'dvr-dahua-xvr5108hs-i3',
                    'short_desc': 'Đầu ghi hybrid 8 kênh 5MP, hỗ trợ HDCVI/AHD/TVI/CVBS/IP, AI Smart.',
                    'brand': 'Dahua', 'model_number': 'XVR5108HS-I3',
                    'is_featured': False, 'order': 2, 'color': COLORS['orange'],
                    'specifications': 'Số kênh: 8\nĐộ phân giải: 5MP\nHybrid: CVI/AHD/TVI/IP\nAI: Có',
                },
            ],
            'phu-kien-cap': [
                {
                    'name': 'Cáp mạng SFTP CAT6 Ngoài trời 305m',
                    'slug': 'cap-mang-sftp-cat6-ngoai-troi-305m',
                    'short_desc': 'Cáp CAT6 chống nhiễu SFTP, lõi đồng nguyên chất, chịu nhiệt UV ngoài trời.',
                    'brand': 'ADCARE', 'model_number': 'CAT6-SFTP-305',
                    'is_featured': False, 'order': 1, 'color': COLORS['gray'],
                    'specifications': 'Loại: CAT6 SFTP\nChiều dài: 305m/cuộn\nMôi trường: Ngoài trời\nBăng thông: 250MHz',
                },
                {
                    'name': 'Nguồn tổng 12V 10A cho camera',
                    'slug': 'nguon-tong-12v-10a-cho-camera',
                    'short_desc': 'Nguồn tập trung 12V-10A, 8 ngõ ra, vỏ sắt, dùng cho hệ thống 4-8 camera.',
                    'brand': 'ADCARE', 'model_number': 'PSU-12V10A-8CH',
                    'is_featured': False, 'order': 2, 'color': COLORS['gray'],
                    'specifications': 'Điện áp: 12V DC\nDòng điện: 10A\nSố ngõ ra: 8\nVỏ: Sắt chống cháy',
                },
            ],
        }

        for cat_name, cat_slug, cat_icon, cat_color, cat_order in categories:
            cat, created = ProductCategory.objects.get_or_create(
                slug=cat_slug,
                defaults={'name': cat_name, 'icon': cat_icon, 'order': cat_order, 'is_active': True},
            )
            if created:
                cat.image.save(f'cat_{cat_slug}.jpg', _placeholder(800, 600, cat_color))

            for p in products_data.get(cat_slug, []):
                prod, prod_created = Product.objects.get_or_create(
                    slug=p['slug'],
                    defaults={
                        'category': cat,
                        'name': p['name'],
                        'short_desc': p['short_desc'],
                        'brand': p['brand'],
                        'model_number': p['model_number'],
                        'specifications': p['specifications'],
                        'is_featured': p['is_featured'],
                        'is_active': True,
                        'order': p['order'],
                    },
                )
                if prod_created:
                    prod.image.save(f'product_{p["slug"]}.jpg', _placeholder(800, 600, p['color']))

        self.stdout.write('  [OK] Products & Categories')

    def _seed_services(self):
        categories = [
            ('Lắp đặt hệ thống', 'lap-dat-he-thong', 'fas fa-tools', COLORS['green'], 1),
            ('Bảo trì & Sửa chữa', 'bao-tri-sua-chua', 'fas fa-wrench', COLORS['blue'], 2),
            ('Tư vấn giải pháp', 'tu-van-giai-phap', 'fas fa-lightbulb', COLORS['orange'], 3),
        ]

        services_data = {
            'lap-dat-he-thong': [
                {
                    'name': 'Lắp đặt camera quan sát',
                    'slug': 'lap-dat-camera-quan-sat',
                    'short_desc': 'Khảo sát, tư vấn và lắp đặt hệ thống camera IP / Analog cho gia đình, văn phòng, kho xưởng.',
                    'description': (
                        '<h3>Dịch vụ lắp đặt camera chuyên nghiệp</h3>'
                        '<p>ADCARE cung cấp trọn gói dịch vụ lắp đặt camera quan sát từ khảo sát thực địa, '
                        'thiết kế hệ thống, thi công đến bàn giao và hướng dẫn sử dụng.</p>'
                        '<ul><li>Khảo sát miễn phí tại nhà/công ty</li>'
                        '<li>Tư vấn số lượng và vị trí lắp đặt tối ưu</li>'
                        '<li>Thi công gọn gàng, không đục tường không cần thiết</li>'
                        '<li>Bảo hành thiết bị 24 tháng, bảo hành công trình 12 tháng</li></ul>'
                    ),
                    'icon': 'fas fa-camera',
                    'is_featured': True, 'order': 1, 'color': COLORS['green'],
                },
                {
                    'name': 'Lắp đặt hệ thống báo động',
                    'slug': 'lap-dat-he-thong-bao-dong',
                    'short_desc': 'Lắp đặt chuông báo động chống trộm, cảm biến chuyển động, còi hú cho gia đình và cửa hàng.',
                    'description': (
                        '<h3>Hệ thống báo động thông minh</h3>'
                        '<p>Bảo vệ tài sản 24/7 với hệ thống báo động hiện đại, kết nối điện thoại thông minh.</p>'
                        '<ul><li>Cảm biến hồng ngoại chống trộm</li>'
                        '<li>Còi hú 120dB</li>'
                        '<li>Thông báo SMS/app khi có sự cố</li>'
                        '<li>Pin dự phòng 8 giờ</li></ul>'
                    ),
                    'icon': 'fas fa-bell',
                    'is_featured': False, 'order': 2, 'color': COLORS['teal'],
                },
                {
                    'name': 'Lắp đặt kiểm soát ra vào',
                    'slug': 'lap-dat-kiem-soat-ra-vao',
                    'short_desc': 'Hệ thống kiểm soát cửa bằng thẻ từ, vân tay, nhận diện khuôn mặt cho văn phòng.',
                    'description': (
                        '<h3>Kiểm soát ra vào chuyên nghiệp</h3>'
                        '<p>Quản lý người ra vào chính xác, ghi lịch sử đầy đủ, tích hợp chấm công.</p>'
                        '<ul><li>Đầu đọc thẻ từ RFID / vân tay</li>'
                        '<li>Nhận diện khuôn mặt không chạm</li>'
                        '<li>Phần mềm quản lý nhân sự</li>'
                        '<li>Xuất báo cáo chấm công</li></ul>'
                    ),
                    'icon': 'fas fa-id-card',
                    'is_featured': True, 'order': 3, 'color': COLORS['purple'],
                },
            ],
            'bao-tri-sua-chua': [
                {
                    'name': 'Bảo trì camera định kỳ',
                    'slug': 'bao-tri-camera-dinh-ky',
                    'short_desc': 'Vệ sinh, kiểm tra và bảo trì toàn bộ hệ thống camera định kỳ 3, 6 hoặc 12 tháng.',
                    'description': (
                        '<h3>Gói bảo trì định kỳ ADCARE</h3>'
                        '<p>Hệ thống camera hoạt động bền bỉ, ổn định với gói bảo trì chuyên nghiệp.</p>'
                        '<ul><li>Vệ sinh lens và vỏ camera</li>'
                        '<li>Kiểm tra kết nối, nguồn điện</li>'
                        '<li>Cập nhật firmware mới nhất</li>'
                        '<li>Kiểm tra dữ liệu lưu trữ</li></ul>'
                    ),
                    'icon': 'fas fa-tools',
                    'is_featured': True, 'order': 1, 'color': COLORS['blue'],
                },
                {
                    'name': 'Sửa chữa camera & đầu ghi',
                    'slug': 'sua-chua-camera-dau-ghi',
                    'short_desc': 'Nhận sửa chữa camera IP, camera Analog, đầu ghi NVR/DVR các hãng Hikvision, Dahua, Kbvision.',
                    'description': (
                        '<h3>Dịch vụ sửa chữa nhanh</h3>'
                        '<p>Tiếp nhận và xử lý sự cố trong ngày, có xe đến tận nơi.</p>'
                        '<ul><li>Chẩn đoán miễn phí</li>'
                        '<li>Linh kiện chính hãng</li>'
                        '<li>Bảo hành sau sửa chữa 3 tháng</li>'
                        '<li>Hỗ trợ khẩn cấp 24/7</li></ul>'
                    ),
                    'icon': 'fas fa-wrench',
                    'is_featured': False, 'order': 2, 'color': COLORS['orange'],
                },
            ],
            'tu-van-giai-phap': [
                {
                    'name': 'Tư vấn giải pháp an ninh tổng thể',
                    'slug': 'tu-van-giai-phap-an-ninh-tong-the',
                    'short_desc': 'Khảo sát và thiết kế hệ thống an ninh toàn diện cho toà nhà, khu công nghiệp, resort.',
                    'description': (
                        '<h3>Tư vấn giải pháp từ chuyên gia</h3>'
                        '<p>Đội ngũ kỹ sư có hơn 10 năm kinh nghiệm, thiết kế giải pháp phù hợp ngân sách.</p>'
                        '<ul><li>Khảo sát thực địa miễn phí</li>'
                        '<li>Báo cáo phân tích rủi ro an ninh</li>'
                        '<li>Thiết kế sơ đồ hệ thống chi tiết</li>'
                        '<li>Dự toán chi phí minh bạch</li></ul>'
                    ),
                    'icon': 'fas fa-lightbulb',
                    'is_featured': True, 'order': 1, 'color': COLORS['orange'],
                },
            ],
        }

        for cat_name, cat_slug, cat_icon, cat_color, cat_order in categories:
            cat, created = ServiceCategory.objects.get_or_create(
                slug=cat_slug,
                defaults={'name': cat_name, 'icon': cat_icon, 'order': cat_order, 'is_active': True},
            )
            if created:
                cat.image.save(f'svc_cat_{cat_slug}.jpg', _placeholder(800, 600, cat_color))

            for s in services_data.get(cat_slug, []):
                svc, svc_created = Service.objects.get_or_create(
                    slug=s['slug'],
                    defaults={
                        'category': cat,
                        'name': s['name'],
                        'short_desc': s['short_desc'],
                        'description': s['description'],
                        'icon': s['icon'],
                        'is_featured': s['is_featured'],
                        'is_active': True,
                        'order': s['order'],
                    },
                )
                if svc_created:
                    svc.image.save(f'service_{s["slug"]}.jpg', _placeholder(800, 600, s['color']))

        self.stdout.write('  [OK] Services & Categories')

    def _seed_news(self):
        news_cats = [
            ('Tin tức công ty', 'tin-tuc-cong-ty', 1),
            ('Kiến thức camera', 'kien-thuc-camera', 2),
            ('Khuyến mãi', 'khuyen-mai', 3),
        ]
        cat_objs = {}
        for name, slug, order in news_cats:
            cat, _ = NewsCategory.objects.get_or_create(
                slug=slug, defaults={'name': name, 'order': order, 'is_active': True}
            )
            cat_objs[slug] = cat

        articles = [
            {
                'title': 'Top 5 Camera IP Tốt Nhất Cho Gia Đình Năm 2024',
                'slug': 'top-5-camera-ip-tot-nhat-cho-gia-dinh-2024',
                'category': 'kien-thuc-camera',
                'summary': 'Tổng hợp 5 mẫu camera IP bán chạy nhất, giá tốt nhất phù hợp cho gia đình Việt Nam năm 2024.',
                'content': (
                    '<p>Chọn camera IP phù hợp cho gia đình không phải là điều dễ dàng khi thị trường '
                    'có hàng trăm model khác nhau. Bài viết này giúp bạn chọn đúng nhất.</p>'
                    '<h3>1. Hikvision DS-2CD2143G2-I — Tổng thể tốt nhất</h3>'
                    '<p>Camera 4MP với công nghệ AcuSense giúp giảm thiểu báo động giả. '
                    'Hồng ngoại 40m, chống bụi nước IP67. Giá tham khảo: 1.200.000đ.</p>'
                    '<h3>2. Dahua IPC-HDW2831T-AS — Chất lượng 8MP giá hợp lý</h3>'
                    '<p>Độ phân giải 8MP cực nét, tích hợp microphone thu âm. '
                    'Lý tưởng cho giám sát nội thất. Giá tham khảo: 1.500.000đ.</p>'
                    '<h3>3. Kbvision KX-C2012SL2 — Giá rẻ nhất phân khúc</h3>'
                    '<p>Lựa chọn ngân sách 2MP với hồng ngoại 30m. Phù hợp cho gia đình '
                    'cần nhiều điểm giám sát với chi phí thấp. Giá: 650.000đ.</p>'
                    '<h3>Kết luận</h3>'
                    '<p>Liên hệ ADCARE để được tư vấn miễn phí và nhận báo giá tốt nhất!</p>'
                ),
                'author': 'Kỹ sư ADCARE',
                'is_featured': True,
                'color': COLORS['blue'],
            },
            {
                'title': 'Hướng Dẫn Lắp Đặt Camera Ngoài Trời Đúng Kỹ Thuật',
                'slug': 'huong-dan-lap-dat-camera-ngoai-troi-dung-ky-thuat',
                'category': 'kien-thuc-camera',
                'summary': 'Những điều cần lưu ý khi lắp đặt camera ngoài trời: vị trí, góc nhìn, chống nước và đi dây.',
                'content': (
                    '<p>Camera ngoài trời cần được lắp đặt đúng kỹ thuật để đảm bảo hoạt động '
                    'ổn định trong mọi điều kiện thời tiết.</p>'
                    '<h3>Chọn vị trí lắp đặt</h3>'
                    '<p>Độ cao lý tưởng là 2.5–3.5m so với mặt đất. Tránh hướng ánh sáng mặt trời '
                    'chiếu trực tiếp vào lens. Góc nhìn nên bao quát tối đa khu vực cần giám sát.</p>'
                    '<h3>Xử lý chống nước cho đầu dây</h3>'
                    '<p>Dùng băng keo tự dính chuyên dụng quấn đầu nối RJ45. '
                    'Đi dây trong ống nhựa luồn dây để bảo vệ cáp khỏi nắng mưa.</p>'
                    '<h3>Kiểm tra sau lắp đặt</h3>'
                    '<p>Kết nối vào NVR/DVR, điều chỉnh góc camera, kiểm tra hình ảnh ban ngày '
                    'và ban đêm trước khi bàn giao.</p>'
                ),
                'author': 'Kỹ thuật viên ADCARE',
                'is_featured': False,
                'color': COLORS['teal'],
            },
            {
                'title': 'Camera IP và Camera Analog: Nên Dùng Loại Nào?',
                'slug': 'camera-ip-va-camera-analog-nen-dung-loai-nao',
                'category': 'kien-thuc-camera',
                'summary': 'So sánh chi tiết camera IP và camera Analog về chất lượng hình ảnh, chi phí, độ khó lắp đặt.',
                'content': (
                    '<p>Đây là câu hỏi phổ biến nhất khi khách hàng bắt đầu xây dựng hệ thống camera.</p>'
                    '<h3>Camera Analog (HDCVI/AHD/TVI)</h3>'
                    '<p><strong>Ưu điểm:</strong> Giá rẻ hơn 30–40%, đi dây đồng trục sẵn có, '
                    'cài đặt đơn giản hơn, phù hợp nâng cấp hệ thống cũ.</p>'
                    '<p><strong>Nhược điểm:</strong> Độ phân giải tối đa 5MP, không có tính năng AI, '
                    'khoảng cách truyền tín hiệu giới hạn 500m.</p>'
                    '<h3>Camera IP (Network Camera)</h3>'
                    '<p><strong>Ưu điểm:</strong> Độ phân giải từ 2MP đến 32MP, có AI nhận diện người/xe, '
                    'truyền tín hiệu qua mạng LAN/WiFi không giới hạn khoảng cách.</p>'
                    '<p><strong>Nhược điểm:</strong> Giá cao hơn, cần hạ tầng mạng tốt.</p>'
                    '<h3>Khuyến nghị của ADCARE</h3>'
                    '<p>Dự án mới: chọn camera IP. Nâng cấp hệ thống cũ: có thể dùng Analog '
                    'để tiết kiệm chi phí. Liên hệ để được tư vấn cụ thể!</p>'
                ),
                'author': 'Chuyên gia ADCARE',
                'is_featured': False,
                'color': COLORS['purple'],
            },
            {
                'title': 'ADCARE Khai Trương Showroom Mới Tại Quận 7 TP.HCM',
                'slug': 'adcare-khai-truong-showroom-moi-tai-quan-7-tphcm',
                'category': 'tin-tuc-cong-ty',
                'summary': 'ADCARE Việt Nam chính thức khai trương showroom thứ 2 tại 123 Nguyễn Văn Linh, Q.7 với không gian trưng bày hơn 50 mẫu camera.',
                'content': (
                    '<p>Ngày 15/01/2024, ADCARE Việt Nam chính thức khai trương showroom thứ 2 '
                    'tại 123 Nguyễn Văn Linh, Phường Tân Phong, Quận 7, TP. Hồ Chí Minh.</p>'
                    '<h3>Không gian trưng bày hiện đại</h3>'
                    '<p>Showroom rộng 150m² với hơn 50 mẫu camera IP, Analog, PTZ đang hoạt động '
                    'thực tế giúp khách hàng trải nghiệm trực tiếp chất lượng hình ảnh.</p>'
                    '<h3>Ưu đãi khai trương</h3>'
                    '<p>Từ ngày 15/01 đến 28/02/2024, khách hàng mua hàng tại showroom mới được '
                    'giảm 10% trên tổng giá trị đơn hàng và miễn phí lắp đặt trong bán kính 10km.</p>'
                    '<h3>Thông tin liên hệ</h3>'
                    '<p>Địa chỉ: 123 Nguyễn Văn Linh, Q.7, TP.HCM<br>'
                    'Hotline: 0901 234 567<br>'
                    'Giờ mở cửa: 8:00 – 17:30 (Thứ 2 – Thứ 7)</p>'
                ),
                'author': 'Ban biên tập ADCARE',
                'is_featured': True,
                'color': COLORS['green'],
            },
            {
                'title': 'Khuyến Mãi Tháng 3: Giảm 15% Camera Dahua — Tặng Ổ Cứng 1TB',
                'slug': 'khuyen-mai-thang-3-giam-15-dahua',
                'category': 'khuyen-mai',
                'summary': 'Toàn bộ camera Dahua giảm 15%, mua đầu ghi NVR tặng kèm ổ cứng WD Purple 1TB. Áp dụng đến hết 31/03/2024.',
                'content': (
                    '<p>ADCARE Việt Nam triển khai chương trình khuyến mãi đặc biệt tháng 3/2024 '
                    'dành cho khách hàng mua sản phẩm Dahua chính hãng.</p>'
                    '<h3>Chi tiết ưu đãi</h3>'
                    '<ul>'
                    '<li>Giảm 15% toàn bộ camera IP và Analog Dahua</li>'
                    '<li>Mua NVR Dahua 8 kênh trở lên: tặng ổ cứng WD Purple 1TB</li>'
                    '<li>Lắp đặt trọn gói từ 4 camera: miễn phí công lắp đặt</li>'
                    '</ul>'
                    '<h3>Điều kiện áp dụng</h3>'
                    '<p>Áp dụng cho đơn hàng từ ngày 01/03 đến 31/03/2024. '
                    'Không áp dụng đồng thời với các chương trình khuyến mãi khác.</p>'
                    '<p><strong>Hotline đặt hàng: 0901 234 567</strong></p>'
                ),
                'author': 'Ban kinh doanh ADCARE',
                'is_featured': False,
                'color': COLORS['accent'],
            },
        ]

        for a in articles:
            art, created = Article.objects.get_or_create(
                slug=a['slug'],
                defaults={
                    'category': cat_objs[a['category']],
                    'title': a['title'],
                    'summary': a['summary'],
                    'content': a['content'],
                    'author': a['author'],
                    'status': 'published',
                    'is_featured': a['is_featured'],
                    'published_at': timezone.now(),
                },
            )
            if created:
                art.image.save(f'news_{a["slug"][:30]}.jpg', _placeholder(1200, 630, a['color']))

        self.stdout.write('  [OK] News & Articles')

    def _seed_partners(self):
        partners = [
            ('Hikvision', 'supplier', COLORS['blue'], 1),
            ('Dahua Technology', 'supplier', COLORS['teal'], 2),
            ('Axis Communications', 'partner', COLORS['orange'], 3),
            ('Bosch Security', 'partner', COLORS['gray'], 4),
            ('Kbvision', 'supplier', COLORS['purple'], 5),
            ('Viettel', 'customer', COLORS['dark'], 6),
        ]
        for name, ptype, color, order in partners:
            obj, created = Partner.objects.get_or_create(
                name=name,
                defaults={'partner_type': ptype, 'order': order, 'is_active': True},
            )
            if created:
                obj.logo.save(f'partner_{name.lower().replace(" ", "_")}.jpg', _placeholder(300, 150, color))

        self.stdout.write('  [OK] Partners')
