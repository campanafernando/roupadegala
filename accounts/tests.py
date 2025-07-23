"""
Testes para os endpoints de atualização de dados
"""

import json

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from .models import Person, PersonsContacts, PersonType


class EmployeeUpdateTests(TestCase):
    def setUp(self):
        """Configuração inicial para os testes"""
        self.client = APIClient()

        # Criar tipos de pessoa
        self.admin_type, _ = PersonType.objects.get_or_create(type="ADMINISTRADOR")
        self.attendant_type, _ = PersonType.objects.get_or_create(type="ATENDENTE")
        self.reception_type, _ = PersonType.objects.get_or_create(type="RECEPÇÃO")
        self.client_type, _ = PersonType.objects.get_or_create(type="CLIENTE")

        # Criar usuários e pessoas
        # Admin
        self.admin_user = User.objects.create_user(
            username="12345678901", password="admin123", email="admin@test.com"
        )
        self.admin_person = Person.objects.create(
            user=self.admin_user,
            name="ADMIN TESTE",
            cpf="12345678901",
            person_type=self.admin_type,
        )
        self.admin_contact = PersonsContacts.objects.create(
            person=self.admin_person, email="admin@test.com", phone="(11) 11111-1111"
        )

        # Atendente
        self.attendant_user = User.objects.create_user(
            username="98765432100", password="attendant123", email="attendant@test.com"
        )
        self.attendant_person = Person.objects.create(
            user=self.attendant_user,
            name="ATENDENTE TESTE",
            cpf="98765432100",
            person_type=self.attendant_type,
        )
        self.attendant_contact = PersonsContacts.objects.create(
            person=self.attendant_person,
            email="attendant@test.com",
            phone="(11) 22222-2222",
        )

        # Cliente (para testar restrições)
        self.client_user = User.objects.create_user(
            username="11122233344", password="client123", email="client@test.com"
        )
        self.client_person = Person.objects.create(
            user=self.client_user,
            name="CLIENTE TESTE",
            cpf="11122233344",
            person_type=self.client_type,
        )

    def get_auth_headers(self, user):
        """Obter headers de autenticação para um usuário"""
        # Simular login para obter token
        response = self.client.post(
            reverse("api_login"),
            {
                "username": user.username,
                "password": (
                    "admin123"
                    if user == self.admin_user
                    else "attendant123" if user == self.attendant_user else "client123"
                ),
            },
        )
        token = response.data.get("access")
        return {"HTTP_AUTHORIZATION": f"Bearer {token}"}

    def test_self_update_success(self):
        """Teste: Usuário pode atualizar seus próprios dados"""
        headers = self.get_auth_headers(self.attendant_user)

        update_data = {
            "name": "ATENDENTE ATUALIZADO",
            "email": "attendant.novo@test.com",
            "phone": "(11) 33333-3333",
        }

        response = self.client.put(
            reverse("api_user_self_update"),
            data=json.dumps(update_data),
            content_type="application/json",
            **headers,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])

        # Verificar se os dados foram atualizados no banco
        self.attendant_person.refresh_from_db()
        self.attendant_contact.refresh_from_db()

        self.assertEqual(self.attendant_person.name, "ATENDENTE ATUALIZADO")
        self.assertEqual(self.attendant_contact.email, "attendant.novo@test.com")
        self.assertEqual(self.attendant_contact.phone, "(11) 33333-3333")

    def test_self_update_ignores_role(self):
        """Teste: Campo role é ignorado na auto-atualização"""
        headers = self.get_auth_headers(self.attendant_user)

        update_data = {
            "name": "ATENDENTE TESTE ROLE",
            "role": "ADMINISTRADOR",  # Deve ser ignorado
        }

        response = self.client.put(
            reverse("api_user_self_update"),
            data=json.dumps(update_data),
            content_type="application/json",
            **headers,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verificar se o cargo não foi alterado
        self.attendant_person.refresh_from_db()
        self.assertEqual(self.attendant_person.person_type.type, "ATENDENTE")

    def test_self_update_client_forbidden(self):
        """Teste: Cliente não pode usar endpoint de auto-atualização"""
        headers = self.get_auth_headers(self.client_user)

        update_data = {"name": "CLIENTE ATUALIZADO"}

        response = self.client.put(
            reverse("api_user_self_update"),
            data=json.dumps(update_data),
            content_type="application/json",
            **headers,
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_update_employee_success(self):
        """Teste: Admin pode atualizar dados de qualquer funcionário"""
        headers = self.get_auth_headers(self.admin_user)

        update_data = {
            "name": "ATENDENTE ATUALIZADO PELO ADMIN",
            "email": "attendant.admin@test.com",
            "phone": "(11) 44444-4444",
            "role": "RECEPÇÃO",
        }

        response = self.client.put(
            reverse(
                "api_employee_update", kwargs={"person_id": self.attendant_person.id}
            ),
            data=json.dumps(update_data),
            content_type="application/json",
            **headers,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verificar se os dados foram atualizados
        self.attendant_person.refresh_from_db()
        self.attendant_contact.refresh_from_db()

        self.assertEqual(self.attendant_person.name, "ATENDENTE ATUALIZADO PELO ADMIN")
        self.assertEqual(self.attendant_person.person_type.type, "RECEPÇÃO")
        self.assertEqual(self.attendant_contact.email, "attendant.admin@test.com")

    def test_employee_update_self_success(self):
        """Teste: Funcionário pode atualizar seus próprios dados via endpoint de funcionários"""
        headers = self.get_auth_headers(self.attendant_user)

        update_data = {
            "name": "ATENDENTE ATUALIZADO VIA EMPLOYEE ENDPOINT",
            "email": "attendant.employee@test.com",
        }

        response = self.client.put(
            reverse(
                "api_employee_update", kwargs={"person_id": self.attendant_person.id}
            ),
            data=json.dumps(update_data),
            content_type="application/json",
            **headers,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verificar se os dados foram atualizados
        self.attendant_person.refresh_from_db()
        self.attendant_contact.refresh_from_db()

        self.assertEqual(
            self.attendant_person.name, "ATENDENTE ATUALIZADO VIA EMPLOYEE ENDPOINT"
        )
        self.assertEqual(self.attendant_contact.email, "attendant.employee@test.com")

    def test_employee_update_other_forbidden(self):
        """Teste: Funcionário não pode atualizar dados de outros funcionários"""
        headers = self.get_auth_headers(self.attendant_user)

        update_data = {"name": "TENTATIVA DE ATUALIZAR ADMIN"}

        response = self.client.put(
            reverse("api_employee_update", kwargs={"person_id": self.admin_person.id}),
            data=json.dumps(update_data),
            content_type="application/json",
            **headers,
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_employee_update_role_forbidden(self):
        """Teste: Funcionário não pode alterar seu próprio cargo"""
        headers = self.get_auth_headers(self.attendant_user)

        update_data = {"name": "TENTATIVA COM ROLE", "role": "ADMINISTRADOR"}

        response = self.client.put(
            reverse(
                "api_employee_update", kwargs={"person_id": self.attendant_person.id}
            ),
            data=json.dumps(update_data),
            content_type="application/json",
            **headers,
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_toggle_status_success(self):
        """Teste: Ativar/desativar funcionário"""
        headers = self.get_auth_headers(self.admin_user)

        # Desativar funcionário
        response = self.client.post(
            reverse("api_employee_toggle_status"),
            data=json.dumps({"person_id": self.attendant_person.id, "active": False}),
            content_type="application/json",
            **headers,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["active"])

        # Verificar se o usuário foi desativado
        self.attendant_user.refresh_from_db()
        self.assertFalse(self.attendant_user.is_active)

        # Reativar funcionário
        response = self.client.post(
            reverse("api_employee_toggle_status"),
            data=json.dumps({"person_id": self.attendant_person.id, "active": True}),
            content_type="application/json",
            **headers,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["active"])

        # Verificar se o usuário foi reativado
        self.attendant_user.refresh_from_db()
        self.assertTrue(self.attendant_user.is_active)

    def test_update_validation_email_unique(self):
        """Teste: Validação de email único"""
        headers = self.get_auth_headers(self.attendant_user)

        # Tentar usar email que já existe
        update_data = {"email": "admin@test.com"}  # Email do admin

        response = self.client.put(
            reverse("api_user_self_update"),
            data=json.dumps(update_data),
            content_type="application/json",
            **headers,
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data["details"])

    def test_update_validation_phone_unique(self):
        """Teste: Validação de telefone único"""
        headers = self.get_auth_headers(self.attendant_user)

        # Tentar usar telefone que já existe
        update_data = {"phone": "(11) 11111-1111"}  # Telefone do admin

        response = self.client.put(
            reverse("api_user_self_update"),
            data=json.dumps(update_data),
            content_type="application/json",
            **headers,
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("phone", response.data["details"])

    def test_get_user_me_success(self):
        """Teste: Endpoint get-user-me retorna dados corretos"""
        headers = self.get_auth_headers(self.attendant_user)

        response = self.client.get(reverse("api_user_me"), **headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])

        user_data = response.data["user"]
        self.assertEqual(user_data["username"], "98765432100")
        self.assertEqual(user_data["person"]["name"], "ATENDENTE TESTE")
        self.assertEqual(user_data["person"]["cpf"], "98765432100")
        self.assertEqual(user_data["person"]["person_type"]["type"], "ATENDENTE")
        self.assertEqual(len(user_data["person"]["contacts"]), 1)
        self.assertEqual(
            user_data["person"]["contacts"][0]["email"], "attendant@test.com"
        )
