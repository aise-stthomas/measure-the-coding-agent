"""Run one task once: a fresh sandbox, the agent's loop, then the score. One JSON record per run.

The record is the row a suite is made of. The full trace, with every raw response, is written
beside it so that the run can be replayed and read."""
import json, os, time, zlib

from src.agent.loop import STOPPED, run
from src.agent.messages import user_message
from src.agent.model import Model
from src.agent.toolbox import Toolbox
from src.agent.trace import Trace
from src.coder.instructions import instructions
from src.coder.tools import Workspace
from src.suite import faults, sandbox
from src.suite.score import score
from src.suite.tasks import ROOT

WORK = os.path.join(ROOT, "work")
MAX_STEPS = 20


def repeats(trace):
    """Calls identical to an earlier call in the same run: the same tool, the same arguments."""
    seen, n = set(), 0
    for t in trace.turns:
        for c in t["calls"]:
            key = (c["name"], json.dumps(c["args"], sort_keys=True))
            n += key in seen
            seen.add(key)
    return n


def run_once(task, k, version="v1", model_name=None, fault_rate=0.0, label="run", model=None,
             show=None, keep=None):
    base = os.path.join(WORK, label, f"{task['name']}-{k}")
    pristine = sandbox.build(task, base + "-start")
    folder = sandbox.build(task, base)

    workspace = Workspace(folder)
    tools = Toolbox()
    for declaration, fn in workspace.tools():
        tools.add(declaration, fn)
    faults.inject(tools, fault_rate, seed=zlib.crc32(f"{task['name']}-{k}".encode()))

    model = model or Model(model_name)
    trace = Trace(on_turn=show)
    started = time.time()
    error = None
    try:
        answer = run(model, instructions(version, folder), [user_message(task["request"])], tools,
                     trace, max_steps=MAX_STEPS)
    except Exception as e:                  # an API failure is a failed run, recorded, not a crash
        answer, error = None, f"{type(e).__name__}: {e}"[:300]
    result = score(task, folder, pristine, answer, stopped=answer == STOPPED)

    calls = [c["name"] for t in trace.turns for c in t["calls"]]
    record = {
        "label": label, "task": task["name"], "slice": task["slice"], "run": k,
        "version": version, "model": model.name, "fault_rate": fault_rate,
        **result,
        "stopped": answer == STOPPED, "error": error,
        "steps": len(trace.turns),
        "tokens_in": sum(t["prompt_tokens"] for t in trace.turns),
        "tokens_out": sum(t["output_tokens"] for t in trace.turns),
        "seconds": round(time.time() - started, 1),
        "calls": calls,
        "tool_errors": sum(1 for t in trace.turns for c in t["calls"]
                           if isinstance(c["result"], dict) and (c["result"].get("error")
                              or (c["name"] == "run" and c["result"].get("exit_code") is None))),
        "repeats": repeats(trace),
        "faults": getattr(tools, "faults", 0),
        "commands": [c["args"].get("command", "") for t in trace.turns for c in t["calls"] if c["name"] == "run"],
        "answer": answer,
    }
    if keep:
        os.makedirs(keep, exist_ok=True)
        with open(os.path.join(keep, f"{task['name']}-{k}.json"), "w") as f:
            json.dump({"record": record, "turns": trace.turns, "responses": trace.responses}, f)
    return record
