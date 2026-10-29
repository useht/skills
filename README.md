# HyperTeams Skills

Claude Code skills measured before they ship: with the skill, without it, and without it but given each skill's listed control documents.

한국어: 스킬은 켜고, 끄고, 표에 적은 원문 상대를 주고 셋으로 재서 내놓습니다. [README.ko.md](README.ko.md)

Gate set. plugin-eval-field-notes was measured on 2026-10-29, the three withdrawn rows on 2026-10-28. Score = mean over cases of the weighted share of criteria passed (0 to 1). Confirmation-set results, both graders' tables and the release criteria are in [benchmarks/](benchmarks/README.md).

| Skill | Task | With skill | Without the skill, given the documents in the next column | Documents given to the control | Δ (95% CI) | Cases × runs | Status |
|---|---|---|---|---|---|---|---|
| [plugin-eval-field-notes](plugins/plugin-eval-field-notes/) | Running and reading `claude plugin eval`: Windows, cost under `-j`, judge verdicts, with/without arm design | 0.825 | 0.183 | the official plugin-evals docs page and `claude plugin eval --help` | +0.64 [+0.54, +0.77] | 5 × 3 | beats the document control, judge-sensitive; not yet compared with other public skills |
| kr-vat-filing | Korean VAT final return for a sole proprietor | 1.000 | 0.976 | the statutes the skill is built on | +0.02 [+0.00, +0.07] | 7 × 3 | withdrawn: did not meet the preregistered release criteria |
| kr-payroll | Korean social-insurance deductions to the won | 1.000 | 1.000 | the statutes, notices and agency pages the skill is built on | +0.00 [+0.00, +0.00] | 7 × 3 | withdrawn: did not meet the preregistered release criteria |
| eu-product-compliance | EU product safety and recall steps from the statute | 0.838 | 0.928 | the regulation text the skill is built on | −0.09 [−0.26, +0.05] | 7 × 3 | withdrawn: did not meet the preregistered release criteria |

Each "without" arm gives the same model (Claude Sonnet), with no skill, the documents named in its row, pasted after the request. Graded by Claude Sonnet against criteria committed before any run, then regraded by Claude Opus; a win over the document control counts only when both graders put the lower end of the interval above zero on both case sets. The full release bar also compares the skill with the strongest public skills for the same task; for plugin-eval-field-notes that comparison has not been run yet. Judge-sensitive: on plugin-eval-field-notes the two graders agreed on 83 to 91 percent of criterion verdicts per run, below the 95 percent we set (before these runs, and not yet validated) for not flagging a run, so read its numbers as one grading of the answers, not a settled score. Not validated against human labels. To rerun the with/without arms: `claude plugin eval plugins/plugin-eval-field-notes --runs 3 --judge-model sonnet`. The document-control arm appends the source text listed in [SOURCE.md](benchmarks/plugin-eval-field-notes/SOURCE.md) to each request; a script for that arm is not published yet.

## Install

```
/plugin marketplace add useht/skills
/plugin install plugin-eval-field-notes@hyperteams
```

claude.ai: Customize > Plugins > Add marketplace: useht/skills

## One question, two answers

Gate case 02: a `-j 8` run of a 7-case suite printed `$15.49`; can that go in a README, a CI cost cap and a per-run estimate? With the docs pasted in, the model answered "**No. $15.49 is a list-price estimate, not what the run cost you.**" and stopped there (score 0.18 on all three runs). With the skill: "Per-run `judgeCostUsd` is the difference of a global running total. Judge calls from cases running at the same time land in each other's figures, so they get counted more than once." It then rejected the $15.49 / 42 division and gave a `-j 1` rerun command (scores 1.00, 1.00, 0.64). Full answers are in the grader evidence in [results/](benchmarks/plugin-eval-field-notes/results/).

## Found a case where it loses?

Open a [counterexample issue](.github/ISSUE_TEMPLATE/counterexample.yml) or a [reproduction issue](.github/ISSUE_TEMPLATE/reproduce.yml). We rerun it and change the numbers above if you are right.

## Skills

[plugin-eval-field-notes](plugins/plugin-eval-field-notes/) holds pitfalls of `claude plugin eval` that we hit in real runs and that the official page does not cover, each with the symptom and the command or script that avoids it. Use it when you build or interpret plugin and skill evals.

## Why this exists

We ship only skills that clear release criteria fixed before the run. For the three withdrawn skills (measured 2026-10-28) the bar was: on both case sets, at least 0.1 above the model without the skill, above the model given the documents, and that document control still leaving at least 0.2 of error to remove. All three failed the last test (the control already scored 0.976, 1.000 and 0.928), and eu-product-compliance also scored below it. From the next release the bar also requires the paired gain over the document control to have a 95% interval above zero on both sets, for both graders. I will not put my name on a skill that is not shown to beat the model with the documents in front of it, so these stay here as measurements, not releases ([REJECTED.md](benchmarks/REJECTED.md)).

## Limits · Security · License

The skill answers from our own measured runs of Claude Code 2.1.309 to 2.1.312; behaviour may change in later versions. See SECURITY.md for what each skill runs or fetches. MIT. Claude and Anthropic are trademarks of Anthropic, PBC; this project is not affiliated with or endorsed by Anthropic.
