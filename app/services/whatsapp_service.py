import httpx, os

WA_TOKEN = (os.getenv("WHATSAPP_TOKEN") or "").strip()
WA_PHONE_ID = (os.getenv("WHATSAPP_PHONE_NUMBER_ID") or "").strip()
WA_URL = f"https://graph.facebook.com/v18.0/{WA_PHONE_ID}/messages"


RESPUESTAS = {
    "horario": "Abrimos todos los días de 10:00 a 20:45 hrs. 😊 Te esperamos!",
    "ubicacion": "Estamos en Gran Avenida José Miguel Carrera 10375, El Bosque, Santiago! 📍",
    "precio": "Los precios y fotos de todas nuestras tortas están en pibaz.cl 🍰 Ahí puedes ver todo el catálogo!",
    "anticipacion": "Las tortas clásicas las pedimos con 1 día de anticipación y las premium con 5 días. Puedes hacer tu pedido en pibaz.cl o visitarnos en el local! 😊",
    "delivery": "Sí! Hacemos delivery a todas las comunas de Santiago 🚚 Solo de tortas, y si reservas antes de las 15:00 te llega el mismo día! Visita pibaz.cl para pedir.",
    "pago": "Aceptamos transferencia, débito, crédito y efectivo. Sin problemas! 😊",
    "sin_azucar": "Pucha, por ahora no tenemos opciones sin azúcar, sin lactosa ni sin gluten 😔 Pero nuestras tortas clásicas son espectaculares! La Tres Leches y la Lucuma Manjar son las favoritas. Míralas en pibaz.cl 🍰",
    "catalogo": "Todas nuestras tortas están en pibaz.cl 🍰 Para la carta del local (pizzas, sandwiches, café) visita cartapibaz.cl. También puedes venir a vernos al local en El Bosque!",
    "chocolate": "Tenemos varias tortas de chocolate que están increíbles 🍫 Selva Negra, Panqueque Chocolate Manjar, Panqueque Chocolate Guinda, Trilogía de Chocolates y Torta Oreo. Míralas en pibaz.cl!",
    "lucuma": "Sí! Tenemos la Torta Lúcuma Manjar que es un clásico favorito 😍 Encuéntrala en pibaz.cl o pasa a verla al local en El Bosque!",
    "comprar_hoy": "Para ver qué tortas tenemos disponibles hoy entra a pibaz.cl sección Retiro Inmediato 🍰 O pasa directamente al local, abrimos hasta las 20:45!",
    "comprar_anticipado": "Perfecto! Para hacer un pedido con anticipación entra a pibaz.cl o pasa al local 😊 Clásicas: 1 día de anticipación. Premium: 5 días.",
    "carta": "La carta del local con pizzas, sandwiches y café está en cartapibaz.cl 😊 Y para tortas visita pibaz.cl!",
    "porciones": "Nuestras tortas parten desde 12 personas 🎂 Puedes ver todos los tamaños disponibles en pibaz.cl!",
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
