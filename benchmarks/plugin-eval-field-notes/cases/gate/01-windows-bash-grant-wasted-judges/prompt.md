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
