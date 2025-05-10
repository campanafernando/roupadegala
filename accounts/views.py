import json
import random
import re
import string

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from .models import City, Person, PersonsAdresses, PersonsContacts, PersonType


def login_view(request):
    if request.user.is_authenticated:
        return redirect("service_control")

    login_form = AuthenticationForm()

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect("service_control")

    return render(request, "login.html", {"login_form": login_form})


def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        password_confirm = request.POST.get("password_confirm")
        name = request.POST.get("name")
        cpf = request.POST.get("cpf")
        email = request.POST.get("email")
        phone = request.POST.get("phone")

        errors = {}

        if password != password_confirm:
            errors["password_error"] = "As senhas não coincidem."
        if User.objects.filter(username=username).exists():
            errors["username_error"] = "Nome de usuário já está em uso."
        if Person.objects.filter(cpf=cpf).exists():
            errors["cpf_error"] = "CPF já cadastrado."
        if PersonsContacts.objects.filter(email=email).exists():
            errors["email_error"] = "Email já está em uso."

        cpf = re.sub(r"\D", "", request.POST.get("cpf", ""))

        if len(cpf) != 11:
            errors["cpf_error"] = "CPF inválido."

        if errors:
            return render(request, "register.html", {"errors": errors})

        user = User.objects.create_user(username=username, password=password)
        employee_type, _ = PersonType.objects.get_or_create(type="EMPLOYEE")
        person = Person.objects.create(
            user=user, name=name, cpf=cpf, person_type=employee_type
        )
        PersonsContacts.objects.create(email=email, phone=phone, person=person)

        login(request, user)
        return redirect("service_control")

    return render(request, "register.html")


# @login_required(login_url="login")
# def employee_redirect_view(request):
#     return render(request, "employee_redirect.html", context={"user": request.user})


def logout_view(request):
    logout(request)
    return redirect("login")


@require_GET
@login_required
def city_search(request):
    query = request.GET.get("q", "")
    cities = City.objects.filter(name__icontains=query).values("id", "name")[:10]

    return JsonResponse(list(cities), safe=False)


@login_required(login_url="login")
def employee_redirect_view(request):
    return render(request, "employee_redirect.html")


@require_POST
@login_required
@csrf_exempt
def register_employee_view(request):
    name = request.POST.get("name")
    cpf = request.POST.get("cpf")
    email = request.POST.get("email")
    phone = request.POST.get("phone")

    errors = {}
    if not cpf or not name or not email or not phone:
        errors["required"] = "Todos os campos são obrigatórios."

    if User.objects.filter(username=cpf).exists():
        errors["cpf_error"] = "CPF já cadastrado como login."
    if Person.objects.filter(cpf=cpf).exists():
        errors["person_error"] = "Funcionário com este CPF já existe."
    if PersonsContacts.objects.filter(email=email).exists():
        errors["email_error"] = "Email já está em uso."
    if PersonsContacts.objects.filter(phone=phone).exists():
        errors["phone_error"] = "Telefone já está em uso"

    cpf = re.sub(r"\D", "", request.POST.get("cpf", ""))

    if len(cpf) != 11:
        errors["cpf_error"] = "CPF inválido."

    if errors:
        return JsonResponse({"success": False, "errors": errors}, status=400)

    password = "".join(random.choices(string.ascii_uppercase + string.digits, k=7))
    user = User.objects.create_user(username=cpf, password=password, is_active=True)
    employee_type, _ = PersonType.objects.get_or_create(type="EMPLOYEE")
    person = Person.objects.create(
        user=user, name=name.upper(), cpf=cpf, person_type=employee_type
    )
    PersonsContacts.objects.create(email=email, phone=phone, person=person)

    request.session["last_password"] = password
    return JsonResponse({"success": True, "password": password})


@require_GET
@login_required
def list_employees(request):
    employees = Person.objects.filter(person_type__type="EMPLOYEE").select_related(
        "user"
    )
    data = []

    for emp in employees:
        contact = emp.personscontacts_set.first()
        password = "****"
        if request.session.get("last_password") and emp.user.username == emp.cpf:
            password = request.session.pop("last_password")

        data.append(
            {
                "id": emp.id,
                "name": emp.name,
                "cpf": emp.cpf,
                "email": contact.email if contact else "",
                "phone": contact.phone if contact else "",
                "active": emp.user.is_active if emp.user else False,
                "password": password,
            }
        )

    return JsonResponse(data, safe=False)


@require_POST
@login_required
def toggle_employee_status(request):
    try:
        data = json.loads(request.body)
        person_id = data.get("person_id")
        new_status = str(data.get("active")).lower() in ["true", "1", "on"]

        print(new_status)

        person = Person.objects.get(id=person_id)
        if person.user:
            person.user.is_active = new_status
            person.user.save()
        return JsonResponse({"success": True})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@require_POST
@login_required
def register_client(request):
    """
    Recebe JSON com:
      - nome, telefone, cpf, cep, rua, numero, bairro, cidade
    Busca a City por nome e cria Person + PersonsContacts + PersonsAdresses.
    """
    try:
        data = json.loads(request.body.decode("utf-8"))
        nome = data.get("nome")
        telefone = data.get("telefone")
        cpf = data.get("cpf")
        cep = data.get("cep")
        rua = data.get("rua")
        numero = data.get("numero")
        bairro = data.get("bairro")
        cidade_nome = data.get("cidade")

        try:
            city = City.objects.get(name__iexact=cidade_nome)
        except City.DoesNotExist:
            return JsonResponse({"error": "Cidade não encontrada"}, status=400)

        pt, _ = PersonType.objects.get_or_create(type="CUSTOMER")

        person = Person.objects.create(
            name=nome, cpf=cpf, person_type=pt, created_by=request.user
        )

        PersonsContacts.objects.create(
            phone=telefone, person=person, created_by=request.user
        )

        PersonsAdresses.objects.create(
            street=rua,
            number=numero,
            neighborhood=bairro,
            cep=cep,
            city=city,
            person=person,
            created_by=request.user,
        )

        return JsonResponse(
            {"id": person.id, "message": "Cliente cadastrado com sucesso"}
        )

    except json.JSONDecodeError:
        return JsonResponse({"error": "JSON inválido"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
