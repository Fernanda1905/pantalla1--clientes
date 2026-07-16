
class ErrorClientes(Exception):
    pass


class ClienteNoEncontrado(ErrorClientes):

    def __init__(self, customer_id: int) -> None:
        super().__init__(f"No existe el cliente con id {customer_id}.")
        self.customer_id = customer_id


class EmailDuplicado(ErrorClientes):

    def __init__(self, email: str) -> None:
        super().__init__(f"Ya existe un cliente registrado con el email '{email}'.")
        self.email = email


class DniDuplicado(ErrorClientes):

    def __init__(self, dni: str) -> None:
        super().__init__(f"Ya existe un cliente registrado con el DNI '{dni}'.")
        self.dni = dni


class DatosInvalidos(ErrorClientes):
    pass
