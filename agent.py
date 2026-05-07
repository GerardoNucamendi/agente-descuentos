"""
Agente de Descuentos - MercadoLibre México
Busca productos con más de 50% de descuento en Electrónica, Moda y Deportes
"""

import requests
import json
from datetime import datetime

DESCUENTO_MINIMO = 50

BUSQUEDAS = [
    # Electrónica
    {"keyword": "celular", "categoria": "Electrónica"},
    {"keyword": "laptop", "categoria": "Electrónica"},
    {"keyword": "audifonos", "categoria": "Electrónica"},
    {"keyword": "tablet", "categoria": "Electrónica"},
    {"keyword": "smartwatch", "categoria": "Electrónica"},
    # Moda y Calzado
    {"keyword": "tenis", "categoria": "Moda y Calzado"},
    {"keyword": "ropa mujer", "categoria": "Moda y Calzado"},
    {"keyword": "zapatos", "categoria": "Moda y Calzado"},
    {"keyword": "chamarra", "categoria": "Moda y Calzado"},
    # Deportes y Suplementos
    {"keyword": "proteina", "categoria": "Deportes y Fitness"},
    {"keyword": "creatina", "categoria": "Deportes y Fitness"},
    {"keyword": "pesas", "categoria": "Deportes y Fitness"},
    {"keyword": "bicicleta", "categoria": "Deportes y Fitness"},
]


def buscar_ofertas(keyword, categoria):
    """Busca usando la API pública de MercadoLibre (sin autenticación)"""
    url = "https://api.mercadolibre.com/sites/MLM/search"
    params = {
        "q": keyword,
        "limit": 20,
        "sort": "relevance",
    }

    try:
        resp = requests.get(url, params=params, timeout=10)
        if resp.status_code != 200:
            print(f"  Error {resp.status_code} buscando '{keyword}'")
            return []

        resultados = resp.json().get("results", [])
        ofertas = []

        for item in resultados:
            precio_original = item.get("original_price")
            precio_actual = item.get("price")

            if not precio_original or not precio_actual:
                continue

            if precio_original <= precio_actual:
                continue

            descuento = ((precio_original - precio_actual) / precio_original) * 100

            if descuento >= DESCUENTO_MINIMO:
                ofertas.append({
                    "titulo": item.get("title"),
                    "precio_original": precio_original,
                    "precio_actual": precio_actual,
                    "descuento": round(descuento, 1),
                    "link": item.get("permalink"),
                    "categoria": categoria,
                })

        return ofertas

    except Exception as e:
        print(f"  Excepcion buscando '{keyword}': {e}")
        return []


def formatear_post(oferta):
    emoji = {"Electrónica": "📱", "Moda y Calzado": "👟", "Deportes y Fitness": "🏋️"}.get(oferta["categoria"], "🛍️")
    return f"""{emoji} OFERTA {oferta['descuento']}% DE DESCUENTO!

{oferta['titulo']}

Antes: ${oferta['precio_original']:,.2f}
AHORA: ${oferta['precio_actual']:,.2f}

Compra aqui: {oferta['link']}

#Ofertas #MercadoLibre #Descuentos
"""


def main():
    print("=" * 60)
    print("AGENTE DE DESCUENTOS - MERCADOLIBRE MEXICO")
    print(f"Descuento minimo: {DESCUENTO_MINIMO}%")
    print("=" * 60)

    todas = []

    for b in BUSQUEDAS:
        print(f"\nBuscando '{b['keyword']}' en {b['categoria']}...")
        ofertas = buscar_ofertas(b["keyword"], b["categoria"])
        print(f"  -> {len(ofertas)} ofertas encontradas")
        todas.extend(ofertas)

    # Eliminar duplicados por link
    vistos = set()
    sin_duplicados = []
    for o in todas:
        if o["link"] not in vistos:
            vistos.add(o["link"])
            sin_duplicados.append(o)

    sin_duplicados.sort(key=lambda x: x["descuento"], reverse=True)

    print(f"\n{'='*60}")
    print(f"TOTAL OFERTAS ENCONTRADAS: {len(sin_duplicados)}")
    print(f"{'='*60}")

    if not sin_duplicados:
        print("No se encontraron ofertas con ese descuento ahora.")
        return

    # Mostrar top 5
    print("\nTOP 5 MEJORES DESCUENTOS:")
    for i, o in enumerate(sin_duplicados[:5], 1):
        print(f"\n{i}. [{o['descuento']}% OFF] {o['titulo'][:60]}")
        print(f"   ${o['precio_original']:,.0f} -> ${o['precio_actual']:,.0f}")
        print(f"   {o['link']}")

    # Guardar JSON
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"ofertas_{timestamp}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(sin_duplicados, f, ensure_ascii=False, indent=2)
    print(f"\nGuardado: {filename}")

    # Guardar posts
    posts_file = f"posts_facebook_{timestamp}.txt"
    with open(posts_file, "w", encoding="utf-8") as f:
        f.write(f"POSTS GENERADOS EL {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n")
        for i, o in enumerate(sin_duplicados, 1):
            f.write(f"--- POST #{i} ---\n")
            f.write(formatear_post(o))
            f.write("\n" + "=" * 50 + "\n\n")
    print(f"Guardado: {posts_file}")


if __name__ == "__main__":
    main()
