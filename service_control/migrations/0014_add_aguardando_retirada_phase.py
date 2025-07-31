# Generated manually to add AGUARDANDO_RETIRADA phase

from django.db import migrations


def add_aguardando_retirada_phase(apps, schema_editor):
    ServiceOrderPhase = apps.get_model("service_control", "ServiceOrderPhase")

    # Verificar se a fase já existe para evitar duplicação
    if not ServiceOrderPhase.objects.filter(name="AGUARDANDO_RETIRADA").exists():
        ServiceOrderPhase.objects.create(name="AGUARDANDO_RETIRADA")


def remove_aguardando_retirada_phase(apps, schema_editor):
    ServiceOrderPhase = apps.get_model("service_control", "ServiceOrderPhase")

    # Remover a fase se existir
    ServiceOrderPhase.objects.filter(name="AGUARDANDO_RETIRADA").delete()


class Migration(migrations.Migration):

    dependencies = [
        ("service_control", "0013_add_data_retirado_field"),
    ]

    operations = [
        migrations.RunPython(
            add_aguardando_retirada_phase,
            remove_aguardando_retirada_phase,
        ),
    ]
