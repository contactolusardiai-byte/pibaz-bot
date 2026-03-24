import re
import os
import httpx
import logging
from enum import Enum
from app.services.whatsapp_service import respuesta_predefinida

logger = logging.getLogger(__name__)

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
BSALE_TOKEN = os.getenv("BSALE_TOKEN", "")

class AITier(Enum):
    STATIC = "static"       # $0.00 - respuestas predefinidas
    GROQ = "groq"           # $0.00 - Llama 3.3 gratis
    OPENAI = "openai"       # $0.001 - GPT-4o mini solo si es necesario
    FALLBACK = "fallback"   # $0.00 - respuesta fija de emergencia

# Keywords que indican pedido complejo → escalar a OpenAI
KEYWORDS_PEDIDO_COMPLEJO = [
    "quiero pedir", "necesito encargar", "cuantas personas",
    "para cuantos", "precio de", "vale la", "cuesta la",
    "torta para", "hacer un pedido", "encargar una",
    "cumpleanos", "matrimonio", "evento", "fiesta",
]

# Keywords de consulta simple → Groq es suficiente
KEYWORDS_CONSULTA_SIMPLE = [
    "ingrediente", "contiene", "lleva", "trae", "viene con",
    "es rica", "es buena", "recomiendan", "cual es mejor",
    "diferencia", "opciones", "variedades",
]

def clasificar_mensaje(mensaje: str) -> AITier:
    """
    Clasifica el mensaje en 4 niveles de costo:
    STATIC → GROQ → OPENAI → FALLBACK
    """
    msg = mensaje.lower().strip()

    # Capa 1: Respuesta estática (regex/keywords) → $0
    if respuesta_predefinida(mensaje):
        return AITier.STATIC

    # Capa 2: Pedido complejo → GPT-4o mini
    for kw in KEYWORDS_PEDIDO_COMPLEJO:
        if kw in msg:
            logger.info(f"Escalando a OpenAI por keyword: '{kw}'")
            return AITier.OPENAI

    # Capa 3: Consulta simple sobre productos → Groq gratis
    for kw in KEYWORDS_CONSULTA_SIMPLE:
        if kw in msg:
            return AITier.GROQ

    # Default: Groq para todo lo demás
    return AITier.GROQ


class AIRouter:

    CONTEXTO_BASE = """Eres el asistente virtual de Pibaz, pasteleria en El Bosque, Santiago.
Horario: todos los dias 10:00-20:45. Tel: +56998116140.
Delivery SOLO tortas a todas las comunas. Pagos: transferencia, debito, credito, efectivo.
Clasicas: 1 dia anticipacion. Premium: 5 dias. Retiro desde 14:00 si son mas de 15 porciones.
NO tematicas, NO heladas, NO sin azucar/lactosa/gluten.
Para comprar: pibaz.cl o presencial. WhatsApp es SOLO informativo.
Mensajes cortos, sin markdown, max 3 lineas."""

    async def get_catalogo(self) -> str:
        try:
            async with httpx.AsyncClient(timeout=4) as c:
                r = await c.get(
                    "https://api.bsale.cl/v1/products.json?limit=74",
                    headers={"access_token": BSALE_TOKEN}
                )
                items = r.json().get("items", [])
                return ", ".join([i["name"] for i in items[:35]])
        except Exception:
            return "Lucuma Manjar, Tres Leches, Selva Negra, Mil Hojas, Cheese Cake, Pompadour, Catalina"

    async def responder_groq(self, mensaje: str, catalogo: str) -> str:
        sistema = f"{self.CONTEXTO_BASE}\n\nCATALOGO REAL: {catalogo}"
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": sistema},
                {"role": "user", "content": mensaje}
            ],
            "max_tokens": 180,
            "temperature": 0.3,
        }
        async with httpx.AsyncClient(timeout=8) as c:
            r = await c.post(
                "https://api.groq.com/openai/v1/chat/completions",
                json=payload, headers=headers
            )
            return r.json()["choices"][0]["message"]["content"]

    async def responder_openai(self, mensaje: str, catalogo: str) -> str:
        sistema = f"{self.CONTEXTO_BASE}\n\nCATALOGO REAL: {catalogo}\nEl cliente quiere hacer un pedido. Ayudalo a entender opciones pero siempre dirigir a pibaz.cl para comprar."
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": sistema},
                {"role": "user", "content": mensaje}
            ],
            "max_tokens": 250,
        }
        async with httpx.AsyncClient(timeout=12) as c:
            r = await c.post(
                "https://api.openai.com/v1/chat/completions",
                json=payload, headers=headers
            )
            return r.json()["choices"][0]["message"]["content"]

    async def procesar(self, mensaje: str) -> dict:
        """
        Punto de entrada principal.
        Retorna respuesta y tier usado (para analytics de costo).
        """
        tier = clasificar_mensaje(mensaje)

        # Capa 1: Estática → sin API
        if tier == AITier.STATIC:
            respuesta = respuesta_predefinida(mensaje)
            return {"respuesta": respuesta, "fuente": AITier.STATIC.value, "costo": 0.0}

        # Obtener catálogo solo si necesitamos IA
        catalogo = await self.get_catalogo()

        # Capa 2: Groq gratis
        if tier == AITier.GROQ:
            try:
                respuesta = await self.responder_groq(mensaje, catalogo)
                return {"respuesta": respuesta, "fuente": AITier.GROQ.value, "costo": 0.0}
            except Exception as e:
                logger.warning(f"Groq fallo, escalando a OpenAI: {e}")

        # Capa 3: OpenAI (pedido complejo o Groq falló)
        try:
            respuesta = await self.responder_openai(mensaje, catalogo)
            costo_estimado = len(mensaje.split()) * 0.000002
            return {"respuesta": respuesta, "fuente": AITier.OPENAI.value, "costo": costo_estimado}
        except Exception as e:
            logger.error(f"OpenAI fallo: {e}")

        # Capa 4: Fallback
        return {
            "respuesta": "Para mas informacion visita pibaz.cl o llamanos al +56998116140. Abrimos 10:00-20:45.",
            "fuente": AITier.FALLBACK.value,
            "costo": 0.0
        }


# Instancia global del router
ai_router = AIRouter()

async def procesar_mensaje(mensaje: str, historial: list = []) -> dict:
    """Wrapper para compatibilidad con el código existente."""
    return await ai_router.procesar(mensaje)
