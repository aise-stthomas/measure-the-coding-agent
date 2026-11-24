"""The toolbox: which tools a request declares, and where each call runs.

Every tool here is a Python function in this process. A function becomes a declaration from
its signature: the name, the arguments and their types. The description is what you write."""
import inspect
from concurrent.futures import ThreadPoolExecutor
from typing import get_args, get_origin, get_type_hints

JSON_TYPES = {int: "integer", float: "number", bool: "boolean", str: "string"}


def json_type(t):
    if get_origin(t) is list:
        return {"type": "array", "items": json_type(get_args(t)[0])}
    return {"type": JSON_TYPES.get(t, "string")}


def declare(fn, description):
    """A function as a declaration: the name and arguments come from its signature."""
    hints = get_type_hints(fn)
    properties, required = {}, []
    for name, param in inspect.signature(fn).parameters.items():
        properties[name] = json_type(hints.get(name, str))
        if param.default is inspect.Parameter.empty:
            required.append(name)
    return {"name": fn.__name__, "description": description,
            "parameters": {"type": "object", "properties": properties, "required": required}}


class Toolbox:
    def __init__(self):
        self.local = {}        # name -> function in this process
        self.declared = []     # what the next request declares, in order
        self.paused = False    # the loop checks it after each step

    def add(self, declaration, fn):
        self.local[declaration["name"]] = fn
        self.declared.append(declaration)

    def declarations(self):
        return self.declared

    def call(self, name, args):
        if name not in self.local:
            return {"error": f"Unknown tool: {name}. Available tools: "
                             f"{', '.join(d['name'] for d in self.declared)}"}
        try:
            return self.local[name](**args)
        except Exception as e:
            return {"error": f"{name} failed: {type(e).__name__}: {e}"}

    def call_all(self, calls):
        # Several calls named in one turn run at the same time.
        if len(calls) == 1:
            return [self.call(calls[0]["name"], calls[0]["args"])]
        with ThreadPoolExecutor(max_workers=len(calls)) as pool:
            return list(pool.map(lambda c: self.call(c["name"], c["args"]), calls))
