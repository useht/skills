My plugin `sci-brief` turns a messy research note into a one-page brief. Layout:

```
sci-brief/
├── .claude-plugin/plugin.json
├── skills/sci-brief/SKILL.md        # tells Claude to study examples/ first
├── examples/science/final.txt       # a finished brief shown as the model answer
└── evals/01-science-note/ … 06-…/
```

Case 01's prompt is the raw note that `examples/science/final.txt` was written from, so that file is essentially case 01's expected output. I wrote all rubrics myself. Examples: "PASS if the reply states how many bytes the brief is" (the skill always reports bytes), and six rubrics of the form "compare the reply with the user's original note; FAIL if any fact was added". I ran:

```
claude plugin eval . --runs 3 --judge-model sonnet
```

Result: WITH 0.854, W/OUT 0.726, Δ +0.128. On case 01 the "no new facts" rubric was WITH 1/3, W/OUT 3/3. I did not pass `--keep-temp`.

A reviewer says this is not publishable evidence that the skill helps. I answered that the docs say a run cannot read the eval directory, so there is no leakage. Who is right? Give me a verdict and a concrete list of what to change before I re-measure.
