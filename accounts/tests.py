from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from .models import Person, PersonType

# Create your tests here.


class EmployeeRegisterAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Cria um admin
        self.admin_user = User.objects.create_user(
            username="admincpf", password="adminpass"
        )
        admin_type, _ = PersonType.objects.get_or_create(type="ADMINISTRADOR")
        self.admin_person = Person.objects.create(
            user=self.admin_user,
            name="Admin",
            cpf="12345678901",
            person_type=admin_type,
        )
        self.client.force_authenticate(user=self.admin_user)
        self.url = reverse("api_register_employee")

    def test_cadastro_funcionario_sucesso(self):
        data = {
            "name": "Novo Funcionario",
            "cpf": "98765432100",
            "email": "novo@teste.com",
            "phone": "34999999999",
            "role": "ATENDENTE",
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.data["success"])
        self.assertIn("password", response.data)
        self.assertEqual(Person.objects.filter(cpf="98765432100").count(), 1)

    def test_cadastro_funcionario_cpf_duplicado(self):
        Person.objects.create(
            name="Outro",
            cpf="11111111111",
            person_type=PersonType.objects.get(type="ATENDENTE"),
        )
        data = {
            "name": "Outro",
            "cpf": "11111111111",
            "email": "outro@teste.com",
            "phone": "34999999998",
            "role": "ATENDENTE",
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.data["success"])
        self.assertIn("cpf", response.data["errors"])

    def test_cadastro_funcionario_email_duplicado(self):
        data1 = {
            "name": "Funcionario1",
            "cpf": "22222222222",
            "email": "duplicado@teste.com",
            "phone": "34999999997",
            "role": "ATENDENTE",
        }
        self.client.post(self.url, data1)
        data2 = {
            "name": "Funcionario2",
            "cpf": "33333333333",
            "email": "duplicado@teste.com",
            "phone": "34999999996",
            "role": "ATENDENTE",
        }
        response = self.client.post(self.url, data2)
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.data["success"])
        self.assertIn("email", response.data["errors"])

    def test_apenas_admin_pode_cadastrar(self):
        # Cria usuário comum
        user = User.objects.create_user(username="comum", password="123")
        self.client.force_authenticate(user=user)
        data = {
            "name": "Funcionario",
            "cpf": "44444444444",
            "email": "comum@teste.com",
            "phone": "34999999995",
            "role": "ATENDENTE",
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 403)
        self.assertIn("detail", response.data)
