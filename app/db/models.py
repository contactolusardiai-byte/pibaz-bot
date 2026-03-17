from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
import enum

# ── ENUMS ──────────────────────────────────────────

class CategoriaProducto(str, enum.Enum):
    clasica = "clasica"
    premium = "premium"
    retiro_inmediato = "retiro_inmediato"

class TipoPedido(str, enum.Enum):
    web = "web"
    presencial = "presencial"

class EstadoPedido(str, enum.Enum):
    confirmado = "confirmado"
    en_preparacion = "en_preparacion"
    listo = "listo"
    entregado = "entregado"
    cancelado = "cancelado"

class TipoEntrega(str, enum.Enum):
    delivery = "delivery"
    retiro = "retiro"

# ── TABLAS ─────────────────────────────────────────

class Producto(Base):
    __tablename__ = "productos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(200), nullable=False)
    descripcion = Column(Text, nullable=True)
    slug_shopify = Column(String(200), unique=True, nullable=True)
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    variantes = relationship("VarianteProducto", back_populates="producto")

class VarianteProducto(Base):
    __tablename__ = "variantes_producto"

    id = Column(Integer, primary_key=True, index=True)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False)
    porciones = Column(Integer, nullable=True)
    descripcion_tamano = Column(String(100), nullable=True)
    precio = Column(Float, nullable=False)
    categoria = Column(Enum(CategoriaProducto), nullable=False)
    dias_anticipacion = Column(Integer, default=1)
    sku_shopify = Column(String(200), unique=True, nullable=True)
    activo = Column(Boolean, default=True)

    producto = relationship("Producto", back_populates="variantes")
    items_pedido = relationship("ItemPedido", back_populates="variante")
    receta = relationship("RecetaItem", back_populates="variante")

class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(200), nullable=False)
    telefono = Column(String(20), nullable=True)
    email = Column(String(200), nullable=True)
    shopify_customer_id = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    pedidos = relationship("Pedido", back_populates="cliente")

class Pedido(Base):
    __tablename__ = "pedidos"

    id = Column(Integer, primary_key=True, index=True)
    numero_pedido = Column(String(50), unique=True, nullable=False)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    tipo_pedido = Column(Enum(TipoPedido), nullable=False)
    tipo_entrega = Column(Enum(TipoEntrega), nullable=False)
    estado = Column(Enum(EstadoPedido), default=EstadoPedido.confirmado)
    fecha_entrega = Column(DateTime(timezone=True), nullable=False)
    direccion_entrega = Column(Text, nullable=True)
    mensaje_torta = Column(String(200), nullable=True)
    shopify_order_id = Column(String(100), nullable=True)
    total = Column(Float, nullable=False)
    notas = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    cliente = relationship("Cliente", back_populates="pedidos")
    items = relationship("ItemPedido", back_populates="pedido")

class ItemPedido(Base):
    __tablename__ = "items_pedido"

    id = Column(Integer, primary_key=True, index=True)
    pedido_id = Column(Integer, ForeignKey("pedidos.id"), nullable=False)
    variante_id = Column(Integer, ForeignKey("variantes_producto.id"), nullable=False)
    cantidad = Column(Integer, default=1)
    precio_unitario = Column(Float, nullable=False)
    subtotal = Column(Float, nullable=False)

    pedido = relationship("Pedido", back_populates="items")
    variante = relationship("VarianteProducto", back_populates="items_pedido")

class Ingrediente(Base):
    __tablename__ = "ingredientes"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(200), nullable=False, unique=True)
    unidad = Column(String(50), nullable=False)
    stock_actual = Column(Float, default=0.0)
    stock_minimo = Column(Float, default=0.0)
    stock_critico = Column(Float, default=0.0)
    activo = Column(Boolean, default=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    recetas = relationship("RecetaItem", back_populates="ingrediente")

class RecetaItem(Base):
    __tablename__ = "recetas"

    id = Column(Integer, primary_key=True, index=True)
    variante_id = Column(Integer, ForeignKey("variantes_producto.id"), nullable=False)
    ingrediente_id = Column(Integer, ForeignKey("ingredientes.id"), nullable=False)
    cantidad = Column(Float, nullable=False)

    variante = relationship("VarianteProducto", back_populates="receta")
    ingrediente = relationship("Ingrediente", back_populates="recetas")

class SobranteVitrina(Base):
    __tablename__ = "sobrantes_vitrina"

    id = Column(Integer, primary_key=True, index=True)
    variante_id = Column(Integer, ForeignKey("variantes_producto.id"), nullable=False)
    cantidad_sobrante = Column(Integer, nullable=False)
    fecha = Column(DateTime(timezone=True), server_default=func.now())
    notas = Column(Text, nullable=True)

    variante = relationship("VarianteProducto")

class ListaAbastecimiento(Base):
    __tablename__ = "listas_abastecimiento"

    id = Column(Integer, primary_key=True, index=True)
    fecha_para = Column(DateTime(timezone=True), nullable=False)
    generada_en = Column(DateTime(timezone=True), server_default=func.now())
    enviada = Column(Boolean, default=False)
    contenido = Column(Text, nullable=False)
    ajustada_por = Column(String(200), nullable=True)
    confirmada = Column(Boolean, default=False)

