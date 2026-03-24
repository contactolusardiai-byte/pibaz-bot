from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import PlainTextResponse
from app.services.ai_service import procesar_mensaje
from app.services.whatsapp_service import enviar_mensaje
import os, json

router = APIRouter()
WA_VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "lusardiai_verify_2026")

@router.get("/webhook/whatsapp")
async def verificar_webhook(request: Request):
    params = dict(request.query_params)
    if params.get("hub.verify_token") == WA_VERIFY_TOKEN:
        return PlainTextResponse(params.get("hub.challenge", "0"))
    raise HTTPException(status_code=403, detail="Token invalido")

@router.post("/webhook/whatsapp")
async def recibir_mensaje(request: Request):
    data = await request.json()
    try:
        entry = data["entry"][0]["changes"][0]["value"]
        if "messages" not in entry:
            return {"status": "ok"}
        mensaje_data = entry["messages"][0]
        telefono = mensaje_data["from"]
        tipo = mensaje_data.get("type", "")
        if tipo != "text":
            await enviar_mensaje(telefono, "Hola! Por ahora solo respondo mensajes de texto. Como puedo ayudarte?")
            return {"status": "ok"}
        texto = mensaje_data["text"]["body"]
        print(f"Mensaje de {telefono}: {texto}")
        resultado = await procesar_mensaje(texto)
        respuesta = resultado["respuesta"]
        fuente = resultado["fuente"]
        print(f"Respuesta ({fuente}): {respuesta}")
        await enviar_mensaje(telefono, respuesta)
        return {"status": "ok"}
    except Exception as e:
        print(f"Error: {e}")
        return {"status": "error"}

@router.get("/webhook/test")
async def test_bot(mensaje: str = "Hola que tortas tienen?"):
    resultado = await procesar_mensaje(mensaje)
    return resultado
