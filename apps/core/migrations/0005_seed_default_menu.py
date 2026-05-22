from django.db import migrations

DEFAULT_MENU = [
    {'title': 'Trang chủ',    'item_type': 'home',     'order': 1},
    {'title': 'Về chúng tôi', 'item_type': 'about',    'order': 2},
    {'title': 'Sản phẩm',     'item_type': 'products', 'order': 3},
    {'title': 'Dịch vụ',      'item_type': 'services', 'order': 4},
    {'title': 'Dự án',        'item_type': 'projects', 'order': 5},
    {'title': 'Tin tức',      'item_type': 'news',     'order': 6},
    {'title': 'Liên hệ',      'item_type': 'contact',  'order': 7},
]


def seed_menu(apps, schema_editor):
    MenuItem = apps.get_model('core', 'MenuItem')
    if not MenuItem.objects.exists():
        for item in DEFAULT_MENU:
            MenuItem.objects.create(**item)


def unseed_menu(apps, schema_editor):
    apps.get_model('core', 'MenuItem').objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_add_menuitem'),
    ]

    operations = [
        migrations.RunPython(seed_menu, unseed_menu),
    ]
