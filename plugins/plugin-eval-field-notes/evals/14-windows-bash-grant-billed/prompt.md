Windows 11, Claude Code 2.1.312, Git 2.47, PowerShell. My skill runs a small check script during the task, so I granted the shell:

```
claude plugin eval . --runs 3 --judge-model sonnet --allow-tools Bash Write Edit --no-publish
```

All 6 cases × 6 runs ended with an error on the progress line about Bash not being allowed to run unsandboxed on this machine (paraphrased), every score is 0.00, and the summary still says `6 case(s) · mean Δ +0.00 · 603s · $2.49`. The HTML report shows judge votes under the errored runs. My PATH also contains `C:\Windows\System32\config\systemprofile\AppData\Local\Microsoft\WindowsApps`, which my shell cannot even list (access denied); not sure whether that is related.

I was about to re-run on this PC with `--threshold 0 --runs 1` to at least get some numbers, then add `--max-cost-usd 3` to keep it cheap. I also have a Linux cloud container (Ubuntu, running as root) I can use.

Tell me: why I was charged $2.49 for runs that all errored, whether re-running on this PC with those flags makes sense, and the concrete plan (commands per machine) to get WITH and W/OUT numbers for this suite.
