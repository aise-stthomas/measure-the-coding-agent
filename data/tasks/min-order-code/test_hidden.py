import pytest

from shop.cart import Item
from shop.discounts import apply_code


def test_big25_at_the_minimum():
    assert apply_code([Item("LAMP-07", 10000)], "BIG25") == 2500


def test_big25_below_the_minimum():
    with pytest.raises(ValueError):
        apply_code([Item("LAMP-07", 9999)], "BIG25")


def test_other_codes_have_no_minimum():
    assert apply_code([Item("PEN-02", 950)], "WELCOME10") == 95
