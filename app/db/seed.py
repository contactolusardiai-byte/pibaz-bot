from sqlalchemy.orm import Session
from app.db.database import SessionLocal, engine
from app.db.models import Producto, VarianteProducto, CategoriaProducto, Base

def seed_productos():
    db = SessionLocal()
    
    try:
        # Verificar si ya hay datos
        if db.query(Producto).count() > 0:
            print("Ya existen productos en la base de datos")
            return

        print("Cargando catálogo de Pibaz...")

        catalogo = [
            # ── BIZCOCHOS ──
            {
                "nombre": "Lúcuma Manjar",
                "categoria": "bizcochos",
                "slug": "torta-lucuma-manjar-nuez",
                "variantes": [
                    {"porciones": 15, "precio": 33000, "cat": CategoriaProducto.clasica, "dias": 1},
                    {"porciones": 20, "precio": 37000, "cat": CategoriaProducto.clasica, "dias": 1},
                    {"porciones": 30, "precio": 42000, "cat": CategoriaProducto.clasica, "dias": 1},
                    {"porciones": 40, "precio": 55000, "cat": CategoriaProducto.premium, "dias": 5},
                ]
            },
            {
                "nombre": "Tres Leches",
                "categoria": "bizcochos",
                "slug": "torta-tres-leches",
                "variantes": [
                    {"porciones": 15, "precio": 33000, "cat": CategoriaProducto.clasica, "dias": 1},
                    {"porciones": 20, "precio": 37000, "cat": CategoriaProducto.premium, "dias": 5},
                    {"porciones": 30, "precio": 42000, "cat": CategoriaProducto.premium, "dias": 5},
                    {"porciones": 40, "precio": 55000, "cat": CategoriaProducto.premium, "dias": 5},
                ]
            },
            {
                "nombre": "Catalina",
                "categoria": "bizcochos",
                "slug": "torta-catalina",
                "variantes": [
                    {"porciones": 15, "precio": 33000, "cat": CategoriaProducto.clasica, "dias": 1},
                    {"porciones": 20, "precio": 37000, "cat": CategoriaProducto.premium, "dias": 5},
                    {"porciones": 30, "precio": 42000, "cat": CategoriaProducto.premium, "dias": 5},
                    {"porciones": 40, "precio": 55000, "cat": CategoriaProducto.premium, "dias": 5},
                ]
            },
            {
                "nombre": "Selva Negra",
                "categoria": "bizcochos",
                "slug": "torta-selva-negra",
                "variantes": [
                    {"porciones": 15, "precio": 35000, "cat": CategoriaProducto.clasica, "dias": 1},
                    {"porciones": 20, "precio": 40000, "cat": CategoriaProducto.clasica, "dias": 1},
                    {"porciones": 30, "precio": 49000, "cat": CategoriaProducto.clasica, "dias": 1},
                    {"porciones": 40, "precio": 63000, "cat": CategoriaProducto.premium, "dias": 5},
                ]
            },
            {
                "nombre": "Torta Moka",
                "categoria": "bizcochos",
                "slug": "torta-moka",
                "variantes": [
                    {"porciones": 15, "precio": 35000, "cat": CategoriaProducto.premium, "dias": 5},
                    {"porciones": 30, "precio": 50000, "cat": CategoriaProducto.premium, "dias": 5},
                ]
            },
            {
                "nombre": "Torta Oreo",
                "categoria": "bizcochos",
                "slug": "torta-oreo-pibaz",
                "variantes": [
                    {"porciones": 15, "precio": 40000, "cat": CategoriaProducto.premium, "dias": 5},
                ]
            },
            # ── MIL HOJAS ──
            {
                "nombre": "Mil Hojas Manjar",
                "categoria": "mil_hojas",
                "slug": "torta-mil-hojas-manjar",
                "variantes": [
                    {"porciones": 15, "precio": 35000, "cat": CategoriaProducto.clasica, "dias": 1},
                    {"porciones": 20, "precio": 42000, "cat": CategoriaProducto.clasica, "dias": 1},
                    {"porciones": 25, "precio": 55000, "cat": CategoriaProducto.clasica, "dias": 1},
                ]
            },
            {
                "nombre": "Mil Hojas Frambuesa",
                "categoria": "mil_hojas",
                "slug": "torta-mil-hojas-frambuesa",
                "variantes": [
                    {"porciones": 15, "precio": 35000, "cat": CategoriaProducto.clasica, "dias": 1},
                    {"porciones": 20, "precio": 42000, "cat": CategoriaProducto.clasica, "dias": 1},
                    {"porciones": 25, "precio": 55000, "cat": CategoriaProducto.clasica, "dias": 1},
                ]
            },
            {
                "nombre": "Mil Hojas Holandesa",
                "categoria": "mil_hojas",
                "slug": "torta-pibaz-holandesa",
                "variantes": [
                    {"porciones": 15, "precio": 35000, "cat": CategoriaProducto.clasica, "dias": 1},
                    {"porciones": 20, "precio": 42000, "cat": CategoriaProducto.clasica, "dias": 1},
                    {"porciones": 25, "precio": 55000, "cat": CategoriaProducto.clasica, "dias": 1},
                ]
            },
            # ── FRUTALES ──
            {
                "nombre": "Torta Piña Crema Manjar",
                "categoria": "frutales",
                "slug": "torta-pina-crema-y-manjar",
                "variantes": [
                    {"porciones": 15, "precio": 38000, "cat": CategoriaProducto.premium, "dias": 5},
                    {"porciones": 20, "precio": 45000, "cat": CategoriaProducto.premium, "dias": 5},
                    {"porciones": 30, "precio": 55000, "cat": CategoriaProducto.premium, "dias": 5},
                    {"porciones": 40, "precio": 65000, "cat": CategoriaProducto.premium, "dias": 5},
                ]
            },
            {
                "nombre": "Torta Durazno Crema Manjar",
                "categoria": "frutales",
                "slug": "torta-durazno-crema-y-manjar",
                "variantes": [
                    {"porciones": 15, "precio": 38000, "cat": CategoriaProducto.premium, "dias": 5},
                    {"porciones": 20, "precio": 45000, "cat": CategoriaProducto.premium, "dias": 5},
                    {"porciones": 30, "precio": 55000, "cat": CategoriaProducto.premium, "dias": 5},
                    {"porciones": 40, "precio": 65000, "cat": CategoriaProducto.premium, "dias": 5},
                ]
            },
            # ── HOJARASCAS ──
            {
                "nombre": "Pompadour",
                "categoria": "hojarascas",
                "slug": "torta-pompadour-pibaz",
                "variantes": [
                    {"porciones": 15, "precio": 35000, "cat": CategoriaProducto.clasica, "dias": 1},
                    {"porciones": 30, "precio": 48000, "cat": CategoriaProducto.clasica, "dias": 1},
                ]
            },
            {
                "nombre": "Torta Amor",
                "categoria": "hojarascas",
                "slug": "torta-amor",
                "variantes": [
                    {"porciones": 15, "precio": 42000, "cat": CategoriaProducto.premium, "dias": 5},
                    {"porciones": 30, "precio": 60000, "cat": CategoriaProducto.premium, "dias": 5},
                ]
            },
            # ── CHOCOLATE ──
            {
                "nombre": "Trilogía de Chocolates",
                "categoria": "chocolate",
                "slug": "trilogia-de-chocolates",
                "variantes": [
                    {"porciones": 20, "precio": 55000, "cat": CategoriaProducto.clasica, "dias": 1},
                ]
            },
            # ── PANQUEQUES ──
            {
                "nombre": "Panqueque Chocolate Manjar",
                "categoria": "panqueques",
                "slug": "torta-panqueque-chocolate-manjar",
                "variantes": [
                    {"porciones": 20, "precio": 45000, "cat": CategoriaProducto.clasica, "dias": 1},
                    {"porciones": 30, "precio": 56000, "cat": CategoriaProducto.clasica, "dias": 1},
                ]
            },
            {
                "nombre": "Panqueque Chocolate Guinda",
                "categoria": "panqueques",
                "slug": "torta-panqueque-chocolate-guinda",
                "variantes": [
                    {"porciones": 20, "precio": 45000, "cat": CategoriaProducto.clasica, "dias": 1},
                    {"porciones": 30, "precio": 56000, "cat": CategoriaProducto.clasica, "dias": 1},
                ]
            },
            {
                "nombre": "Panqueque Naranja",
                "categoria": "panqueques",
                "slug": "torta-panqueque-naranja",
                "variantes": [
                    {"porciones": 20, "precio": 40000, "cat": CategoriaProducto.premium, "dias": 5},
                    {"porciones": 30, "precio": 48000, "cat": CategoriaProducto.premium, "dias": 5},
                    {"porciones": 40, "precio": 60000, "cat": CategoriaProducto.premium, "dias": 5},
                ]
            },
            # ── ESPECIALES ──
            {
                "nombre": "Cheese Cake Variedades",
                "categoria": "especiales",
                "slug": "cheese-cake-frambuesa",
                "variantes": [
                    {"porciones": 12, "precio": 28000, "cat": CategoriaProducto.clasica, "dias": 1},
                ]
            },
            {
                "nombre": "Torta Yogurt Frambuesa",
                "categoria": "especiales",
                "slug": "torta-yogurt-frambuesa",
                "variantes": [
                    {"porciones": 12, "precio": 25000, "cat": CategoriaProducto.clasica, "dias": 1},
                ]
            },
            {
                "nombre": "Pie de Limón",
                "categoria": "especiales",
                "slug": "pie-de-limon-pibaz",
                "variantes": [
                    {"porciones": 12, "precio": 20000, "cat": CategoriaProducto.clasica, "dias": 1},
                ]
            },
            {
                "nombre": "Tarta Plátano Manjar",
                "categoria": "especiales",
                "slug": "tartaleta-de-platano-y-manjar",
                "variantes": [
                    {"porciones": 12, "precio": 20000, "cat": CategoriaProducto.clasica, "dias": 1},
                ]
            },
        ]

        total_productos = 0
        total_variantes = 0

        for item in catalogo:
            producto = Producto(
                nombre=item["nombre"],
                descripcion=item["categoria"],
                slug_shopify=item["slug"],
                activo=True
            )
            db.add(producto)
            db.flush()

            for v in item["variantes"]:
                variante = VarianteProducto(
                    producto_id=producto.id,
                    porciones=v["porciones"],
                    descripcion_tamano=f"{v['porciones']} personas",
                    precio=v["precio"],
                    categoria=v["cat"],
                    dias_anticipacion=v["dias"],
                    sku_shopify=f"{item['slug']}-{v['porciones']}p",
                    activo=True
                )
                db.add(variante)
                total_variantes += 1

            total_productos += 1

        db.commit()
        print(f"✅ Cargados {total_productos} productos")
        print(f"✅ Cargadas {total_variantes} variantes")
        print("✅ Catálogo Pibaz listo!")

    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_productos()
