from shop.money import format_cents


def test_commas():
    assert format_cents(123456) == "$1,234.56"
    assert format_cents(100000000) == "$1,000,000.00"


def test_below_a_thousand():
    assert format_cents(99999) == "$999.99"


def test_negative_with_commas():
    assert format_cents(-123456789) == "-$1,234,567.89"
