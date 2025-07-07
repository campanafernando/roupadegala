from datetime import date

from django.contrib.auth.models import User
from django.test import TestCase

from accounts.models import Person, PersonType
from service_control.models import ServiceOrder, ServiceOrderItem, ServiceOrderPhase

from .models import ColorCatalogue, Product, TemporaryProduct


class ProductAndTemporaryProductTest(TestCase):
    def setUp(self):
        self.color = ColorCatalogue.objects.create(name="Preto")
        self.product = Product.objects.create(
            name="Terno Slim", color=self.color, size="M", stock=2
        )
        self.temp_product = TemporaryProduct.objects.create(
            name="Terno Custom", color="Azul", size="G"
        )
        self.phase, _ = ServiceOrderPhase.objects.get_or_create(name="PENDENTE")
        self.user = User.objects.create_user(username="cliente", password="123")
        self.person_type = PersonType.objects.create(type="CLIENTE")
        self.person = Person.objects.create(
            user=self.user,
            name="Cliente",
            cpf="99999999999",
            person_type=self.person_type,
        )

    def test_create_product(self):
        assert self.product.name == "Terno Slim"
        assert self.product.color.name == "Preto"
        assert self.product.stock == 2

    def test_create_temporary_product(self):
        assert self.temp_product.name == "Terno Custom"
        assert self.temp_product.color == "Azul"
        assert self.temp_product.size == "G"

    def test_service_order_with_product_and_temporary(self):
        os = ServiceOrder.objects.create(
            renter=self.person,
            order_date=date.today(),
            event_date=date.today(),
            occasion="Festa",
            service_order_phase=self.phase,
            devolucao_date=date.today(),
        )
        item1 = ServiceOrderItem.objects.create(
            service_order=os, product=self.product, color_catalogue=self.color
        )
        item2 = ServiceOrderItem.objects.create(
            service_order=os,
            temporary_product=self.temp_product,
            color_catalogue=self.color,
        )
        assert item1.product == self.product
        assert item2.temporary_product == self.temp_product
        assert item1.temporary_product is None
        assert item2.product is None
