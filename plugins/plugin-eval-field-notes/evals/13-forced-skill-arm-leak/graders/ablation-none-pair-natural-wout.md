---
type: llm
weight: 3
---
The user asks for the command(s) to run the forced arm correctly and which numbers to pair for forced-vs-no-skill. A correct reply runs the forced cases with `--ablation none` (with-arm only, e.g. `claude plugin eval . --case '<forced cases>' --runs 3 --ablation none --judge-model sonnet --no-publish`) and pairs their score with the without-arm score of the naturally phrased cases (the natural run's W/OUT).

PASS: The reply gives a forced-case command using `--ablation none` and says the forced score is paired with the natural-prompt suite's W/OUT score as the no-skill number.
FAIL: The reply keeps the default two-arm ablation for the forced cases, omits `--ablation none`, or pairs the forced score with the forced cases' own W/OUT instead of the natural W/OUT.

판정은 아래 사용자 요청 원문과 대조한다.

[사용자 요청 원문]
I'm benchmarking the skill `changelog` in my plugin `relnotes` (Claude Code 2.1.312) and want three numbers: natural (the user phrases the request, the skill may or may not fire), forced (the skill definitely fires), and no skill. `claude plugin eval --help` shows no option to force a skill, so I made a second copy of each case whose prompt starts with `/changelog` and ran the default two-arm suite:

```
claude plugin eval . --runs 3 --judge-model sonnet --no-publish
```

The forced cases came out WITH 1.00, W/OUT 0.00, Δ +1.00 on every case. In the report every W/OUT reply says something like "The /changelog command is not installed in this session", while the with-arm replies clearly follow the skill (my regex grader for the skill's section header passes). But my `graders/skill-fired.md` (`type: tool_used`, `tool: Skill`, `input_match` on `changelog`) shows `passed: false` in the with-arm of every forced run, so I cannot tell from the report how many forced runs actually invoked the skill.

What I need: (1) the command(s) to run the forced arm correctly and which numbers to pair for forced-vs-no-skill, (2) how to count skill invocations in the forced runs from the results or trace, and (3) whether the +1.00 is usable at all.

[공개 정답 원문 발췌]
# Ground truth — 13-forced-skill-arm-leak

## Key facts a correct answer must contain

1. `claude plugin eval` 2.1.312 has no option that forces a skill to be invoked; starting the prompt with `/skill-name` is the available route, and it does invoke the skill in the with-arm. [K0-eb000acfb4] [K0-9f3c9c0606]
2. The `/changelog` prompt leaks the skill's name into the without-arm, whose reply only says the command is not installed, so the forced cases' W/OUT 0.00 and Δ +1.00 measure nothing about the skill and must be discarded. [K0-9f3c9c0606]
3. Run the forced cases with `--ablation none` (with-arm only), and pair their score with the without-arm score of the naturally phrased cases (the natural run's W/OUT). [K0-9f3c9c0606]
4. A slash invocation leaves no `Skill` tool call in the transcript (the slash is expanded), so a `tool_used: Skill` grader cannot count it; count a forced run as invoked when the first `system/init` line of its transcript lists the skill in `skills`/`slash_commands` as `relnotes:changelog` (or `changelog`). [K0-38e8f21712]
5. The regex grader's default target is `last_message`, the final reply, so a passing header regex shows the skill's output reached the reply; it is a result check, not an invocation count. [K0-38e8f21712] [doc: What a grader can look at]

## A correct answer must NOT

- Report the forced cases' Δ +1.00 as the skill's effect, or use the slash-prompt without-arm as the "no skill" number.
- Claim a flag, frontmatter field, or `allowed_tools` setting exists that forces skill invocation.
- Propose fixing the invocation count by making `tool_used: Skill` scored (`arm: both`), since a slash run produces no Skill call for it to count.
