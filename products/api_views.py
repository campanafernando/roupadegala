"""
Views API para o app products
"""

import base64
import io

import qrcode
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    Brand,
    Button,
    Color,
    ColorCatalogue,
    Fabric,
    Lapel,
    Model,
    Pattern,
    Product,
    ProductType,
)
from .serializers import (
    BrandSerializer,
    ButtonSerializer,
    CatalogListSerializer,
    ColorCatalogueSerializer,
    FabricSerializer,
    LapelSerializer,
    ModelSerializer,
    PatternSerializer,
    ProductSerializer,
    ProductStockUpdateSerializer,
    ProductTypeSerializer,
    ProductUpdateSerializer,
    TemporaryProductCreateSerializer,
    TemporaryProductSerializer,
)


@extend_schema(
    tags=["products"],
    summary="Dashboard de produtos",
    description="Retorna estatísticas e métricas dos produtos",
    responses={
        200: {
            "description": "Estatísticas dos produtos",
            "type": "object",
            "properties": {
                "total_products": {"type": "integer"},
                "in_stock": {"type": "integer"},
                "out_of_stock": {"type": "integer"},
                "products_by_type": {
                    "type": "object",
                    "additionalProperties": {"type": "integer"},
                },
                "products_by_brand": {
                    "type": "object",
                    "additionalProperties": {"type": "integer"},
                },
            },
        }
    },
)
class ProductDashboardAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Dashboard de produtos com estatísticas"""
        total_products = Product.objects.count()
        in_stock = Product.objects.filter(on_stock=True).count()
        out_of_stock = Product.objects.filter(on_stock=False).count()

        # Produtos por tipo
        products_by_type = {}
        for product_type in ProductType.objects.all():
            count = Product.objects.filter(product_type=product_type).count()
            products_by_type[product_type.description] = count

        # Produtos por marca
        products_by_brand = {}
        for brand in Brand.objects.all():
            count = Product.objects.filter(brand=brand).count()
            products_by_brand[brand.description] = count

        return Response(
            {
                "total_products": total_products,
                "in_stock": in_stock,
                "out_of_stock": out_of_stock,
                "products_by_type": products_by_type,
                "products_by_brand": products_by_brand,
            }
        )


@extend_schema(
    tags=["products"],
    summary="Lista de produtos",
    description="Retorna a lista de produtos com filtros opcionais",
    parameters=[
        OpenApiParameter(
            name="product_type",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Filtrar por tipo de produto",
            required=False,
        ),
        OpenApiParameter(
            name="brand",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Filtrar por marca",
            required=False,
        ),
        OpenApiParameter(
            name="in_stock",
            type=OpenApiTypes.BOOL,
            location=OpenApiParameter.QUERY,
            description="Filtrar por disponibilidade em estoque",
            required=False,
        ),
    ],
    responses={200: ProductSerializer(many=True)},
)
class ProductListAPIView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProductSerializer
    queryset = Product.objects.all()

    def get_queryset(self):
        queryset = Product.objects.select_related(
            "product_type",
            "brand",
            "fabric",
            "color",
            "pattern",
            "button",
            "lapel",
            "model",
        )

        # Filtros
        product_type = self.request.GET.get("product_type")
        brand = self.request.GET.get("brand")
        in_stock = self.request.GET.get("in_stock")

        if product_type:
            queryset = queryset.filter(
                product_type__description__icontains=product_type
            )
        if brand:
            queryset = queryset.filter(brand__description__icontains=brand)
        if in_stock is not None:
            queryset = queryset.filter(on_stock=in_stock.lower() == "true")

        return queryset


@extend_schema(
    tags=["products"],
    summary="Criar produto",
    description="Cria um novo produto no sistema",
    request=ProductSerializer,
    responses={
        201: {
            "description": "Produto criado com sucesso",
            "type": "object",
            "properties": {
                "success": {"type": "boolean"},
                "product": {"$ref": "#/components/schemas/Product"},
            },
        },
        400: {"description": "Dados inválidos"},
    },
)
class ProductCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Criar novo produto"""
        serializer = ProductSerializer(data=request.data)

        if serializer.is_valid():
            product = serializer.save(created_by=request.user)
            return Response(
                {"success": True, "product": ProductSerializer(product).data},
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProductUpdateSerializer

    def put(self, request, product_id):
        """Atualizar produto"""
        try:
            product = Product.objects.get(id=product_id)
            serializer = ProductSerializer(product, data=request.data, partial=True)

            if serializer.is_valid():
                product = serializer.save(updated_by=request.user)
                return Response(
                    {"success": True, "product": ProductSerializer(product).data}
                )

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Product.DoesNotExist:
            return Response(
                {"error": "Produto não encontrado"}, status=status.HTTP_404_NOT_FOUND
            )


class ProductStockUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProductStockUpdateSerializer

    def post(self, request):
        """Atualizar estoque de produtos"""
        try:
            product_id = request.data.get("product_id")
            on_stock = request.data.get("on_stock", True)

            product = Product.objects.get(id=product_id)
            product.on_stock = on_stock
            product.save(update_fields=["on_stock"])

            return Response(
                {
                    "success": True,
                    "message": f"Estoque do produto {product.label_code} atualizado",
                    "on_stock": on_stock,
                }
            )

        except Product.DoesNotExist:
            return Response(
                {"error": "Produto não encontrado"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": f"Erro ao atualizar estoque: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@extend_schema(
    tags=["products"],
    summary="Gerar QR Code",
    description="Gera um QR Code para um produto específico",
    parameters=[
        OpenApiParameter(
            name="product_id",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
            description="ID do produto",
        )
    ],
    responses={
        200: {
            "description": "QR Code gerado com sucesso",
            "type": "object",
            "properties": {
                "success": {"type": "boolean"},
                "qr_code": {"type": "string", "description": "QR Code em base64"},
                "label_code": {"type": "string"},
                "product_info": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "type": {"type": "string"},
                        "brand": {"type": "string"},
                        "color": {"type": "string"},
                    },
                },
            },
        },
        404: {"description": "Produto não encontrado"},
    },
)
class ProductQRCodeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, product_id):
        """Gerar QR Code para produto"""
        try:
            product = Product.objects.get(id=product_id)

            # Criar QR Code
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(product.label_code)
            qr.make(fit=True)

            img = qr.make_image(fill_color="black", back_color="white")

            # Converter para base64
            buffer = io.BytesIO()
            img.save(buffer, format="PNG")
            img_str = base64.b64encode(buffer.getvalue()).decode()

            return Response(
                {
                    "success": True,
                    "qr_code": img_str,
                    "label_code": product.label_code,
                    "product_info": {
                        "id": product.id,
                        "type": (
                            product.product_type.description
                            if product.product_type
                            else None
                        ),
                        "brand": product.brand.description if product.brand else None,
                        "color": (
                            f"{product.color.color.description} - {product.color.color_intensity.description}"
                            if product.color
                            else None
                        ),
                    },
                }
            )

        except Product.DoesNotExist:
            return Response(
                {"error": "Produto não encontrado"}, status=status.HTTP_404_NOT_FOUND
            )


class ColorListAPIView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ColorCatalogueSerializer
    queryset = ColorCatalogue.objects.all()

    def get(self, request):
        """Lista de cores disponíveis"""
        colors = ColorCatalogue.objects.all()
        return Response(ColorCatalogueSerializer(colors, many=True).data)


class ColorWithIntensityListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Lista todas as combinações de cor e intensidade"""
        combos = Color.objects.select_related("color", "color_intensity").all()
        data = [
            {
                "id": combo.id,
                "color_id": combo.color.id,
                "color": combo.color.description,
                "intensity_id": combo.color_intensity.id,
                "intensity": combo.color_intensity.description,
            }
            for combo in combos
        ]
        return Response(data)


class TemporaryProductCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TemporaryProductCreateSerializer

    def post(self, request):
        """Criar produto temporário"""
        serializer = TemporaryProductSerializer(data=request.data)

        if serializer.is_valid():
            temp_product = serializer.save(created_by=request.user)
            return Response(
                {
                    "success": True,
                    "temporary_product": TemporaryProductSerializer(temp_product).data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CatalogListAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CatalogListSerializer

    def get(self, request):
        """Lista todos os catálogos (marcas, tecidos, etc.)"""
        catalogs = {
            "brands": BrandSerializer(Brand.objects.all(), many=True).data,
            "fabrics": FabricSerializer(Fabric.objects.all(), many=True).data,
            "colors": ColorCatalogueSerializer(
                ColorCatalogue.objects.all(), many=True
            ).data,
            "patterns": PatternSerializer(Pattern.objects.all(), many=True).data,
            "buttons": ButtonSerializer(Button.objects.all(), many=True).data,
            "lapels": LapelSerializer(Lapel.objects.all(), many=True).data,
            "models": ModelSerializer(Model.objects.all(), many=True).data,
            "product_types": ProductTypeSerializer(
                ProductType.objects.all(), many=True
            ).data,
        }

        return Response(catalogs)
