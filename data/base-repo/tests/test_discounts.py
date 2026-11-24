import pytest

from shop.cart import Item
from shop.discounts import apply_code


def test_welcome10():
    assert apply_code([Item("MUG-11", 1900, 2)], "WELCOME10") == 380


def test_unknown_code():
    with pytest.raises(ValueError):
        apply_code([Item("MUG-11", 1900)], "NOPE")
