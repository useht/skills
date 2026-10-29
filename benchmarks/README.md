# Benchmarks

Every skill here is measured in three arms on cases and graders committed before the first run: with the skill, without it, and a control that gets no skill but has the documents the skill relies on pasted after the request. A skill ships only if it beats the control, not just the bare model.

## Method

- Runner: `claude plugin eval`, 3 runs per case, no tool grant unless a case needs one.
- Grader: the tool's LLM judge (Claude Sonnet). The same stored answers are then regraded by Claude Opus; a claim stands only if it holds under both.
- Score: weighted share of graders passed per run, averaged per case. Differences are paired per case with a case-cluster bootstrap (50,000 resamples, seed 20261028) 95% interval.
- Two case sets per skill, gate and confirmation, by different authors; the confirmation author does not see the gate set.
- Release rule: with − control lower bound above zero on both sets under both graders. Runs where the two graders agree on fewer than 95% of criterion verdicts are marked judge-sensitive.

## All results

| Skill | Date | Set | with | control | Δ with − control (95% CI) | Outcome |
|---|---|---|---|---|---|---|
| [plugin-eval-field-notes](plugin-eval-field-notes/README.md) | 2026-10-29 | gate | 0.825 | 0.183 | +0.64 [+0.54, +0.77] | passes (Opus: +0.60 [+0.40, +0.83]); judge-sensitive |
| plugin-eval-field-notes | 2026-10-29 | confirmation | 0.848 | 0.593 | +0.26 [+0.15, +0.42] | passes (Opus: +0.28 [+0.19, +0.43]); judge-sensitive |
| kr-vat-filing | 2026-10-28 | gate / confirmation | 1.000 / 1.000 | 0.976 / 0.942 | +0.02 / +0.06 | withdrawn ([REJECTED.md](REJECTED.md)) |
| kr-payroll | 2026-10-28 | gate / confirmation | 1.000 / 0.978 | 1.000 / 0.990 | +0.00 / −0.01 | withdrawn |
| eu-product-compliance | 2026-10-28 | gate / confirmation | 0.838 / 0.884 | 0.928 / 0.893 | −0.09 / −0.01 | withdrawn |

The withdrawn skills' cases and raw results are not in this repository; their numbers are reported as measured.

## Limits

Graders are models, not people, and they disagree on 9 to 17 percent of verdicts in the runs above. Five cases per set is small: the intervals are wide and a different case author could move them. The skills answer from what we measured on Claude Code 2.1.309 to 2.1.312.
