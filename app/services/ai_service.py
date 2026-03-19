import os, httpx
from app.services.whatsapp_service import respuesta_predefinida

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
BSALE_TOKEN = os.getenv("BSALE_TOKEN")

async def get_catalogo_bsale():
    try:
        headers = {"access_token": BSALE_TOKEN}
        async with httpx.AsyncClient(timeout=5) as client:
            r = await client.get("https://api.bsale.cl/v1/products.json?limit=74", headers=headers)
            data = r.json()
            productos = [item["name"] for item in data.get("items", [])]
            return ", ".join(productos[:30])
    except:
        return "Lucuma Manjar, Tres Leches, Selva Negra, Mil Hojas, Cheese Cake, Pompadour"

async def responder_con_groq(mensaje: str, catalogo: str, historial: list = []):
    sistema = f"""Eres el asistente virtual de Pibaz, pasteleria y cafeteria en El Bosque, Santiago de Chile.

CATALOGO REAL: {catalogo}

REGLAS ABSOLUTAS - debes seguirlas siempre:
1. WhatsApp es SOLO para informar, NUNCA para tomar pedidos
2. Para cualquier compra o pedido: dirigir a pibaz.cl o al local presencialmente
3. NUNCA preguntes porciones, fecha, datos de contacto ni nada relacionado a un pedido
4. Si alguien quiere comprar di: "Puedes hacer tu pedido en pibaz.cl o visitarnos en el local"
5. Usa SOLO productos del catalogo real
6. Mensajes cortos y amables (es WhatsApp)
7. Horario: todos los dias 10:00 a 20:45 hrs
8. Delivery solo tortas, reservar antes de 15:00 para mismo dia"""

    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    messages = [{"role": "system", "content": sistema}]
    messages.extend(historial)
    messages.append({"role": "user", "content": mensaje})
    payload = {"model": "llama-3.3-70b-versatile", "messages": messages, "max_tokens": 200, "temperature": 0.3}
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.post("https://api.groq.com/openai/v1/chat/completions", json=payload, headers=headers)
        return r.json()["choices"][0]["message"]["content"]

async def responder_con_openai(mensaje: str, catalogo: str, historial: list = []):
    sistema = f"Asistente Pibaz. Catalogo: {catalogo}. NUNCA tomes pedidos, siempre dirigir a pibaz.cl o al local. Mensajes cortos."
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
    messages = [{"role": "system", "content": sistema}]
    messages.extend(historial)
    messages.append({"role": "user", "content": mensaje})
    payload = {"model": "gpt-4o-mini", "messages": messages, "max_tokens": 200}
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.post("https://api.openai.com/v1/chat/completions", json=payload, headers=headers)
        return r.json()["choices"][0]["message"]["content"]

async def procesar_mensaje(mensaje: str, historial: list = []):
    predefinida = respuesta_predefinida(mensaje)
    if predefinida:
        return {"respuesta": predefinida, "fuente": "predefinida"}
    catalogo = await get_catalogo_bsale()
    try:
        respuesta = await responder_con_groq(mensaje, catalogo, historial)
        return {"respuesta": respuesta, "fuente": "groq"}
    except Exception as e:
        print(f"Groq fallo: {e}")
    try:
        respuesta = await responder_con_openai(mensaje, catalogo, historial)
        return {"respuesta": respuesta, "fuente": "openai"}
    except Exception as e:
        print(f"OpenAI fallo: {e}")
    return {
        "respuesta": "Hola! Puedes ver nuestras tortas en pibaz.cl o visitarnos en el local. Abrimos todos los dias de 10:00 a 20:45 hrs.",
        "fuente": "fallback"
    }
