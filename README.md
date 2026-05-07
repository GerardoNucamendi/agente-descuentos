# 🤖 Agente de Descuentos - MercadoLibre México

Busca automáticamente productos con **más del 50% de descuento** en:
- 📱 Electrónica
- 👟 Moda y Calzado  
- 🏋️ Deportes y Suplementos

Y genera posts listos para publicar en **Facebook**.

---

## 🚀 Instalación rápida (3 pasos)

### Paso 1 — Clona o sube el código a GitHub

1. Ve a [github.com](https://github.com) y crea una cuenta gratis si no tienes
2. Crea un nuevo repositorio (ej: `agente-descuentos`)
3. Sube los archivos `agent.py` y la carpeta `.github/`

### Paso 2 — Agrega tus credenciales como Secrets

En tu repositorio de GitHub:
1. Ve a **Settings** → **Secrets and variables** → **Actions**
2. Haz clic en **"New repository secret"**
3. Agrega estos dos secrets:

| Nombre | Valor |
|--------|-------|
| `ML_CLIENT_ID` | Tu Client ID de MercadoLibre |
| `ML_CLIENT_SECRET` | Tu Secret Key de MercadoLibre |

### Paso 3 — Activa el workflow

1. Ve a la pestaña **Actions** en tu repositorio
2. Haz clic en **"I understand my workflows, go ahead and enable them"**
3. ¡Listo! El agente correrá automáticamente cada 6 horas

---

## ▶️ Correr manualmente

En la pestaña **Actions** → selecciona el workflow → clic en **"Run workflow"**

---

## 📥 Ver los resultados

Después de cada ejecución:
1. Ve a **Actions** → clic en la ejecución más reciente
2. Baja hasta **Artifacts**
3. Descarga el archivo ZIP con:
   - `ofertas_FECHA.json` — datos completos de las ofertas
   - `posts_facebook_FECHA.txt` — posts listos para copiar y pegar en Facebook

---

## ⚙️ Configuración

Puedes editar `agent.py` para ajustar:

```python
DESCUENTO_MINIMO = 50  # Cambia el % mínimo de descuento

KEYWORDS_POR_CATEGORIA = {
    "Electrónica": ["celular", "laptop", ...],  # Agrega más palabras clave
    ...
}
```

---

## 🔧 Correr en tu computadora (opcional)

```bash
# Instalar dependencia
pip install requests

# Configurar credenciales
export ML_CLIENT_ID="tu_client_id"
export ML_CLIENT_SECRET="tu_secret_key"

# Correr
python agent.py
```

---

## 📋 Próximos pasos sugeridos

- [ ] Conectar con Facebook Graph API para publicar automáticamente
- [ ] Agregar Amazon México (requiere cuenta de afiliado)
- [ ] Filtrar por precio máximo o mínimo
- [ ] Enviar las ofertas por Telegram o WhatsApp
