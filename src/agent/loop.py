"""The loop: sample, parse, stop, invoke, append, limit. Two places a program can step in:
`prepare` decides what is sent, and `after_step` runs after every step."""
from src.agent.messages import (model_message, model_turn, results_message, text_in,
                                tool_calls_in)

STOPPED = "(stopped by the step limit)"
PAUSED = "(paused: waiting for a person)"
NO_ANSWER = "(no answer: the turn had no text)"


def run(model, system, contents, tools, trace, agent="lead", max_steps=12,
        prepare=None, after_step=None, first_step=1):
    for step in range(first_step, max_steps + 1):
        # SAMPLE: what is sent may differ from what is kept.
        sent = prepare(contents) if prepare else contents
        response = model.generate(system, sent, tools.declarations())
        turn = model_turn(response)

        # PARSE and STOP: a turn that names no tool is the answer.
        calls = tool_calls_in(turn)
        if not calls:
            trace.record(agent, step, response, [], [])
            answer = text_in(turn).strip() or NO_ANSWER
            contents.append(model_message(answer))
            if after_step:
                after_step(step, contents, "done")
            return answer

        # INVOKE: the toolbox decides where each call runs.
        results = tools.call_all(calls)

        # APPEND, then write the run down.
        contents.append(turn)
        contents.append(results_message(calls, results))
        trace.record(agent, step, response, calls, results)
        if after_step:
            after_step(step, contents, "waiting" if tools.paused else "running")
        if tools.paused:
            return PAUSED

    # LIMIT: your code ends the run, whatever was sampled.
    return STOPPED
