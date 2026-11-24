"""What a suite reports, from its records.

  uv run report.py results/v1.jsonl
"""
import json, sys
from collections import Counter, defaultdict

from src.suite.stats import distribution, pass_at_k, pass_hat_k, quantile, wilson

PRICE_IN, PRICE_OUT = 0.25, 1.50     # dollars per million tokens; set from the provider's price page


def load(path):
    return [json.loads(line) for line in open(path)]


def cost(r):
    return (r["tokens_in"] * PRICE_IN + r["tokens_out"] * PRICE_OUT) / 1e6


def pct(x):
    return f"{100 * x:.0f}%"


def main(path):
    rows = load(path)
    print(f"{path}: {len(rows)} runs   model {rows[0]['model']}   instructions {rows[0]['version']}"
          f"   fault rate {rows[0]['fault_rate']}\n")

    print("1. Task success, scored from the repository each run left behind")
    print(f"   {'slice':<10}{'success':>10}{'rate':>7}   95% interval")
    slices = defaultdict(list)
    for r in rows:
        slices[r["slice"]].append(r)
    for name in ["fix", "report", "feature", "blocked"] + sorted(set(slices) - {"fix", "report", "feature", "blocked"}):
        if name not in slices:
            continue
        s = sum(r["success"] for r in slices[name]); m = len(slices[name])
        lo, hi = wilson(s, m)
        print(f"   {name:<10}{s:>5} / {m:<3}{pct(s / m):>6}   {pct(lo)}-{pct(hi)}")
    s = sum(r["success"] for r in rows); lo, hi = wilson(s, len(rows))
    n = len(rows)
    print(f"   {'all':<10}{s:>5} / {n:<3}{pct(s / n):>6}   {pct(lo)}-{pct(hi)}")
    blocked = slices.get("blocked", [])
    if blocked:
        guessed = sum(bool(r["changed"]) for r in blocked)
        asked = sum(not r["stopped"] for r in blocked)
        print(f"   blocked runs that changed the repository anyway: {guessed} of {len(blocked)}."
              f"   that handed back with an answer: {asked} of {len(blocked)}")

    print("\n2. Per task: is it reliable, or did it pass once?")
    tasks = defaultdict(list)
    for r in rows:
        tasks[r["task"]].append(r["success"])
    k = min(3, min(len(v) for v in tasks.values()))
    print(f"   {'task':<25}{'passed':>8}   pass@{k}   pass^{k}")
    for t, v in sorted(tasks.items()):
        c, m = sum(v), len(v)
        print(f"   {t:<25}{c:>4} / {m:<3}  {pass_at_k(c, m, k):>5.2f}   {pass_hat_k(c, m, k):>5.2f}")
    mean_at = sum(pass_at_k(sum(v), len(v), k) for v in tasks.values()) / len(tasks)
    mean_hat = sum(pass_hat_k(sum(v), len(v), k) for v in tasks.values()) / len(tasks)
    print(f"   {'mean over tasks':<25}{'':>10}  {mean_at:>5.2f}   {mean_hat:>5.2f}")

    print("\n3. Violations: things that must never happen. A count, not an average")
    v = Counter(x for r in rows for x in r["violations"])
    for name in ("test_weakened", "generated_by_hand"):
        lo, hi = wilson(v[name], n)
        print(f"   {name:<20}{v[name]:>4} of {n} runs   95% interval {pct(lo)}-{pct(hi)}")

    print("\n4. Said it was done; the repository says otherwise")
    claimed = [r for r in rows if r["claimed_done"]]
    wrong = [r for r in claimed if not r["success"]]
    print(f"   {len(wrong)} of {len(claimed)} runs whose answer claimed success had not succeeded")

    print("\n5. Steps, tokens and cost per run, as distributions")
    for key, fmt in (("steps", "{:.0f}"), ("repeats", "{:.0f}"), ("tokens_in", "{:,.0f}")):
        vals = [r[key] for r in rows]
        print(f"   {key:<12} median {fmt.format(quantile(vals, .5)):>7}   p90 {fmt.format(quantile(vals, .9)):>7}"
              f"   max {fmt.format(max(vals)):>7}")
    costs = [cost(r) for r in rows]
    ok = [cost(r) for r in rows if r["success"]]
    print(f"   cost per run median ${quantile(costs, .5):.4f}   p90 ${quantile(costs, .9):.4f}   max ${max(costs):.4f}")
    if ok:
        print(f"   cost per successful task ${sum(costs) / len(ok):.4f}  (all spend / successes)")
    print(f"   stopped by the step limit: {sum(r['stopped'] for r in rows)}   API errors: {sum(bool(r['error']) for r in rows)}")

    print("\n6. Tool calls: the agent's behaviour, as a distribution")
    d = distribution(c for r in rows for c in r["calls"])
    total_calls = sum(len(r["calls"]) for r in rows)
    for name, share in sorted(d.items(), key=lambda x: -x[1]):
        print(f"   {name:<12}{pct(share):>5}")
    print(f"   {total_calls} calls, {total_calls / n:.1f} per run; tool errors {sum(r['tool_errors'] for r in rows)}"
          + (f"; injected faults {sum(r['faults'] for r in rows)}" if rows[0]["fault_rate"] else ""))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "results/v1.jsonl")
