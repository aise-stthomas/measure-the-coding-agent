"""A quote for a cart: every amount the customer sees, in cents.
Tax and free shipping are both on the price after the discount."""
from shop.cart import TAX_RATE, subtotal, weight
from shop.discounts import apply_code
from shop.money import round_half_up
from shop.shipping import shipping_cents


def quote(items, code=None):
    sub = subtotal(items)
    discount = apply_code(items, code) if code else 0
    after = sub - discount
    tax = round_half_up(after * TAX_RATE)
    shipping = shipping_cents(weight(items), after)
    return {"subtotal": sub, "discount": discount, "tax": tax, "shipping": shipping,
            "total": after + tax + shipping}
