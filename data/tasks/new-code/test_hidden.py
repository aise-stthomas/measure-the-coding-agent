from shop.cart import Item
from shop.discounts import apply_code


def test_spring20():
    assert apply_code([Item("MUG-11", 1900, 2)], "SPRING20") == 760


def test_old_codes_still_work():
    assert apply_code([Item("MUG-11", 1900, 2)], "WELCOME10") == 380
