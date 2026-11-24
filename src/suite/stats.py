"""The numbers a suite reports. Every rate is an estimate, so every rate gets an interval."""
from collections import Counter
from math import comb, sqrt
import random


def wilson(successes, n, z=1.96):
    """95% interval for a rate. Works at 0 and at n, where the plain formula does not."""
    if n == 0:
        return 0.0, 1.0
    p = successes / n
    centre = (p + z * z / (2 * n)) / (1 + z * z / n)
    half = z * sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return max(0.0, centre - half), min(1.0, centre + half)


def pass_at_k(c, n, k):
    """Chance at least one of k runs succeeds, from c successes in n runs of one task."""
    if n - c < k:
        return 1.0
    return 1 - comb(n - c, k) / comb(n, k)


def pass_hat_k(c, n, k):
    """Chance all k runs succeed, from c successes in n runs of one task."""
    return comb(c, k) / comb(n, k)


def distribution(names):
    counts = Counter(names)
    total = sum(counts.values()) or 1
    return {k: v / total for k, v in counts.items()}


def tvd(p, q):
    """Total variation distance between two distributions: half the sum of the gaps. 0 to 1."""
    return 0.5 * sum(abs(p.get(k, 0) - q.get(k, 0)) for k in set(p) | set(q))


def paired_bootstrap(per_task_a, per_task_b, draws=10000, seed=0):
    """Difference in mean success, b minus a, resampling tasks, with each task's runs kept together."""
    tasks = sorted(set(per_task_a) & set(per_task_b))
    diffs = [per_task_b[t] - per_task_a[t] for t in tasks]
    rng = random.Random(seed)
    means = sorted(sum(rng.choice(diffs) for _ in diffs) / len(diffs) for _ in range(draws))
    return sum(diffs) / len(diffs), means[int(0.025 * draws)], means[int(0.975 * draws)]


def quantile(values, q):
    values = sorted(values)
    if not values:
        return 0
    return values[min(len(values) - 1, int(q * len(values)))]
