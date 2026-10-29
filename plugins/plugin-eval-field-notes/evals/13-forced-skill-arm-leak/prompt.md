I'm benchmarking the skill `changelog` in my plugin `relnotes` (Claude Code 2.1.312) and want three numbers: natural (the user phrases the request, the skill may or may not fire), forced (the skill definitely fires), and no skill. `claude plugin eval --help` shows no option to force a skill, so I made a second copy of each case whose prompt starts with `/changelog` and ran the default two-arm suite:

```
claude plugin eval . --runs 3 --judge-model sonnet --no-publish
```

The forced cases came out WITH 1.00, W/OUT 0.00, Δ +1.00 on every case. In the report every W/OUT reply says something like "The /changelog command is not installed in this session", while the with-arm replies clearly follow the skill (my regex grader for the skill's section header passes). But my `graders/skill-fired.md` (`type: tool_used`, `tool: Skill`, `input_match` on `changelog`) shows `passed: false` in the with-arm of every forced run, so I cannot tell from the report how many forced runs actually invoked the skill.

What I need: (1) the command(s) to run the forced arm correctly and which numbers to pair for forced-vs-no-skill, (2) how to count skill invocations in the forced runs from the results or trace, and (3) whether the +1.00 is usable at all.
