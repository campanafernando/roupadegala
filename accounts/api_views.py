"""
Views API para o app accounts
"""

import re

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiExample, OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView

from .models import City, Person, PersonsContacts, PersonType
from .serializers import (
    ClientRegisterSerializer,
    ClientSearchSerializer,
    EmployeeRegisterSerializer,
    EmployeeToggleStatusSerializer,
    EmployeeUpdateSerializer,
    PasswordResetSerializer,
    PersonSerializer,
)


@extend_schema(
    tags=["auth"],
    summary="Login de usuário",
    description="Autentica um usuário e retorna access token e refresh token",
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
                "access": {"type": "string", "description": "Access token JWT"},
                "refresh": {"type": "string", "description": "Refresh token JWT"},
                "user": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "username": {"type": "string"},
                        "is_active": {"type": "boolean"},
                        "person_type": {"type": "string"},
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
                "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                "user": {
                    "id": 1,
                    "username": "12345678901",
                    "is_active": True,
                    "person_type": "ATENDENTE",
                },
            },
            response_only=True,
            status_codes=["200"],
        )
    ],
)
class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        """Login de usuário via API com JWT"""
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
            # Gerar tokens JWT
            refresh = RefreshToken.for_user(user)

            # Buscar informações da pessoa
            person_type = "N/A"
            try:
                person = user.person
                person_type = person.person_type.type if person.person_type else "N/A"
            except Exception as e:
                return Response(
                    {"error": f"Erro ao buscar informações da pessoa: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            return Response(
                {
                    "success": True,
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "is_active": user.is_active,
                        "person_type": person_type,
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
    summary="Refresh token",
    description="Renova o access token usando o refresh token",
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "refresh": {"type": "string", "description": "Refresh token JWT"},
            },
            "required": ["refresh"],
        }
    },
    responses={
        200: {
            "description": "Token renovado com sucesso",
            "type": "object",
            "properties": {
                "access": {"type": "string", "description": "Novo access token JWT"},
            },
        },
        401: {"description": "Refresh token inválido ou expirado"},
    },
)
class RefreshTokenAPIView(TokenRefreshView):
    """Endpoint para renovar access token"""

    pass


@extend_schema(
    tags=["auth"],
    summary="Logout",
    description="Invalida o refresh token atual",
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "refresh": {
                    "type": "string",
                    "description": "Refresh token JWT para invalidar",
                },
            },
            "required": ["refresh"],
        }
    },
    responses={
        200: {
            "description": "Logout realizado com sucesso",
            "type": "object",
            "properties": {
                "success": {"type": "boolean"},
                "message": {"type": "string"},
            },
        },
        400: {"description": "Refresh token inválido"},
    },
)
class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Logout de usuário via API"""
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return Response(
                    {"error": "Refresh token é obrigatório"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(
                {
                    "success": True,
                    "message": "Logout realizado com sucesso",
                }
            )
        except Exception as e:
            return Response(
                {"error": f"Token inválido - {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
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
                "access": {"type": "string", "description": "Access token JWT"},
                "refresh": {"type": "string", "description": "Refresh token JWT"},
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

            # Gerar tokens JWT
            refresh = RefreshToken.for_user(user)

            return Response(
                {
                    "success": True,
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
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
    permission_classes = [AllowAny]

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


@extend_schema(
    tags=["accounts"],
    summary="Atualizar dados de funcionário",
    description="Atualiza os dados de um funcionário existente. Administradores podem atualizar qualquer funcionário, incluindo o cargo. Funcionários podem atualizar apenas seus próprios dados (exceto cargo).",
    request=EmployeeUpdateSerializer,
    responses={
        200: {
            "description": "Dados atualizados com sucesso",
            "type": "object",
            "properties": {
                "success": {"type": "boolean"},
                "message": {"type": "string"},
                "employee": {"$ref": "#/components/schemas/Person"},
            },
        },
        400: {"description": "Dados inválidos"},
        403: {"description": "Permissão negada"},
        404: {"description": "Funcionário não encontrado"},
        500: {"description": "Erro interno do servidor"},
    },
)
class EmployeeUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EmployeeUpdateSerializer

    def put(self, request, person_id):
        """Atualizar dados de funcionário"""
        try:
            # Verificar se o usuário é ADMINISTRADOR ou está atualizando seus próprios dados
            user_person = getattr(request.user, "person", None)
            is_admin = user_person and user_person.person_type.type == "ADMINISTRADOR"
            is_self_update = user_person and user_person.id == person_id

            if not (is_admin or is_self_update):
                return Response(
                    {
                        "error": "Apenas administradores podem atualizar outros funcionários ou você pode atualizar seus próprios dados."
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

            # Buscar o funcionário
            try:
                person = Person.objects.get(id=person_id)
                if person.person_type.type not in [
                    "ADMINISTRADOR",
                    "ATENDENTE",
                    "RECEPÇÃO",
                ]:
                    return Response(
                        {"error": "Pessoa não é um funcionário."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            except Person.DoesNotExist:
                return Response(
                    {"error": "Funcionário não encontrado."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Se não for admin, não pode alterar o role
            if not is_admin and "role" in request.data:
                return Response(
                    {
                        "error": "Você não pode alterar seu próprio cargo. Apenas administradores podem fazer isso."
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

            # Validar dados
            serializer = self.serializer_class(
                data=request.data, context={"person_id": person_id}
            )
            if not serializer.is_valid():
                return Response(
                    {"error": "Dados inválidos", "details": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Atualizar dados da pessoa
            if serializer.validated_data.get("name"):
                person.name = serializer.validated_data["name"].upper()

            if serializer.validated_data.get("role") and is_admin:
                new_role = serializer.validated_data["role"]
                person_type, _ = PersonType.objects.get_or_create(type=new_role)
                person.person_type = person_type

            person.updated_by = request.user
            person.save()

            # Atualizar contatos
            contact = person.contacts.first()
            if contact:
                if serializer.validated_data.get("email"):
                    contact.email = serializer.validated_data["email"]
                if serializer.validated_data.get("phone"):
                    contact.phone = serializer.validated_data["phone"]
                contact.updated_by = request.user
                contact.save()
            else:
                # Criar contato se não existir
                PersonsContacts.objects.create(
                    person=person,
                    email=serializer.validated_data.get("email", ""),
                    phone=serializer.validated_data.get("phone", ""),
                    created_by=request.user,
                )

            message = (
                "Dados atualizados com sucesso"
                if is_self_update
                else "Funcionário atualizado com sucesso"
            )

            return Response(
                {
                    "success": True,
                    "message": message,
                    "employee": PersonSerializer(person).data,
                }
            )

        except Exception as e:
            return Response(
                {"error": f"Erro ao atualizar dados: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@extend_schema(
    tags=["auth"],
    summary="Atualizar dados do usuário logado",
    description="Permite que o usuário atualize seus próprios dados (nome, email, telefone). Não permite alteração de cargo.",
    request=EmployeeUpdateSerializer,
    responses={
        200: {
            "description": "Dados atualizados com sucesso",
            "type": "object",
            "properties": {
                "success": {"type": "boolean"},
                "message": {"type": "string"},
                "user": {"$ref": "#/components/schemas/Person"},
            },
        },
        400: {"description": "Dados inválidos"},
        401: {"description": "Usuário não autenticado"},
        500: {"description": "Erro interno do servidor"},
    },
)
class UserSelfUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EmployeeUpdateSerializer

    def put(self, request):
        """Atualizar dados do usuário logado"""
        try:
            user_person = getattr(request.user, "person", None)
            if not user_person:
                return Response(
                    {"error": "Usuário não possui dados de pessoa associados."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Verificar se é funcionário
            if user_person.person_type.type not in [
                "ADMINISTRADOR",
                "ATENDENTE",
                "RECEPÇÃO",
            ]:
                return Response(
                    {"error": "Apenas funcionários podem atualizar dados."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            # Remover role dos dados se presente (usuário não pode alterar seu próprio cargo)
            data = request.data.copy()
            if "role" in data:
                del data["role"]

            # Validar dados
            serializer = self.serializer_class(
                data=data, context={"person_id": user_person.id}
            )
            if not serializer.is_valid():
                return Response(
                    {"error": "Dados inválidos", "details": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Atualizar dados da pessoa
            if serializer.validated_data.get("name"):
                user_person.name = serializer.validated_data["name"].upper()

            user_person.updated_by = request.user
            user_person.save()

            # Atualizar contatos
            contact = user_person.contacts.first()
            if contact:
                if serializer.validated_data.get("email"):
                    contact.email = serializer.validated_data["email"]
                if serializer.validated_data.get("phone"):
                    contact.phone = serializer.validated_data["phone"]
                contact.updated_by = request.user
                contact.save()
            else:
                # Criar contato se não existir
                PersonsContacts.objects.create(
                    person=user_person,
                    email=serializer.validated_data.get("email", ""),
                    phone=serializer.validated_data.get("phone", ""),
                    created_by=request.user,
                )

            return Response(
                {
                    "success": True,
                    "message": "Seus dados foram atualizados com sucesso",
                    "user": PersonSerializer(user_person).data,
                }
            )

        except Exception as e:
            return Response(
                {"error": f"Erro ao atualizar dados: {str(e)}"},
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
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")

        if not old_password or not new_password:
            return Response(
                {"error": "Senha antiga e nova são obrigatórias"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = request.user
            if not user.check_password(old_password):
                return Response(
                    {"error": "Senha antiga inválida"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user.set_password(new_password)
            user.save()

            return Response(
                {
                    "success": True,
                    "message": "Senha alterada com sucesso",
                    "new_password": new_password,
                }
            )

        except Exception as e:
            return Response(
                {"error": f"Erro ao resetar senha: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@extend_schema(
    tags=["auth"],
    summary="Dados do usuário logado",
    description="Retorna todos os dados disponíveis do usuário autenticado",
    responses={
        200: {
            "description": "Dados do usuário logado",
            "type": "object",
            "properties": {
                "success": {"type": "boolean"},
                "user": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "username": {"type": "string"},
                        "email": {"type": "string"},
                        "first_name": {"type": "string"},
                        "last_name": {"type": "string"},
                        "is_active": {"type": "boolean"},
                        "date_joined": {"type": "string", "format": "date-time"},
                        "last_login": {"type": "string", "format": "date-time"},
                        "person": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "integer"},
                                "name": {"type": "string"},
                                "cpf": {"type": "string"},
                                "person_type": {
                                    "type": "object",
                                    "properties": {
                                        "id": {"type": "integer"},
                                        "type": {"type": "string"},
                                    },
                                },
                                "contacts": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "id": {"type": "integer"},
                                            "email": {"type": "string"},
                                            "phone": {"type": "string"},
                                        },
                                    },
                                },
                                "addresses": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "id": {"type": "integer"},
                                            "cep": {"type": "string"},
                                            "rua": {"type": "string"},
                                            "numero": {"type": "string"},
                                            "bairro": {"type": "string"},
                                            "cidade": {
                                                "type": "object",
                                                "properties": {
                                                    "id": {"type": "integer"},
                                                    "name": {"type": "string"},
                                                    "uf": {"type": "string"},
                                                },
                                            },
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
            },
        },
        401: {"description": "Usuário não autenticado"},
    },
    examples=[
        OpenApiExample(
            "Dados do usuário",
            value={
                "success": True,
                "user": {
                    "id": 1,
                    "username": "12345678901",
                    "email": "joao@email.com",
                    "first_name": "João",
                    "last_name": "Silva",
                    "is_active": True,
                    "date_joined": "2024-01-15T10:30:00Z",
                    "last_login": "2024-01-20T14:45:00Z",
                    "person": {
                        "id": 1,
                        "name": "JOÃO SILVA",
                        "cpf": "12345678901",
                        "person_type": {
                            "id": 1,
                            "type": "ATENDENTE",
                        },
                        "contacts": [
                            {
                                "id": 1,
                                "email": "joao@email.com",
                                "phone": "(11) 99999-9999",
                            }
                        ],
                        "addresses": [
                            {
                                "id": 1,
                                "cep": "01234-567",
                                "rua": "Rua das Flores",
                                "numero": "123",
                                "bairro": "Centro",
                                "cidade": {
                                    "id": 1,
                                    "name": "São Paulo",
                                    "uf": "SP",
                                },
                            }
                        ],
                    },
                },
            },
            response_only=True,
            status_codes=["200"],
        )
    ],
)
class GetUserMeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Retorna dados completos do usuário logado"""
        try:
            user = request.user

            # Dados básicos do usuário
            user_data = {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "is_active": user.is_active,
                "date_joined": (
                    user.date_joined.isoformat() if user.date_joined else None
                ),
                "last_login": user.last_login.isoformat() if user.last_login else None,
            }

            # Dados da pessoa (se existir)
            try:
                person = user.person
                if person:
                    # Dados do tipo de pessoa
                    person_type_data = None
                    if person.person_type:
                        person_type_data = {
                            "id": person.person_type.id,
                            "type": person.person_type.type,
                        }

                    # Contatos da pessoa
                    contacts_data = []
                    for contact in person.contacts.all():
                        contacts_data.append(
                            {
                                "id": contact.id,
                                "email": contact.email,
                                "phone": contact.phone,
                            }
                        )

                    # Endereços da pessoa
                    addresses_data = []
                    for address in person.personsadresses_set.all():
                        city_data = None
                        if address.city:
                            city_data = {
                                "id": address.city.id,
                                "name": address.city.name,
                                "uf": address.city.uf,
                            }

                        addresses_data.append(
                            {
                                "id": address.id,
                                "cep": address.cep,
                                "rua": address.street,
                                "numero": address.number,
                                "bairro": address.neighborhood,
                                "cidade": city_data,
                            }
                        )

                    user_data["person"] = {
                        "id": person.id,
                        "name": person.name,
                        "cpf": person.cpf,
                        "person_type": person_type_data,
                        "contacts": contacts_data,
                        "addresses": addresses_data,
                    }
                else:
                    user_data["person"] = None

            except Exception as e:
                return Response(
                    {"error": f"Erro ao buscar dados da pessoa: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            return Response(
                {
                    "success": True,
                    "user": user_data,
                }
            )

        except Exception as e:
            return Response(
                {"error": f"Erro ao buscar dados do usuário: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
