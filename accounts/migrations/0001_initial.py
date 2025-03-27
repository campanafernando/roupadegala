# Generated by Django 5.1.4 on 2025-03-16 20:57

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="City",
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
                ("date_created", models.DateTimeField(auto_now_add=True, null=True)),
                ("date_updated", models.DateTimeField(blank=True, null=True)),
                ("date_canceled", models.DateTimeField(blank=True, null=True)),
                ("code", models.CharField(max_length=255)),
                ("name", models.CharField(db_index=True, max_length=255)),
                ("uf", models.CharField(max_length=255)),
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
            ],
            options={
                "db_table": "city",
            },
        ),
        migrations.CreateModel(
            name="Person",
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
                ("date_created", models.DateTimeField(auto_now_add=True, null=True)),
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
                ("date_updated", models.DateTimeField(blank=True, null=True)),
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
                ("date_canceled", models.DateTimeField(blank=True, null=True)),
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
                ("name", models.CharField(max_length=255)),
                (
                    "cpf",
                    models.CharField(blank=True, max_length=20, null=True, unique=True),
                ),
                (
                    "user",
                    models.OneToOneField(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "person",
            },
        ),
        migrations.CreateModel(
            name="PersonsAdresses",
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
                ("date_created", models.DateTimeField(auto_now_add=True, null=True)),
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
                ("date_updated", models.DateTimeField(blank=True, null=True)),
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
                ("date_canceled", models.DateTimeField(blank=True, null=True)),
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
                ("address", models.CharField(max_length=255)),
                ("neighborhood", models.CharField(max_length=255)),
                (
                    "city",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="accounts.city"
                    ),
                ),
                (
                    "person",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="accounts.person",
                    ),
                ),
            ],
            options={
                "db_table": "persons_adresses",
            },
        ),
        migrations.CreateModel(
            name="PersonsContacts",
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
                ("date_created", models.DateTimeField(auto_now_add=True, null=True)),
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
                ("date_updated", models.DateTimeField(blank=True, null=True)),
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
                ("date_canceled", models.DateTimeField(blank=True, null=True)),
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
                ("phone", models.CharField(max_length=255)),
                (
                    "email",
                    models.EmailField(
                        blank=True, max_length=254, null=True, unique=True
                    ),
                ),
                (
                    "person",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="accounts.person",
                    ),
                ),
            ],
            options={
                "db_table": "persons_contacts",
            },
        ),
        migrations.CreateModel(
            name="PersonType",
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
                ("date_created", models.DateTimeField(auto_now_add=True, null=True)),
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
                ("date_updated", models.DateTimeField(blank=True, null=True)),
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
                ("date_canceled", models.DateTimeField(blank=True, null=True)),
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
                ("type", models.CharField(max_length=50, unique=True)),
            ],
            options={
                "db_table": "person_type",
            },
        ),
        migrations.AddField(
            model_name="person",
            name="person_type",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="accounts.persontype"
            ),
        ),
        migrations.AddIndex(
            model_name="city",
            index=models.Index(fields=["name"], name="city_name_88111b_idx"),
        ),
    ]
