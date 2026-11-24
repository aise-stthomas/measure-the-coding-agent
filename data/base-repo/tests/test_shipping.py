from shop.shipping import shipping_cents


def test_light():
    assert shipping_cents(400, 2000) == 499


def test_at_the_first_limit():
    assert shipping_cents(1000, 2000) == 499


def test_medium():
    assert shipping_cents(3000, 2000) == 899


def test_heavy():
    assert shipping_cents(9000, 2000) == 1499


def test_free():
    assert shipping_cents(9000, 7500) == 0
