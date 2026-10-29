---
type: llm
weight: 2
---
Six rubrics say "compare the reply with the user's original note; FAIL if any fact was added", and on case 01 the with-arm got 1/3 vs W/OUT 3/3. A correct reply explains that the `llm` judge sees only the final reply (default `focus: last_message`), so those rubrics were judged without the note — correct, note-grounded content was read as invented — and the fix is to paste the request's original note text into those rubrics before re-measuring.

PASS: The reply explains that the judge only sees the final reply and not the original note, links that to the 1/3 vs 3/3 result, and tells the user to put the original note text into those rubrics.
FAIL: The reply does not explain that the judge lacks the note, or proposes a fix other than giving the judge the note text (for example only changing the judge model or re-running).

판정은 아래 사용자 요청 원문과 대조한다.

[사용자 요청 원문]
My plugin `sci-brief` turns a messy research note into a one-page brief. Layout:

```
sci-brief/
├── .claude-plugin/plugin.json
├── skills/sci-brief/SKILL.md        # tells Claude to study examples/ first
├── examples/science/final.txt       # a finished brief shown as the model answer
└── evals/01-science-note/ … 06-…/
```

Case 01's prompt is the raw note that `examples/science/final.txt` was written from, so that file is essentially case 01's expected output. I wrote all rubrics myself. Examples: "PASS if the reply states how many bytes the brief is" (the skill always reports bytes), and six rubrics of the form "compare the reply with the user's original note; FAIL if any fact was added". I ran:

```
claude plugin eval . --runs 3 --judge-model sonnet
```

Result: WITH 0.854, W/OUT 0.726, Δ +0.128. On case 01 the "no new facts" rubric was WITH 1/3, W/OUT 3/3. I did not pass `--keep-temp`.

A reviewer says this is not publishable evidence that the skill helps. I answered that the docs say a run cannot read the eval directory, so there is no leakage. Who is right? Give me a verdict and a concrete list of what to change before I re-measure.

[공개 정답 원문 발췌]
# Ground truth — 05-plugin-example-file-contamination

## Key facts a correct answer must contain

1. Verdict: the reviewer is right — Δ +0.128 (WITH 0.854 / W/OUT 0.726) is not publishable evidence as it stands. [K0-afe8cc2f9b] [K0-a12ba2a051]
2. Isolation hides only the eval directory; the plugin's own files are loaded and readable by the with-arm, so `examples/science/final.txt` holding case 01's answer is a contamination channel, and without `--keep-temp` transcripts there is no way to show the agent did not read it. [K0-afe8cc2f9b] [K0-8f90233376] [doc: How runs are isolated]
3. Rubrics written by the skill author encode the skill's method as correctness (e.g. "states the byte count"), which penalises the without-arm for not following the skill rather than for a worse outcome; rubrics must be rewritten around the user's outcome. [K0-a12ba2a051] [K0-afe8cc2f9b]
4. The `llm` judge sees only the final reply (default `focus: last_message`), so the six "compare with the user's original note" rubrics were judged blind — which is why the with-arm lost 1/3 vs 3/3 on case 01 "no new facts" (correct, note-grounded content was read as invented); paste the request's original text into those rubrics before re-measuring. [K0-8f90233376] [K0-83124cdcc1] [K0-556fdffaf0] [doc: What a grader can look at]
5. Re-measure only after: the example file is removed from the plugin or replaced with content no case uses, the run is made with `--keep-temp` so transcripts can be checked for contamination, an expected result is written down before the run, and a rule exists to re-read disagreeing cells for both arms. [K0-afe8cc2f9b] [K0-dc517e4f1a]

## A correct answer must NOT

- Declare the result clean on the grounds that "the agent can't read the eval directory".
- Accept Δ > 0 by itself as proof the skill helps.
- Offer a judge-model change (`--judge-model`) or more runs as the remedy without the contamination and rubric fixes.
