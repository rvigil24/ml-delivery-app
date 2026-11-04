"""T32: mapeo BSON explícito por tipos del dominio, sin pickle ni imports dinámicos."""

from dataclasses import fields, is_dataclass
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from enum import Enum
from typing import Union, get_args, get_origin, get_type_hints

from bson.decimal128 import Decimal128


def encode(value):
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, datetime):
        if value.tzinfo is None or value.utcoffset() != timedelta(0):
            raise ValueError("Solo se persisten fechas UTC conscientes")
        # BSON date trunca microsegundos: preservar el instante exacto del historial.
        return value.astimezone(timezone.utc).isoformat(timespec="microseconds")
    if isinstance(value, Decimal):
        if not value.is_finite():
            raise ValueError("Solo se persisten Decimal finitos")
        return Decimal128(value)
    if is_dataclass(value):
        return {f.name: encode(getattr(value, f.name)) for f in fields(value) if f.init}
    if isinstance(value, (tuple, list)):
        return [encode(item) for item in value]
    return value


def decode(spec, value):
    origin, args = get_origin(spec), get_args(spec)
    if origin is Union:
        if value is None and type(None) in args:
            return None
        return decode(next(arg for arg in args if arg is not type(None)), value)
    if origin is tuple:
        if args[-1] is Ellipsis:
            return tuple(decode(args[0], item) for item in value)
        if len(value) != len(args):
            raise ValueError("Tupla BSON incompatible")
        return tuple(decode(arg, item) for arg, item in zip(args, value))
    if spec is Decimal:
        return value.to_decimal()
    if spec is datetime:
        stamp = datetime.fromisoformat(value)
        if stamp.tzinfo is None or stamp.utcoffset() != timedelta(0):
            raise ValueError("Fecha almacenada sin UTC")
        return stamp.astimezone(timezone.utc)
    if isinstance(spec, type) and issubclass(spec, Enum):
        return spec(value)
    if is_dataclass(spec):
        hints = get_type_hints(spec)
        return spec(**{f.name: decode(hints[f.name], value[f.name]) for f in fields(spec) if f.init})
    return value


def schema_for(spec):
    """Validación de estructura/tipos en MongoDB; semántica adicional en dominio."""
    origin, args = get_origin(spec), get_args(spec)
    if origin is Union:
        return {"anyOf": [schema_for(arg) for arg in args]}
    if spec is type(None):
        return {"bsonType": "null"}
    if origin is tuple:
        if args[-1] is Ellipsis:
            return {"bsonType": "array", "items": schema_for(args[0])}
        return {"bsonType": "array", "minItems": len(args), "maxItems": len(args),
                "items": {"anyOf": [schema_for(arg) for arg in args]}}
    if isinstance(spec, type) and issubclass(spec, Enum):
        return {"bsonType": "string", "enum": [item.value for item in spec]}
    if is_dataclass(spec):
        hints = get_type_hints(spec)
        names = [f.name for f in fields(spec) if f.init]
        properties = {name: schema_for(hints[name]) for name in names}
        if spec.__name__ == "Location":
            properties["latitude"].update(minimum=-90, maximum=90)
            properties["longitude"].update(minimum=-180, maximum=180)
        return {"bsonType": "object", "required": names, "additionalProperties": False, "properties": properties}
    if spec is datetime:
        return {"bsonType": "string", "pattern": r"^\d{4}-\d{2}-\d{2}T.*\.\d{6}\+00:00$"}
    result = {"bsonType": {str: "string", int: ["int", "long"], float: ["double", "int", "long"],
                           bool: "bool", Decimal: "decimal"}[spec]}
    if spec is str:
        result["minLength"] = 1
    if spec is Decimal:
        result["minimum"] = 0
    return result
