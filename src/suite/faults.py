"""Fault injection: some calls to a tool fail, the way a real sandbox, network or server does.
Seeded, so a run's faults are the same each time it is repeated."""
import random

FAULT = {"exit_code": None, "output": "error: the sandbox did not respond. Nothing ran. Try again."}


def inject(toolbox, rate, seed, tool="run"):
    if not rate:
        return toolbox
    rng = random.Random(seed)
    real = toolbox.call
    toolbox.faults = 0

    def call(name, args):
        if name == tool and rng.random() < rate:
            toolbox.faults += 1
            return dict(FAULT)
        return real(name, args)

    toolbox.call = call
    return toolbox
