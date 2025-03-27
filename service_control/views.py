from django.contrib.auth.models import User
from django.shortcuts import render


def service_control_view(request):
    return render(request, "service_control.html", context={"user": request.user})
