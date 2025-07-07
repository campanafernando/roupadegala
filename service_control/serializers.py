from rest_framework import serializers

from accounts.serializers import PersonSerializer
from products.serializers import (
    ColorCatalogueSerializer,
    ProductSerializer,
    TemporaryProductSerializer,
)

from .models import ServiceOrder, ServiceOrderItem, ServiceOrderPhase


class ServiceOrderPhaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceOrderPhase
        fields = "__all__"


class ServiceOrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    temporary_product = TemporaryProductSerializer(read_only=True)
    color_catalogue = ColorCatalogueSerializer(read_only=True)

    class Meta:
        model = ServiceOrderItem
        fields = "__all__"


class ServiceOrderSerializer(serializers.ModelSerializer):
    renter = PersonSerializer(read_only=True)
    employee = PersonSerializer(read_only=True)
    attendant = PersonSerializer(read_only=True)
    items = ServiceOrderItemSerializer(many=True, read_only=True)
    service_order_phase = ServiceOrderPhaseSerializer(read_only=True)

    class Meta:
        model = ServiceOrder
        fields = "__all__"


class ServiceOrderDashboardSerializer(serializers.Serializer):
    em_atraso = serializers.DictField(child=serializers.IntegerField())
    hoje = serializers.DictField(child=serializers.IntegerField())
    proximos_10_dias = serializers.DictField(child=serializers.IntegerField())


# Serializers adicionais para corrigir erros do Swagger


class ServiceOrderDetailSerializer(serializers.ModelSerializer):
    """Serializer para detalhes de ordem de serviço"""

    class Meta:
        model = ServiceOrder
        fields = "__all__"


class ServiceOrderClientSerializer(serializers.Serializer):
    """Serializer para dados do cliente da ordem de serviço"""

    order_id = serializers.IntegerField(help_text="ID da ordem de serviço")
    id = serializers.IntegerField(help_text="ID do cliente")
    nome = serializers.CharField(help_text="Nome do cliente")
    cpf = serializers.CharField(help_text="CPF do cliente")
    telefones = serializers.ListField(
        child=serializers.CharField(), help_text="Lista de telefones"
    )
    enderecos = serializers.ListField(
        child=serializers.DictField(), help_text="Lista de endereços"
    )


class ServiceOrderMarkPaidSerializer(serializers.Serializer):
    """Serializer para marcar ordem como paga"""

    pass


class ServiceOrderRefuseSerializer(serializers.Serializer):
    """Serializer para recusar ordem de serviço"""

    justification_refusal = serializers.CharField(
        required=False, help_text="Justificativa da recusa"
    )


class ServiceOrderUpdateSerializer(serializers.Serializer):
    """Serializer para atualização de ordem de serviço"""

    order_id = serializers.IntegerField(help_text="ID da ordem de serviço")
    total_value = serializers.DecimalField(
        max_digits=10, decimal_places=2, help_text="Valor total"
    )
    advance_payment = serializers.DecimalField(
        max_digits=10, decimal_places=2, help_text="Valor pago"
    )
    remaining_payment = serializers.DecimalField(
        max_digits=10, decimal_places=2, help_text="Valor restante"
    )
    payment_method = serializers.CharField(
        required=False, help_text="Método de pagamento"
    )
    observations = serializers.CharField(required=False, help_text="Observações")
    due_date = serializers.DateField(required=False, help_text="Data de vencimento")
    items = serializers.ListField(
        child=serializers.DictField(), help_text="Lista de itens"
    )


class ServiceOrderListByPhaseSerializer(serializers.Serializer):
    """Serializer para listagem de ordens por fase"""

    phase_name = serializers.CharField(help_text="Nome da fase para filtrar")
