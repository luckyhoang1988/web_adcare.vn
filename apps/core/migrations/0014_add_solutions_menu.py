from django.db import migrations
from django.db.models import F


def add_solutions_menu(apps, schema_editor):
    MenuItem = apps.get_model('core', 'MenuItem')
    if MenuItem.objects.filter(item_type='solutions').exists():
        return
    services = (MenuItem.objects
                .filter(item_type='services', parent__isnull=True)
                .order_by('order').first())
    if services:
        # Chừa chỗ ngay sau "Dịch vụ": đẩy các menu cấp 1 phía sau lùi 1 bậc
        MenuItem.objects.filter(parent__isnull=True, order__gt=services.order).update(order=F('order') + 1)
        new_order = services.order + 1
    else:
        last = MenuItem.objects.filter(parent__isnull=True).order_by('-order').first()
        new_order = (last.order + 1) if last else 0
    MenuItem.objects.create(
        title='Giải pháp', item_type='solutions', order=new_order, is_active=True,
    )


def remove_solutions_menu(apps, schema_editor):
    MenuItem = apps.get_model('core', 'MenuItem')
    MenuItem.objects.filter(item_type='solutions').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_alter_menuitem_item_type'),
    ]

    operations = [
        migrations.RunPython(add_solutions_menu, remove_solutions_menu),
    ]
