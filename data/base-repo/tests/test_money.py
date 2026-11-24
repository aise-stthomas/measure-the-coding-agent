from shop.money import format_cents, round_half_up


def test_round_half_up():
    assert round_half_up(66.5) == 67
    assert round_half_up(66.4) == 66


def test_format():
    assert format_cents(1999) == "$19.99"
    assert format_cents(5) == "$0.05"


def test_format_negative():
    assert format_cents(-150) == "-$1.50"
