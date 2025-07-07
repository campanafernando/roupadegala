from django.contrib.auth.models import User
from drf_spectacular.utils import OpenApiExample, extend_schema_serializer
from rest_framework import serializers

from .models import City, Person, PersonsAdresses, PersonsContacts, PersonType


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = "__all__"


class PersonTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonType
        fields = "__all__"


class PersonsContactsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonsContacts
        fields = "__all__"


class PersonsAdressesSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonsAdresses
        fields = "__all__"


class PersonSerializer(serializers.ModelSerializer):
    contacts = PersonsContactsSerializer(many=True, read_only=True)

    class Meta:
        model = Person
        fields = "__all__"


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            "Exemplo de registro de funcionário",
            value={
                "name": "João Silva",
                "cpf": "12345678901",
                "email": "joao.silva@email.com",
                "phone": "(11) 99999-9999",
                "role": "ATENDENTE",
            },
            request_only=True,
        )
    ]
)
class EmployeeRegisterSerializer(serializers.Serializer):
    name = serializers.CharField(
        max_length=255, help_text="Nome completo do funcionário"
    )
    cpf = serializers.CharField(
        max_length=20, help_text="CPF do funcionário (apenas números)"
    )
    email = serializers.EmailField(help_text="Email do funcionário")
    phone = serializers.CharField(max_length=255, help_text="Telefone do funcionário")
    role = serializers.ChoiceField(
        choices=[
            ("ADMINISTRADOR", "ADMINISTRADOR"),
            ("ATENDENTE", "ATENDENTE"),
            ("RECEPÇÃO", "RECEPÇÃO"),
        ],
        help_text="Cargo/função do funcionário",
    )

    def validate_cpf(self, value):
        cpf = "".join(filter(str.isdigit, value))
        if len(cpf) != 11:
            raise serializers.ValidationError("CPF inválido.")
        if User.objects.filter(username=cpf).exists():
            raise serializers.ValidationError("CPF já cadastrado como login.")
        if Person.objects.filter(cpf=cpf).exists():
            raise serializers.ValidationError("Funcionário com este CPF já existe.")
        return cpf

    def validate_email(self, value):
        if PersonsContacts.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email já está em uso.")
        return value

    def validate_phone(self, value):
        if PersonsContacts.objects.filter(phone=value).exists():
            raise serializers.ValidationError("Telefone já está em uso.")
        return value

    def create(self, validated_data):
        import random
        import string

        password = "".join(random.choices(string.ascii_uppercase + string.digits, k=7))
        cpf = validated_data["cpf"]
        user = User.objects.create_user(username=cpf, password=password, is_active=True)
        employee_type, _ = PersonType.objects.get_or_create(type=validated_data["role"])
        person = Person.objects.create(
            user=user,
            name=validated_data["name"].upper(),
            cpf=cpf,
            person_type=employee_type,
        )
        PersonsContacts.objects.create(
            email=validated_data["email"], phone=validated_data["phone"], person=person
        )
        return {"person": person, "password": password}


# Serializers adicionais para corrigir erros do Swagger


class PasswordResetSerializer(serializers.Serializer):
    cpf = serializers.CharField(
        max_length=20, help_text="CPF do usuário para reset de senha"
    )


class ClientRegisterSerializer(serializers.Serializer):
    nome = serializers.CharField(max_length=255, help_text="Nome completo do cliente")
    telefone = serializers.CharField(max_length=255, help_text="Telefone do cliente")
    cpf = serializers.CharField(max_length=20, help_text="CPF do cliente")
    cep = serializers.CharField(max_length=10, help_text="CEP do endereço")
    rua = serializers.CharField(max_length=255, help_text="Rua do endereço")
    numero = serializers.CharField(max_length=10, help_text="Número do endereço")
    bairro = serializers.CharField(max_length=255, help_text="Bairro do endereço")
    cidade = serializers.CharField(max_length=255, help_text="Nome da cidade")


class ClientSearchSerializer(serializers.Serializer):
    cpf = serializers.CharField(max_length=20, help_text="CPF do cliente para busca")


class EmployeeToggleStatusSerializer(serializers.Serializer):
    person_id = serializers.IntegerField(help_text="ID da pessoa/funcionário")
    active = serializers.BooleanField(help_text="Status ativo/inativo")
