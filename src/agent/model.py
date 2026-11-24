"""The model: one HTTP POST. No SDK, so that this file is the wire format."""
import json, os, time, urllib.error, urllib.request

from src.wire import log

BASE = "https://generativelanguage.googleapis.com/v1beta/models/{model}:{verb}"
MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.1-flash-lite")


class Model:
    def __init__(self, name=None):
        self.name = name or MODEL

    def request_for(self, system, contents, declarations=None):
        request = {"systemInstruction": {"parts": [{"text": system}]}}
        if declarations:
            request["tools"] = [{"functionDeclarations": declarations}]
        request["contents"] = contents
        return request

    def generate(self, system, contents, declarations=None):
        request = self.request_for(system, contents, declarations)
        response = self.post("generateContent", request)
        log("model", {"request": request, "response": response})
        return response

    def count_tokens(self, system, contents, declarations=None):
        """What a request would cost in input tokens, without running it."""
        request = self.request_for(system, contents, declarations)
        request["model"] = f"models/{self.name}"
        return self.post("countTokens", {"generateContentRequest": request})["totalTokens"]

    def post(self, verb, request, attempts=6):
        body = json.dumps(request).encode()
        headers = {"Content-Type": "application/json",
                   "x-goog-api-key": os.environ["GEMINI_API_KEY"]}
        started = time.monotonic()
        for attempt in range(attempts):
            try:
                req = urllib.request.Request(BASE.format(model=self.name, verb=verb), body, headers)
                with urllib.request.urlopen(req, timeout=90) as r:
                    response = json.load(r)
                # Added by us; not part of the wire format.
                response["latency_ms"] = int((time.monotonic() - started) * 1000)
                response["received_at"] = time.time()
                return response
            except urllib.error.HTTPError as e:
                if e.code not in (429, 500, 503) or attempt == attempts - 1:
                    raise RuntimeError(f"{e.code}: {e.read().decode()[:400]}")
            except (urllib.error.URLError, TimeoutError):
                if attempt == attempts - 1:
                    raise
            time.sleep(min(2 ** attempt, 30))


class ReplayModel:
    """Answers with recorded responses, in order. No key, no network, no cost.
    The tools still run for real, so a code change shows up; a new sample cannot."""
    def __init__(self, responses):
        self.responses = list(responses)
        self.name = "replay"

    def generate(self, system, contents, declarations=None):
        if not self.responses:
            raise RuntimeError("replay ran out of recorded responses: the run took a different path")
        return self.responses.pop(0)
