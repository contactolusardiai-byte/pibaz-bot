import httpx
import os
from typing import Optional

BSALE_TOKEN = os.getenv("BSALE_TOKEN")
BSALE_URL = os.getenv("BSALE_URL", "https://api.bsale.cl/v1")
HEADERS = {"access_token": BSALE_TOKEN, "Content-Type": "application/json"}

async def get_productos(limit: int = 50, offset: int = 0):
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{BSALE_URL}/products.json?limit={limit}&offset={offset}", headers=HEADERS)
        return r.json()

async def get_ventas_hoy():
    from datetime import datetime
    hoy = int(datetime.now().replace(hour=0,minute=0,second=0).timestamp())
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{BSALE_URL}/documents.json?emissiondateinitialsearch={hoy}&limit=50", headers=HEADERS)
        return r.json()

async def get_stock():
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{BSALE_URL}/stocks.json?limit=50", headers=HEADERS)
        return r.json()

async def get_pedidos_pendientes():
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{BSALE_URL}/documents.json?documenttypeid=9&limit=20", headers=HEADERS)
        return r.json()
