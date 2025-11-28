from rest_framework import serializers

from accounts.serializers import PersonSerializer
from products.serializers import (
    ColorCatalogueSerializer,
    ProductSerializer,
    TemporaryProductSerializer,
)

from .models import (
    Event,
    EventParticipant,
    RefusalReason,
    ServiceOrder,
    ServiceOrderItem,
    ServiceOrderPhase,
)


class ServiceOrderPhaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceOrderPhase
        fields = "__all__"


class RefusalReasonSerializer(serializers.ModelSerializer):
    """Serializer para motivos de recusa/cancelamento"""

    class Meta:
        model = RefusalReason
        fields = ["id", "name"]


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
    event_date = serializers.SerializerMethodField(help_text="Data do evento vinculado")
    event_name = serializers.SerializerMethodField(help_text="Nome do evento vinculado")

    class Meta:
        model = ServiceOrder
        fields = "__all__"

    def get_event_date(self, obj):
        """Retorna a data do evento vinculado"""
        if obj.event and obj.event.event_date:
            if hasattr(obj.event.event_date, "date"):
                return obj.event.event_date.date()
            return obj.event.event_date
        return None

    def get_event_name(self, obj):
        """Retorna o nome do evento vinculado"""
        return obj.event.name if obj.event else None


class ServiceOrderDashboardSerializer(serializers.Serializer):
    em_atraso = serializers.DictField(child=serializers.IntegerField())
    hoje = serializers.DictField(child=serializers.IntegerField())
    proximos_10_dias = serializers.DictField(child=serializers.IntegerField())


class StatusMetricsSerializer(serializers.Serializer):
    """Serializer para métricas de status"""

    provas = serializers.IntegerField(help_text="Número de provas")
    retiradas = serializers.IntegerField(help_text="Número de retiradas")
    devolucoes = serializers.IntegerField(help_text="Número de devoluções")


class FinancialMetricsSerializer(serializers.Serializer):
    """Serializer para métricas financeiras"""

    total_pedidos = serializers.DecimalField(
        max_digits=10, decimal_places=2, help_text="Valor total dos pedidos"
    )
    total_recebido = serializers.DecimalField(
        max_digits=10, decimal_places=2, help_text="Valor total recebido"
    )
    numero_pedidos = serializers.IntegerField(help_text="Número de pedidos")


class SalesMetricsSerializer(serializers.Serializer):
    """Serializer para métricas de vendas"""

    total_vendido = serializers.DecimalField(
        max_digits=10, decimal_places=2, help_text="Valor total vendido"
    )
    numero_itens = serializers.IntegerField(help_text="Número de itens vendidos")


class ServiceMetricsSerializer(serializers.Serializer):
    """Serializer para métricas de atendimento"""

    total_atendimentos = serializers.IntegerField(help_text="Total de atendimentos")
    atendimentos_finalizados = serializers.IntegerField(
        help_text="Atendimentos finalizados"
    )
    atendimentos_cancelados = serializers.IntegerField(
        help_text="Atendimentos cancelados"
    )
    em_andamento = serializers.IntegerField(help_text="Atendimentos em andamento")


class ConversionMetricsSerializer(serializers.Serializer):
    """Serializer para métricas de conversão"""

    taxa_conversao = serializers.FloatField(help_text="Taxa de conversão em percentual")
    atendimentos_iniciados = serializers.IntegerField(
        help_text="Atendimentos iniciados"
    )
    concluidos_sucesso = serializers.IntegerField(help_text="Concluídos com sucesso")


class ChannelMetricsSerializer(serializers.Serializer):
    """Serializer para métricas de canal"""

    total = serializers.IntegerField(help_text="Total de pedidos do canal")
    percentual = serializers.FloatField(help_text="Percentual do canal")


class ServiceOrderDashboardResponseSerializer(serializers.Serializer):
    """Serializer para resposta completa do dashboard analítico"""

    status = serializers.DictField(
        child=StatusMetricsSerializer(),
        help_text="Status das OS por período (em_atraso, hoje, proximos_10_dias)",
    )

    resultados = serializers.DictField(
        child=FinancialMetricsSerializer(),
        help_text="Resultados financeiros por período (dia, semana, mes)",
    )

    vendas = serializers.DictField(
        child=SalesMetricsSerializer(),
        help_text="Métricas de vendas por período (dia, semana, mes)",
    )

    atendimentos = serializers.DictField(
        child=ServiceMetricsSerializer(),
        help_text="Métricas de atendimento por período (dia, semana, mes)",
    )

    conversao = serializers.DictField(
        child=ConversionMetricsSerializer(),
        help_text="Métricas de conversão por período (dia, semana, mes)",
    )

    canais = serializers.DictField(
        child=serializers.DictField(
            child=ChannelMetricsSerializer(),
            help_text="Métricas por canal de aquisição",
        ),
        help_text="Distribuição por canal de origem (Instagram, Facebook, etc.) por período",
    )


# Serializers adicionais para corrigir erros do Swagger


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
        required=False,
        allow_blank=True,
        help_text="Justificativa detalhada da recusa (opcional)",
    )
    justification_reason_id = serializers.IntegerField(
        required=True, help_text="ID do motivo de recusa"
    )


class ServiceOrderMarkRetrievedSerializer(serializers.Serializer):
    """Serializer para marcar ordem de serviço como retirada"""

    pass


class ServiceOrderListByPhaseSerializer(serializers.Serializer):
    """Serializer para listagem de ordens por fase com dados do cliente"""

    # Dados da OS
    id = serializers.IntegerField(help_text="ID da ordem de serviço")
    total_value = serializers.DecimalField(
        max_digits=10, decimal_places=2, help_text="Valor total"
    )
    advance_payment = serializers.DecimalField(
        max_digits=10, decimal_places=2, help_text="Valor pago"
    )
    esta_atrasada = serializers.BooleanField(
        help_text="Flag indicando se a OS está atrasada (retirada ou devolução)"
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
    production_date = serializers.DateField(
        help_text="Data em que a OS foi movida para produção", allow_null=True
    )
    justificativa_atraso = serializers.CharField(
        help_text="Justificativa do atraso (quando aplicável)",
        allow_null=True,
        allow_blank=True,
    )

    # Dados de recusa/cancelamento
    justification_refusal = serializers.CharField(
        help_text="Justificativa detalhada da recusa (texto livre)",
        allow_null=True,
        allow_blank=True,
    )
    justification_reason = serializers.CharField(
        help_text="Motivo estruturado da recusa",
        allow_null=True,
        allow_blank=True,
    )

    # Datas adicionais
    data_recusa = serializers.DateField(
        help_text="Data em que a OS foi recusada", allow_null=True
    )
    data_finalizado = serializers.DateField(
        help_text="Data em que a OS foi finalizada", allow_null=True
    )

    # Dados do evento vinculado
    event_date = serializers.DateField(
        help_text="Data do evento vinculado", allow_null=True
    )
    event_name = serializers.CharField(
        help_text="Nome do evento vinculado", allow_null=True
    )

    # Dados do cliente
    client = serializers.DictField(help_text="Dados completos do cliente")

    # Dados da ordem de serviço formatados para o frontend
    ordem_servico = serializers.DictField(
        help_text="Dados completos da OS no formato do frontend",
        allow_null=True,
    )


# Serializer para o payload do frontend
class FrontendOrderItemSerializer(serializers.Serializer):
    """Serializer para itens de roupa do payload do frontend"""

    tipo = serializers.CharField(
        help_text="Tipo do produto (paleto, camisa, calca, etc)"
    )
    numero = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        help_text="Número/tamanho do item",
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
    numero = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        help_text="Número/tamanho do acessório",
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


class FrontendPaymentItemSerializer(serializers.Serializer):
    """Serializer para item individual de pagamento"""

    amount = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        allow_null=True,
        help_text="Valor do pagamento",
    )
    forma_pagamento = serializers.CharField(
        required=False,
        allow_null=True,
        allow_blank=True,
        help_text="Forma de pagamento (credito, dinheiro, etc)",
    )


class FrontendSignalSerializer(serializers.Serializer):
    """Serializer para dados do sinal"""

    total = serializers.DecimalField(
        max_digits=10, decimal_places=2, help_text="Valor total do sinal"
    )
    pagamentos = FrontendPaymentItemSerializer(
        many=True, help_text="Lista de pagamentos do sinal"
    )


class FrontendPaymentSerializer(serializers.Serializer):
    """Serializer para dados de pagamento do payload do frontend"""

    total = serializers.DecimalField(
        max_digits=10, decimal_places=2, help_text="Valor total"
    )
    sinal = FrontendSignalSerializer(help_text="Dados do sinal")
    restante = serializers.DecimalField(
        max_digits=10, decimal_places=2, help_text="Valor restante"
    )


class FrontendOrderServiceSerializer(serializers.Serializer):
    """Serializer para dados da ordem de serviço do payload do frontend"""

    data_pedido = serializers.DateField(required=False, help_text="Data do pedido")
    data_evento = serializers.DateField(required=False, help_text="Data do evento")
    data_retirada = serializers.DateField(required=False, help_text="Data de retirada")
    data_prova = serializers.DateField(
        required=False, allow_null=True, help_text="Data da prova"
    )
    data_devolucao = serializers.DateField(
        required=False, help_text="Data de devolução"
    )
    ocasiao = serializers.CharField(
        required=False, allow_blank=True, help_text="Ocasião do evento"
    )
    modalidade = serializers.ChoiceField(
        choices=[
            ("Aluguel", "Aluguel"),
            ("Compra", "Compra"),
            ("Aluguel + Venda", "Aluguel + Venda"),
        ],
        required=False,
        help_text="Modalidade do serviço",
    )
    employee_id = serializers.IntegerField(
        required=False,
        allow_null=True,
        help_text="ID do atendente/recepcionista responsável",
    )
    itens = FrontendOrderItemSerializer(
        many=True, required=False, help_text="Lista de itens"
    )
    acessorios = FrontendAccessorySerializer(
        many=True, required=False, help_text="Lista de acessórios"
    )
    pagamento = FrontendPaymentSerializer(
        required=False, help_text="Dados de pagamento"
    )


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
    complemento = serializers.CharField(
        help_text="Complemento do endereço", allow_blank=True, required=False
    )


class FrontendClientSerializer(serializers.Serializer):
    """Serializer para dados do cliente do payload do frontend"""

    nome = serializers.CharField(required=False, help_text="Nome do cliente")
    cpf = serializers.CharField(required=False, help_text="CPF do cliente")
    email = serializers.EmailField(
        help_text="Email do cliente", required=False, allow_blank=True
    )
    contatos = FrontendContactSerializer(
        many=True, required=False, help_text="Lista de contatos"
    )
    enderecos = FrontendAddressSerializer(
        many=True, required=False, help_text="Lista de endereços"
    )


class FrontendServiceOrderUpdateSerializer(serializers.Serializer):
    """Serializer completo para o payload do frontend - todos os campos opcionais para permitir atualizações parciais"""

    ordem_servico = FrontendOrderServiceSerializer(
        required=False, help_text="Dados da ordem de serviço"
    )
    cliente = FrontendClientSerializer(required=False, help_text="Dados do cliente")


# --- Eventos ---


class EventParticipantSerializer(serializers.ModelSerializer):
    person = PersonSerializer(read_only=True)

    class Meta:
        model = EventParticipant
        fields = "__all__"


class EventSerializer(serializers.ModelSerializer):
    participants = EventParticipantSerializer(many=True, read_only=True)

    class Meta:
        model = Event
        fields = "__all__"


class EventCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255, help_text="Nome do evento")
    description = serializers.CharField(
        required=False, allow_blank=True, help_text="Descrição do evento"
    )
    event_date = serializers.DateField(
        required=False, allow_null=True, help_text="Data do evento (YYYY-MM-DD)"
    )


class EventUpdateSerializer(serializers.Serializer):
    name = serializers.CharField(
        max_length=255, required=False, help_text="Nome do evento"
    )
    description = serializers.CharField(
        required=False, allow_blank=True, help_text="Descrição do evento"
    )
    event_date = serializers.DateField(
        required=False, allow_null=True, help_text="Data do evento (YYYY-MM-DD)"
    )


class EventAddParticipantsSerializer(serializers.Serializer):
    participant_ids = serializers.ListField(
        child=serializers.IntegerField(), help_text="IDs de pessoas a adicionar"
    )


class EventLinkServiceOrderSerializer(serializers.Serializer):
    """Serializer para vincular ordem de serviço a um evento"""

    service_order_id = serializers.IntegerField(help_text="ID da ordem de serviço")
    event_id = serializers.IntegerField(help_text="ID do evento")


class EventStatusSerializer(serializers.Serializer):
    """Serializer para listagem de eventos com status"""

    id = serializers.IntegerField()
    name = serializers.CharField()
    description = serializers.CharField()
    event_date = serializers.DateField(allow_null=True)
    service_orders_count = serializers.IntegerField(
        help_text="Número de ordens de serviço vinculadas"
    )
    status = serializers.CharField(
        help_text="Status do evento: FINALIZADO, CANCELADO, POSSUI PENDÊNCIAS"
    )
    date_created = serializers.DateTimeField()
    date_updated = serializers.DateTimeField(allow_null=True)


class EventServiceOrderSerializer(serializers.Serializer):
    """Serializer para dados das OS vinculadas ao evento"""

    id = serializers.IntegerField(help_text="ID da ordem de serviço")
    date_created = serializers.DateTimeField(help_text="Data e hora de criação da OS")
    phase = serializers.CharField(
        allow_null=True,
        help_text="Fase atual da OS (PENDENTE, EM_PRODUCAO, AGUARDANDO_RETIRADA, etc.)",
    )
    total_value = serializers.DecimalField(
        max_digits=10, decimal_places=2, help_text="Valor total da OS"
    )
    client_name = serializers.CharField(
        allow_null=True, help_text="Nome do cliente da ordem de serviço"
    )


class EventDetailSerializer(serializers.Serializer):
    """Serializer para detalhamento completo de um evento"""

    id = serializers.IntegerField()
    name = serializers.CharField()
    description = serializers.CharField()
    event_date = serializers.DateField(allow_null=True)
    service_orders_count = serializers.IntegerField(
        help_text="Número de ordens de serviço vinculadas"
    )
    status = serializers.CharField(
        help_text="Status do evento: AGENDADO, FINALIZADO, CANCELADO, POSSUI PENDÊNCIAS, N/A"
    )
    date_created = serializers.DateTimeField()
    date_updated = serializers.DateTimeField(
        allow_null=True,
        help_text="Data de atualização mais recente (considerando evento e OS vinculadas)",
    )
    service_orders = EventServiceOrderSerializer(
        many=True, help_text="Lista das ordens de serviço vinculadas ao evento"
    )
