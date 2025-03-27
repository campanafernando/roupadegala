import os

from django.conf import settings
from django.db import connection, migrations


def load_products_sql(apps, schema_editor):
    """
    Executa o script 'products.sql' apenas se as principais tabelas relacionadas a produto estiverem vazias.
    """
    sql_path = os.path.join(settings.BASE_DIR, "seed_aux_files", "products.sql")

    if not os.path.exists(sql_path):
        print(f"⚠️ Arquivo não encontrado: {sql_path}")
        return

    # Tabelas a verificar antes de executar
    tables_to_check = [
        "products_brand",
        "products_fabric",
        "products_color_catalogue",
        "products_color_intensity",
        "products_color",
        "products_pattern",
        "products_button",
        "products_lapel",
        "products_type",
        "products_model",
    ]

    with connection.cursor() as cursor:
        any_table_has_data = False
        for table in tables_to_check:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            if count > 0:
                print(f"ℹ️ Tabela '{table}' já possui dados ({count} registros).")
                any_table_has_data = True

        if any_table_has_data:
            print(
                "🚫 Dados já existentes nas tabelas. 'products.sql' não será executado."
            )
            return

        # Executa os inserts do arquivo
        with open(sql_path, "r", encoding="utf-8") as f:
            sql_script = f.read()

        sql_statements = sql_script.split(";")

        for statement in sql_statements:
            if statement.strip():
                cursor.execute(statement)

        print("✅ Script 'products.sql' executado com sucesso.")


class Migration(migrations.Migration):

    dependencies = [
        # Aponte para a última migração anterior neste app
        ("products", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(load_products_sql),
    ]
