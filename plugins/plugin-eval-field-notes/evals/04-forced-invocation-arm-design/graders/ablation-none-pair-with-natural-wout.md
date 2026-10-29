---
type: llm
weight: 3
---
The user's step 3 runs the forced cases with the default ablation and compares forced Δ with natural Δ. A correct reply must say forced cases cannot run two-arm: the without-arm receives the same `/ledgerly:close-month ...` text, the skill name leaks into the no-plugin session, and it answers that the command is not installed — so a Δ from a forced case is meaningless. The forced cases must run with `--ablation none` (e.g. `claude plugin eval . --case 'forced/*' --runs 3 --ablation none --judge-model sonnet`) and their scores paired with the W/OUT scores of the natural-prompt suite.

PASS: The reply rejects the default with-without ablation for forced cases because the slash text leaks into the no-plugin arm, gives a command with `--ablation none` for the forced cases, and pairs the forced (with-arm) scores with the natural suite's W/OUT scores as the baseline.
FAIL: The reply endorses running forced cases under the default ablation or interprets a forced-case Δ, says the `/name` text is harmless to the no-plugin arm, omits `--ablation none`, or pairs the forced numbers with the forced cases' own W/OUT instead of the natural W/OUT.

판정은 아래 사용자 요청 원문과 대조한다.

[사용자 요청 원문]
My plugin `ledgerly` has one skill, `close-month`. Natural triggering is flaky: over 4 cases × 3 runs the `skill-fired` grader passed 7/12. Its file is:

```
---
type: tool_used
tool: Skill
input_match: '"skill"\s*:\s*"(?:[\w-]+:)?close-month"'
---
```

Besides fixing the description, I want a ceiling number: what the skill scores when it is definitely invoked. I read `claude plugin eval --help` (2.1.312) and found no flag that forces a skill, so my plan is:

1. Copy the 4 cases to `evals/forced/<case>/` and change each prompt body to `/ledgerly:close-month ` followed by the same text as the natural case.
2. Keep both graders (`criteria.md`, type `llm`, and the `skill-fired.md` above).
3. Run `claude plugin eval . --case 'forced/*' --runs 3 --judge-model sonnet` with the default ablation, then compare the forced Δ with the natural Δ.

Is this plan right? Give me the exact command(s) to run, tell me how I will know in each forced run that the skill really was invoked, and tell me how to pair the forced numbers with a baseline.

[공개 정답 원문 발췌]
# Ground truth — 04-forced-invocation-arm-design

## Key facts a correct answer must contain

1. Correct premise: `claude plugin eval` 2.1.312 has `--model`, `--judge-model`, `--runs`, `--case`, `--json` but no option that forces a skill; writing the `/plugin:skill` form into the prompt body is the way, and it does invoke the skill in the with-arm (measured: the with-arm reply contained the skill's instruction tokens). [K0-eb000acfb4] [K0-9f3c9c0606]
2. Forced cases must not run two-arm: the without-arm receives the same `/ledgerly:close-month ...` text, the skill name leaks into the no-plugin session, and it answers that the command is not installed in this session — so a Δ from a forced case is meaningless. Run them with `--ablation none` (e.g. `claude plugin eval . --case 'forced/*' --runs 3 --ablation none --judge-model sonnet`) and pair their scores with the W/OUT scores of the natural-prompt suite. [K0-9f3c9c0606]
3. The `tool_used: Skill` grader will not fire for a slash-invoked skill: the transcript contains no Skill tool call (the slash command is expanded in place), so invocation is counted from the run's first `system/init` line, whose `skills` / `slash_commands` lists `ledgerly:close-month` (or `close-month`) — read from the kept run transcripts (`--keep-temp`) or trace, not from the `skill-fired` grader. [K0-38e8f21712]
4. A `regex` grader over the reply (default target `last_message`) that matches a phrase unique to the skill's instructions is a cheap confirmation that the skill content was used in a forced run. [K0-9f3c9c0606] [K0-38e8f21712] [doc: What a grader can look at]
5. Expect the forced ceiling to be close to the natural with-arm number rather than far above it: measured forced invocation 21/21 with scores of the same shape as natural (0.828 vs 0.838; 0.934 vs 0.884). [K0-cb995b3ced]

## A correct answer must NOT

- Report or interpret a Δ produced by running forced cases under the default `with-without` ablation.
- Rely on `tool_used: Skill` (or `tool_order` on Skill) to count invocations in forced runs, or tell the user the 7/12 grader will now read 12/12.
- Claim a `--skill`/force flag exists, or that the `/name` text is harmless to the no-plugin arm.
