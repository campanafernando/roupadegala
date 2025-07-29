"""
Views API para o app products
"""

import base64
import io

import pandas as pd
import qrcode
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiExample, OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

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
    permission_classes = [AllowAny]
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
    description="Cria um novo produto no sistema ou importa produtos via Excel",
    request={
        "application/json": ProductSerializer,
        "multipart/form-data": {
            "type": "object",
            "properties": {
                "excel_file": {
                    "type": "string",
                    "format": "binary",
                    "description": "Arquivo Excel para importação em lote",
                }
            },
        },
    },
    responses={
        201: {
            "description": "Produto(s) criado(s) com sucesso",
            "type": "object",
            "properties": {
                "success": {"type": "boolean"},
                "message": {"type": "string"},
                "products_created": {"type": "integer"},
                "products_updated": {"type": "integer"},
                "errors": {"type": "array", "items": {"type": "string"}},
            },
        },
        400: {"description": "Dados inválidos"},
    },
)
class ProductCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Criar novo produto ou importar via Excel"""

        # Verificar se é uma importação de Excel
        if "excel_file" in request.FILES:
            return self._import_from_excel(request)

        # Criação individual de produto
        serializer = ProductSerializer(data=request.data)

        if serializer.is_valid():
            product = serializer.save(created_by=request.user)
            return Response(
                {"success": True, "product": ProductSerializer(product).data},
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def _import_from_excel(self, request):
        """Importar produtos do arquivo Excel"""
        try:
            excel_file = request.FILES["excel_file"]

            # Verificar extensão do arquivo
            if not excel_file.name.endswith((".xlsx", ".xls")):
                return Response(
                    {"error": "Arquivo deve ser um Excel (.xlsx ou .xls)"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Ler o arquivo Excel
            df = pd.read_excel(excel_file)

            # Validar se o arquivo tem dados
            if df.empty:
                return Response(
                    {"error": "Arquivo Excel está vazio"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Validar colunas obrigatórias
            required_columns = ["Tipo", "ID"]
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                return Response(
                    {
                        "error": f"Colunas obrigatórias ausentes: {', '.join(missing_columns)}"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            products_created = 0
            products_updated = 0
            errors = []
            processed_label_codes = set()  # Para detectar duplicatas no próprio Excel

            for index, row in df.iterrows():
                try:
                    # Pular linhas vazias ou com dados incompletos
                    if pd.isna(row.get("Tipo")) or pd.isna(row.get("ID")):
                        continue

                    # Verificar duplicatas no próprio Excel
                    label_code = str(row.get("ID", "")).strip()
                    if label_code in processed_label_codes:
                        errors.append(
                            f"Linha {index + 2}: ID '{label_code}' duplicado no Excel"
                        )
                        continue

                    processed_label_codes.add(label_code)

                    # Mapear dados do Excel para o modelo
                    product_data = self._map_excel_row_to_product(row)

                    # Verificar se produto já existe pelo label_code
                    existing_product = Product.objects.filter(
                        label_code=product_data["label_code"]
                    ).first()

                    if existing_product:
                        # Atualizar produto existente
                        serializer = ProductSerializer(
                            existing_product, data=product_data, partial=True
                        )
                        if serializer.is_valid():
                            serializer.save(updated_by=request.user)
                            products_updated += 1
                        else:
                            errors.append(f"Linha {index + 2}: {serializer.errors}")
                    else:
                        # Criar novo produto
                        serializer = ProductSerializer(data=product_data)
                        if serializer.is_valid():
                            serializer.save(created_by=request.user)
                            products_created += 1
                        else:
                            errors.append(f"Linha {index + 2}: {serializer.errors}")

                except Exception as e:
                    errors.append(f"Linha {index + 2}: {str(e)}")

            # Preparar mensagem de resposta
            if products_created == 0 and products_updated == 0 and errors:
                return Response(
                    {
                        "success": False,
                        "message": "Nenhum produto foi processado devido a erros",
                        "products_created": products_created,
                        "products_updated": products_updated,
                        "errors": errors,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            message = f"Importação concluída. {products_created} produtos criados, {products_updated} atualizados."
            if errors:
                message += f" {len(errors)} erros encontrados."

            return Response(
                {
                    "success": True,
                    "message": message,
                    "products_created": products_created,
                    "products_updated": products_updated,
                    "errors": errors,
                },
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            return Response(
                {"error": f"Erro ao processar arquivo Excel: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def _map_excel_row_to_product(self, row):
        """Mapear uma linha do Excel para dados do produto"""

        # Obter ou criar ProductType
        tipo_nome = str(row.get("Tipo", "")).strip()
        if not tipo_nome or tipo_nome.lower() in ["nan", "none", ""]:
            raise ValueError("Tipo do produto é obrigatório")

        product_type, _ = ProductType.objects.get_or_create(
            description=tipo_nome, defaults={"acronym": tipo_nome[:5].upper()}
        )

        # Obter ou criar Brand
        marca_nome = str(row.get("Marca", "")).strip()
        brand = None
        if marca_nome and marca_nome.lower() not in ["nan", "none", ""]:
            brand, _ = Brand.objects.get_or_create(description=marca_nome)

        # Obter ou criar Fabric
        material_nome = str(row.get("Material", "")).strip()
        fabric = None
        if material_nome and material_nome.lower() not in ["nan", "none", ""]:
            fabric, _ = Fabric.objects.get_or_create(description=material_nome)

        # Obter ou criar Color e ColorIntensity
        cor_nome = str(row.get("Cor", "")).strip()
        intensidade_nome = str(row.get("Intensidade de cor", "")).strip()
        color = None

        if cor_nome and cor_nome.lower() not in ["nan", "none", ""]:
            color_catalogue, _ = ColorCatalogue.objects.get_or_create(
                description=cor_nome
            )

            if intensidade_nome and intensidade_nome.lower() not in ["nan", "none", ""]:
                color_intensity, _ = ColorIntensity.objects.get_or_create(
                    description=intensidade_nome
                )
                color, _ = Color.objects.get_or_create(
                    color=color_catalogue, color_intensity=color_intensity
                )
            else:
                # Criar cor sem intensidade
                color_intensity, _ = ColorIntensity.objects.get_or_create(
                    description="Padrão"
                )
                color, _ = Color.objects.get_or_create(
                    color=color_catalogue, color_intensity=color_intensity
                )

        # Obter ou criar Pattern
        padronagem_nome = str(row.get("Padronagem", "")).strip()
        pattern = None
        if padronagem_nome and padronagem_nome.lower() not in ["nan", "none", ""]:
            pattern, _ = Pattern.objects.get_or_create(description=padronagem_nome)

        # Obter ou criar Button
        botoes_nome = str(row.get("Botões", "")).strip()
        button = None
        if botoes_nome and botoes_nome.lower() not in ["nan", "none", ""]:
            button, _ = Button.objects.get_or_create(description=botoes_nome)

        # Obter ou criar Lapel
        lapela_nome = str(row.get("Lapela", "")).strip()
        lapel = None
        if lapela_nome and lapela_nome.lower() not in ["nan", "none", ""]:
            lapel, _ = Lapel.objects.get_or_create(description=lapela_nome)

        # Obter ou criar Model
        nome_produto = str(row.get("Nome do produto", "")).strip()
        model = None
        if nome_produto and nome_produto.lower() not in ["nan", "none", ""]:
            model, _ = Model.objects.get_or_create(description=nome_produto)

        # Usar o ID do Excel como label_code - VALIDAÇÃO CRÍTICA
        label_code = str(row.get("ID", "")).strip()
        if not label_code or label_code.lower() in ["nan", "none", ""]:
            raise ValueError("ID do produto é obrigatório")

        # Verificar se o label_code já existe no banco
        if Product.objects.filter(label_code=label_code).exists():
            # Não criar erro aqui, apenas retornar os dados para atualização
            pass

        return {
            "product_type": product_type.id,
            "brand": brand.id if brand else None,
            "fabric": fabric.id if fabric else None,
            "color": color.id if color else None,
            "pattern": pattern.id if pattern else None,
            "button": button.id if button else None,
            "lapel": lapel.id if lapel else None,
            "model": model.id if model else None,
            "label_code": label_code,
            "on_stock": True,
        }


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
    permission_classes = [AllowAny]
    serializer_class = ProductSerializer

    def get(self, request, product_id):
        """Gerar QR Code para um produto"""
        try:
            product = Product.objects.get(id=product_id)

            # Criar QR Code
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(f"Produto: {product.label_code}")
            qr.make(fit=True)

            # Converter para imagem
            img = qr.make_image(fill_color="black", back_color="white")

            # Converter para base64
            buffer = io.BytesIO()
            img.save(buffer, format="PNG")
            qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()

            return Response(
                {
                    "success": True,
                    "qr_code": f"data:image/png;base64,{qr_code_base64}",
                    "label_code": product.label_code,
                    "product_info": {
                        "id": product.id,
                        "type": (
                            product.product_type.description
                            if product.product_type
                            else ""
                        ),
                        "brand": product.brand.description if product.brand else "",
                        "color": product.color.description if product.color else "",
                    },
                }
            )

        except Product.DoesNotExist:
            return Response(
                {"error": "Produto não encontrado"}, status=status.HTTP_404_NOT_FOUND
            )


@extend_schema(
    tags=["products"],
    summary="Lista de cores e combinações",
    description="Retorna todas as cores do catálogo e todas as combinações possíveis com intensidades, incluindo versões sem intensidade",
    responses={
        200: {
            "description": "Lista de cores e combinações",
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "color": {"type": "string", "description": "Nome da cor"},
                    "intensity": {
                        "type": "string",
                        "description": "Intensidade da cor (null se sem intensidade)",
                    },
                    "combined": {
                        "type": "string",
                        "description": "String combinada para pesquisa (ex: 'Preto FOSCO', 'Azul')",
                    },
                },
            },
        }
    },
    examples=[
        OpenApiExample(
            "Exemplo de resposta",
            value=[
                {"color": "Preto", "intensity": None, "combined": "Preto"},
                {"color": "Preto", "intensity": "FOSCO", "combined": "Preto FOSCO"},
                {"color": "Azul", "intensity": "BRILHO", "combined": "Azul BRILHO"},
            ],
            response_only=True,
            status_codes=["200"],
        )
    ],
)
class ColorListAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        """Lista todas as cores e combinações possíveis com intensidades"""
        from .models import Color, ColorCatalogue, ColorIntensity

        # Buscar todas as cores do catálogo
        colors = ColorCatalogue.objects.all()
        # Buscar todas as intensidades
        intensities = ColorIntensity.objects.all()
        # Buscar todas as combinações existentes
        color_combinations = Color.objects.select_related(
            "color", "color_intensity"
        ).all()

        result = []

        # 1. Adicionar cores sem intensidade (apenas do catálogo)
        for color in colors:
            result.append(
                {
                    "color": color.description,
                    "intensity": None,
                    "combined": color.description,
                }
            )

        # 2. Adicionar todas as combinações possíveis de cor + intensidade
        for color in colors:
            for intensity in intensities:
                # Verificar se esta combinação existe na tabela Color
                existing_combo = color_combinations.filter(
                    color=color, color_intensity=intensity
                ).first()

                if existing_combo:
                    # Combinação existe - usar dados reais
                    result.append(
                        {
                            "color": color.description,
                            "intensity": intensity.description,
                            "combined": f"{color.description} {intensity.description}",
                        }
                    )
                else:
                    # Combinação não existe - criar virtual
                    result.append(
                        {
                            "color": color.description,
                            "intensity": intensity.description,
                            "combined": f"{color.description} {intensity.description}",
                        }
                    )

        return Response(result)


@extend_schema(
    tags=["products"],
    summary="Lista de marcas",
    description="Retorna todas as marcas disponíveis no sistema",
    responses={
        200: {
            "description": "Lista de marcas",
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer", "description": "ID da marca"},
                    "description": {"type": "string", "description": "Nome da marca"},
                },
            },
        }
    },
    examples=[
        OpenApiExample(
            "Exemplo de resposta",
            value=[
                {"id": 1, "description": "Armani"},
                {"id": 2, "description": "Zara"},
                {"id": 3, "description": "Hugo Boss"},
            ],
            response_only=True,
            status_codes=["200"],
        )
    ],
)
class BrandListAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        """Lista todas as marcas disponíveis"""
        brands = Brand.objects.all()
        data = [
            {
                "id": brand.id,
                "description": brand.description,
            }
            for brand in brands
        ]
        return Response(data)


class ColorWithIntensityListAPIView(APIView):
    permission_classes = [AllowAny]

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
    permission_classes = [AllowAny]
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
