---
type: llm
weight: 3
---
The user granted Bash on native Windows (no WSL) and every run in both arms was refused with "no sandbox backend". A correct reply must explain that native Windows has no sandbox backend, so with any shell grant (Bash or PowerShell) Claude Code refuses every agent run instead of running it unconfined, and that the all-zero table in both arms is that refusal, not a result about the plugin; it must not suggest retrying on this Windows PC with a shell grant.

PASS: The reply states that native Windows lacks a sandbox backend so shell-granted runs are refused (in both WITH and W/OUT arms), reads the 0.00 scores as that refusal rather than as a plugin result, and never proposes running on the Windows PC with Bash or PowerShell in `--allow-tools` under any variation.
FAIL: The reply attributes the zeros to the skill or rubric, or proposes retrying on native Windows with `--allow-tools Bash` or `PowerShell` under any variation (different `-j`, `--max-cost-usd`, `--trust-plugin`, `--runs 1`, running as administrator, installing a package, disabling the sandbox) as if the runs could then execute.

판정은 아래 사용자 요청 원문과 대조한다.

[사용자 요청 원문]
I'm testing my plugin `tidy-notes` on my Windows 11 laptop (Claude Code 2.1.312, native Windows, no WSL installed, Max subscription). The skill normalises a notes file by running a small Python script through Bash and then writing the cleaned file back. From the plugin root I ran:

```
claude plugin eval . --runs 3 --judge-model sonnet --allow-tools Bash Write Edit -j 4
```

Near the top of the output there was an "access is denied" line mentioning `C:\Windows\System32\config\systemprofile\AppData\Local\Microsoft\WindowsApps`. Then every progress line, WITH and W/OUT alike, ended with an error saying the run was refused because no sandbox backend is available on this platform. Summary:

```
CASE             WITH  W/OUT Δ      RUNS COST   NOTES
normalise-basic  0.00  0.00  +0.00  6    $0.83  run refused: no sandbox backend
dedupe-headers   0.00  0.00  +0.00  6    $0.81  run refused: no sandbox backend
keep-frontmatter 0.00  0.00  +0.00  6    $0.85  run refused: no sandbox backend

3 case(s) · mean Δ +0.00 · 95s · $2.49
```

Each case has two `llm` graders and one `tool_used` grader. No agent run did anything, yet it reports $2.49 and my plan usage dropped.

I have a Linux cloud box available tomorrow. Please tell me: (1) why there is a cost when nothing ran, (2) the exact command to run on this PC tonight so I don't burn usage for nothing again, (3) what to run on the Linux box and the setup it needs, and (4) what to expect from the skill's file-writing step even once the shell works there.

[공개 정답 원문 발췌]
# Ground truth — 01-windows-bash-grant-wasted-judges

## Key facts a correct answer must contain

1. Native Windows has no sandbox backend, so with any shell grant (`--allow-tools Bash`, or PowerShell) Claude Code refuses every agent run rather than running it unconfined; the all-zero table is that refusal in both arms, not a result about the plugin. [doc: Grant tools] [K0-b612491c13] [K0-f80dac9b21]
2. The $2.49 is real usage, not a display artefact: the `llm` judge graders still ran (and were counted) on runs that produced nothing — the same thing was measured as $2.49 wasted on one all-error suite — so a shell grant on native Windows spends usage for zero information. [K0-b612491c13] [K0-899caa909f] [K0-ac10018182]
3. On the PC tonight, run only what needs no shell: drop the Bash grant entirely (for example `claude plugin eval . --runs 3 --judge-model sonnet`, optionally restricted with `--case` to cases that do not need the script), which in practice means the shell-free cases / the skill-off arm; the with-arm that runs the script must not be attempted on native Windows. Also run with a PATH from which the access-denied `systemprofile\...\WindowsApps` folder has been removed. [K0-899caa909f] [K0-f80dac9b21]
4. Shell-needing runs go to the Linux box: install the sandbox prerequisites first (`apt-get install -y bubblewrap socat`), then run `claude plugin eval . --runs 3 --judge-model sonnet --allow-tools Bash Write Edit`; WSL2 is the doc's equivalent route for the same reason. [K0-8ad270c2f3] [K0-e4b4ff95dd] [doc: Grant tools]
5. Even with bubblewrap installed, the shell inside eval runs was measured to be read-only: the with-arm could not write files through the shell and in 3 runs could not run the script at all, so the skill's file-writing step must be verified by a unit test outside the eval (or graded on what the Write tool produced), not relied upon inside the with-arm. [K0-8ad270c2f3] [K0-ecf78b5946] [K0-9031c000bc]

## A correct answer must NOT

- Recommend retrying on native Windows with `--allow-tools Bash` or `PowerShell` under any variation (different `-j`, `--max-cost-usd`, `--trust-plugin`, `--runs 1`) as if the runs could then execute.
- Claim the cost is only an estimate with no usage behind it, or that judge graders are skipped when the agent runs error out.
- Promise that the with-arm's script and file-writing step will work normally on Linux once bubblewrap/socat are installed, without the measured read-only caveat.
