"""
Views API para o app accounts
"""

import random
import re
import string

from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiExample, OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import City, Person, PersonsContacts, PersonType
from .serializers import (
    ClientRegisterSerializer,
    ClientSearchSerializer,
    EmployeeRegisterSerializer,
    EmployeeToggleStatusSerializer,
    PasswordResetSerializer,
    PersonSerializer,
)


@extend_schema(
    tags=["auth"],
    summary="Login de usuário",
    description="Autentica um usuário e retorna um token de acesso",
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "username": {"type": "string", "description": "CPF do usuário"},
                "password": {"type": "string", "description": "Senha do usuário"},
            },
            "required": ["username", "password"],
        }
    },
    responses={
        200: {
            "description": "Login realizado com sucesso",
            "type": "object",
            "properties": {
                "success": {"type": "boolean"},
                "token": {"type": "string"},
                "user": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "username": {"type": "string"},
                        "is_active": {"type": "boolean"},
                    },
                },
            },
        },
        400: {"description": "Dados inválidos"},
        401: {"description": "Credenciais inválidas"},
    },
    examples=[
        OpenApiExample(
            "Login bem-sucedido",
            value={
                "success": True,
                "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
                "user": {"id": 1, "username": "12345678901", "is_active": True},
            },
            response_only=True,
            status_codes=["200"],
        )
    ],
)
class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        """Login de usuário via API"""
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response(
                {"error": "Username e password são obrigatórios"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Limpar CPF de pontos e traços
        username = re.sub(r"\D", "", username)

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            token, created = Token.objects.get_or_create(user=user)

            return Response(
                {
                    "success": True,
                    "token": token.key,
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "is_active": user.is_active,
                    },
                }
            )
        else:
            return Response(
                {"error": "CPF ou senha incorretos"},
                status=status.HTTP_401_UNAUTHORIZED,
            )


@extend_schema(
    tags=["auth"],
    summary="Registro de usuário",
    description="Cria uma nova conta de usuário",
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "username": {"type": "string", "description": "Nome de usuário"},
                "password": {"type": "string", "description": "Senha"},
                "password_confirm": {
                    "type": "string",
                    "description": "Confirmação da senha",
                },
                "name": {"type": "string", "description": "Nome completo"},
                "cpf": {"type": "string", "description": "CPF"},
                "email": {"type": "string", "format": "email", "description": "Email"},
                "phone": {"type": "string", "description": "Telefone"},
            },
            "required": [
                "username",
                "password",
                "password_confirm",
                "name",
                "cpf",
                "email",
                "phone",
            ],
        }
    },
    responses={
        200: {
            "description": "Usuário criado com sucesso",
            "type": "object",
            "properties": {
                "success": {"type": "boolean"},
                "token": {"type": "string"},
                "user": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "username": {"type": "string"},
                        "name": {"type": "string"},
                    },
                },
            },
        },
        400: {"description": "Dados inválidos ou usuário já existe"},
    },
)
class RegisterAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        """Registro de novo usuário via API"""
        username = request.data.get("username")
        password = request.data.get("password")
        password_confirm = request.data.get("password_confirm")
        name = request.data.get("name")
        cpf = request.data.get("cpf")
        email = request.data.get("email")
        phone = request.data.get("phone")

        errors = {}

        if password != password_confirm:
            errors["password_error"] = "As senhas não coincidem."
        if User.objects.filter(username=username).exists():
            errors["username_error"] = "Nome de usuário já está em uso."
        if Person.objects.filter(cpf=cpf).exists():
            errors["cpf_error"] = "CPF já cadastrado."
        if PersonsContacts.objects.filter(email=email).exists():
            errors["email_error"] = "Email já está em uso."

        cpf = re.sub(r"\D", "", cpf)

        if len(cpf) != 11:
            errors["cpf_error"] = "CPF inválido."

        if errors:
            return Response({"errors": errors}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.create_user(username=username, password=password)
            employee_type, _ = PersonType.objects.get_or_create(type="ATENDENTE")
            person = Person.objects.create(
                user=user, name=name, cpf=cpf, person_type=employee_type
            )
            PersonsContacts.objects.create(email=email, phone=phone, person=person)

            login(request, user)
            token, created = Token.objects.get_or_create(user=user)

            return Response(
                {
                    "success": True,
                    "token": token.key,
                    "user": {"id": user.id, "username": user.username, "name": name},
                }
            )
        except Exception as e:
            return Response(
                {"error": f"Erro ao criar usuário: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@extend_schema(
    tags=["accounts"],
    summary="Busca de cidades",
    description="Busca cidades por nome",
    parameters=[
        OpenApiParameter(
            name="q",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Termo de busca para o nome da cidade",
            examples=[OpenApiExample("Exemplo", value="São Paulo")],
        )
    ],
    responses={
        200: {
            "description": "Lista de cidades encontradas",
            "type": "array",
            "items": {
                "type": "object",
                "properties": {"id": {"type": "integer"}, "name": {"type": "string"}},
            },
        }
    },
)
class CitySearchAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Busca de cidades por nome"""
        query = request.GET.get("q", "")
        if not query:
            return Response([], status=status.HTTP_200_OK)

        cities = City.objects.filter(name__icontains=query).values("id", "name")[:10]
        return Response(list(cities))


@extend_schema(
    tags=["accounts"],
    summary="Registro de funcionário",
    description="Cria um novo funcionário no sistema",
    request=EmployeeRegisterSerializer,
    responses={
        200: {
            "description": "Funcionário criado com sucesso",
            "type": "object",
            "properties": {
                "success": {"type": "boolean"},
                "password": {
                    "type": "string",
                    "description": "Senha gerada automaticamente",
                },
                "employee": {"$ref": "#/components/schemas/Person"},
            },
        },
        400: {"description": "Dados inválidos ou funcionário já existe"},
    },
)
class EmployeeRegisterAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Registro de funcionário via API"""
        user_person = getattr(request.user, "person", None)
        if not user_person or user_person.person_type.type != "ADMINISTRADOR":
            return Response(
                {"error": "Apenas administradores podem registrar novos funcionários."},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = EmployeeRegisterSerializer(data=request.data)

        if serializer.is_valid():
            try:
                result = serializer.save()
                return Response(
                    {
                        "success": True,
                        "password": result["password"],
                        "employee": PersonSerializer(result["person"]).data,
                    }
                )
            except Exception as e:
                return Response(
                    {"error": f"Erro ao criar funcionário: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=["accounts"],
    summary="Lista de funcionários",
    description="Retorna a lista de todos os funcionários",
    responses={
        200: {
            "description": "Lista de funcionários",
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "name": {"type": "string"},
                    "cpf": {"type": "string"},
                    "email": {"type": "string"},
                    "phone": {"type": "string"},
                    "role": {"type": "string"},
                    "active": {"type": "boolean"},
                },
            },
        }
    },
)
class EmployeeListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Lista de funcionários"""
        employees = Person.objects.filter(
            person_type__type__in=["ATENDENTE", "RECEPÇÃO"]
        ).select_related("user", "person_type")

        data = []
        for emp in employees:
            contact = emp.contacts.first()
            data.append(
                {
                    "id": emp.id,
                    "name": emp.name,
                    "cpf": emp.cpf,
                    "email": contact.email if contact else "",
                    "phone": contact.phone if contact else "",
                    "role": emp.person_type.type,
                    "active": emp.user.is_active if emp.user else False,
                }
            )

        return Response(data)


class EmployeeToggleStatusAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EmployeeToggleStatusSerializer

    def post(self, request):
        """Ativa/desativa funcionário"""
        try:
            person_id = request.data.get("person_id")
            new_status = str(request.data.get("active")).lower() in ["true", "1", "on"]

            person = Person.objects.get(id=person_id)
            if person.user:
                person.user.is_active = new_status
                person.user.save()

                return Response({"success": True, "active": new_status})
            else:
                return Response(
                    {"error": "Funcionário não possui usuário associado"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except Person.DoesNotExist:
            return Response(
                {"error": "Funcionário não encontrado"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"error": f"Erro ao alterar status: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ClientRegisterAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ClientRegisterSerializer

    def post(self, request):
        """Registro de cliente via API"""
        try:
            name = request.data.get("name")
            cpf = request.data.get("cpf", "").replace(".", "").replace("-", "")
            email = request.data.get("email")
            phone = request.data.get("phone")

            if not all([name, cpf, phone]):
                return Response(
                    {"error": "Nome, CPF e telefone são obrigatórios"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if len(cpf) != 11:
                return Response(
                    {"error": "CPF inválido"}, status=status.HTTP_400_BAD_REQUEST
                )

            if Person.objects.filter(cpf=cpf).exists():
                return Response(
                    {"error": "CPF já cadastrado"}, status=status.HTTP_400_BAD_REQUEST
                )

            client_type, _ = PersonType.objects.get_or_create(type="CLIENTE")
            person = Person.objects.create(
                name=name.upper(),
                cpf=cpf,
                person_type=client_type,
                created_by=request.user,
            )

            PersonsContacts.objects.create(
                email=email, phone=phone, person=person, created_by=request.user
            )

            return Response({"success": True, "client": PersonSerializer(person).data})

        except Exception as e:
            return Response(
                {"error": f"Erro ao criar cliente: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ClientSearchAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ClientSearchSerializer

    def get(self, request):
        """Busca cliente por CPF"""
        cpf = request.GET.get("cpf", "").replace(".", "").replace("-", "")

        if not cpf:
            return Response(
                {"error": "CPF é obrigatório"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            person = Person.objects.get(cpf=cpf)
            contact = person.contacts.first()
            address = person.personsadresses_set.first()

            data = {
                "id": person.id,
                "name": person.name,
                "cpf": person.cpf,
                "email": contact.email if contact else "",
                "phone": contact.phone if contact else "",
                "address": (
                    {
                        "street": address.street if address else "",
                        "number": address.number if address else "",
                        "neighborhood": address.neighborhood if address else "",
                        "city": address.city.name if address else "",
                        "cep": address.cep if address else "",
                    }
                    if address
                    else None
                ),
            }

            return Response(data)

        except Person.DoesNotExist:
            return Response(
                {"error": "Cliente não encontrado"}, status=status.HTTP_404_NOT_FOUND
            )


class PasswordResetAPIView(APIView):
    permission_classes = [AllowAny]
    serializer_class = PasswordResetSerializer

    def post(self, request):
        """Reset de senha via API"""
        cpf = request.data.get("cpf", "").replace(".", "").replace("-", "")

        if not cpf:
            return Response(
                {"error": "CPF é obrigatório"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            person = Person.objects.get(cpf=cpf)
            if not person.user:
                return Response(
                    {"error": "Usuário não encontrado"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Gerar nova senha
            new_password = "".join(
                random.choices(string.ascii_uppercase + string.digits, k=7)
            )
            person.user.set_password(new_password)
            person.user.save()

            return Response(
                {
                    "success": True,
                    "message": "Senha alterada com sucesso",
                    "new_password": new_password,
                }
            )

        except Person.DoesNotExist:
            return Response(
                {"error": "CPF não encontrado"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": f"Erro ao resetar senha: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
