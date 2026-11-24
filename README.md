# measure-the-coding-agent

AI Systems Engineering lab. Measure a coding agent the way you would measure any agent: a suite
of tasks, each run several times in a fresh sandbox, scored from the state the run leaves
behind, with intervals on every rate.

- The agent is the coding agent built from scratch in the earlier lab: read, search, edit, write
  and run, and the loop. Plain HTTP to the Gemini API, no SDK.
- The tasks are ten small changes to a shop's checkout code, in four slices. Each task has
  held-out tests that the agent never sees.
- The instructions are in [LAB.md](LAB.md).

```bash
uv sync
cp .env.example .env              # your Gemini key
uv run check_suite.py             # every task can fail, and can pass
uv run run_one.py tax-rounding    # one run, every turn shown, then its score
uv run run_suite.py --label v1 --runs 3
uv run report.py results/v1.jsonl
```
