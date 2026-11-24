"""Money is in cents, as int. One rounding rule for the whole shop: half up."""
from decimal import ROUND_HALF_UP, Decimal


def round_half_up(amount):
    """A number of cents, possibly fractional, to a whole cent. 66.5 -> 67."""
    return int(Decimal(str(amount)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def format_cents(cents):
    """1999 -> "$19.99", -150 -> "-$1.50"."""
    sign = "-" if cents < 0 else ""
    cents = abs(cents)
    return f"{sign}${cents // 100}.{cents % 100:02d}"
