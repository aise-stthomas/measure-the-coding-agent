"""Discount codes: a code takes a percent off the subtotal."""
from generated.codes import CODES
from shop.cart import subtotal
from shop.money import round_half_up


def percent_for(code):
    key = code.strip().upper()
    if key not in CODES:
        raise ValueError(f"unknown discount code: {code}")
    return CODES[key]


def apply_code(items, code):
    """The discount in cents for this cart and code."""
    return round_half_up(subtotal(items) * percent_for(code) / 100)
