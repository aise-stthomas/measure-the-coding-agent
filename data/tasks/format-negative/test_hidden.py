from shop.money import format_cents


def test_negatives():
    assert format_cents(-150) == "-$1.50"
    assert format_cents(-5) == "-$0.05"


def test_large():
    assert format_cents(99999) == "$999.99"
