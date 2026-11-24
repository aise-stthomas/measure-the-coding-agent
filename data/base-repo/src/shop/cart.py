"""A cart and its total."""
from dataclasses import dataclass

from shop.money import round_half_up

TAX_RATE = 0.07


@dataclass
class Item:
    sku: str
    price_cents: int
    qty: int = 1
    weight_grams: int = 0


def subtotal(items):
    return sum(i.price_cents * i.qty for i in items)


def weight(items):
    return sum(i.weight_grams * i.qty for i in items)


def tax(items):
    return round_half_up(subtotal(items) * TAX_RATE)


def total(items):
    return subtotal(items) + tax(items)
