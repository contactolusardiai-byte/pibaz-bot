import logging
import asyncio
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.db.models import (
    VarianteProducto, Receta, Ingrediente,
    SobranteVitrina
)
from app.services.whatsapp_service import enviar_mensaje
import os

logger = logging.getLogger(__name__)
ADMIN_PHONE = os.getenv("ADMIN_PHONE", "")

class InventoryService:

    def __init__(self, db: Session):
        self.db = db

    def get_receta(self, variante_id: int) -> list:
        """Obtiene los ingredientes y cantidades de una receta."""
        receta = self.db.query(Receta).filter(
            Receta.variante_id == variante_id,
            Receta.activo == True
        ).all()
        return receta

    def descontar_ingrediente(self, ingrediente_id: int, cantidad: float) -> dict:
        """
        Descuenta cantidad de un ingrediente.
        Retorna estado del stock post-descuento.
        """
        ingrediente = self.db.query(Ingrediente).filter(
            Ingrediente.id == ingrediente_id
        ).with_for_update().first()

        if not ingrediente:
            logger.error(f"Ingrediente {ingrediente_id} no encontrado")
            return {"ok": False, "error": "ingrediente_no_encontrado"}

        stock_anterior = ingrediente.stock_actual
        ingrediente.stock_actual = max(0, ingrediente.stock_actual - cantidad)

        alerta = ingrediente.stock_actual <= ingrediente.stock_minimo
        bajo_cero = stock_anterior < cantidad

        logger.info(
            f"Ingrediente '{ingrediente.nombre}': "
            f"{stock_anterior} -> {ingrediente.stock_actual} "
            f"{'⚠️ BAJO MINIMO' if alerta else ''}"
        )

        return {
            "ok": True,
            "ingrediente": ingrediente.nombre,
            "stock_anterior": stock_anterior,
            "stock_actual": ingrediente.stock_actual,
            "alerta_minimo": alerta,
            "bajo_cero": bajo_cero,
            "unidad": ingrediente.unidad,
        }

    def procesar_venta(self, variante_id: int, cantidad: int = 1) -> dict:
        """
        Proceso transaccional completo:
        1. Obtiene receta de la variante vendida
        2. Descuenta ingredientes proporcionalmente
        3. Registra alertas de stock mínimo
        """
        alertas = []
        errores = []

        try:
            receta = self.get_receta(variante_id)

            if not receta:
                logger.warning(f"Variante {variante_id} sin receta configurada")
                return {"ok": True, "alertas": [], "sin_receta": True}

            for item in receta:
                cantidad_total = item.cantidad * cantidad
                resultado = self.descontar_ingrediente(
                    item.ingrediente_id,
                    cantidad_total
                )

                if not resultado["ok"]:
                    errores.append(resultado)
                    continue

                if resultado["alerta_minimo"]:
                    alertas.append(resultado)

            self.db.commit()
            logger.info(f"Venta procesada: variante {variante_id} x{cantidad}")

            return {
                "ok": True,
                "variante_id": variante_id,
                "alertas": alertas,
                "errores": errores,
            }

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error en procesar_venta: {e}")
            return {"ok": False, "error": str(e)}

    def procesar_items_pedido(self, items: list) -> dict:
        """
        Procesa todos los items de un pedido de Shopify.
        items = [{"sku": "torta-lucuma-15p", "quantity": 2}, ...]
        """
        from app.db.models import VarianteProducto
        alertas_totales = []
        resultados = []

        for item in items:
            sku = item.get("sku", "")
            qty = item.get("quantity", 1)

            if not sku:
                continue

            variante = self.db.query(VarianteProducto).filter(
                VarianteProducto.sku_shopify == sku,
                VarianteProducto.activo == True
            ).first()

            if not variante:
                logger.warning(f"SKU '{sku}' no encontrado en DB")
                continue

            resultado = self.procesar_venta(variante.id, qty)
            resultados.append(resultado)

            if resultado.get("alertas"):
                alertas_totales.extend(resultado["alertas"])

        return {
            "ok": True,
            "resultados": resultados,
            "alertas": alertas_totales,
        }


async def enviar_alertas_stock(alertas: list):
    """
    Envía WhatsApp al admin si hay ingredientes bajo mínimo.
    Se ejecuta en background para no bloquear el webhook.
    """
    if not alertas or not ADMIN_PHONE:
        return

    lineas = ["ALERTA STOCK MINIMO - Pibaz\n"]
    for a in alertas:
        lineas.append(
            f"- {a['ingrediente']}: {a['stock_actual']:.1f} {a['unidad']} "
            f"(minimo: stock bajo)"
        )
    lineas.append("\nRevisar abastecimiento urgente.")

    try:
        await enviar_mensaje(ADMIN_PHONE, "\n".join(lineas))
        logger.info(f"Alerta de stock enviada a {ADMIN_PHONE}")
    except Exception as e:
        logger.error(f"Error enviando alerta de stock: {e}")
