from datetime import date, timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from accounts.models import Person, PersonType
from products.models import ColorCatalogue, TemporaryProduct
from service_control.models import ServiceOrderItem

from .models import ServiceOrder, ServiceOrderPhase

# Create your tests here.


class ServiceOrderListAPITest(TestCase):
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
        self.phase, _ = ServiceOrderPhase.objects.get_or_create(name="PENDENTE")
        self.url = reverse("os_list")
        # Cria OS para cada cenário
        today = date.today()
        ServiceOrder.objects.create(
            renter=self.admin_person,
            employee=self.admin_person,
            attendant=self.admin_person,
            order_date=today,
            event_date=today,
            occasion="Evento",
            service_order_phase=self.phase,
            prova_date=today,
        )
        ServiceOrder.objects.create(
            renter=self.admin_person,
            employee=self.admin_person,
            attendant=self.admin_person,
            order_date=today,
            event_date=today,
            occasion="Evento",
            service_order_phase=self.phase,
            retirada_date=today,
        )
        ServiceOrder.objects.create(
            renter=self.admin_person,
            employee=self.admin_person,
            attendant=self.admin_person,
            order_date=today,
            event_date=today,
            occasion="Evento",
            service_order_phase=self.phase,
            devolucao_date=today,
        )
        ServiceOrder.objects.create(
            renter=self.admin_person,
            employee=self.admin_person,
            attendant=self.admin_person,
            order_date=today,
            event_date=today,
            occasion="Evento",
            service_order_phase=self.phase,
            devolucao_date=today - timedelta(days=2),
        )
        ServiceOrder.objects.create(
            renter=self.admin_person,
            employee=self.admin_person,
            attendant=self.admin_person,
            order_date=today,
            event_date=today,
            occasion="Evento",
            service_order_phase=self.phase,
            devolucao_date=today + timedelta(days=5),
        )
        ServiceOrder.objects.create(
            renter=self.admin_person,
            employee=self.admin_person,
            attendant=self.admin_person,
            order_date=today,
            event_date=today,
            occasion="Evento",
            service_order_phase=self.phase,
            devolucao_date=today + timedelta(days=11),
        )

    def test_list_em_atraso(self):
        resp = self.client.get(self.url + "?status=em_atraso")
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(any(os["devolucao_date"] for os in resp.data))
        self.assertTrue(
            all(
                os["devolucao_date"] < str(date.today())
                for os in resp.data
                if os["devolucao_date"]
            )
        )

    def test_list_hoje(self):
        resp = self.client.get(self.url + "?status=hoje")
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(
            any(
                os["prova_date"] == str(date.today())
                or os["retirada_date"] == str(date.today())
                or os["devolucao_date"] == str(date.today())
                for os in resp.data
            )
        )

    def test_list_proximos_10_dias(self):
        resp = self.client.get(self.url + "?status=proximos_10_dias")
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(
            any(
                os["devolucao_date"]
                and date.today()
                < date.fromisoformat(os["devolucao_date"])
                <= date.today() + timedelta(days=10)
                for os in resp.data
            )
        )

    def test_list_tipo_prova(self):
        resp = self.client.get(self.url + "?tipo=prova")
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(
            all(
                os["prova_date"] == str(date.today())
                for os in resp.data
                if os["prova_date"]
            )
        )


class ServiceOrderRESTfulAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_user(
            username="admincpf2", password="adminpass2"
        )
        admin_type, _ = PersonType.objects.get_or_create(type="ADMINISTRADOR")
        self.admin_person = Person.objects.create(
            user=self.admin_user,
            name="Admin2",
            cpf="12345678902",
            person_type=admin_type,
        )
        self.client.force_authenticate(user=self.admin_user)
        self.phase, _ = ServiceOrderPhase.objects.get_or_create(name="PENDENTE")
        self.color = ColorCatalogue.objects.create(name="Azul")
        self.temp_product = TemporaryProduct.objects.create(
            name="Terno Azul", color="Azul", size="G"
        )

    def test_create_os_restful(self):
        data = {
            "cliente": "Cliente REST",
            "telefone": "11999999999",
            "cpf": "11122233344",
            "data_evento": "2024-12-25",
            "ocasiao": "Festa",
            "origem": "Loja",
        }
        response = self.client.post("/api/v1/os/", data)
        assert response.status_code == 200 or response.status_code == 201
        assert "order_id" in response.json()

    def test_list_pending_os_restful(self):
        response = self.client.get("/api/v1/os/pending/")
        assert response.status_code == 200
        assert "data" in response.json()

    def test_advance_phases(self):
        from datetime import date, timedelta

        from service_control.views import advance_service_order_phases

        os_atrasada = ServiceOrder.objects.create(
            renter=self.admin_person,
            employee=self.admin_person,
            attendant=self.admin_person,
            order_date=date.today() - timedelta(days=10),
            event_date=date.today() - timedelta(days=5),
            occasion="Evento",
            service_order_phase=self.phase,
            devolucao_date=date.today() - timedelta(days=2),
        )
        advance_service_order_phases()
        os_atrasada.refresh_from_db()
        assert os_atrasada.service_order_phase.name in [
            "EM ATRASO",
            "em atraso",
            "ATRASADA",
        ]

    def test_temporary_product_in_os(self):
        from datetime import date

        os = ServiceOrder.objects.create(
            renter=self.admin_person,
            employee=self.admin_person,
            attendant=self.admin_person,
            order_date=date.today(),
            event_date=date.today(),
            occasion="Teste Temp",
            service_order_phase=self.phase,
            devolucao_date=date.today(),
        )
        item = ServiceOrderItem.objects.create(
            service_order=os,
            temporary_product=self.temp_product,
            color_catalogue=self.color,
        )
        assert item.temporary_product is not None
        assert item.product is None
        assert item.temporary_product.name == "Terno Azul"
