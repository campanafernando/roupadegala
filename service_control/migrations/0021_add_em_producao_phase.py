# Generated manually to add EM_PRODUCAO phase

from django.db import migrations


def add_em_producao_phase(apps, schema_editor):
    ServiceOrderPhase = apps.get_model("service_control", "ServiceOrderPhase")

    # Verificar se a fase já existe para evitar duplicação
    if not ServiceOrderPhase.objects.filter(name="EM_PRODUCAO").exists():
        ServiceOrderPhase.objects.create(name="EM_PRODUCAO")


def remove_em_producao_phase(apps, schema_editor):
    ServiceOrderPhase = apps.get_model("service_control", "ServiceOrderPhase")

    # Remover a fase se existir
    ServiceOrderPhase.objects.filter(name="EM_PRODUCAO").delete()


class Migration(migrations.Migration):

    dependencies = [
        ("service_control", "0020_add_refusal_reason_model"),
    ]

    operations = [
        migrations.RunPython(
            add_em_producao_phase,
            remove_em_producao_phase,
        ),
    ]
