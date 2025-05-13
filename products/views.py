# import base64
import io
import json

import qrcode
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from .models import (
    Brand,
    Button,
    Color,
    ColorCatalogue,
    ColorIntensity,
    Fabric,
    Lapel,
    Model,
    Pattern,
    Product,
    ProductType,
)
from .utils import decimal_default


def product_dashboard(request):
    if request.method == "POST" and request.POST.get("product_type"):
        try:
            # Criação de novo produto
            product_type_id = request.POST.get("product_type")
            brand_id = request.POST.get("brand")
            fabric_id = request.POST.get("fabric")
            color_catalogue_id = request.POST.get("color_catalogue")
            color_intensity_id = request.POST.get("color_intensity")
            pattern_id = request.POST.get("pattern") or None
            button_id = request.POST.get("button") or None
            lapel_id = request.POST.get("lapel") or None
            model_id = request.POST.get("model") or None
            on_stock = request.POST.get("on_stock") == "true"

            color, _ = Color.objects.get_or_create(
                color_id=color_catalogue_id, color_intensity_id=color_intensity_id
            )

            product = Product.objects.create(
                product_type_id=product_type_id,
                brand_id=brand_id,
                fabric_id=fabric_id,
                color=color,
                pattern_id=pattern_id,
                button_id=button_id,
                lapel_id=lapel_id,
                model_id=model_id,
                on_stock=on_stock,
            )

            messages.success(
                request, f"Produto cadastrado com sucesso: {product.label_code}"
            )
            return redirect("products:dashboard")

        except Exception as e:
            messages.error(request, f"Erro ao cadastrar o produto: {str(e)}")

    products = Product.objects.select_related(
        "product_type",
        "brand",
        "fabric",
        "color__color",
        "color__color_intensity",
        "model",
    ).filter(canceled_by__isnull=True)

    products_aggrid_data = [
        {
            "id": p.id,
            "product_type": p.product_type.description,
            "brand": p.brand.description if p.brand else "",
            "fabric": p.fabric.description if p.fabric else "",
            "color": str(p.color),
            "model": p.model.description if p.model else "",
            "label_code": p.label_code,
            "on_stock": p.on_stock,
        }
        for p in products
    ]

    context = {
        "product_types": ProductType.objects.all(),
        "brands": Brand.objects.all(),
        "fabrics": Fabric.objects.all(),
        "patterns": Pattern.objects.all(),
        "buttons": Button.objects.all(),
        "lapels": Lapel.objects.all(),
        "models": Model.objects.all(),
        "color_catalogues": ColorCatalogue.objects.all(),
        "color_intensities": ColorIntensity.objects.all(),
        "products_aggrid_data": json.dumps(
            products_aggrid_data, default=decimal_default
        ),
    }

    return render(request, "product_dashboard.html", context)


@csrf_exempt
@require_POST
@login_required
def update_product_stock(request):
    data = json.loads(request.body.decode("utf-8"))
    product_id = data.get("product_id")
    on_stock = data.get("on_stock")
    canceled = data.get("canceled")

    try:
        product = Product.objects.get(id=product_id)

        product.on_stock = on_stock

        if canceled:
            product.date_canceled = timezone.now()
            product.canceled_by = request.user

        product.save()
        return JsonResponse({"success": True})
    except Product.DoesNotExist:
        return JsonResponse(
            {"success": False, "error": "Produto não encontrado"}, status=404
        )


@require_GET
@login_required
def generate_product_qr(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
        qr_value = f"https://seudominio.com/products/{product_id}/detail"

        qr = qrcode.make(qr_value)
        buffer = io.BytesIO()
        qr.save(buffer, format="PNG")
        buffer.seek(0)

        response = HttpResponse(buffer, content_type="image/png")
        response["Content-Disposition"] = (
            f"attachment; filename=qr_{product.label_code}.png"
        )

        return response

    except Product.DoesNotExist:
        return JsonResponse(
            {"success": False, "error": "Produto não encontrado"}, status=404
        )


def list_colors(request):
    colors = ColorCatalogue.objects.all()
    intensities = ColorIntensity.objects.all()

    combinations = []
    for color in colors:
        for intensity in intensities:
            combinations.append(
                {
                    "id": f"{color.id}_{intensity.id}",  # ID composto
                    "description": f"{color.description} - {intensity.description}",
                }
            )

    return JsonResponse({"colors": combinations})
