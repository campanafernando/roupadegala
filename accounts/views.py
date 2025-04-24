from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_GET

from accounts.models import City


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

        errors = {}

        if password != password_confirm:
            errors["password_error"] = "As senhas não coincidem."
        if User.objects.filter(username=username).exists():
            errors["username_error"] = "Nome de usuário já está em uso."

        if errors:
            return render(request, "register.html", {"errors": errors})

        user = User.objects.create_user(username=username, password=password)
        login(request, user)
        return redirect(
            "service_control"
        )  # Redireciona para a página inicial ou outra página desejada

    return render(request, "register.html")


@login_required(login_url="login")
def employee_redirect_view(request):
    return render(request, "employee_redirect.html", context={"user": request.user})


def logout_view(request):
    logout(request)
    return redirect("login")


@require_GET
@login_required
def city_search(request):
    query = request.GET.get("q", "")
    cities = City.objects.filter(name__icontains=query).values("id", "name")[:10]

    return JsonResponse(list(cities), safe=False)
