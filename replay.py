"""Replay a recorded run: the same responses, in order, with no model, no key and no cost.
The tools run for real against a fresh sandbox, and every tool result is compared with the one
recorded. A change to the tools or the sandbox shows up as a result that differs.

  uv run replay.py results/v1/tax-rounding-1.json
  uv run replay.py results/v1                       every recorded run in a folder: a free CI check

A replay answers "did a code change alter what a recorded run saw or did?". It cannot answer
"is the agent better?": that needs new samples.
"""
import glob, json, os, re, sys

from src.agent.model import ReplayModel
from src.suite.runner import run_once
from src.suite.tasks import load

TIMING = re.compile(r" in \d+\.\d+s")      # pytest's timing line differs on every run


def results(turns):
    return [TIMING.sub("", json.dumps(c["result"], sort_keys=True)) for t in turns for c in t["calls"]]


def replay(path):
    saved = json.load(open(path))
    before = saved["record"]
    keep = os.path.join("work", "replay-traces")
    try:
        after = run_once(load(before["task"]), before["run"], version=before["version"],
                         fault_rate=before["fault_rate"], label="replay",
                         model=ReplayModel(saved["responses"]), keep=keep)
    except Exception as e:
        print(f"  ERROR      {os.path.basename(path)}: {e}")
        return False
    now = json.load(open(os.path.join(keep, os.path.basename(path))))
    a, b = results(saved["turns"]), results(now["turns"])
    differ = sum(x != y for x, y in zip(a, b)) + abs(len(a) - len(b))
    same = differ == 0 and after["success"] == before["success"] and not after["error"]
    print(f"  {'same' if same else 'DIFFERENT':<10} {os.path.basename(path):<32} {len(a)} tool results, "
          f"{differ} differ · recorded {'pass' if before['success'] else 'fail'}, "
          f"replayed {'pass' if after['success'] else 'fail'}" + (f" ({after['error'][:80]})" if after["error"] else ""))
    return same


target = sys.argv[1] if len(sys.argv) > 1 else "results/v1"
paths = sorted(glob.glob(os.path.join(target, "*.json"))) if os.path.isdir(target) else [target]
matched = [replay(p) for p in paths]
print(f"\n{sum(matched)} of {len(matched)} replays matched what was recorded")
sys.exit(0 if all(matched) else 1)
