from fastapi import FastAPI
from app.db.database import engine
from app.db import models

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Pibaz Bot - Lusardi AI",
    description="Sistema de automatizacion para Pibaz",
    version="1.0.0"
)

from app.api.bsale_router import router as bsale_router
from app.api.wa_webhook import router as wa_router

app.include_router(bsale_router, prefix="/api")
app.include_router(wa_router, prefix="/api")

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
    return {"status": "ok", "tablas_creadas": tablas, "total": len(tablas)}
