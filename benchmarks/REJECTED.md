# Rejected

Skills we built or started and did not release, with the numbers and the bar as they stood at the time. Append only: rows are never edited or removed; a later remeasurement gets a new row.

| Date | Skill | What it did | What was measured | Bar at the time | Why it stopped |
|---|---|---|---|---|---|
| 2026-10-28 | kr-vat-filing | Korean VAT final return for a sole proprietor | Gate: with 1.000, model given the statutes 0.976, Δ +0.02 [+0.00, +0.07]. Confirmation: 1.000 vs 0.942, Δ +0.06 [+0.00, +0.14]. 7 cases × 3 runs each | On both sets: at least 0.1 above the model without the skill, above the model given the documents, and that document control still leaving at least 0.2 of error to remove | The control left 0.024 and 0.058 of error: the gain was the statute text, not the skill |
| 2026-10-28 | kr-payroll | Korean social-insurance deductions to the won | Gate: 1.000 vs 1.000, Δ +0.00 [+0.00, +0.00]. Confirmation: 0.978 vs 0.990, Δ −0.01 [−0.04, +0.02] | same | The model given the statutes, notices and agency pages did the same calculation |
| 2026-10-28 | eu-product-compliance | EU product safety and recall steps from the statute | Gate: 0.838 vs 0.928, Δ −0.09 [−0.26, +0.05]. Confirmation: 0.884 vs 0.893, Δ −0.01 [−0.06, +0.06] | same | Below the control: the skill narrowed answers to the recall frame and missed duties the model found in the regulation text |
| 2026-10-28 | effect-ts-current | Effect (TypeScript) v4 API names | With − without: gate +0.184 (0.939 vs 0.755), confirmation +0.040 (0.973 vs 0.933) | at least 0.1 above the model without the skill on both sets | In repositories where effect is installed the model reads `node_modules` and gets the names itself; the gain was only before install |
| 2026-10-28 | grounded-handoff | Session handoff notes that state only what the log shows | One-run probe, 1 − without on three candidate cells in turn: 0.091, 0.088, 0.077 | before building: a one-run probe leaving at least 0.1 of error, then a 3-run gate leaving at least 0.2 | The model without a skill already passed; not built |

From 2026-10-29 the release bar also requires the paired gain over the document control to have a 95% interval above zero on both case sets, under both graders (Sonnet and Opus).
