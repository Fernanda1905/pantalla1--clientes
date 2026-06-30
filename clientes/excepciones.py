
class ErrorClientes(Exception):
    """Error base del módulo de clientes."""


class ClienteNoEncontrado(ErrorClientes):
    """Se lanza cuando no existe un cliente con el ID buscado."""

    def __init__(self, customer_id: int) -> None:
        super().__init__(f"No existe el cliente con id {customer_id}.")
        self.customer_id = customer_id


class EmailDuplicado(ErrorClientes):
    """Se lanza cuando ya existe un cliente con el mismo email."""

    def __init__(self, email: str) -> None:
        super().__init__(f"Ya existe un cliente registrado con el email '{email}'.")
        self.email = email


class DniDuplicado(ErrorClientes):
    """Se lanza cuando ya existe un cliente con el mismo DNI."""

    def __init__(self, dni: str) -> None:
        super().__init__(f"Ya existe un cliente registrado con el DNI '{dni}'.")
        self.dni = dni


class DatosInvalidos(ErrorClientes):
    """Se lanza cuando los datos de un cliente no pasan las validaciones."""
