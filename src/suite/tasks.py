"""The task suite: one folder per task under data/tasks/.

task.toml   slice, request, and the breaks applied to the base repository
test_*.py   held-out tests: never in the agent's workspace, run only when the run is scored"""
import glob, os, tomllib

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TASKS = os.path.join(ROOT, "data", "tasks")
BASE = os.path.join(ROOT, "data", "base-repo")


def load(name):
    folder = os.path.join(TASKS, name)
    with open(os.path.join(folder, "task.toml"), "rb") as f:
        task = tomllib.load(f)
    task["name"] = name
    task["hidden"] = sorted(glob.glob(os.path.join(folder, "test_*.py")))
    task.setdefault("break", [])
    return task


def all_tasks(names=None):
    found = sorted(n for n in os.listdir(TASKS) if os.path.isfile(os.path.join(TASKS, n, "task.toml")))
    return [load(n) for n in found if not names or n in names]
