from shop.cart import Item
from shop.discounts import apply_code


def test_lower_case():
    assert apply_code([Item("MUG-11", 1900, 2)], "welcome10") == 380


def test_mixed_case():
    assert apply_code([Item("MUG-11", 1900, 2)], "Friends15") == 570
