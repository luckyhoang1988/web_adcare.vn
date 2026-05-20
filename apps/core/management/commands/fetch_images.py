import urllib.request

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from apps.core.models import Slider, AboutSection
from apps.products.models import ProductCategory, Product
from apps.services.models import ServiceCategory, Service
from apps.news.models import Article
from apps.partners.models import Partner


def _fetch(seed, w, h, filename):
    url = f'https://picsum.photos/seed/{seed}/{w}/{h}'
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = resp.read()
        return ContentFile(data, name=filename)
    except Exception as e:
        return None


class Command(BaseCommand):
    help = 'Download real photos from picsum.photos for all content'

    def handle(self, *args, **options):
        self.stdout.write('Downloading images...')
        errors = 0

        # Sliders (1920x800) — landscape/city vibes
        seeds = {'Giai phap Camera': 'city', 'Dich Vu Lap Dat': 'building', 'Camera Hikvision': 'technology'}
        for obj in Slider.objects.all():
            seed = next((v for k, v in seeds.items() if k in obj.title), obj.pk)
            cf = _fetch(seed, 1920, 800, f'slider_{obj.pk}.jpg')
            if cf:
                obj.image.delete(save=False)
                obj.image.save(f'slider_{obj.pk}.jpg', cf, save=True)
                self.stdout.write('  [OK] Slider: ' + str(obj.pk))
            else:
                errors += 1

        # About section (700x500)
        for obj in AboutSection.objects.all():
            cf = _fetch('office', 700, 500, f'about_{obj.pk}.jpg')
            if cf:
                obj.image.delete(save=False)
                obj.image.save(f'about_{obj.pk}.jpg', cf, save=True)
                self.stdout.write('  [OK] About: ' + str(obj.pk))
            else:
                errors += 1

        # Product categories (800x600)
        cat_seeds = {
            'camera-ip': 'digital',
            'camera-analog': 'electronics',
            'camera-ptz': 'tech',
            'dau-ghi-hinh': 'computer',
            'phu-kien-cap': 'cable',
        }
        for obj in ProductCategory.objects.all():
            seed = cat_seeds.get(obj.slug, obj.slug)
            cf = _fetch(seed, 800, 600, f'cat_{obj.slug}.jpg')
            if cf:
                obj.image.delete(save=False)
                obj.image.save(f'cat_{obj.slug}.jpg', cf, save=True)
                self.stdout.write('  [OK] Category: ' + str(obj.pk))
            else:
                errors += 1

        # Products (800x600) — use slug as seed for consistent results
        prod_seeds = {
            'camera-ip-hikvision-ds-2cd2143g2-i': 'security1',
            'camera-ip-dahua-ipc-hdw2831t-as': 'security2',
            'camera-ip-axis-p3245-v': 'security3',
            'camera-analog-hikvision-ds-2ce16d0t-irf': 'surveillance1',
            'camera-analog-dahua-hac-hdw1500tl-a': 'surveillance2',
            'camera-ptz-hikvision-ds-2de4425iwg-e': 'camera1',
            'camera-ptz-dahua-sd49425xb-hnr': 'camera2',
            'nvr-hikvision-ds-7608ni-q1': 'electronics1',
            'dvr-dahua-xvr5108hs-i3': 'electronics2',
            'cap-mang-sftp-cat6-ngoai-troi-305m': 'cable1',
            'nguon-tong-12v-10a-cho-camera': 'power1',
        }
        for obj in Product.objects.all():
            seed = prod_seeds.get(obj.slug, f'product{obj.pk}')
            cf = _fetch(seed, 800, 600, f'product_{obj.pk}.jpg')
            if cf:
                obj.image.delete(save=False)
                obj.image.save(f'product_{obj.pk}.jpg', cf, save=True)
                self.stdout.write('  [OK] Product: ' + str(obj.pk))
            else:
                errors += 1

        # Service categories (800x600)
        svc_cat_seeds = {
            'lap-dat-he-thong': 'worker',
            'bao-tri-sua-chua': 'repair',
            'tu-van-giai-phap': 'meeting',
        }
        for obj in ServiceCategory.objects.all():
            seed = svc_cat_seeds.get(obj.slug, obj.slug)
            cf = _fetch(seed, 800, 600, f'svccat_{obj.pk}.jpg')
            if cf:
                obj.image.delete(save=False)
                obj.image.save(f'svccat_{obj.pk}.jpg', cf, save=True)
                self.stdout.write('  [OK] ServiceCat: ' + str(obj.pk))
            else:
                errors += 1

        # Services (800x600)
        svc_seeds = {
            'lap-dat-camera-quan-sat': 'installation1',
            'lap-dat-he-thong-bao-dong': 'installation2',
            'lap-dat-kiem-soat-ra-vao': 'installation3',
            'bao-tri-camera-dinh-ky': 'maintenance1',
            'sua-chua-camera-dau-ghi': 'maintenance2',
            'tu-van-giai-phap-an-ninh-tong-the': 'consultation',
        }
        for obj in Service.objects.all():
            seed = svc_seeds.get(obj.slug, f'service{obj.pk}')
            cf = _fetch(seed, 800, 600, f'service_{obj.pk}.jpg')
            if cf:
                obj.image.delete(save=False)
                obj.image.save(f'service_{obj.pk}.jpg', cf, save=True)
                self.stdout.write('  [OK] Service: ' + str(obj.pk))
            else:
                errors += 1

        # Articles (1200x630)
        article_seeds = {
            'top-5-camera-ip-tot-nhat-cho-gia-dinh-2024': 'tech10',
            'huong-dan-lap-dat-camera-ngoai-troi-dung-ky-thuat': 'tech11',
            'camera-ip-va-camera-analog-nen-dung-loai-nao': 'tech12',
            'adcare-khai-truong-showroom-moi-tai-quan-7-tphcm': 'office10',
            'khuyen-mai-thang-3-giam-15-dahua': 'sale10',
        }
        for obj in Article.objects.all():
            seed = article_seeds.get(obj.slug, f'news{obj.pk}')
            cf = _fetch(seed, 1200, 630, f'article_{obj.pk}.jpg')
            if cf:
                obj.image.delete(save=False)
                obj.image.save(f'article_{obj.pk}.jpg', cf, save=True)
                self.stdout.write('  [OK] Article: ' + str(obj.pk))
            else:
                errors += 1

        # Partners — dùng gradient màu khác nhau thay ảnh thật
        # (logo thường là ảnh vector, dùng picsum sẽ trông lạ)
        partner_seeds = {
            'Hikvision': 'brand1',
            'Dahua Technology': 'brand2',
            'Axis Communications': 'brand3',
            'Bosch Security': 'brand4',
            'Kbvision': 'brand5',
            'Viettel': 'brand6',
        }
        for obj in Partner.objects.all():
            seed = partner_seeds.get(obj.name, f'partner{obj.pk}')
            cf = _fetch(seed, 300, 150, f'partner_{obj.pk}.jpg')
            if cf:
                obj.logo.delete(save=False)
                obj.logo.save(f'partner_{obj.pk}.jpg', cf, save=True)
                self.stdout.write('  [OK] Partner: ' + str(obj.pk))
            else:
                errors += 1

        if errors:
            self.stdout.write(self.style.WARNING(f'Done with {errors} error(s). Check your internet connection.'))
        else:
            self.stdout.write(self.style.SUCCESS('All images downloaded! Reload http://localhost:8000'))
