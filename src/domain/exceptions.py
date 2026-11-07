"""Jerarquía de excepciones del dominio CleanPro.

Cada tipo de violación de negocio tiene su propia clase para que la capa API
pueda traducirla a un código HTTP semántico sin conocer las reglas:

* DomainError            -> 422 (dato o invariante inválida)
* TransicionInvalida     -> 409 (la State Machine rechaza el cambio de estado)
* ConflictoDeAgenda      -> 409 (traslape de horario de una cuadrilla)
* AutorizacionRequerida  -> 403 (la operación excede el permiso del rol, RN-01/RN-02)
"""


class DomainError(ValueError):
    """Excepción base para violaciones de invariantes del dominio CleanPro."""


class TransicionInvalida(DomainError):
    """La máquina de estados no permite pasar del estado actual al solicitado."""


class ConflictoDeAgenda(DomainError):
    """La cuadrilla ya tiene un servicio en el horario solicitado (CA-06.3, CA-07.2)."""


class AutorizacionRequerida(DomainError):
    """La operación requiere autorización de gerencia (RN-01, RN-02)."""
