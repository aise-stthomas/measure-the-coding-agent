"""Score the runs of a suite again, from the repositories they left behind, without running the
agent. Use it after you change the scorer: the end states are kept in work/<label>/.

  uv run rescore.py results/v1.jsonl          rewrites the file, and says what changed
"""
import json, os, sys

from src.suite.runner import WORK
from src.suite.score import score
from src.suite.tasks import load

path = sys.argv[1]
rows = [json.loads(line) for line in open(path)]
moved = 0
for r in rows:
    base = os.path.join(WORK, r["label"], f"{r['task']}-{r['run']}")
    new = score(load(r["task"]), base, base + "-start", r["answer"], stopped=r["stopped"])
    if (new["success"], new["violations"]) != (r["success"], r["violations"]):
        moved += 1
        print(f"  {r['task']:<24} run {r['run']}  success {r['success']} -> {new['success']}   "
              f"violations {r['violations']} -> {new['violations']}")
    r.update(new)
with open(path, "w") as f:
    f.writelines(json.dumps(r) + "\n" for r in rows)
print(f"\n{moved} of {len(rows)} runs scored differently. {path} rewritten.")
