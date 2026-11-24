"""A fresh sandbox for every run: the base repository, the task's breaks, and a git repository
with one commit. Nothing from a previous run, and nothing from the held-out tests."""
import os, shutil, subprocess

from src.suite.tasks import BASE

IGNORE = shutil.ignore_patterns("__pycache__", ".pytest_cache")


def build(task, folder):
    if os.path.isdir(folder):
        shutil.rmtree(folder)
    shutil.copytree(BASE, folder, ignore=IGNORE)
    for b in task["break"]:
        path = os.path.join(folder, b["file"])
        text = open(path).read()
        assert text.count(b["old"]) == 1, f"{task['name']}: break not found in {b['file']}"
        open(path, "w").write(text.replace(b["old"], b["new"]))
    git = lambda *a: subprocess.run(["git", *a], cwd=folder, check=True, capture_output=True)
    git("init", "-q", "-b", "main")
    git("config", "user.name", "lab")
    git("config", "user.email", "lab@example.com")
    with open(os.path.join(folder, ".git", "info", "exclude"), "a") as f:
        f.write("__pycache__/\n.pytest_cache/\n")
    git("add", ".")
    git("commit", "-q", "-m", "start")
    return folder


def files(folder):
    """path -> contents, for every file a run could have changed."""
    found = {}
    for dirpath, dirs, names in os.walk(folder):
        dirs[:] = [d for d in dirs if d not in (".git", "__pycache__", ".pytest_cache")]
        for n in names:
            full = os.path.join(dirpath, n)
            found[os.path.relpath(full, folder)] = open(full, "rb").read()
    return found
