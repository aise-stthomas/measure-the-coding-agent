"""The shape of the conversation: building its entries and reading them."""


def user_message(text):
    return {"role": "user", "parts": [{"text": text}]}


def model_message(text):
    return {"role": "model", "parts": [{"text": text}]}


def model_turn(response):
    candidates = response.get("candidates") or [{}]
    return candidates[0].get("content", {"role": "model", "parts": []})


def tool_calls_in(turn):
    calls = []
    for part in turn.get("parts", []):
        if "functionCall" in part:
            call = part["functionCall"]
            calls.append({"name": call["name"], "args": call.get("args", {})})
    return calls


def text_in(turn):
    return "".join(part.get("text", "") for part in turn.get("parts", []) if not part.get("thought"))


def results_message(calls, results):
    parts = []
    for call, result in zip(calls, results):
        reply = {"name": call["name"], "response": {"result": result}}
        parts.append({"functionResponse": reply})
    return {"role": "user", "parts": parts}
