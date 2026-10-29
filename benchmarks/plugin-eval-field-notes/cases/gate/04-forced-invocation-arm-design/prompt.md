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
