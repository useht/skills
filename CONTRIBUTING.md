# Contributing

We take two kinds of contribution:

1. **Reproductions** — you ran a benchmark in [benchmarks/](benchmarks/README.md) and got different numbers. Open a [reproduction issue](.github/ISSUE_TEMPLATE/reproduce.yml) with the command and versions you used, plus the result JSON.
2. **Counterexamples** — a question where the skill gives a worse answer than the model without it, or than the model given the documents. Open a [counterexample issue](.github/ISSUE_TEMPLATE/counterexample.yml) with the question and both answers.

If you are right we rerun, change the tables and keep the old numbers in [REJECTED.md](benchmarks/REJECTED.md) or the benchmark history.

We do not take pull requests that add skills or rewrite them without a measured reason.
