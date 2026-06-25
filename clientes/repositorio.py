from __future__ import annotations

from datetime import datetime

from .modelos import Cliente, EstadoCliente
from .config import get_supabase


def _a_cliente(fila: dict) -> Cliente:
    """Convierte una fila de Supabase (con joins) en un objeto Cliente."""
    address = fila.get("address") or {}
    city = address.get("city") or {}
    country = city.get("country") or {}

    fecha = fila.get("create_date")
    if isinstance(fecha, str):
        try:
            fecha_registro = datetime.fromisoformat(fecha.replace("Z", "+00:00"))
        except ValueError:
            fecha_registro = datetime.utcnow()
    else:
        fecha_registro = fecha or datetime.utcnow()

    activo = fila.get("active", 1)
    estado = EstadoCliente.ACTIVO if activo in (1, True, "1") else EstadoCliente.INACTIVO

    return Cliente(
        customer_id=fila["customer_id"],
        nombre=fila.get("first_name", ""),
        apellido=fila.get("last_name", ""),
        email=fila.get("email", ""),
        address=address.get("address", ""),
        city=city.get("city", ""),
        country=country.get("country", ""),
        codigo_postal=address.get("postal_code"),
        telefono=address.get("phone"),
        dni=fila.get("dni"),
        store_id=fila.get("store_id", 0),
        estado=estado,
        fecha_registro=fecha_registro,
    )

_SELECT = (
    "customer_id,store_id,first_name,last_name,email,active,create_date,dni,"
    "address(address,postal_code,phone,city(city,country(country)))"
)


class ClienteRepositorio:
    """Acceso a datos de la tabla customer (Pantalla 1 - Listado y Búsqueda)."""

    def __init__(self) -> None:
        self.db = get_supabase()

    def listar(self, nombre: str | None = None, store_id: int | None = None,
               estado: EstadoCliente | None = None,
               pagina: int = 1, por_pagina: int = 10) -> tuple[int, list[Cliente]]:
        """Lista clientes con filtros opcionales (nombre, tienda, estado) y paginación."""
        query = self.db.table("customer").select(_SELECT, count="exact")

        if nombre:
            query = query.or_(
                f"first_name.ilike.%{nombre}%,last_name.ilike.%{nombre}%"
            )

        if store_id is not None:
            query = query.eq("store_id", store_id)

        if estado is not None:
            query = query.eq("active", 1 if estado == EstadoCliente.ACTIVO else 0)

        desde = (pagina - 1) * por_pagina
        hasta = desde + por_pagina - 1
        resp = query.order("customer_id").range(desde, hasta).execute()

        total = resp.count or 0
        items = [_a_cliente(f) for f in (resp.data or [])]
        return total, items

    def obtener(self, customer_id: int) -> Cliente | None:
        """Obtiene un cliente puntual por su ID, o None si no existe."""
        resp = (
            self.db.table("customer")
            .select(_SELECT)
            .eq("customer_id", customer_id)
            .limit(1)
            .execute()
        )
        filas = resp.data or []
        return _a_cliente(filas[0]) if filas else None

    # Registro de cliente (POST)
    # customer, su API expone el servicio de crear clientes.

    def obtener_por_dni(self, dni: str) -> Cliente | None:
        """Obtiene un cliente por DNI, o None si no existe."""
        resp = (
            self.db.table("customer")
            .select(_SELECT)
            .eq("dni", dni)
            .limit(1)
            .execute()
        )
        filas = resp.data or []
        return _a_cliente(filas[0]) if filas else None

    def existe_email(self, email: str) -> bool:
        """True si ya hay un cliente con ese email."""
        resp = (
            self.db.table("customer").select("customer_id")
            .eq("email", email).limit(1).execute()
        )
        return bool(resp.data)

    def _obtener_o_crear_country(self, country: str) -> int:
        resp = self.db.table("country").select("country_id").eq("country", country).limit(1).execute()
        if resp.data:
            return resp.data[0]["country_id"]
        nuevo = self.db.table("country").insert({"country": country}).execute()
        return nuevo.data[0]["country_id"]

    def _obtener_o_crear_city(self, city: str, country_id: int) -> int:
        resp = (
            self.db.table("city").select("city_id")
            .eq("city", city).eq("country_id", country_id).limit(1).execute()
        )
        if resp.data:
            return resp.data[0]["city_id"]
        nuevo = self.db.table("city").insert({"city": city, "country_id": country_id}).execute()
        return nuevo.data[0]["city_id"]

    def _crear_address(self, address: str, city_id: int,
                       postal_code: str | None, phone: str | None) -> int:
        datos = {
            "address": address, "city_id": city_id,
            "postal_code": postal_code or "", "phone": phone or "",
            "district": "",   # Sakila exige district NOT NULL
        }
        nuevo = self.db.table("address").insert(datos).execute()
        return nuevo.data[0]["address_id"]

    def dar_de_baja(self, customer_id: int) -> None:
        """Marca un cliente como inactivo (active = 0)."""
        self.db.table("customer").update({"active": 0}).eq("customer_id", customer_id).execute()

    def editar(self, customer_id: int, datos: dict) -> None:
        """Actualiza los campos indicados en la tabla customer."""
        self.db.table("customer").update(datos).eq("customer_id", customer_id).execute()

    def crear(self, datos: dict) -> int:
        """Registra un cliente nuevo resolviendo la dirección en cascada
        (country -> city -> address -> customer). Devuelve el customer_id."""
        country_id = self._obtener_o_crear_country(datos["country"])
        city_id = self._obtener_o_crear_city(datos["city"], country_id)
        address_id = self._crear_address(
            datos["address"], city_id, datos.get("codigo_postal"), datos.get("telefono")
        )
        fila = {
            "store_id": datos["store_id"],
            "first_name": datos["nombre"],
            "last_name": datos["apellido"],
            "email": datos["email"],
            "address_id": address_id,
            "active": 1,
            "create_date": datetime.utcnow().isoformat(),
        }
        nuevo = self.db.table("customer").insert(fila).execute()
        return nuevo.data[0]["customer_id"]
