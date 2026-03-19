import os, httpx
from app.services.whatsapp_service import respuesta_predefinida

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
BSALE_TOKEN = os.getenv("BSALE_TOKEN")

CONTEXTO_PIBAZ = """Eres el asistente virtual de Pibaz, pasteleria y cafeteria en El Bosque, Santiago de Chile.

NEGOCIO:
- Pasteleria + cafeteria con pizzas y sandwiches
- Carta completa del local en cartapibaz.cl
- Tortas en pibaz.cl
- Horario: todos los dias 10:00 a 20:45 hrs
- Direccion: Gran Avenida Jose Miguel Carrera 10375, El Bosque
- Telefono: +56998116140
- Delivery a TODAS las comunas de Santiago (solo tortas)
- Pagos: transferencia, debito, credito y efectivo

PEDIDOS DE TORTAS:
- Tortas clasicas: 1 dia de anticipacion
- Tortas premium: 5 dias de anticipacion
- Tortas de mas de 15 porciones: retiro desde las 14:00 hrs
- Si se atrasan: la torta estara disponible hasta las 20:45 sin problema
- NO hacemos tortas con tematica ni diseños personalizados
- NO hacemos tortas heladas

RESTRICCIONES ALIMENTARIAS:
- NO tenemos productos sin azucar, sin lactosa ni sin gluten

DESCRIPCION DE TORTAS:
- Para descripcion, ingredientes y fotos de CUALQUIER torta: pibaz.cl (todas estan ahi)
- Cada torta tiene su descripcion completa en la pagina web

RESERVA DE MESAS:
- Depende del dia, llamar al +56998116140 o ir al local directamente

CONFIRMACION DE PEDIDOS:
- Si el cliente quiere confirmar un pedido: pedirle su NUMERO DE PEDIDO
- Decirle: "Envianos tu numero de pedido y lo revisamos de inmediato"

REGLAS ABSOLUTAS:
1. WhatsApp es SOLO informativo, NUNCA tomar pedidos
2. Para comprar tortas: pibaz.cl o presencial en el local
3. Para carta del local (pizzas, sandwiches, cafe): cartapibaz.cl
4. NUNCA pedir datos de pedido (porciones, fecha, nombre)
5. Si preguntan descripcion de torta: dirigir a pibaz.cl
6. Si preguntan por despacho: SI llegamos a todas las comunas de Santiago
7. Mensajes cortos y amables"""

async def confirmar_pedido_bsale(numero_pedido: str):
    try:
        headers = {"access_token": BSALE_TOKEN}
        async with httpx.AsyncClient(timeout=8) as client:
            r = await client.get(
                f"https://api.bsale.cl/v1/documents.json?number={numero_pedido}&limit=5",
                headers=headers
            )
            data = r.json()
            if data.get("count", 0) > 0:
                doc = data["items"][0]
                total = doc.get("totalAmount", 0)
                fecha = doc.get("emissionDate", "")
                estado = doc.get("state", 0)
                estado_texto = "Pagado y confirmado" if estado == 0 else "En proceso"
                from datetime import datetime
                if fecha:
                    fecha_legible = datetime.fromtimestamp(fecha).strftime("%d/%m/%Y")
                else:
                    fecha_legible = "No disponible"
                return f"Tu pedido #{numero_pedido} esta {estado_texto}. Fecha: {fecha_legible}. Total: ${total:,}. Te esperamos en el local!"
            else:
                return f"No encontramos el pedido #{numero_pedido}. Verifica el numero o llamanos al +56998116140."
    except Exception as e:
        print(f"Error Bsale: {e}")
        return f"No pudimos verificar el pedido #{numero_pedido} en este momento. Llamanos al +56998116140."

async def get_catalogo_bsale():
    try:
        headers = {"access_token": BSALE_TOKEN}
        async with httpx.AsyncClient(timeout=5) as client:
            r = await client.get("https://api.bsale.cl/v1/products.json?limit=74", headers=headers)
            data = r.json()
            productos = [item["name"] for item in data.get("items", [])]
            return ", ".join(productos[:40])
    except:
        return "Lucuma Manjar, Tres Leches, Selva Negra, Mil Hojas, Cheese Cake, Pompadour"

async def responder_con_groq(mensaje: str, catalogo: str, historial: list = []):
    sistema = f"{CONTEXTO_PIBAZ}\n\nCATALOGO: {catalogo}"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    messages = [{"role": "system", "content": sistema}]
    messages.extend(historial)
    messages.append({"role": "user", "content": mensaje})
    payload = {"model": "llama-3.3-70b-versatile", "messages": messages, "max_tokens": 200, "temperature": 0.3}
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.post("https://api.groq.com/openai/v1/chat/completions", json=payload, headers=headers)
        return r.json()["choices"][0]["message"]["content"]

async def responder_con_openai(mensaje: str, catalogo: str, historial: list = []):
    sistema = f"{CONTEXTO_PIBAZ}\n\nCATALOGO: {catalogo}"
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

    # Detectar numero de pedido en el mensaje
    import re
    numeros = re.findall(r'\b\d{4,}\b', mensaje)
    if numeros and any(w in mensaje.lower() for w in ["pedido", "orden", "compra", "confirmar", "verificar"]):
        respuesta = await confirmar_pedido_bsale(numeros[0])
        return {"respuesta": respuesta, "fuente": "bsale"}

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
        "respuesta": "Para mas informacion visita pibaz.cl o llamanos al +56998116140. Abrimos todos los dias de 10:00 a 20:45 hrs.",
        "fuente": "fallback"
    }
