# Generated manually to add ATRASADO phase
from django.db import migrations


def add_atrasado_phase(apps, schema_editor):
    ServiceOrderPhase = apps.get_model("service_control", "ServiceOrderPhase")
    if not ServiceOrderPhase.objects.filter(name="ATRASADO").exists():
        ServiceOrderPhase.objects.create(name="ATRASADO")


def remove_atrasado_phase(apps, schema_editor):
    ServiceOrderPhase = apps.get_model("service_control", "ServiceOrderPhase")
    ServiceOrderPhase.objects.filter(name="ATRASADO").delete()


class Migration(migrations.Migration):

    dependencies = [
        ("service_control", "0014_add_aguardando_retirada_phase"),
    ]

    operations = [
        migrations.RunPython(
            add_atrasado_phase,
            remove_atrasado_phase,
        ),
    ]
