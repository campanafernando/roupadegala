# Generated manually - Adiciona campo esta_atrasada

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("service_control", "0022_revert_os_4_to_pendente"),
    ]

    operations = [
        migrations.AddField(
            model_name="serviceorder",
            name="esta_atrasada",
            field=models.BooleanField(
                default=False,
                help_text="Flag indicando se a OS está atrasada (retirada ou devolução)",
            ),
        ),
    ]
