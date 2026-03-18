
from fastapi import APIRouter
from app.services.bsale_service import get_productos, get_ventas_hoy, get_stock

router = APIRouter()

@router.get("/bsale/productos")
async def productos():
    data = await get_productos(limit=10)
    return {"total": data.get("count"), "productos": [i["name"] for i in data.get("items", [])]}

@router.get("/bsale/ventas-hoy")
async def ventas_hoy():
    data = await get_ventas_hoy()
    return {"total_ventas": data.get("count"), "ventas": data.get("items", [])}

@router.get("/bsale/stock")
async def stock():
    data = await get_stock()
    return data
