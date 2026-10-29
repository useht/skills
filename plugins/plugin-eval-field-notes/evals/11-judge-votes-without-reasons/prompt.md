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
