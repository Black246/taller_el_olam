# backend/app/core/exceptions.py

class BusinessException(Exception):
    """
    Excepción base de negocio
    """

    def __init__(self, message="Error de negocio"):
        self.message = message
        super().__init__(self.message)


class ValidationException(BusinessException):
    """
    Error de validación
    """

    pass


class NotFoundException(BusinessException):
    """
    Recurso no encontrado
    """

    pass


class AuthorizationException(BusinessException):
    """
    Error de autorización
    """

    pass