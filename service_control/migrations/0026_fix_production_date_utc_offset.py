from django.db import migrations
from datetime import timedelta, date


def fix_production_dates_utc_offset(apps, schema_editor):
    """
    Corrige as production_date que foram salvas usando timezone.now().date()
    que retorna a data em UTC. Como São Paulo é UTC-3, qualquer salvamento
    feito após 21h (horário de Brasília) ficou com a data do dia seguinte.

    Esta migration subtrai 1 dia de todas as production_date que estão
    no futuro ou iguais à data de hoje (indicando erro de timezone).
    """
    ServiceOrder = apps.get_model("service_control", "ServiceOrder")
    today = date.today()

    # Buscar OS com production_date preenchida que pode estar errada
    orders = ServiceOrder.objects.filter(production_date__isnull=False)

    count = 0
    for order in orders:
        old_date = order.production_date
        # Se a production_date é maior que order_date, provavelmente está errada
        # Ou se é igual/maior que hoje e foi criada recentemente
        if old_date > order.order_date or old_date >= today:
            order.production_date = old_date - timedelta(days=1)
            order.save(update_fields=["production_date"])
            count += 1
            print(
                f"OS {order.id}: production_date {old_date} -> {order.production_date}"
            )

    if count:
        print(f"Total: {count} OS corrigidas")
    else:
        print("Nenhuma OS com production_date para corrigir")


def reverse_fix(apps, schema_editor):
    """Reverter: adiciona 1 dia de volta"""
    ServiceOrder = apps.get_model("service_control", "ServiceOrder")

    for order in ServiceOrder.objects.filter(production_date__isnull=False):
        order.production_date = order.production_date + timedelta(days=1)
        order.save(update_fields=["production_date"])


class Migration(migrations.Migration):

    dependencies = [
        ("service_control", "0025_alter_production_date_to_date_field"),
    ]

    operations = [
        migrations.RunPython(fix_production_dates_utc_offset, reverse_fix),
    ]
