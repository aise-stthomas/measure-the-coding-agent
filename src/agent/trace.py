"""The trace: one record per turn, for every agent in a run. A lead and its workers form a tree."""
import json, threading, time

from src.wire import log

from src.agent.messages import model_turn, text_in


def show_turn(turn):
    who = turn["agent"]
    print(f"\n[{who}] step {turn['step']}   {turn['prompt_tokens']} tokens in, "
          f"{turn['output_tokens']} out, {turn['latency_ms']} ms")
    if turn["text"]:
        print(f"  text:   {turn['text'][:600]}")
    for c in turn["calls"]:
        print(f"  call:   {c['name']}({json.dumps(c['args'])[:200]})")
        print(f"  result: {json.dumps(c['result'])[:240]}")


class Trace:
    def __init__(self, on_turn=show_turn):
        self.turns = []
        self.responses = []      # every raw response, in order: what replay answers with
        self.on_turn = on_turn
        self.lock = threading.Lock()

    def record(self, agent, step, response, calls, results):
        usage = response.get("usageMetadata", {})
        turn = {
            "agent": agent,
            "step": step,
            "model": response.get("modelVersion"),
            "prompt_tokens": usage.get("promptTokenCount", 0),
            "output_tokens": usage.get("candidatesTokenCount", 0),
            "latency_ms": response.get("latency_ms", 0),
            "calls": [{**call, "result": result} for call, result in zip(calls, results)],
            "text": text_in(model_turn(response)),
            "ended": response.get("received_at", time.time()),
        }
        log("trace", turn)
        with self.lock:
            self.turns.append(turn)
            self.responses.append(response)
        if self.on_turn:
            self.on_turn(turn)

    def tokens(self, agent=None):
        return sum(t["prompt_tokens"] for t in self.turns if agent is None or t["agent"] == agent)

    def largest(self, agent=None):
        return max((t["prompt_tokens"] for t in self.turns if agent is None or t["agent"] == agent), default=0)

    def summary(self):
        agents = sorted({t["agent"] for t in self.turns}, key=lambda a: (a != "lead", a))
        for a in agents:
            ts = [t for t in self.turns if t["agent"] == a]
            print(f"  {a:<34} turns {len(ts):>2}   input tokens {sum(t['prompt_tokens'] for t in ts):>7,}"
                  f"   largest request {max(t['prompt_tokens'] for t in ts):>6,}")
        print(f"  {'all agents':<34} turns {len(self.turns):>2}   input tokens {self.tokens():>7,}")
