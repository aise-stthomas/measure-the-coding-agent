from shop.cart import Item, subtotal, tax, total


def test_subtotal():
    assert subtotal([Item("MUG-11", 1900, 2)]) == 3800


def test_tax_is_whole_cents():
    assert tax([Item("TEA-04", 1999)]) == 140


def test_total():
    assert total([Item("TEA-04", 1999)]) == 2139
