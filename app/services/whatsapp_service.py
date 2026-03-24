import httpx, os

WA_TOKEN = (os.getenv("WHATSAPP_TOKEN") or "").strip()
WA_PHONE_ID = (os.getenv("WHATSAPP_PHONE_NUMBER_ID") or "").strip()
WA_URL = f"https://graph.facebook.com/v18.0/{WA_PHONE_ID}/messages"

RESPUESTAS = {
    "horario": "Abrimos todos los dias de 10:00 a 20:45 hrs.",
    "ubicacion": "Estamos en Gran Avenida Jose Miguel Carrera 10375, El Bosque, Santiago.",
    "precio": "Puedes ver precios y disponibilidad en pibaz.cl",
    "anticipacion": "Tortas clasicas: 1 dia de anticipacion. Tortas premium: 5 dias. Puedes pedirlas en pibaz.cl o en el local.",
    "delivery": "Si! Hacemos envios a todas las comunas de Santiago. Delivery solo de tortas, reserva antes de las 15:00 para recibir el mismo dia. Visita pibaz.cl o acercate al local.",
    "pago": "Aceptamos transferencia, debito, credito y efectivo.",
    "sin_azucar": "Por el momento no contamos con productos sin azucar, sin lactosa ni sin gluten.",
    "catalogo": "Todas nuestras tortas estan en pibaz.cl. Tambien puedes visitarnos en el local en El Bosque. Abrimos todos los dias de 10:00 a 20:45 hrs.",
    "chocolate": "Tenemos varias tortas de chocolate: Selva Negra, Panqueque Chocolate Manjar, Panqueque Chocolate Guinda, Trilogia de Chocolates y Torta Oreo. Encuentralas en pibaz.cl o visitanos en el local.",
    "lucuma": "Si! Tenemos la Torta Lucuma Manjar en distintas porciones. Encuentrala en pibaz.cl o visitanos en el local en El Bosque.",
    "comprar_hoy": "Para tortas disponibles hoy visita pibaz.cl seccion Retiro Inmediato o acercate al local en El Bosque. Abrimos de 10:00 a 20:45 hrs.",
    "comprar_anticipado": "Puedes hacer tu pedido en pibaz.cl o en el local. Tortas clasicas: 1 dia de anticipacion. Tortas premium: 5 dias.",
    "carta": "Nuestra carta de cafeteria, pizzas y sandwiches la encuentras en cartapibaz.cl. Para tortas visita pibaz.cl",
    "porciones": "Nuestras tortas parten desde 12 personas. Puedes ver todas las opciones y tamanios en pibaz.cl",
}

PALABRAS_CLAVE = {
    "horario": ["horario", "hora", "abren", "cierran", "atienden", "abiertos", "hasta que hora"],
    "ubicacion": ["donde", "ubicacion", "direccion", "llegar", "queda", "como llegar"],
    "precio": ["precio", "cuanto", "cuesta", "valor", "tarifa", "cobran", "vale"],
    "anticipacion": ["anticipacion", "plazo", "con cuanto", "cuanto tiempo"],
    "delivery": ["delivery", "despacho", "envio", "llevan", "domicilio", "despachan", "maipu", "santiago", "comunas", "envian", "llegan"],
    "pago": ["pago", "pagar", "transferencia", "tarjeta", "efectivo", "webpay", "mercadopago"],
    "sin_azucar": ["sin azucar", "diabetico", "diabetes", "light", "sin gluten", "celiaco", "vegano", "sin lactosa", "lactosa", "intolerante"],
    "catalogo": ["que tortas", "que tienen", "catalogo", "tortas tienen", "que pasteles", "que ofrecen", "que venden", "que hay"],
    "chocolate": ["chocolate", "choco"],
    "lucuma": ["lucuma"],
    "comprar_hoy": ["retiro inmediato", "disponible ahora", "para hoy", "mismo dia", "ahora mismo"],
    "comprar_anticipado": ["para manana", "para el sabado", "para el domingo", "para la proxima", "encargar"],
    "carta": ["carta", "menu", "pizza", "sandwich", "cafe", "bebida", "almuerzo", "comida"],
    "porciones": ["porciones", "personas", "cuantas", "tamanio", "tamano", "chica", "grande", "mas chica", "mas grande"],
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
