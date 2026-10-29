In my plugin `eu-product-compliance`, case `accident-notify` has an `llm` grader `accident-notify-belgium-sbg`; I ran the suite with `--judge-model sonnet`. On W/OUT run 2 that grader got FAIL FAIL FAIL, although the stored answer (the grader's `evidence` field under `cases[].arms.without[1]` in `aggregate-result.json`) says, among other things:

"Under GPSR Article 20 the manufacturer must notify the accident without undue delay through the Safety Business Gateway, selecting Belgium as the Member State where the accident occurred."

That is what the rubric asks for. The rubric is long (about 9,800 characters) and the answer about 5,800. In the JSON and in report.html the only explanation text for that grader is `judge votes: FAIL FAIL FAIL`.

To understand the verdict I re-ran the judge myself: `claude -p --model sonnet --tools ""` with the same rubric and the same answer pasted in. It answered PASS with a paragraph of reasoning. With `CLAUDE_CODE_DISABLE_THINKING=1` set it was PASS again.

There are 10 such disagreeing cells in this suite, all on the W/OUT side. Which verdict should I trust for the Δ I publish? Where can I find the judge's reasoning? And give me a step-by-step procedure that reproduces the eval tool's judge faithfully so I can check the other cells.
