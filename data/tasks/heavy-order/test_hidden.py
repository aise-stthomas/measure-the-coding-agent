from shop.cart import Item, weight
from shop.checkout import quote


def test_weight_counts_qty():
    assert weight([Item("CUP-03", 900, 3, 400)]) == 1200


def test_three_cups_ship_medium():
    assert quote([Item("CUP-03", 900, 3, 400)])["shipping"] == 899
