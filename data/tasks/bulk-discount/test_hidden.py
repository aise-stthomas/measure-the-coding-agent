from shop.cart import Item, bulk_discount


def test_no_bulk_lines():
    assert bulk_discount([Item("MUG-11", 1900, 9)]) == 0


def test_one_bulk_line():
    assert bulk_discount([Item("PEN-02", 190, 10)]) == 95


def test_mixed_and_rounding():
    assert bulk_discount([Item("PEN-02", 190, 10), Item("CAP-01", 213, 10), Item("MUG-11", 1900, 2)]) == 202   # 95 + 106.5
