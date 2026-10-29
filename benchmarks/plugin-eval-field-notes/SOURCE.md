# Document control for plugin-eval-field-notes

The control arm ran the same model with no plugin and appended, after each request, a block headed `[참고 원문]` ("reference source") containing:

- the official page "Test plugins with evals", https://code.claude.com/docs/en/plugin-evals.md, fetched 2026-10-28 with curl, unchanged;
- the output of `claude plugin eval --help` and `claude plugin --help` from Claude Code 2.1.312.

Together about 81 KB. These are Anthropic's text, so this repository does not copy them: in `results/02-control-*.json` and `results/04-control-*.json` the appended block in each `promptMarkdown` is replaced by a one-line note. Everything else in those files is the raw tool output. `python benchmarks/plugin-eval-field-notes/rerun.py source` rebuilds this text from the live page and your local CLI and compares its SHA-256 with the registered one (`0d6fa3ce…`); `rerun.py run` appends it to each `prompt.md` under the same heading.

At the time of the runs this was the only public source on the subject; the pitfalls the skill covers were not in it.
