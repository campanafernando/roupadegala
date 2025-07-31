# Generated manually to add AGUARDANDO_DEVOLUCAO phase

from django.db import migrations


def add_aguardando_devolucao_phase(apps, schema_editor):
    ServiceOrderPhase = apps.get_model("service_control", "ServiceOrderPhase")

    # Verificar se a fase já existe para evitar duplicação
    if not ServiceOrderPhase.objects.filter(name="AGUARDANDO_DEVOLUCAO").exists():
        ServiceOrderPhase.objects.create(name="AGUARDANDO_DEVOLUCAO")


def remove_aguardando_devolucao_phase(apps, schema_editor):
    ServiceOrderPhase = apps.get_model("service_control", "ServiceOrderPhase")

    # Remover a fase se existir
    ServiceOrderPhase.objects.filter(name="AGUARDANDO_DEVOLUCAO").delete()


class Migration(migrations.Migration):

    dependencies = [
        ("service_control", "0010_serviceorder_service_type"),
    ]

    operations = [
        migrations.RunPython(
            add_aguardando_devolucao_phase,
            remove_aguardando_devolucao_phase,
        ),
    ]
