import os

import django
import pandas as pd

# Inicializar Django antes de importar os models
os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE", "roupadegala.settings"
)  # substitua 'your_project'
django.setup()

from .models import Brand, Color, Fabric, Pattern, Product


def load_products_from_excel():
    excel_path = os.path.join(os.path.dirname(__file__), "products.xlsx")
    if not os.path.exists(excel_path):
        print("Arquivo products.xlsx não encontrado.")
        return

    df = pd.read_excel(excel_path)

    # Padronizar colunas
    df.columns = df.columns.str.strip().str.upper()

    # Dicionários para cache de dados existentes
    brand_cache = {b.name: b for b in Brand.objects.all()}
    fabric_cache = {f.name: f for f in Fabric.objects.all()}
    color_cache = {(c.name, c.intensity): c for c in Color.objects.all()}
    pattern_cache = {p.name: p for p in Pattern.objects.all()}

    product_type_map = {
        "SMOKING (SMK)": "SMK",
        "PALETO (PLT)": "PLT",
        "BLAZER (BLZ)": "BLZ",
        "COLETE (CLT)": "VST",
        "CALÇA (CLC)": "PNT",
    }

    for _, row in df.iterrows():
        tipo = product_type_map.get(row["PRODUTOS"], "UNK")

        # Marca
        brand_name = row["MARCA"]
        if pd.notna(brand_name):
            brand = brand_cache.get(brand_name) or Brand.objects.create(name=brand_name)
            brand_cache[brand_name] = brand
        else:
            brand = None

        # Tecido
        fabric_name = row["MATERIAL"]
        if pd.notna(fabric_name):
            fabric = fabric_cache.get(fabric_name) or Fabric.objects.create(
                name=fabric_name
            )
            fabric_cache[fabric_name] = fabric
        else:
            fabric = None

        # Cor
        color_name = row["COR"]
        intensity = (
            row["INTENSIDADE DE COR"] if pd.notna(row["INTENSIDADE DE COR"]) else None
        )
        color_key = (color_name, intensity)
        if pd.notna(color_name):
            color = color_cache.get(color_key) or Color.objects.create(
                name=color_name, intensity=intensity
            )
            color_cache[color_key] = color
        else:
            color = None

        # Padronagem
        pattern = None
        pattern_name = row.get("PADRONAGEM")
        if pd.notna(pattern_name):
            pattern = pattern_cache.get(pattern_name) or Pattern.objects.create(
                name=pattern_name
            )
            pattern_cache[pattern_name] = pattern

        # Verifica se já existe um produto igual
        exists = Product.objects.filter(
            type=tipo,
            brand=brand,
            fabric=fabric,
            color=color,
            pattern=pattern,
            buttons=row["BOTOES"] if pd.notna(row["BOTOES"]) else None,
            lapel=row["LAPELA"] if pd.notna(row["LAPELA"]) else None,
            model=row["MODELO"] if pd.notna(row["MODELO"]) else None,
        ).exists()

        if not exists:
            Product.objects.create(
                type=tipo,
                brand=brand,
                fabric=fabric,
                color=color,
                pattern=pattern,
                buttons=row["BOTOES"] if pd.notna(row["BOTOES"]) else None,
                lapel=row["LAPELA"] if pd.notna(row["LAPELA"]) else None,
                model=row["MODELO"] if pd.notna(row["MODELO"]) else None,
            )

    print("Produtos atualizados com sucesso!")


# ⚙️ Chamar ao iniciar o servidor
load_products_from_excel()
