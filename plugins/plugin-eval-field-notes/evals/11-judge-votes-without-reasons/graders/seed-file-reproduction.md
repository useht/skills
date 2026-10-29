---
type: llm
weight: 1
---
If the user wants to reproduce the eval tool's verdict on a saved reply, the faithful route is to put the saved reply in a case workspace as a file and judge it through the eval tool itself with a grader `focus: { source: file, path: seed.md }` (equivalent wording accepted), which returned the same three FAIL votes.

PASS: The reply offers reproducing the verdict by placing the saved reply as a file in the case workspace and grading it with the eval tool's own judge via a file-sourced `focus`/target.
FAIL: The reply offers no eval-tool-based reproduction route, or proposes only external re-judging (`claude -p`, API call, another script).

판정은 아래 사용자 요청 원문과 대조한다.

[사용자 요청 원문]
I ran my plugin's suite with `claude plugin eval . --runs 3 --judge-model sonnet --json results.json --no-publish` (Claude Code 2.1.312, Linux). Case `menu-rewrite` came out WITH 0.33 / W/OUT 1.00 and I need to know why the judge failed the with-arm runs on the `no-fake-source` grader. `results.json` is 5.3 MB. One with-arm run, trimmed:

```json
{"cases":[{"name":"menu-rewrite","arms":{"with":[{"error":null,"score":0.5,"graderResults":[
  {"name":"no-fake-source","passed":false,"scored":true,"judgeVotes":["FAIL","FAIL","FAIL"],
   "explanation":"judge votes: FAIL FAIL FAIL","evidence":"<the run's full final reply, about 5,800 characters>"},
  {"name":"keeps-tone","passed":true,"scored":true,"judgeVotes":["PASS","PASS","PASS"],
   "explanation":"judge votes: PASS PASS PASS","evidence":"<the same 5,800 characters again>"}
]}]}}]}
```

The docs say a failed grader is shown with its explanation plus the judge's votes and evidence, so I opened `report.html` too, but I cannot find a single sentence from the judge about why it voted FAIL. My plan was to feed each `evidence` text and the rubric to `claude -p --model sonnet` and ask it to explain its verdict.

Please tell me (1) where the judge's reasoning is for these runs, or, if my `claude -p` plan is wrong, the right way to find out why they failed, and (2) a short Python script that writes one Markdown file per case/arm/run with every grader's votes and the final reply written out once, not once per grader, so I can read the failed runs side by side.

[공개 정답 원문 발췌]
# Ground truth — 11-judge-votes-without-reasons

## Key facts a correct answer must contain

1. The result JSON (and the report rendered from it) records, per grader and per run, only the three votes (`judgeVotes`) and an `explanation` that is nothing more than "judge votes: …"; the judge's reasons are not stored anywhere in the output, so no field, report section, or flag yields them for these runs. [K0-dc11561567] [K0-a446e4e46d] [K0-83124cdcc1]
2. The `evidence` field is the run's final reply and the same text is repeated under every grader of that run (measured: 4.66 MB of a 5.3 MB file was this repetition, identical across graders in all 366 runs), so the script must take the reply once per run and dedupe rather than copy it per grader. [K0-5f501a82d7] [K0-ee431a12e2] [K0-1a53242e1b]
3. The way to find out why a run failed is to re-read the `evidence` text against the grader's rubric yourself, blind to which arm it came from and applied identically to both arms (the recorded practice: mix with/without replies and re-read the cells where the verdict is disputed). [K0-dc517e4f1a] [K0-83124cdcc1] [K0-1a53242e1b]
4. Re-judging with `claude -p` does not reproduce the eval tool's judge: the tool's judge call runs with thinking disabled and `claude -p` cannot be made to (measured agreement 0.72 over 36 grader×run cells, every disagreement being a FAIL that `claude -p` turned into PASS); a faithful reproduction is to put the saved reply in a case workspace as a file and judge it through the eval tool with `focus: { source: file, path: seed.md }`, which returned the same three FAIL votes. [K0-8c5c9fcd98] [K0-51517dfab6] [K0-633ba95907]

## A correct answer must NOT

- Claim the judge's reasoning text exists in `results.json` or `report.html` (for example under `explanation`) or tell the user to look harder for it there.
- Present `claude -p` re-judging as a faithful reproduction of the eval tool's verdict.
- Produce a script that writes the `evidence` once per grader (duplicating the reply) instead of once per run.
