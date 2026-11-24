"""Compare two versions of the agent on the same tasks: success paired by task, cost, and the
distribution of tool calls.

  uv run compare.py results/v1.jsonl results/v2.jsonl

A change in the tool-call distribution is only a shift if it is larger than the distance between
two random halves of the SAME version's runs: that is the noise floor, printed beside it.
"""
import json, random, sys
from collections import defaultdict

from report import cost, load, pct
from src.suite.stats import distribution, paired_bootstrap, tvd, wilson


def per_task(rows):
    by = defaultdict(list)
    for r in rows:
        by[r["task"]].append(r["success"])
    return {t: sum(v) / len(v) for t, v in by.items()}


def calls(rows):
    return distribution(c for r in rows for c in r["calls"])


def noise_floor(rows, draws=500, seed=0):
    """How far apart two halves of the SAME version's runs land, split at random many times.
    The 95th percentile: a distance between two versions above it is unlikely to be noise."""
    rng = random.Random(seed)
    distances = []
    for _ in range(draws):
        shuffled = rows[:]
        rng.shuffle(shuffled)
        half = len(shuffled) // 2
        distances.append(tvd(calls(shuffled[:half]), calls(shuffled[half:])))
    return sorted(distances)[int(0.95 * draws)]


def main(a_path, b_path):
    a, b = load(a_path), load(b_path)
    name_a, name_b = a_path.split("/")[-1][:-6], b_path.split("/")[-1][:-6]

    print(f"{'':<28}{name_a:>14}{name_b:>14}")
    for label, fn in (("task success", lambda rs: sum(r["success"] for r in rs) / len(rs)),
                      ("median steps", lambda rs: sorted(r["steps"] for r in rs)[len(rs) // 2]),
                      ("mean input tokens", lambda rs: sum(r["tokens_in"] for r in rs) / len(rs)),
                      ("cost per run", lambda rs: sum(map(cost, rs)) / len(rs)),
                      ("cost per success", lambda rs: sum(map(cost, rs)) / max(1, sum(r["success"] for r in rs))),
                      ("violations", lambda rs: sum(len(r["violations"]) for r in rs)),
                      ("claimed done, was not", lambda rs: sum(r["claimed_done"] and not r["success"] for r in rs))):
        va, vb = fn(a), fn(b)
        fmt = (lambda v: pct(v)) if label == "task success" else (
              (lambda v: f"${v:.4f}") if label.startswith("cost") else (lambda v: f"{v:,.0f}"))
        print(f"{label:<28}{fmt(va):>14}{fmt(vb):>14}")

    print("\nSuccess, task by task (each task's runs averaged, so tasks count equally)")
    ta, tb = per_task(a), per_task(b)
    for t in sorted(ta):
        mark = "" if ta[t] == tb.get(t) else ("  better" if tb.get(t, 0) > ta[t] else "  worse")
        print(f"  {t:<26}{pct(ta[t]):>6}{pct(tb.get(t, 0)):>8}{mark}")
    diff, lo, hi = paired_bootstrap(ta, tb)
    print(f"  difference ({name_b} minus {name_a}): {100 * diff:+.0f} points, "
          f"95% interval {100 * lo:+.0f} to {100 * hi:+.0f} (bootstrap over tasks)")

    print("\nTool-call distribution")
    da, db = calls(a), calls(b)
    for name in sorted(set(da) | set(db), key=lambda n: -da.get(n, 0)):
        print(f"  {name:<14}{pct(da.get(name, 0)):>6}{pct(db.get(name, 0)):>8}")
    print(f"  distance {name_a} to {name_b} (total variation):         {tvd(da, db):.3f}")
    print(f"  noise floor: two random halves of {name_a}, 95th percentile: {noise_floor(a):.3f}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
