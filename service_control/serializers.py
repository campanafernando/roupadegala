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


class ServiceOrderListByPhaseSerializer(serializers.Serializer):
    """Serializer para listagem de ordens por fase com dados do cliente"""

    # Dados da OS
    id = serializers.IntegerField(help_text="ID da ordem de serviço")
    event_date = serializers.DateField(help_text="Data do evento")
    occasion = serializers.CharField(help_text="Tipo de evento")
    total_value = serializers.DecimalField(
        max_digits=10, decimal_places=2, help_text="Valor total"
    )
    advance_payment = serializers.DecimalField(
        max_digits=10, decimal_places=2, help_text="Valor pago"
    )
    remaining_payment = serializers.DecimalField(
        max_digits=10, decimal_places=2, help_text="Valor restante"
    )
    employee_name = serializers.CharField(help_text="Nome do atendente")
    attendant_name = serializers.CharField(help_text="Nome do recepcionista")
    order_date = serializers.DateField(help_text="Data de criação da OS")
    prova_date = serializers.DateField(help_text="Data da prova", allow_null=True)
    retirada_date = serializers.DateField(help_text="Data de retirada", allow_null=True)
    devolucao_date = serializers.DateField(
        help_text="Data de devolução", allow_null=True
    )

    # Dados do cliente
    client = serializers.DictField(help_text="Dados completos do cliente")


# Serializer para o payload do frontend
class FrontendOrderItemSerializer(serializers.Serializer):
    """Serializer para itens de roupa do payload do frontend"""

    tipo = serializers.CharField(
        help_text="Tipo do produto (paleto, camisa, calca, etc)"
    )
    numero = serializers.CharField(
        required=False, allow_blank=True, allow_null=True, help_text="Número/tamanho"
    )
    cor = serializers.CharField(
        required=False, allow_blank=True, allow_null=True, help_text="Cor do produto"
    )
    manga = serializers.CharField(
        required=False, allow_blank=True, allow_null=True, help_text="Tamanho da manga"
    )
    marca = serializers.CharField(
        required=False, allow_blank=True, allow_null=True, help_text="Marca do produto"
    )
    ajuste = serializers.CharField(
        required=False, allow_blank=True, allow_null=True, help_text="Ajuste necessário"
    )
    extras = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        help_text="Informações extras",
    )
    cintura = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        help_text="Tamanho da cintura",
    )
    perna = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        help_text="Comprimento da perna",
    )
    ajuste_cintura = serializers.CharField(
        required=False, allow_blank=True, allow_null=True, help_text="Ajuste da cintura"
    )
    ajuste_comprimento = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        help_text="Ajuste do comprimento",
    )
    venda = serializers.BooleanField(
        required=False, default=False, help_text="Indica se o item foi vendido"
    )


class FrontendAccessorySerializer(serializers.Serializer):
    """Serializer para acessórios do payload do frontend"""

    tipo = serializers.CharField(help_text="Tipo do acessório")
    cor = serializers.CharField(
        required=False, allow_blank=True, allow_null=True, help_text="Cor do acessório"
    )
    descricao = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        help_text="Descrição do acessório",
    )
    marca = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        help_text="Marca do acessório",
    )
    extensor = serializers.BooleanField(
        required=False, default=False, help_text="Se possui extensor"
    )
    venda = serializers.BooleanField(
        required=False, default=False, help_text="Indica se o acessório foi vendido"
    )


class FrontendPaymentSerializer(serializers.Serializer):
    """Serializer para dados de pagamento do payload do frontend"""

    total = serializers.DecimalField(
        max_digits=10, decimal_places=2, help_text="Valor total"
    )
    sinal = serializers.DecimalField(
        max_digits=10, decimal_places=2, help_text="Valor do sinal"
    )
    restante = serializers.DecimalField(
        max_digits=10, decimal_places=2, help_text="Valor restante"
    )


class FrontendOrderServiceSerializer(serializers.Serializer):
    """Serializer para dados da ordem de serviço do payload do frontend"""

    data_pedido = serializers.DateField(required=False, help_text="Data do pedido")
    data_evento = serializers.DateField(help_text="Data do evento")
    data_retirada = serializers.DateField(required=False, help_text="Data de retirada")
    ocasiao = serializers.CharField(help_text="Tipo de ocasião")
    modalidade = serializers.ChoiceField(
        choices=[
            ("Aluguel", "Aluguel"),
            ("Compra", "Compra"),
            ("Aluguel + Venda", "Aluguel + Venda"),
        ],
        help_text="Modalidade do serviço",
    )
    itens = FrontendOrderItemSerializer(
        many=True, required=False, help_text="Lista de itens"
    )
    acessorios = FrontendAccessorySerializer(
        many=True, required=False, help_text="Lista de acessórios"
    )
    pagamento = FrontendPaymentSerializer(help_text="Dados de pagamento")


class FrontendContactSerializer(serializers.Serializer):
    """Serializer para contatos do cliente do payload do frontend"""

    tipo = serializers.CharField(help_text="Tipo de contato (telefone, email, etc)")
    valor = serializers.CharField(help_text="Valor do contato")


class FrontendAddressSerializer(serializers.Serializer):
    """Serializer para endereços do cliente do payload do frontend"""

    cep = serializers.CharField(help_text="CEP")
    rua = serializers.CharField(help_text="Rua")
    numero = serializers.CharField(help_text="Número")
    bairro = serializers.CharField(help_text="Bairro")
    cidade = serializers.CharField(help_text="Cidade")


class FrontendClientSerializer(serializers.Serializer):
    """Serializer para dados do cliente do payload do frontend"""

    nome = serializers.CharField(help_text="Nome do cliente")
    cpf = serializers.CharField(help_text="CPF do cliente")
    contatos = FrontendContactSerializer(
        many=True, required=False, help_text="Lista de contatos"
    )
    enderecos = FrontendAddressSerializer(
        many=True, required=False, help_text="Lista de endereços"
    )


class FrontendServiceOrderUpdateSerializer(serializers.Serializer):
    """Serializer completo para o payload do frontend"""

    ordem_servico = FrontendOrderServiceSerializer(
        help_text="Dados da ordem de serviço"
    )
    cliente = FrontendClientSerializer(help_text="Dados do cliente")
