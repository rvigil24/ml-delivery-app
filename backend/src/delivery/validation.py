"""Conversión de errores de validación del dominio a respuestas HTTP."""

from fastapi import HTTPException


def valid(function):
    try:
        return function()
    except ValueError:
        raise HTTPException(
            422,
            detail={
                "code": "invalid_request",
                "message": "Datos de dominio inválidos.",
            },
        ) from None
