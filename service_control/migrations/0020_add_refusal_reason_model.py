# Generated manually

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("service_control", "0019_remove_serviceorder_event_date_and_more"),
    ]

    operations = [
        # Criar tabela RefusalReason
        migrations.CreateModel(
            name="RefusalReason",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "date_created",
                    models.DateTimeField(auto_now_add=True, blank=True, null=True),
                ),
                ("date_updated", models.DateTimeField(blank=True, null=True)),
                ("date_canceled", models.DateTimeField(blank=True, null=True)),
                (
                    "name",
                    models.CharField(
                        help_text="Nome do motivo de recusa",
                        max_length=100,
                        unique=True,
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="created_%(class)s",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "updated_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="updated_%(class)s",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "canceled_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="canceled_%(class)s",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Motivo de Recusa",
                "verbose_name_plural": "Motivos de Recusa",
                "db_table": "refusal_reasons",
            },
        ),
        # Adicionar campo justification_reason na ServiceOrder
        migrations.AddField(
            model_name="serviceorder",
            name="justification_reason",
            field=models.ForeignKey(
                blank=True,
                help_text="Motivo de recusa/cancelamento",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="service_orders",
                to="service_control.refusalreason",
            ),
        ),
        # Inserir os motivos padrão
        migrations.RunPython(
            code=lambda apps, schema_editor: [
                apps.get_model("service_control", "RefusalReason").objects.create(
                    name="CANCELAMENTO DO EVENTO"
                ),
                apps.get_model("service_control", "RefusalReason").objects.create(
                    name="DESISTÊNCIA"
                ),
                apps.get_model("service_control", "RefusalReason").objects.create(
                    name="MUDANÇA DE DATA DO EVENTO"
                ),
                apps.get_model("service_control", "RefusalReason").objects.create(
                    name="OUTROS"
                ),
            ],
            reverse_code=migrations.RunPython.noop,
        ),
    ]
