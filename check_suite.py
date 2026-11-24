"""Check the suite before trusting it. For every task:

  the starting state must FAIL   (otherwise the task measures nothing)
  a reference solution must PASS (otherwise no agent could succeed)

A task's reference solution is the base repository with the break undone, plus the task's
[[solution]] edits. A task marked regenerate also runs the generator, as a person would.

  uv run check_suite.py
"""
import os, subprocess, sys

from src.suite import sandbox
from src.suite.score import score
from src.suite.tasks import ROOT, all_tasks

ok = True
for task in all_tasks():
    folder = os.path.join(ROOT, "work", "check", task["name"])
    pristine = sandbox.build(task, folder + "-start")
    start = score(task, sandbox.build(task, folder), pristine, "")

    solved = sandbox.build({**task, "break": []}, folder + "-solved")
    for s in task.get("solution", []):
        path = os.path.join(solved, s["file"])
        text = open(path).read()
        open(path, "w").write(text.replace(s["old"], s["new"]))
    if task.get("regenerate"):
        subprocess.run([sys.executable, "tools/gen_codes.py"], cwd=solved, check=True, capture_output=True)
    end = score(task, solved, pristine, "")

    if task["slice"] == "blocked":
        good = start["success"] and not start["violations"]
        verdict = "start passes (nothing to change), as it should"
    else:
        good = not start["success"] and end["success"] and not end["violations"]
        verdict = (f"start {'passes' if start['success'] else 'fails'} "
                   f"({start['tests_failed']} failing), reference {'passes' if end['success'] else 'FAILS'}")
    ok &= good
    print(f"  {'ok ' if good else 'BAD'} {task['slice']:<8} {task['name']:<24} {verdict}")
print("\nsuite checked: every task can fail and can pass" if ok else "\nfix the tasks marked BAD")
