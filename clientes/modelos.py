from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


# Valores controlados

class EstadoCliente(str, Enum):
    ACTIVO = "activo"
    INACTIVO = "inactivo"

# Entidad principal: Cliente

@dataclass
class Cliente:
    customer_id: int
    nombre: str
    apellido: str
    email: str
    address: str
    city: str
    country: str
    codigo_postal: str | None
    telefono: str | None
    dni: str | None
    store_id: int
    estado: EstadoCliente
    fecha_registro: datetime

    @property
    def nombre_completo(self) -> str:
        return f"{self.nombre} {self.apellido}"

    def to_dict(self) -> dict:
        return {
            "customer_id": self.customer_id,
            "nombre": self.nombre,
            "apellido": self.apellido,
            "email": self.email,
            "address": self.address,
            "city": self.city,
            "country": self.country,
            "codigo_postal": self.codigo_postal,
            "telefono": self.telefono,
            "dni": self.dni,
            "store_id": self.store_id,
            "estado": self.estado.value,
            "fecha_registro": self.fecha_registro.strftime("%d/%m/%Y"),
        }

# Datos para registrar un cliente nuevo (entrada del POST)

@dataclass
class DatosNuevoCliente:
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
    dni: str | None = None


# Datos para editar un cliente (entrada del PUT) — todos opcionales

@dataclass
class DatosEdicionCliente:
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
