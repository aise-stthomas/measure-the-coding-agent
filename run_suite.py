"""Run every task k times and write one record per run to results/<label>.jsonl.

  uv run run_suite.py --label v1                          the agent as it is, 5 runs per task
  uv run run_suite.py --label v2 --version v2             the proposed instructions
  uv run run_suite.py --label new-model --model gemini-3.5-flash-lite
  uv run run_suite.py --label faults --fault-rate 0.3     3 in 10 shell commands fail
  uv run run_suite.py --label quick --runs 2 --tasks tax-rounding new-code

Then: uv run report.py results/v1.jsonl
"""
import argparse, json, os
from concurrent.futures import ThreadPoolExecutor, as_completed

from dotenv import load_dotenv
load_dotenv()

from src.suite.runner import run_once
from src.suite.tasks import all_tasks

parser = argparse.ArgumentParser()
parser.add_argument("--label", required=True)
parser.add_argument("--runs", type=int, default=5)
parser.add_argument("--version", default="v1")
parser.add_argument("--model", default=None)
parser.add_argument("--fault-rate", type=float, default=0.0)
parser.add_argument("--tasks", nargs="*")
parser.add_argument("--workers", type=int, default=4, help="runs at the same time; lower it if you hit 429s")
args = parser.parse_args()

tasks = all_tasks(args.tasks)
jobs = [(t, k) for t in tasks for k in range(1, args.runs + 1)]
os.makedirs("results", exist_ok=True)
out = os.path.join("results", f"{args.label}.jsonl")
keep = os.path.join("results", args.label)
print(f"{len(tasks)} tasks x {args.runs} runs = {len(jobs)} runs -> {out}")

with open(out, "w") as f, ThreadPoolExecutor(max_workers=args.workers) as pool:
    futures = [pool.submit(run_once, t, k, args.version, args.model, args.fault_rate, args.label,
                           None, None, keep) for t, k in jobs]
    for n, future in enumerate(as_completed(futures), 1):
        r = future.result()
        f.write(json.dumps(r) + "\n")
        f.flush()
        mark = "pass" if r["success"] else "FAIL"
        extra = " ".join(r["violations"]) + (" stopped" if r["stopped"] else "") + (f" {r['error'][:60]}" if r["error"] else "")
        print(f"  {n:>3}/{len(jobs)}  {mark}  {r['task']:<24} run {r['run']}  {r['steps']:>2} steps  {extra}")
print(f"\nwrote {out}.  Next: uv run report.py {out}")
