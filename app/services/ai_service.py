import os, httpx
from app.services.whatsapp_service import respuesta_predefinida

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
BSALE_TOKEN = os.getenv("BSALE_TOKEN")

CONTEXTO = """Eres el asistente virtual de Pibaz, pasteleria y cafeteria en El Bosque, Santiago.
Horario: todos los dias 10:00 a 20:45. Direccion: Gran Av JM Carrera 10375, El Bosque.
Telefono: +56998116140. Delivery todas las comunas de Santiago, solo tortas.
Pagos: transferencia, debito, credito, efectivo.
Tortas clasicas: 1 dia anticipacion. Premium: 5 dias. Retiro desde 14:00 si son mas de 15 porciones.
No hacemos tortas tematicas ni heladas. No tenemos sin azucar, sin lactosa ni sin gluten.
Para ver tortas: pibaz.cl. Para carta local: cartapibaz.cl.
Reservas mesas: llamar al +56998116140.
Si preguntan por pedido: pedir numero de pedido.
REGLA ABSOLUTA: WhatsApp es SOLO informativo. Para comprar ir a pibaz.cl o al local.
NUNCA pedir datos de pedido. Mensajes cortos, sin bullets, sin markdown, max 3 lineas."""

async def get_catalogo():
    try:
        async with httpx.AsyncClient(timeout=5) as c:
            r = await c.get("https://api.bsale.cl/v1/products.json?limit=74", headers={"access_token": BSALE_TOKEN})
            items = r.json().get("items", [])
            return ", ".join([i["name"] for i in items[:40]])
    except:
        return "Lucuma Manjar, Tres Leches, Selva Negra, Mil Hojas, Cheese Cake, Pompadour"

async def procesar_mensaje(mensaje: str, historial: list = []):
    pred = respuesta_predefinida(mensaje)
    if pred:
        return {"respuesta": pred, "fuente": "predefinida"}
    catalogo = await get_catalogo()
    sistema = CONTEXTO + "\n\nCATALOGO: " + catalogo
    try:
        headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
        msgs = [{"role": "system", "content": sistema}, {"role": "user", "content": mensaje}]
        payload = {"model": "llama-3.3-70b-versatile", "messages": msgs, "max_tokens": 200, "temperature": 0.3}
        async with httpx.AsyncClient(timeout=10) as c:
            r = await c.post("https://api.groq.com/openai/v1/chat/completions", json=payload, headers=headers)
            return {"respuesta": r.json()["choices"][0]["message"]["content"], "fuente": "groq"}
    except Exception as e:
        print(f"Groq fallo: {e}")
    try:
        headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
        msgs = [{"role": "system", "content": sistema}, {"role": "user", "content": mensaje}]
        payload = {"model": "gpt-4o-mini", "messages": msgs, "max_tokens": 200}
        async with httpx.AsyncClient(timeout=15) as c:
            r = await c.post("https://api.openai.com/v1/chat/completions", json=payload, headers=headers)
            return {"respuesta": r.json()["choices"][0]["message"]["content"], "fuente": "openai"}
    except Exception as e:
        print(f"OpenAI fallo: {e}")
    return {"respuesta": "Para mas info visita pibaz.cl o llamanos al +56998116140. Abrimos 10:00 a 20:45.", "fuente": "fallback"}

    return {"respuesta": "Para mas info visita pibaz.cl o llamanos al +56998116140. Abrimos 10:00 a 20:45.", "fuente": "fallback"}
