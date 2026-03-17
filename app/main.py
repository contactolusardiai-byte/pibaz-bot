from fastapi import FastAPI
from app.db.database import engine
from app.db import models

# Crear todas las tablas al arrancar
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Pibaz Bot - Lusardi AI",
    description="Sistema de automatización para Pibaz",
    version="1.0.0"
)

@app.get("/")
def root():
    return {"status": "ok", "empresa": "Lusardi AI", "cliente": "Pibaz"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/tablas")
def verificar_tablas():
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tablas = inspector.get_table_names()
    return {
        "status": "ok",
        "tablas_creadas": tablas,
        "total": len(tablas)
    }
