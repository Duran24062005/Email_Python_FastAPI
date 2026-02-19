class DomainError(Exception):
    """Error base de dominio"""
    pass


class ValidationError(DomainError):
    pass


class EmailAlreadyExists(DomainError):
    pass


class WeakPassword(DomainError):
    pass