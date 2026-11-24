from shop.shipping import shipping_cents


def test_exactly_fifty():
    assert shipping_cents(3000, 5000) == 0


def test_just_under():
    assert shipping_cents(3000, 4999) == 899
