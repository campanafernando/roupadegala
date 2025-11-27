from django.db import migrations
from django.utils import timezone
from datetime import timedelta


def fix_production_dates(apps, schema_editor):
    """
    Corrige as production_date que foram salvas com timezone errado.
    Subtrai 1 dia das datas que estão no futuro em relação ao dia em que foram criadas.
    """
    ServiceOrder = apps.get_model("service_control", "ServiceOrder")
    
    # Buscar todas as OS com production_date preenchida
    orders_with_production_date = ServiceOrder.objects.filter(
        production_date__isnull=False
    )
    
    for order in orders_with_production_date:
        # Subtrai 1 dia da production_date para corrigir o timezone
        order.production_date = order.production_date - timedelta(days=1)
        order.save()
        print(f"OS {order.id}: production_date corrigida para {order.production_date}")


def reverse_fix(apps, schema_editor):
    """
    Reverter a correção (adiciona 1 dia de volta)
    """
    ServiceOrder = apps.get_model("service_control", "ServiceOrder")
    
    orders_with_production_date = ServiceOrder.objects.filter(
        production_date__isnull=False
    )
    
    for order in orders_with_production_date:
        order.production_date = order.production_date + timedelta(days=1)
        order.save()


class Migration(migrations.Migration):

    dependencies = [
        ("service_control", "0025_alter_production_date_to_date_field"),
    ]

    operations = [
        migrations.RunPython(fix_production_dates, reverse_fix),
    ]

