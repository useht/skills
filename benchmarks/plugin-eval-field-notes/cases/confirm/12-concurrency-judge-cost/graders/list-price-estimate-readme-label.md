---
type: llm
weight: 1
---
Even the `-j 1` figure is a list-price estimate of the model calls; with a subscription login it is drawn from plan usage rather than billed separately. A correct reply tells the user to label the README number that way.

PASS: The reply says the `costUsd` number (even at `-j 1`) is a list-price estimate, that with a subscription it draws on plan usage rather than being a separate charge, and that the README should label it as an estimate.
FAIL: The reply presents the `-j 1` figure as the actual amount billed, or does not tell the user to label it as a list-price estimate.

판정은 아래 사용자 요청 원문과 대조한다.

[사용자 요청 원문]
Our CI job runs `claude plugin eval . --trust-plugin --runs 3 --judge-model sonnet -j 8 --json results.json --no-publish --max-cost-usd 20` on a 7-case suite (Claude Code 2.1.312). The last three runs reported `costUsd` 15.43, 15.47 and 15.49, and the per-run judge cost values inside the JSON look far too large: a run with two `llm` graders shows a judge cost about 7x what I get from list price for six short sonnet calls.

To check, I took a 2-case subset (same prompts, same two graders, same sonnet judge) and ran it twice. With `-j 1` the judge costs across the runs add up to $0.079; with `-j 2` the same work adds up to $0.147. The agent-run part of the cost was about the same both times.

I need two things decided today: (a) the number we put in the README as "cost of one full suite run", with the per-case cost table that goes with it — can I use the 15.4x figures from the -j 8 runs? (b) whether to lower `--max-cost-usd` or `-j` so we stop overspending. Give me the decision with its reason, and the exact command line for whatever calibration run you want me to do before I publish anything.

[공개 정답 원문 발췌]
# Ground truth — 12-concurrency-judge-cost

## Key facts a correct answer must contain

1. Under concurrency the tool attributes a run's judge cost as the difference of a global cumulative cost counter (`judgeCostUsd: dy()-r` in the binary), so judge calls of other runs in flight are counted into it; the judge share of `costUsd` is inflated whenever `-j` is above 1. [K0-dea4b2d738]
2. The measured size of the effect is the user's own: the same two judge items cost $0.079 at `-j 1` and $0.147 at `-j 2` (1.86x), and this is a reporting artifact, not extra model work, so the "overspending" does not exist and lowering `-j` or `--max-cost-usd` to stop it addresses nothing. [K0-dea4b2d738] [K0-bfa92c4008] [K0-e919bd6e8e]
3. The -j 8 figures (15.43–15.49) and any per-case table derived from them cannot be published as the suite's cost; the real figure must be re-measured with `-j 1`, so the calibration command must run at `-j 1` (for example `claude plugin eval . --trust-plugin --runs 3 --judge-model sonnet -j 1 --json results-j1.json --no-publish`). [K0-dea4b2d738] [K0-7eba9c130c]
4. Even the -j 1 figure is a list-price estimate of the calls; with a subscription login it is drawn from plan usage rather than billed separately, and the README must label it that way. [doc: Requirements] [K0-fd42ca560e]

## A correct answer must NOT

- Approve publishing the -j 8 `costUsd` (or per-case costs computed from it) as the suite's cost.
- Explain the -j 2 vs -j 1 gap as judge randomness, retries, or rate-limit effects, or recommend lowering `-j` as a way to cut real spend.
