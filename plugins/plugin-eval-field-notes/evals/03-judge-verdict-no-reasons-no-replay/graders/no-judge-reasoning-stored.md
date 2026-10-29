---
type: llm
weight: 2
---
The user asks where the judge's reasoning can be found. A correct reply must say the eval tool stores no judge reasoning: per grader the result keeps only `evidence` (the final answer) and `judgeVotes` (three votes), `explanation` is just the "judge votes: ..." string, and report.html has nothing more — so the reasoning cannot be recovered after the fact.

PASS: The reply states that no judge reasoning is stored anywhere in `aggregate-result.json` or report.html (only votes and the evidence text exist) and that it cannot be recovered from the finished run.
FAIL: The reply says the reasoning exists in report.html, `aggregate-result.json`, another field, a flag, a log or a verbose mode, or tells the user to look harder in those outputs.

판정은 아래 사용자 요청 원문과 대조한다.

[사용자 요청 원문]
In my plugin `eu-product-compliance`, case `accident-notify` has an `llm` grader `accident-notify-belgium-sbg`; I ran the suite with `--judge-model sonnet`. On W/OUT run 2 that grader got FAIL FAIL FAIL, although the stored answer (the grader's `evidence` field under `cases[].arms.without[1]` in `aggregate-result.json`) says, among other things:

"Under GPSR Article 20 the manufacturer must notify the accident without undue delay through the Safety Business Gateway, selecting Belgium as the Member State where the accident occurred."

That is what the rubric asks for. The rubric is long (about 9,800 characters) and the answer about 5,800. In the JSON and in report.html the only explanation text for that grader is `judge votes: FAIL FAIL FAIL`.

To understand the verdict I re-ran the judge myself: `claude -p --model sonnet --tools ""` with the same rubric and the same answer pasted in. It answered PASS with a paragraph of reasoning. With `CLAUDE_CODE_DISABLE_THINKING=1` set it was PASS again.

There are 10 such disagreeing cells in this suite, all on the W/OUT side. Which verdict should I trust for the Δ I publish? Where can I find the judge's reasoning? And give me a step-by-step procedure that reproduces the eval tool's judge faithfully so I can check the other cells.

[공개 정답 원문 발췌]
# Ground truth — 03-judge-verdict-no-reasons-no-replay

## Key facts a correct answer must contain

1. The eval tool stores no judge reasoning: per grader the result keeps `evidence` (the final answer) and `judgeVotes` (three votes), and `explanation` is only the "judge votes: ..." string; report.html has nothing more, so the reasoning cannot be recovered after the fact. [K0-a446e4e46d] [K0-dc11561567] [K0-c11d398397]
2. `claude -p` does not reproduce the eval judge: the tool's judge call runs with thinking disabled, while `claude -p` still spends thinking tokens (174–364 measured) even with `CLAUDE_CODE_DISABLE_THINKING=1`, `alwaysThinkingEnabled: false` and `MAX_THINKING_TOKENS` removed; measured agreement was only 0.72 over 36 grader×run cells, with all 10 mismatches being W/OUT FAIL → PASS — so the `claude -p` PASS says nothing about the eval judge. [K0-51517dfab6] [K0-8c5c9fcd98]
3. The faithful reproduction is to feed the stored answer back to the eval tool itself: put the exact `evidence` text into a case's workspace as a file (e.g. `seed.md`, written by a `context.scaffold_script` run with `--scaffold`) and grade it with the same rubric using `focus: { source: file, path: seed.md }`; this reproduced the original FAIL FAIL FAIL on the identical answer, and over the whole case the same judge model agreed 0.97 by this route. [K0-8c5c9fcd98] [K0-633ba95907] [doc: Seed the workspace or conversation] [doc: What a grader can look at]
4. The no-thinking judge is suspected of grading the W/OUT arm harshly on long rubrics (9,500–10,000 characters) and long answers, which inflates Δ: a thinking-enabled sonnet passed this cell, and an opus re-judge flipped 6 of its 7 mismatches on the W/OUT side from FAIL to PASS; so the published Δ must carry this as a stated risk, and disagreeing cells are re-read blind with both arms treated alike (hide which arm, shuffle), not only the W/OUT ones. [K0-f451780ea5] [K0-633ba95907] [K0-dc517e4f1a] [K0-b62db52986]

## A correct answer must NOT

- Say that report.html or `aggregate-result.json` contains the judge's explanation or reasoning for `llm` graders (beyond the votes and the evidence).
- Treat the `claude -p` PASS as a faithful reproduction, or propose more `claude -p` flags/environment variables as the way to reproduce the judge.
- Propose correcting only the W/OUT cells (one-sided re-reading) or silently replacing the original verdicts with the `claude -p` ones.
