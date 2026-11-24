from shop.cart import Item, tax, total


def test_tax_rounds_half_up():
    assert tax([Item("PEN-02", 950)]) == 67          # 66.5 cents: half up, not to even


def test_tax_is_int():
    assert isinstance(tax([Item("TEA-04", 1999)]), int)


def test_total_of_two_lines():
    assert total([Item("TEA-04", 1999), Item("PEN-02", 950)]) == 3155
