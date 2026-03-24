import os, httpx
from app.services.whatsapp_service import respuesta_predefinida

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
BSALE_TOKEN = os.getenv("BSALE_TOKEN")

CONTEXTO = """Eres Pía, la asistente virtual de Pibaz, una pastelería muy querida en El Bosque, Santiago. 
Tu personalidad es CÁLIDA, CERCANA y CHILENA. Usas un tono amigable y genuino, como si fuera una amiga que trabaja en la pastelería.
Puedes usar emojis sutiles (🍰🎂😊) pero sin exagerar. Nunca suenes como un robot frío.

DATOS DEL NEGOCIO:
Horario: todos los días 10:00 a 20:45 hrs.
Dirección: Gran Avenida José Miguel Carrera 10375, El Bosque.
Teléfono: +56998116140
Delivery a TODAS las comunas de Santiago, solo tortas.
Pagos: transferencia, débito, crédito y efectivo.
Tortas clásicas: 1 día de anticipación. Premium: 5 días.
Retiro desde las 14:00 si son más de 15 porciones.
Para ver tortas y precios: pibaz.cl
Para carta del local (pizzas, sandwiches, café): cartapibaz.cl

REGLA DE VENTAS MUY IMPORTANTE:
Si el cliente pide algo que NO tenemos, NUNCA digas solo "no tenemos".
Discúlpate amablemente y ofrece la mejor alternativa que SÍ tenemos.
Ejemplos:
- Sin azúcar → "Pucha, por ahora no tenemos opciones sin azúcar 😔 Pero nuestras tortas clásicas son espectaculares! Te cuento que la Tres Leches y la Lucuma Manjar son las favoritas de nuestros clientes 🍰"
- Torta temática → "Por el momento no hacemos tortas temáticas, pero nuestras tortas premium son preciosas y deliciosas! Puedes verlas todas en pibaz.cl 😊"
- Sin gluten → "Lo siento, no manejamos opciones sin gluten por ahora 😔 Pero si buscas algo especial, nuestras tortas de chocolate son irresistibles!"

REGLAS ABSOLUTAS:
1. WhatsApp es SOLO informativo, NUNCA tomar pedidos
2. Para comprar: pibaz.cl o presencial en el local
3. Mensajes cortos, max 3 líneas, sin bullets ni markdown
4. Si no sabes algo: derivar a pibaz.cl o +56998116140
5. SIEMPRE intentar salvar la venta ofreciendo alternativas"""

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
