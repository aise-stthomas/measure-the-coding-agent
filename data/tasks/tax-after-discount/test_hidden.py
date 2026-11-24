from shop.cart import Item
from shop.checkout import quote


def test_tax_after_discount():
    q = quote([Item("TEA-04", 1999, 1, 300)], "WELCOME10")
    assert q == {"subtotal": 1999, "discount": 200, "tax": 126, "shipping": 499, "total": 2424}


def test_no_code_unchanged():
    assert quote([Item("TEA-04", 1999, 1, 300)])["tax"] == 140
