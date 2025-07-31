# Generated manually to add data_retirado field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("service_control", "0012_add_data_devolvido_field"),
    ]

    operations = [
        migrations.AddField(
            model_name="serviceorder",
            name="data_retirado",
            field=models.DateTimeField(
                blank=True,
                help_text="Data e hora em que foi retirado",
                null=True,
            ),
        ),
    ]
