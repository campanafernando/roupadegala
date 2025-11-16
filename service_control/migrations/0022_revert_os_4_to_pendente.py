# Generated manually to reverter OS ID 4 de EM_PRODUCAO para PENDENTE

from django.db import migrations


def revert_os_4_to_pendente(apps, schema_editor):
    """Voltar OS ID 4 de EM_PRODUCAO para PENDENTE"""
    ServiceOrder = apps.get_model("service_control", "ServiceOrder")
    ServiceOrderPhase = apps.get_model("service_control", "ServiceOrderPhase")

    try:
        # Buscar a OS ID 4
        os = ServiceOrder.objects.get(id=4)

        # Verificar se está em EM_PRODUCAO
        if os.service_order_phase and os.service_order_phase.name == "EM_PRODUCAO":
            # Buscar fase PENDENTE
            pendente_phase = ServiceOrderPhase.objects.filter(name="PENDENTE").first()

            if pendente_phase:
                os.service_order_phase = pendente_phase
                os.save()
                print(f"OS {os.id} revertida de EM_PRODUCAO para PENDENTE")
            else:
                print("Fase PENDENTE não encontrada")
        else:
            print(f"OS {os.id} não está em EM_PRODUCAO, sem alteração")
    except ServiceOrder.DoesNotExist:
        print("OS ID 4 não existe, sem alteração")


def reverse_revert(apps, schema_editor):
    """Reverso: não faz nada, pois é uma correção pontual"""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("service_control", "0021_add_em_producao_phase"),
    ]

    operations = [
        migrations.RunPython(
            revert_os_4_to_pendente,
            reverse_revert,
        ),
    ]
