"""Run one task once, show every turn, and score the state the run leaves behind.

  uv run run_one.py                         the first task
  uv run run_one.py tax-rounding
  uv run run_one.py new-code --version v2
"""
import argparse, json

from dotenv import load_dotenv
load_dotenv()

from src.agent.trace import show_turn
from src.suite.runner import run_once
from src.suite.tasks import all_tasks, load

parser = argparse.ArgumentParser()
parser.add_argument("task", nargs="?", default=None)
parser.add_argument("--version", default="v1")
parser.add_argument("--model", default=None)
args = parser.parse_args()

task = load(args.task) if args.task else all_tasks()[0]
print(f"task: {task['name']}   slice: {task['slice']}\nrequest: {task['request']}")
record = run_once(task, 1, version=args.version, model_name=args.model, label="one", show=show_turn,
                  keep="results/one")
print("\nanswer:", record["answer"])
print("\nscore, read from the repository the run left behind:")
for key in ("success", "tests_passed", "tests_failed", "changed", "violations", "claimed_done",
            "steps", "tokens_in", "tokens_out", "calls"):
    print(f"  {key:<14} {json.dumps(record[key])}")
print(f"\nThe run's repository is work/one/{task['name']}-1/. The trace is results/one/{task['name']}-1.json.")
