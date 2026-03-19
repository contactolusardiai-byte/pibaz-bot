import httpx, os

WA_TOKEN = os.getenv("WHATSAPP_TOKEN")
WA_PHONE_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
WA_URL = f"https://graph.facebook.com/v18.0/{WA_PHONE_ID}/messages"

RESPUESTAS = {
    "horario": "Abrimos todos los dias de 10:00 a 20:45 hrs.",
    "ubicacion": "Estamos en El Bosque, Santiago. Escríbenos para la ubicacion exacta.",
    "precio": "Puedes ver precios y disponibilidad en pibaz.cl",
    "anticipacion": "Tortas clasicas: 1 dia de anticipacion. Tortas premium: 5 dias.\n\nPuedes hacer tu pedido en pibaz.cl o directamente en el local.",
    "delivery": "El delivery es solo de tortas. Puedes reservar hasta las 15:00 para recibir el mismo dia.\n\nVisita pibaz.cl o acercate al local en El Bosque.",
    "pago": "Aceptamos transferencia, debito, credito y efectivo.",
    "sin_azucar": "Por el momento no contamos con tortas sin azucar. Puedes ver nuestro catalogo completo en pibaz.cl",
    "catalogo": "Todas nuestras tortas estan disponibles en pibaz.cl en la seccion Retiro Inmediato.\n\nTambien puedes visitarnos directamente en el local en El Bosque, Santiago. Abrimos todos los dias de 10:00 a 20:45 hrs.",
    "chocolate": "Tenemos varias tortas con chocolate:\n- Selva Negra\n- Panqueque Chocolate con Manjar\n- Panqueque Chocolate con Guinda\n- Trilogia de Chocolates\n- Torta Oreo\n\nEncuentralas en pibaz.cl seccion Retiro Inmediato o visitanos en el local.",
    "lucuma": "Si! Tenemos la Torta Lucuma Manjar en distintas porciones.\n\nEncuentrala en pibaz.cl seccion Retiro Inmediato o visitanos en el local en El Bosque.",
    "comprar_hoy": "Para tortas disponibles hoy visita pibaz.cl seccion Retiro Inmediato o acercate al local en El Bosque. Abrimos de 10:00 a 20:45 hrs.",
    "comprar_anticipado": "Para pedidos con anticipacion visita pibaz.cl o acercate al local.\n\nTortas clasicas: 1 dia de anticipacion.\nTortas premium: 5 dias de anticipacion.",
}

PALABRAS_CLAVE = {
    "horario": ["horario", "hora", "abren", "cierran", "atienden", "abiertos"],
    "ubicacion": ["donde", "ubicacion", "direccion", "llegar", "local", "queda"],
    "precio": ["precio", "cuanto", "cuesta", "valor", "tarifa", "cobran"],
    "anticipacion": ["anticipacion", "plazo", "con cuanto"],
    "delivery": ["delivery", "despacho", "envio", "llevan", "domicilio", "despachan"],
    "pago": ["pago", "pagar", "transferencia", "tarjeta", "efectivo", "webpay"],
    "sin_azucar": ["sin azucar", "diabetico", "diabetes", "light", "sin gluten", "celiaco", "vegano"],
    "catalogo": ["que tortas", "que tienen", "catalogo", "menu", "tortas tienen", "que pasteles", "que ofrecen", "que venden"],
    "chocolate": ["chocolate", "choco"],
    "lucuma": ["lucuma"],
    "comprar_hoy": ["hoy", "retiro inmediato", "disponible ahora", "para hoy", "mismo dia"],
    "comprar_anticipado": ["pedir", "comprar", "reservar", "encargar", "para manana", "para el", "para la proxima"],
}

def respuesta_predefinida(mensaje: str):
    msg = mensaje.lower()
    for categoria, palabras in PALABRAS_CLAVE.items():
        for palabra in palabras:
            if palabra in msg:
                return RESPUESTAS[categoria]
    return None

async def enviar_mensaje(telefono: str, texto: str):
    if not WA_TOKEN or not WA_PHONE_ID:
        print(f"[SIM] Para {telefono}: {texto}")
        return {"status": "simulado"}
    headers = {"Authorization": f"Bearer {WA_TOKEN}", "Content-Type": "application/json"}
    payload = {"messaging_product": "whatsapp", "to": telefono, "type": "text", "text": {"body": texto}}
    async with httpx.AsyncClient() as client:
        r = await client.post(WA_URL, json=payload, headers=headers)
        return r.json()
