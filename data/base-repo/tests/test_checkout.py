from shop.cart import Item
from shop.checkout import quote


def test_quote_one_item():
    q = quote([Item("TEA-04", 1999, 1, 300)])
    assert q == {"subtotal": 1999, "discount": 0, "tax": 140, "shipping": 499, "total": 2638}


def test_quote_free_shipping():
    q = quote([Item("MUG-11", 1900, 3, 400)])
    assert q["shipping"] == 0
