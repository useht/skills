# plugin-eval-field-notes

A Claude Code skill for people who build and read `claude plugin eval` suites. The official page explains the format and flags; this skill holds what we learned by running the tool (Claude Code 2.1.309 to 2.1.312) that the page does not say: a Bash grant on native Windows makes every run error while the judges still bill, `COST` is overcounted when cases run with `-j` above 1, judge verdicts come with no stored reasons and cannot be replayed with `claude -p`, a `/name` prompt in the without-arm leaks the skill, and plugin example files can carry a case's expected answer into the with-arm.

Each note says what goes wrong and how it shows in the output, then gives the command or script that avoids it. `references/pitfalls.md` ties every note to the run it came from (ids like `K0-...` point into our private research log); `references/recipes.md` has paste-ready scripts that you run yourself.

## Measured

On 5 gate cases and 5 confirmation cases written before any run (3 runs each, Claude Sonnet), the skill beat the same model given the official docs page and `claude plugin eval --help`: +0.64 [+0.54, +0.77] and +0.26 [+0.15, +0.42], and again when regraded by Claude Opus (+0.60 and +0.28). The two graders agreed on 83 to 91 percent of verdicts per run, so treat the numbers as judge-sensitive. Details: [benchmarks/plugin-eval-field-notes](../../benchmarks/plugin-eval-field-notes/README.md).

## Install

```
/plugin marketplace add useht/skills
/plugin install plugin-eval-field-notes@hyperteams
```

The `evals/` folder holds the ten benchmark cases in `claude plugin eval` form. MIT.
