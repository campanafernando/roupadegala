from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.db import migrations


def create_initial_admin_users(apps, schema_editor):
    User = apps.get_model("auth", "User")
    Person = apps.get_model("accounts", "Person")
    PersonType = apps.get_model("accounts", "PersonType")

    # Crie (ou pegue) o tipo de pessoa "ADMINISTRADOR"
    admin_type, _ = PersonType.objects.get_or_create(type="ADMINISTRADOR")

    # Lista de usuários para serem criados
    users_data = [
        {"cpf": "10484917650", "name": "NICHOLAS LOUREIRO", "username": "10484917650"},
        {"cpf": "14387060654", "name": "FERNANDO CAMPANA", "username": "14387060654"},
        {
            "cpf": "11171552696",
            "name": "MARCO TULIO RODRIGUES",
            "username": "11171552696",
        },
    ]

    for data in users_data:
        user = User.objects.create(
            username=data["username"],
            password=make_password(
                settings.ADMIN_PASSWORD
            ),  # Altere conforme necessário
            is_active=True,
        )
        Person.objects.create(
            user=user,
            name=data["name"],
            cpf=data["cpf"],
            person_type=admin_type,
        )


class Migration(migrations.Migration):

    dependencies = [
        (
            "accounts",
            "0003_rename_address_personsadresses_cep_and_more",
        ),  # Altere para o nome da última migration
    ]

    operations = [
        migrations.RunPython(create_initial_admin_users),
    ]
