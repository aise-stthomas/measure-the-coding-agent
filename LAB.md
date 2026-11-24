# Lab: measure the coding agent

The coding agent from the earlier lab, measured. Fourteen tasks, each a small change to a shop's
checkout code. Every run gets a fresh sandbox, and every run is scored from the state it leaves
behind, with tests it never saw.

## Setup

```bash
uv sync
cp .env.example .env          # paste your Gemini key
```

A suite is many runs: 14 tasks × 3 runs is 42 runs of up to 20 model calls each. If your key is
on the free tier, its daily limit can stop a suite partway. Use `--runs 2`, or `--tasks` to run a
few tasks, or put a small amount of credit on your key with a budget alert set first. A run that
fails on the API is recorded as a failed run with its error, not dropped.

## Where everything is

| Path | What it is |
|---|---|
| `src/agent/` | the loop, the model (and `ReplayModel`), the trace, the toolbox |
| `src/coder/tools.py` | the agent's tools: read a file, search, edit by exact string, write a file, run a command |
| `src/coder/instructions.py` | three versions of the instructions: v1, v2 and v3 |
| `data/base-repo/` | the shop's code, its tests and its project file, `AGENT.md` |
| `data/tasks/<name>/` | one task: `task.toml` (slice, request, the change that breaks it) and its held-out tests |
| `src/suite/sandbox.py` | builds a fresh sandbox for one run |
| `src/suite/score.py` | scores the state a run leaves behind, and counts violations |
| `src/suite/stats.py` | the Wilson interval, pass@k and pass^k, total variation distance, the paired bootstrap |
| `check_suite.py` | checks every task before you trust the suite |
| `run_one.py` | one run, every turn shown, then its score |
| `run_suite.py` | every task, k runs each, one record per run in `results/<label>.jsonl` |
| `report.py`, `checks.py`, `compare.py`, `replay.py` | what a suite reports, checks on the path, two versions, replay |
| `rescore.py` | scores a suite's runs again from the repositories they left in `work/`, after you change the scorer |

## Section 1 · Check the suite

```bash
uv run check_suite.py
```

For every task, the starting state must fail and a reference solution must pass.

1. Open `data/tasks/tax-rounding/`. Read `task.toml` and `test_hidden.py`. What does the
   held-out test check that the repository's own tests do not?
2. Break a task on purpose: change one of its held-out tests so that it expects the wrong
   value, and run `check_suite.py` again. What does it report? Put the test back.
3. Read the two blocked tasks. What is the right end state for each, and why does the check for
   them not run any tests?

## Section 2 · One run, scored

```bash
uv run run_one.py tax-rounding
uv run run_one.py tax-rate
```

1. For the first run: which turn told you the run had worked? Is that what the score used?
2. Read `src/suite/score.py`. Name every place the run's final answer is used.
3. Look at the run's repository with `git -C work/one/tax-rate-1 diff`. What did the agent do
   with a request that leaves out the new rate?

## Section 3 · The suite

```bash
uv run run_suite.py --label v1 --runs 3
uv run report.py results/v1.jsonl
```

1. Which slice is weakest? Write its rate with its interval, not the rate alone.
2. Find a task whose pass@3 and pass^3 differ. Say in one sentence what each number means for
   that task.
3. The report counts violations. How many runs would you need, with none seen, before the top
   of the interval is under 5%?
4. Read the step and cost lines. What is the cost per successful task, and why is it larger than
   the cost per run?

## Section 4 · The path, and the scorer

```bash
uv run checks.py results/v1
```

1. Pick a run that passed and that a check flagged. Read its trace in `results/v1/<task>-<run>.json`.
   Would you accept how it got there?
2. Write a check of your own in `checks.py` and add it to `CHECKS`. Ideas: it read a file it
   never used, its last test run failed but its answer says the tests pass, it changed a file
   outside `src/`.
3. Which of your check's hits were real? A check is an instrument too: count the ones it got
   wrong.
4. Find the runs the report counts as `test_weakened` and read each one's diff with
   `git -C work/v1/<task>-<run> diff tests`. Is every one a violation? Change the check in
   `src/suite/score.py` if you disagree, then `uv run rescore.py results/v1.jsonl`: the runs
   are scored again from what they left behind, without running the agent.

## Section 5 · Two versions

```bash
uv run run_suite.py --label v2 --version v2 --runs 3
uv run run_suite.py --label v3 --version v3 --runs 3
uv run compare.py results/v1.jsonl results/v2.jsonl
uv run compare.py results/v1.jsonl results/v3.jsonl
```

Read the three versions in `src/coder/instructions.py` first.

1. Would you ship v2? Give the numbers that decide it, each with its interval.
2. v3 adds one sentence for the blocked slice. Did the blocked slice change? Did any other slice?
3. Why does `compare.py` compare task by task and not the two overall rates?

## Section 6 · A new model

```bash
uv run run_suite.py --label new-model --model gemini-3.5-flash-lite --runs 3
uv run compare.py results/v1.jsonl results/new-model.jsonl
```

Nothing in the code changed, only the model.

1. Read the tool-call distribution for each. Which tool's share moved the most?
2. Is the distance between the two larger than the noise floor printed under it? What would you
   conclude if it were not?
3. Which of these numbers could you watch in production, where there are no held-out tests?

## Section 7 · Faults and replay

```bash
uv run run_suite.py --label faults --fault-rate 0.3 --runs 3
uv run compare.py results/v1.jsonl results/faults.jsonl
uv run replay.py results/v1
```

`--fault-rate 0.3` makes 3 in 10 shell commands fail with "the sandbox did not respond",
seeded so that a run's faults are the same each time.

1. How much did success drop, and how many more steps did a run take? Find a run that did
   something other than retry after a fault.
2. `replay.py` reruns every recorded run with no model and no key. Change one tool in
   `src/coder/tools.py` (for example, cut `OUTPUT_LIMIT` to 200) and replay again. What does
   replay catch, and what can it never tell you?
