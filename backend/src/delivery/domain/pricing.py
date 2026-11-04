"""T22: reglas monetarias aprobadas, sin importes comerciales predeterminados."""

from dataclasses import dataclass, field
from decimal import Context, Decimal, DecimalException, Inexact, ROUND_HALF_UP, localcontext

from .models import QuoteAmounts


class PricingConfigurationMissing(RuntimeError):
    pass


def _currency(value: str) -> None:
    if (not isinstance(value, str) or len(value) != 3 or not value.isascii()
            or not value.isalpha() or not value.isupper()):
        raise ValueError("currency debe ser un código de tres letras mayúsculas")


def _decimal(value: Decimal, name: str) -> None:
    if not isinstance(value, Decimal) or not value.is_finite() or value < 0:
        raise ValueError(f"{name} debe ser Decimal finito no negativo")


@dataclass(frozen=True)
class PricingPolicy:
    version: str
    currency: str
    monetary_quantum: Decimal
    customer_base: Decimal
    customer_per_km: Decimal
    courier_base: Decimal
    courier_per_km: Decimal
    rounding: str = field(default=ROUND_HALF_UP, init=False)

    def __post_init__(self) -> None:
        if not isinstance(self.version, str) or not self.version.strip():
            raise ValueError("version debe ser texto no vacío")
        _currency(self.currency)
        for name in ("monetary_quantum", "customer_base", "customer_per_km", "courier_base", "courier_per_km"):
            _decimal(getattr(self, name), name)
        quantum = self.monetary_quantum
        digits = quantum.as_tuple().digits
        if quantum == 0 or digits[0] != 1 or any(digit != 0 for digit in digits[1:]):
            raise ValueError("monetary_quantum debe ser una potencia de diez positiva")
        # Decimal('0.0100') y Decimal('100') deben cuantizar a 1E-2 y 1E+2.
        object.__setattr__(self, "monetary_quantum", Decimal((0, (1,), quantum.as_tuple().exponent + len(digits) - 1)))


@dataclass(frozen=True)
class OperatorCosts:
    """Costos por envío del operador; excluir lo ya incluido en el pago al repartidor."""

    currency: str
    variable_cost: Decimal
    attributable_cost: Decimal

    def __post_init__(self) -> None:
        _currency(self.currency)
        _decimal(self.variable_cost, "variable_cost")
        _decimal(self.attributable_cost, "attributable_cost")


def calculate_amounts(distance_km: Decimal, policy: PricingPolicy, costs: OperatorCosts) -> QuoteAmounts:
    _decimal(distance_km, "distance_km")
    if not isinstance(policy, PricingPolicy) or not isinstance(costs, OperatorCosts):
        raise ValueError("Se requieren PricingPolicy y OperatorCosts")
    if costs.currency != policy.currency:
        raise ValueError("Los costos y la política deben usar la misma moneda")
    try:
        # Contexto local reproducible; no depender del contexto Decimal del llamador.
        with localcontext(Context(prec=28, rounding=ROUND_HALF_UP)) as context:
            context.traps[Inexact] = True
            fee = policy.customer_base + policy.customer_per_km * distance_km
            payment = policy.courier_base + policy.courier_per_km * distance_km
            context.traps[Inexact] = False
            quantum = policy.monetary_quantum
            fee = fee.quantize(quantum)
            payment = payment.quantize(quantum)
            variable = costs.variable_cost.quantize(quantum)
            attributable = costs.attributable_cost.quantize(quantum)
            context.traps[Inexact] = True
            margin = fee - payment - variable - attributable
            return QuoteAmounts(policy.currency, fee, payment, variable, attributable, margin)
    except DecimalException as error:
        raise ValueError("El cálculo excede la precisión decimal soportada; no se emite un importe aproximado") from error
