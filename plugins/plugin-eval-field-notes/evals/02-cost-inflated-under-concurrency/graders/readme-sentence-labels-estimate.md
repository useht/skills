---
type: llm
weight: 1
---
The user asks for the exact README sentence. A correct reply proposes a sentence that labels the figure as a list-price estimate (usage, not a charge) measured at `-j 1`, leaving the number to be filled after that run; a `-j 8` figure, if quoted at all, is only an upper bound whose judge share is inflated by concurrency.

PASS: The proposed README sentence describes the number as an estimate at list price measured at `-j 1` (with a placeholder or the value to be filled in after the `-j 1` run), and does not state the `-j 8` figure as the suite's cost except as an explicitly inflated upper bound.
FAIL: The proposed sentence says "about $15" (or any `-j 8`-derived number) as the cost of a run, or omits that it is an estimate measured at `-j 1`, or no README sentence is given.

판정은 아래 사용자 요청 원문과 대조한다.

[사용자 요청 원문]
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

[공개 정답 원문 발췌]
# Ground truth — 02-cost-inflated-under-concurrency

## Key facts a correct answer must contain

1. The figure is a list-price estimate of the model calls, not a charge: on a claude.ai subscription nothing is billed separately, the calls draw down plan usage, which is why the console shows no charge. [doc: Requirements] [K0-fd42ca560e]
2. Under concurrency (`-j` greater than 1) the judge portion is over-counted: the tool records each run's judge cost as the difference of a global running total (`judgeCostUsd` = total-now minus total-at-start), so judge calls of runs executing at the same time are added into each other's figure; measured on the same two judge items, `-j 1` reported $0.079 and `-j 2` $0.147 (about 1.86x). [K0-dea4b2d738] [K0-bfa92c4008]
3. Therefore the `-j 8` totals ($15.43–15.49) are inflated upward on the judge share and cannot be published as the suite's cost or divided into a per-run cost; the true estimate is unknown until measured at `-j 1`. [K0-dea4b2d738] [K0-7eba9c130c] [K0-a4bcfdeec3]
4. To get a publishable number, re-run with `-j 1` (the full suite, or a `--case`/`--runs 1` sample scaled with that caveat stated) and report that figure as "a list-price estimate measured at `-j 1`"; a `-j 8` figure may only be quoted as an upper bound whose judge share is inflated by concurrency. [K0-dea4b2d738] [doc: Requirements]

## A correct answer must NOT

- Present $15.49 as the actual money spent, or as a number independent of `-j`.
- Compute a per-run cost by dividing the `-j 8` total (the $0.37 figure).
- Explain the empty console as a billing delay or bug rather than as subscription usage.
