from shop.cart import Item
from shop.discounts import apply_code


def test_friends15():
    assert apply_code([Item("TEA-04", 1999)], "FRIENDS15") == 300     # 299.85


def test_rounds_half_up():
    assert apply_code([Item("PEN-02", 950)], "WELCOME10") == 95
    assert apply_code([Item("PEN-02", 1005)], "WELCOME10") == 101    # 100.5
