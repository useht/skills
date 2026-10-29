My plugin `contract-redline` has 7 cases, each with two `llm` graders. On a Max subscription I ran:

```
claude plugin eval . --runs 3 --ablation with-without --judge-model sonnet --allow-tools Bash Write Edit -j 8
```

Summary line: `7 case(s) · mean Δ +0.07 · 1271s · $15.49`. The same command the next day ended with `$15.43`. In `aggregate-result.json`, `"costUsd": 15.49`. My Anthropic console shows no charge for either day.

I want to use this number in three places and need to know whether it is safe:
(a) README: "a full run of this suite costs about $15";
(b) CI: `--max-cost-usd 20`;
(c) a note to my team that one agent run costs about $15.49 / 42 ≈ $0.37.

Is the reported figure the actual cost of the run? If not, what exactly is off, in which direction, and why? What should I run to get a number I can publish? Give me the concrete command and the exact sentence I should put in the README.
