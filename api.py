"""
API REST de la Pantalla 1 - Listado y Búsqueda de Clientes.

Servicios que expone:
  GET   /clientes          -> lista / busca clientes (filtros + paginación)
  GET   /clientes/{id}     -> obtiene un cliente por su ID
  POST  /clientes          -> registra un cliente nuevo

Cómo levantar la API:
    uvicorn api:app --reload --port 8001

Documentación interactiva (para probar en el navegador):
    http://localhost:8001/docs

Interfaz gráfica:
    http://localhost:8001/
"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from pathlib import Path

from clientes.servicio import ClienteServicio
from clientes.modelos import EstadoCliente, DatosNuevoCliente, DatosEdicionCliente
from clientes.excepciones import ClienteNoEncontrado, EmailDuplicado, DniDuplicado, DatosInvalidos

app = FastAPI(
    title="API Pantalla 1 - Clientes (Andrea)",
    description="Listado, búsqueda y registro de clientes. Sistema distribuido Sakila.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
)

svc = ClienteServicio()


class ClienteNuevoIn(BaseModel):
    nombre: str
    apellido: str
    email: str
    address: str
    city: str
    country: str
    store_id: int = 1
    codigo_postal: str | None = None
    telefono: str | None = None
    dni: str | None = None


class ClienteEdicionIn(BaseModel):
    nombre: str | None = None
    apellido: str | None = None
    email: str | None = None
    address: str | None = None
    city: str | None = None
    country: str | None = None
    store_id: int | None = None
    codigo_postal: str | None = None
    telefono: str | None = None
    dni: str | None = None
    estado: str | None = None


@app.get("/", response_class=HTMLResponse)
def interfaz():
    """Sirve la página web (la interfaz gráfica) desde el propio FastAPI."""
    ruta = Path(__file__).parent / "index.html"
    return HTMLResponse(ruta.read_text(encoding="utf-8"))


@app.get("/api")
def info_api():
    """Información de la API (qué servicios expone)."""
    return {
        "modulo": "Pantalla 1 - Listado y Búsqueda de Clientes",
        "autor": "Andrea",
        "servicios": ["GET /clientes", "GET /clientes/{id}", "POST /clientes"],
        "docs": "Abre /docs para probar la API",
    }


@app.get("/clientes")
def listar_clientes(
    nombre: str | None = Query(None, description="Buscar por nombre o apellido"),
    tienda: int | None = Query(None, description="Filtrar por tienda (1 o 2)"),
    estado: str | None = Query(None, description="activo o inactivo"),
    pagina: int = Query(1, ge=1),
    por_pagina: int = Query(10, ge=1, le=100),
):
    estado_enum = None
    if estado == "activo":
        estado_enum = EstadoCliente.ACTIVO
    elif estado == "inactivo":
        estado_enum = EstadoCliente.INACTIVO

    resultado = svc.listar_clientes(
        nombre=nombre, store_id=tienda, estado=estado_enum,
        pagina=pagina, por_pagina=por_pagina,
    )
    resultado["items"] = [c.to_dict() for c in resultado["items"]]
    return resultado


@app.get("/clientes/dni/{dni}")
def obtener_por_dni(dni: str):
    try:
        return svc.obtener_cliente_por_dni(dni).to_dict()
    except ClienteNoEncontrado:
        raise HTTPException(status_code=404, detail=f"Cliente con DNI {dni} no encontrado")


@app.get("/clientes/{customer_id}")
def obtener_cliente(customer_id: int):
    try:
        return svc.obtener_cliente(customer_id).to_dict()
    except ClienteNoEncontrado:
        raise HTTPException(status_code=404, detail=f"Cliente {customer_id} no encontrado")


@app.put("/clientes/{customer_id}")
def editar_cliente(customer_id: int, datos: ClienteEdicionIn):
    try:
        actualizado = svc.editar_cliente(customer_id, DatosEdicionCliente(
            nombre=datos.nombre, apellido=datos.apellido, email=datos.email,
            address=datos.address, city=datos.city, country=datos.country,
            store_id=datos.store_id,
            codigo_postal=datos.codigo_postal, telefono=datos.telefono,
            dni=datos.dni, estado=datos.estado,
        ))
        return actualizado.to_dict()
    except ClienteNoEncontrado:
        raise HTTPException(status_code=404, detail=f"Cliente {customer_id} no encontrado")
    except DniDuplicado as e:
        raise HTTPException(status_code=409, detail=str(e))
    except DatosInvalidos as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/clientes/{customer_id}")
def dar_de_baja(customer_id: int):
    try:
        svc.dar_de_baja(customer_id)
        return {"mensaje": f"Cliente {customer_id} dado de baja correctamente"}
    except ClienteNoEncontrado:
        raise HTTPException(status_code=404, detail=f"Cliente {customer_id} no encontrado")


@app.post("/clientes", status_code=201)
def registrar_cliente(datos: ClienteNuevoIn):
    try:
        nuevo = svc.registrar_cliente(DatosNuevoCliente(
            nombre=datos.nombre, apellido=datos.apellido, email=datos.email,
            address=datos.address, city=datos.city, country=datos.country,
            store_id=datos.store_id,
            codigo_postal=datos.codigo_postal, telefono=datos.telefono,
            dni=datos.dni,
        ))
        return nuevo.to_dict()
    except EmailDuplicado as e:
        raise HTTPException(status_code=409, detail=str(e))
    except DniDuplicado as e:
        raise HTTPException(status_code=409, detail=str(e))
    except DatosInvalidos as e:
        raise HTTPException(status_code=400, detail=str(e))
