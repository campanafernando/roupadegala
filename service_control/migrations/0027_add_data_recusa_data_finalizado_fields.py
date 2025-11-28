"""Generated manually to add data_recusa and data_finalizado fields

Adds two DateTimeFields to `ServiceOrder` to store refusal and finalized timestamps.
"""

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("service_control", "0026_fix_production_date_utc_offset"),
    ]

    operations = [
        migrations.AddField(
            model_name="serviceorder",
            name="data_recusa",
            field=models.DateTimeField(
                blank=True,
                help_text="Data e hora em que a OS foi recusada",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="serviceorder",
            name="data_finalizado",
            field=models.DateTimeField(
                blank=True,
                help_text="Data e hora em que a OS foi finalizada",
                null=True,
            ),
        ),
    ]
