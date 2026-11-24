from shop.shipping import shipping_cents


def test_at_each_limit():
    assert shipping_cents(1000, 2000) == 499
    assert shipping_cents(5000, 2000) == 899


def test_just_over():
    assert shipping_cents(1001, 2000) == 899
    assert shipping_cents(5001, 2000) == 1499
