from __future__ import annotations

import re

from .excepciones import ClienteNoEncontrado, EmailDuplicado, DatosInvalidos
from .modelos import Cliente, EstadoCliente, DatosNuevoCliente
from .repositorio import ClienteRepositorio

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_TIENDAS_VALIDAS = {1, 2}


class ClienteServicio:
    """Lógica de negocio de la Pantalla 1 (Listado y Búsqueda)."""

    def __init__(self, repositorio: ClienteRepositorio | None = None) -> None:
        self.repo = repositorio or ClienteRepositorio()

    def listar_clientes(self, nombre: str | None = None, store_id: int | None = None,
                        estado: EstadoCliente | None = None,
                        pagina: int = 1, por_pagina: int = 10) -> dict:
        """Lista/busca clientes con filtros y paginación. Devuelve un dict con
        el total, la página actual, el total de páginas y los items."""
        if pagina < 1:
            pagina = 1
        if por_pagina < 1:
            por_pagina = 10

        total, items = self.repo.listar(nombre, store_id, estado, pagina, por_pagina)
        total_paginas = (total + por_pagina - 1) // por_pagina if total else 0

        return {
            "total": total,
            "pagina": pagina,
            "por_pagina": por_pagina,
            "total_paginas": total_paginas,
            "items": items,
        }

    def obtener_cliente(self, customer_id: int) -> Cliente:
        """Devuelve un cliente por id. Lanza ClienteNoEncontrado si no existe."""
        cliente = self.repo.obtener(customer_id)
        if not cliente:
            raise ClienteNoEncontrado(customer_id)
        return cliente

    def registrar_cliente(self, datos: DatosNuevoCliente) -> Cliente:
        """Registra un cliente nuevo: valida los datos, verifica que el email no
        esté repetido, lo crea (con su dirección) y devuelve el Cliente creado."""
        # Validaciones
        for campo, valor in [("nombre", datos.nombre), ("apellido", datos.apellido),
                             ("address", datos.address), ("city", datos.city),
                             ("country", datos.country)]:
            if not valor or not str(valor).strip():
                raise DatosInvalidos(f"El campo '{campo}' es obligatorio.")
        if not _EMAIL_RE.match(datos.email):
            raise DatosInvalidos(f"El email '{datos.email}' no tiene un formato válido.")
        if datos.store_id not in _TIENDAS_VALIDAS:
            raise DatosInvalidos(f"store_id={datos.store_id} no es válido. Tiendas: {sorted(_TIENDAS_VALIDAS)}.")

        if self.repo.existe_email(datos.email):
            raise EmailDuplicado(datos.email)

        nuevo_id = self.repo.crear({
            "nombre": datos.nombre.strip(),
            "apellido": datos.apellido.strip(),
            "email": datos.email.strip().lower(),
            "address": datos.address.strip(),
            "city": datos.city.strip(),
            "country": datos.country.strip(),
            "codigo_postal": datos.codigo_postal,
            "telefono": datos.telefono,
            "store_id": datos.store_id,
        })
        return self.obtener_cliente(nuevo_id)
