"""
Agente de Descuentos - MercadoLibre México
Busca productos con más de 50% de descuento en Electrónica, Moda y Deportes
"""

import requests
import json
import os
from datetime import datetime

# ============================================================
# CONFIGURACIÓN - Pon tus credenciales aquí o en variables de entorno
# ============================================================
CLIENT_ID = os.getenv("ML_CLIENT_ID", "8471418706132879")
CLIENT_SECRET = os.getenv("ML_CLIENT_SECRET", "ZlQdAlTXH01NBvAnoGfRzQVCU0jSVMtA")

DESCUENTO_MINIMO = 50  # Porcentaje mínimo de descuento

# Categorías de MercadoLibre México
CATEGORIAS = {
    "Electrónica":        "MLM1000",
    "Moda y Calzado":     "MLM1430",
    "Deportes y Fitness": "MLM1276",
}

# Palabras clave extra para búsqueda dentro de cada categoría
KEYWORDS_POR_CATEGORIA = {
    "Electrónica":        ["celular", "laptop", "audífonos", "tablet", "smartwatch"],
    "Moda y Calzado":     ["tenis", "ropa", "zapatos", "chamarra", "vestido"],
    "Deportes y Fitness": ["proteína", "creatina", "pesas", "bicicleta", "ropa deportiva"],
}

# ============================================================
# AUTENTICACIÓN
# ============================================================
def obtener_token():
    """Obtiene access token usando Client Credentials flow"""
    url = "https://api.mercadolibre.com/oauth/token"
    payload = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }
    resp = requests.post(url, data=payload)
    resp.raise_for_status()
    token = resp.json().get("access_token")
    print(f"✅ Token obtenido correctamente")
    return token


# ============================================================
# BÚSQUEDA DE OFERTAS
# ============================================================
def buscar_ofertas(token, categoria_id, keyword, limite=10):
    """Busca productos en una categoría y filtra por descuento"""
    url = "https://api.mercadolibre.com/sites/MLM/search"
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "category": categoria_id,
        "q": keyword,
        "limit": limite,
        "sort": "price_asc",
    }
    resp = requests.get(url, headers=headers, params=params)
    if resp.status_code != 200:
        print(f"  ⚠️ Error buscando '{keyword}': {resp.status_code}")
        return []

    resultados = resp.json().get("results", [])
    ofertas = []

    for item in resultados:
        precio_original = item.get("original_price")
        precio_actual = item.get("price")

        # Solo productos que tienen precio original (están en oferta)
        if not precio_original or not precio_actual:
            continue

        descuento = ((precio_original - precio_actual) / precio_original) * 100

        if descuento >= DESCUENTO_MINIMO:
            ofertas.append({
                "titulo": item.get("title"),
                "precio_original": precio_original,
                "precio_actual": precio_actual,
                "descuento": round(descuento, 1),
                "link": item.get("permalink"),
                "imagen": item.get("thumbnail", "").replace("I.jpg", "O.jpg"),
                "vendedor": item.get("seller", {}).get("nickname", ""),
                "categoria": item.get("category_id", ""),
            })

    return ofertas


def buscar_todas_las_categorias(token):
    """Recorre todas las categorías y keywords, devuelve lista de ofertas"""
    todas = []

    for nombre_cat, cat_id in CATEGORIAS.items():
        print(f"\n📦 Buscando en: {nombre_cat}")
        keywords = KEYWORDS_POR_CATEGORIA[nombre_cat]

        for kw in keywords:
            print(f"  🔍 '{kw}'...")
            ofertas = buscar_ofertas(token, cat_id, kw)
            for o in ofertas:
                o["nombre_categoria"] = nombre_cat
            todas.extend(ofertas)
            print(f"     → {len(ofertas)} ofertas encontradas")

    # Eliminar duplicados por link
    vistos = set()
    sin_duplicados = []
    for o in todas:
        if o["link"] not in vistos:
            vistos.add(o["link"])
            sin_duplicados.append(o)

    # Ordenar por mayor descuento primero
    sin_duplicados.sort(key=lambda x: x["descuento"], reverse=True)
    return sin_duplicados


# ============================================================
# FORMATO PARA FACEBOOK
# ============================================================
def formatear_post_facebook(oferta):
    """Genera el texto del post para Facebook"""
    emoji_cat = {
        "Electrónica": "📱",
        "Moda y Calzado": "👟",
        "Deportes y Fitness": "🏋️",
    }.get(oferta["nombre_categoria"], "🛍️")

    texto = f"""🔥 ¡OFERTA INCREÍBLE! {emoji_cat}

{oferta['titulo']}

💰 Antes: ${oferta['precio_original']:,.2f}
✅ AHORA: ${oferta['precio_actual']:,.2f}
🏷️ ¡{oferta['descuento']}% de DESCUENTO!

👉 Compra aquí: {oferta['link']}

#Ofertas #MercadoLibre #Descuentos #{oferta['nombre_categoria'].replace(' ', '')}
"""
    return texto


# ============================================================
# GUARDAR RESULTADOS
# ============================================================
def guardar_resultados(ofertas):
    """Guarda las ofertas en JSON y genera los posts de Facebook"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Guardar JSON completo
    with open(f"ofertas_{timestamp}.json", "w", encoding="utf-8") as f:
        json.dump(ofertas, f, ensure_ascii=False, indent=2)

    # Guardar posts de Facebook en TXT
    with open(f"posts_facebook_{timestamp}.txt", "w", encoding="utf-8") as f:
        f.write(f"=== POSTS GENERADOS EL {datetime.now().strftime('%d/%m/%Y %H:%M')} ===\n\n")
        for i, oferta in enumerate(ofertas, 1):
            f.write(f"--- POST #{i} ({oferta['nombre_categoria']}) ---\n")
            f.write(formatear_post_facebook(oferta))
            f.write("\n" + "="*60 + "\n\n")

    print(f"\n✅ Guardados: ofertas_{timestamp}.json")
    print(f"✅ Guardados: posts_facebook_{timestamp}.txt")
    return timestamp


# ============================================================
# MAIN
# ============================================================
def main():
    print("=" * 60)
    print("🤖 AGENTE DE DESCUENTOS - MERCADOLIBRE MÉXICO")
    print(f"   Descuento mínimo: {DESCUENTO_MINIMO}%")
    print(f"   Categorías: {', '.join(CATEGORIAS.keys())}")
    print("=" * 60)

    # 1. Autenticar
    token = obtener_token()

    # 2. Buscar ofertas
    ofertas = buscar_todas_las_categorias(token)

    # 3. Mostrar resumen
    print(f"\n{'='*60}")
    print(f"🎯 TOTAL DE OFERTAS ENCONTRADAS: {len(ofertas)}")
    print(f"{'='*60}")

    if not ofertas:
        print("😕 No se encontraron ofertas con ese descuento en este momento.")
        print("   Intenta aumentar el rango de keywords o bajar el % mínimo.")
        return

    # 4. Mostrar top 5
    print("\n🏆 TOP 5 MEJORES DESCUENTOS:")
    for i, o in enumerate(ofertas[:5], 1):
        print(f"\n{i}. [{o['descuento']}% OFF] {o['titulo'][:60]}...")
        print(f"   ${o['precio_original']:,.0f} → ${o['precio_actual']:,.0f}")
        print(f"   {o['link']}")

    # 5. Guardar todo
    guardar_resultados(ofertas)

    print("\n🚀 ¡Listo! Revisa los archivos generados para copiar y pegar en Facebook.")


if __name__ == "__main__":
    main()
