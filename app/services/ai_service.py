import os, httpx
from app.services.whatsapp_service import respuesta_predefinida

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
BSALE_TOKEN = os.getenv("BSALE_TOKEN")

CONTEXTO = """Eres Pia, la asistente virtual de Pibaz, una pasteleria muy querida en El Bosque, Santiago.
Tu personalidad es CALIDA, CERCANA y CHILENA. Tono amigable, como una amiga que trabaja en la pasteleria.
Puedes usar emojis sutiles (🍰🎂😊) pero sin exagerar. Nunca suenes fria ni robotica.

NEGOCIO:
- Horario: todos los dias 10:00 a 20:45 hrs
- Direccion: Gran Avenida Jose Miguel Carrera 10375, El Bosque, Santiago
- Telefono: +56998116140
- Delivery a TODAS las comunas de Santiago, solo tortas
- Pagos: transferencia, debito, credito y efectivo
- Tortas clasicas: 1 dia anticipacion. Premium: 5 dias
- Retiro desde las 14:00 si son mas de 15 porciones
- Tortas y precios: pibaz.cl
- Carta local (pizzas, sandwiches, cafe): cartapibaz.cl

REGLA DE VENTAS:
Si el cliente pide algo que NO tenemos, NUNCA digas solo "no tenemos".
Disculate amablemente y ofrece la mejor alternativa que SI tenemos.
- Sin azucar/lactosa/gluten: ofrece tortas clasicas favoritas
- Torta tematica: ofrece tortas premium que si tenemos

REGLAS ABSOLUTAS:
1. WhatsApp es SOLO informativo, NUNCA tomar pedidos
2. Para comprar: pibaz.cl o presencial
3. Si preguntan ingredientes de una torta: NUNCA inventar, derivar a pibaz.cl
4. Mensajes cortos, max 3 lineas, sin bullets ni markdown
5. Si no sabes algo: derivar a pibaz.cl o +56998116140"""

async def get_catalogo():
    try:
        async with httpx.AsyncClient(timeout=5) as c:
            r = await c.get(
                "https://api.bsale.cl/v1/products.json?limit=74",
                headers={"access_token": BSALE_TOKEN}
            )
            items = r.json().get("items", [])
            return ", ".join([i["name"] for i in items[:40]])
    except:
        return "Lucuma Manjar, Tres Leches, Selva Negra, Mil Hojas, Cheese Cake, Pompadour, Catalina"

async def responder_con_openai(mensaje: str, catalogo: str) -> str:
    sistema = f"{CONTEXTO}\n\nCATALOGO REAL: {catalogo}"
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "system", "content": sistema}, {"role": "user", "content": mensaje}],
        "max_tokens": 200,
        "temperature": 0.7,
    }
    async with httpx.AsyncClient(timeout=12) as c:
        r = await c.post("https://api.openai.com/v1/chat/completions", json=payload, headers=headers)
        return r.json()["choices"][0]["message"]["content"]

async def responder_con_groq(mensaje: str, catalogo: str) -> str:
    sistema = f"{CONTEXTO}\n\nCATALOGO REAL: {catalogo}"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "system", "content": sistema}, {"role": "user", "content": mensaje}],
        "max_tokens": 200,
        "temperature": 0.5,
    }
    async with httpx.AsyncClient(timeout=8) as c:
        r = await c.post("https://api.groq.com/openai/v1/chat/completions", json=payload, headers=headers)
        return r.json()["choices"][0]["message"]["content"]

async def procesar_mensaje(mensaje: str, historial: list = []):
    predefinida = respuesta_predefinida(mensaje)
    if predefinida:
        return {"respuesta": predefinida, "fuente": "predefinida"}
    catalogo = await get_catalogo()
    try:
        respuesta = await responder_con_openai(mensaje, catalogo)
        return {"respuesta": respuesta, "fuente": "openai"}
    except Exception as e:
        print(f"OpenAI fallo: {e}")
    try:
        respuesta = await responder_con_groq(mensaje, catalogo)
        return {"respuesta": respuesta, "fuente": "groq"}
    except Exception as e:
        print(f"Groq fallo: {e}")
    return {
        "respuesta": "Hola! Para mas informacion visita pibaz.cl o llamanos al +56998116140 😊 Abrimos todos los dias de 10:00 a 20:45!",
        "fuente": "fallback"
    }
