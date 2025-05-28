import os

from django.conf import settings
from django.db import connection, migrations


def load_cities_from_sql(apps, schema_editor):
    """
    Insere os dados do arquivo 'cities.sql' na tabela 'city' apenas se a tabela estiver vazia.
    """
    City = apps.get_model("accounts", "City")  # Garante que a tabela já existe
    cities_sql_path = os.path.join(settings.BASE_DIR, ".aux_files", "cities.sql")

    if not os.path.exists(cities_sql_path):
        print(f"⚠️ Arquivo não encontrado: {cities_sql_path}")
        return

    with connection.cursor() as cursor:
        cursor.execute(
            f"SELECT COUNT(*) FROM {City._meta.db_table}"
        )  # Usa o nome real da tabela
        count = cursor.fetchone()[0]

        if count == 0:
            with open(cities_sql_path, "r", encoding="utf-8") as f:
                sql_script = f.read()
                sql_statements = sql_script.split(";")
                for statement in sql_statements:
                    if statement.strip():
                        cursor.execute(statement)


def insert_person_types(apps, schema_editor):
    """
    Insere os tipos de pessoa: ADMIN, COLLABORATOR, CUSTOMER caso ainda não existam.
    """
    PersonType = apps.get_model(
        "accounts", "PersonType"
    )  # Garante que a tabela já existe
    existing_types = {
        pt.type for pt in PersonType.objects.all()
    }  # Obtém os tipos já existentes

    types_to_insert = ["ADMINISTRADOR", "ATENDENTE", "CLIENTE"]

    for person_type in types_to_insert:
        if person_type not in existing_types:
            PersonType.objects.create(type=person_type)
            print(f"✅ Inserido: {person_type}")


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0001_initial"),  # Garante que a primeira migração já rodou
    ]

    operations = [
        migrations.RunPython(load_cities_from_sql),
        migrations.RunPython(insert_person_types),
    ]
