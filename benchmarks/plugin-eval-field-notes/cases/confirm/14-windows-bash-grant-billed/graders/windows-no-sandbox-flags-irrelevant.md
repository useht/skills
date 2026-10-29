---
type: llm
weight: 3
---
The user on native Windows granted Bash, all 36 runs errored with scores 0.00, and they plan to re-run on the PC with `--threshold 0 --runs 1` plus `--max-cost-usd 3`. A correct reply must say native Windows has no sandbox backend, so with `--allow-tools Bash` every run is refused with a run error and scores 0; `--threshold`, `--runs`, or a cost cap change nothing about that, so the planned re-run on this PC makes no sense.

PASS: The reply explains the refusal by the missing sandbox backend on native Windows and says re-running on this PC with Bash granted — with or without `--threshold 0`, `--runs 1`, `--max-cost-usd` — will be refused again, so it should not be done.
FAIL: The reply proposes re-running on native Windows with Bash (or PowerShell) granted under any flag variation, or claims the sandbox can be disabled/bypassed there, or says the flags will yield numbers.

판정은 아래 사용자 요청 원문과 대조한다.

[사용자 요청 원문]
Windows 11, Claude Code 2.1.312, Git 2.47, PowerShell. My skill runs a small check script during the task, so I granted the shell:

```
claude plugin eval . --runs 3 --judge-model sonnet --allow-tools Bash Write Edit --no-publish
```

All 6 cases × 6 runs ended with an error on the progress line about Bash not being allowed to run unsandboxed on this machine (paraphrased), every score is 0.00, and the summary still says `6 case(s) · mean Δ +0.00 · 603s · $2.49`. The HTML report shows judge votes under the errored runs. My PATH also contains `C:\Windows\System32\config\systemprofile\AppData\Local\Microsoft\WindowsApps`, which my shell cannot even list (access denied); not sure whether that is related.

I was about to re-run on this PC with `--threshold 0 --runs 1` to at least get some numbers, then add `--max-cost-usd 3` to keep it cheap. I also have a Linux cloud container (Ubuntu, running as root) I can use.

Tell me: why I was charged $2.49 for runs that all errored, whether re-running on this PC with those flags makes sense, and the concrete plan (commands per machine) to get WITH and W/OUT numbers for this suite.

[공개 정답 원문 발췌]
# Ground truth — 14-windows-bash-grant-billed

## Key facts a correct answer must contain

1. Native Windows has no sandbox backend, so with `--allow-tools Bash` every run is refused with a run error and scores 0; `--threshold`, `--runs`, or a cost cap change nothing about that. [doc: Grant tools] [K0-b612491c13] [K0-f80dac9b21]
2. The judge graders still ran on those errored runs, so the $2.49 was real spend with nothing measured, and re-running on native Windows with Bash granted spends it again. [K0-b612491c13] [K0-ac10018182]
3. The plan used in the field: on the PC run only what needs no shell (drop the Bash grant; the without-arm), and run the shell-needing with-arm on Linux, in the cloud container after `apt-get install -y bubblewrap socat` with `--allow-tools Bash Write Edit` (WSL2 is the doc's alternative). [K0-8ad270c2f3] [K0-899caa909f] [doc: Grant tools]
4. On the PC, run the eval with a PATH from which the access-denied `systemprofile\…\WindowsApps` folder has been removed. [K0-899caa909f]
5. If `--keep-temp` is used, delete only the `claude-eval-*` temp folders named in the log (on the root container the tool warns it cannot seal the folder, and wildcard deletion of `/tmp/claude-eval-*` is blocked). [K0-899caa909f] [K0-2bd1d79e6d]

## A correct answer must NOT

- Propose re-running on native Windows with Bash granted, with or without `--threshold 0`, `--runs 1`, or `--max-cost-usd`.
- Say the errored runs cost nothing because they scored 0 or did no agent work.
- Claim that installing bubblewrap/socat (or any package) on native Windows makes the Bash grant work there.
