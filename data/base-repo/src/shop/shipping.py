"""Shipping: free from $50.00, otherwise by weight."""
FREE_FROM_CENTS = 5000
RATES = [(1000, 499), (5000, 899)]      # (up to and including this many grams, cents)
HEAVY_CENTS = 1499


def shipping_cents(weight_grams, subtotal_cents):
    if subtotal_cents >= FREE_FROM_CENTS:
        return 0
    for limit, cents in RATES:
        if weight_grams <= limit:
            return cents
    return HEAVY_CENTS
