# Generated manually to add data_devolvido field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("service_control", "0011_add_aguardando_devolucao_phase"),
    ]

    operations = [
        migrations.AddField(
            model_name="serviceorder",
            name="data_devolvido",
            field=models.DateTimeField(
                blank=True,
                help_text="Data e hora em que foi devolvido",
                null=True,
            ),
        ),
    ]
