# Benchmark: plugin-eval-field-notes

Measured 2026-10-29 with Claude Code 2.1.312. Cases, graders and the skill were committed together in our private working repository at commit `29e61f4` before any run; [prereg-sha256.txt](prereg-sha256.txt) lists the SHA-256 of every registered file (paths are the private tree's), so you can check the copies here are the ones that were run. The control's source text is described in [SOURCE.md](SOURCE.md) and not copied.

## Arms

All arms: model `claude-sonnet-5-5`, no tool grant, 3 runs per case.

- with — the plugin in [plugins/plugin-eval-field-notes](../../plugins/plugin-eval-field-notes/), invoked naturally (no `/name` in the prompt); the skill was invoked in 15 of 15 runs on each set.
- without — same model, no plugin.
- control — same model, no plugin, the documents in SOURCE.md appended after the request.

Two case sets of 5, each written by a different author: gate (`cases/gate/`) and confirmation (`cases/confirm/`), the confirmation author not having seen the gate set. Graders were written blind from the request and a reference answer (`정답.md` in each case folder; `출처.md` names the measured runs the case was built from). Score per run = weighted share of graders passed; case score = mean of its runs.

## Results

Paired per-case difference, case-cluster bootstrap 50,000 resamples (seed 20261028), 95% interval.

| Grader | Set | with | control | without | with − control | with − without | control − without |
|---|---|---|---|---|---|---|---|
| Sonnet (the tool's judge) | gate | 0.825 | 0.183 | 0.249 | +0.64 [+0.54, +0.77] | +0.58 [+0.35, +0.80] | −0.07 [−0.22, +0.08] |
| Sonnet | confirmation | 0.848 | 0.593 | 0.390 | +0.26 [+0.15, +0.42] | +0.46 [+0.18, +0.69] | +0.20 [+0.00, +0.38] |
| Opus (regrade of the same answers) | gate | 0.933 | 0.331 | 0.273 | +0.60 [+0.40, +0.83] | +0.66 [+0.44, +0.86] | +0.06 [+0.01, +0.15] |
| Opus | confirmation | 0.956 | 0.676 | 0.562 | +0.28 [+0.19, +0.43] | +0.39 [+0.18, +0.59] | +0.11 [−0.06, +0.28] |

Win rule, fixed before the runs: with − control has a lower bound above zero on both sets, under both graders. Met. Comparison with other public skills for the same task is not run yet. No case was lost by the skill against the control under either grader.

Judge-sensitive. Agreement between the two graders on criterion verdicts, per run: with/gate 0.907, control/gate 0.827, with/confirmation 0.833, control/confirmation 0.880. All four are below the 0.95 we set before these runs for not flagging a run (a threshold not yet validated). Most disagreements we saw in earlier runs were a Sonnet FAIL that Opus passed. Neither grader was checked against human labels.

## Files

| File | What it is |
|---|---|
| `results/01-with-gate-29e61f4.json`, `03-with-confirm-…` | raw `claude plugin eval` output, with and without arms (local paths replaced by `<local>` by the export) |
| `results/02-control-gate-29e61f4.json`, `04-control-confirm-…` | raw output of the control arm, appended source text omitted (SOURCE.md) |
| `judges/*--opus.json` | the Opus regrade: per-criterion verdicts and agreement with the original grader |
| `cases/gate/`, `cases/confirm/` | the registered cases: `prompt.md`, `graders/`, reference answer, provenance |

Cost as printed by the tool (list-price estimate, overcounted under `-j` concurrency — the skill's own section 4): with/gate $17.13, control/gate $11.44, with/confirmation $18.21, control/confirmation $10.41; after removing the concurrency overcount of the judge share, $8.19, $5.95, $7.70 and $5.55. The Opus regrade was reported at $117.04 in total, not corrected (no correction is available for that path), so it is an overestimate.

## Rerun

```
python benchmarks/plugin-eval-field-notes/rerun.py source            # docs page + CLI help -> rerun-out/source.md, hash checked
python benchmarks/plugin-eval-field-notes/rerun.py run all --dry-run # print the four commands
python benchmarks/plugin-eval-field-notes/rerun.py run all           # gate and confirmation, with/without and control
```

`source` rebuilds the control's text in the measured layout; on 2026-10-29 with Claude Code 2.1.312 it matched the registered SHA-256 byte for byte, and the control prompts it builds are identical to the 10 measured ones. `run` calls `claude plugin eval` with the measured settings and writes raw JSON to `rerun-out/`. It does not compute intervals; the per-case scores are in the JSON. For the with/without arms alone, `claude plugin eval plugins/plugin-eval-field-notes --runs 3 --judge-model sonnet` also works (`evals/` holds the same prompts and graders as `cases/`).
