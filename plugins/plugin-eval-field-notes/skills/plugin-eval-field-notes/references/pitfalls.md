# Pitfall ledger - every claim in SKILL.md, traced to its source

Each entry: ledger id, kind (`failure` = something went wrong and was diagnosed; `measured` = a number or behaviour observed), source path as recorded in the knowledge-base ledger (`<repo>[@<commit>]:<path>:<line>`), and the pitfall in one or two lines. Several ids are the same finding recorded in more than one place; they are grouped so a reader can see the duplication rather than mistake it for independent confirmation. Numbers are single measurements from one project in Oct 2026 on Claude Code 2.1.309-2.1.312; quote them as such.

## A. Native Windows

| id | kind | source | pitfall |
|---|---|---|---|
| K0-b612491c13 | failure | ai-income@7eb5a42:공개스킬/HANDOFF.md:64 | Windows has no shell isolation backend; with `--allow-tools Bash` every run ends in error, only the judges run, and the cost is spent (one without-arm-only run: $2.49 wasted). |
| K0-f80dac9b21 | failure | ai-income@8c2a460:공개스킬/HANDOFF.md:36 | Same finding; conclusion: on the PC evaluate only arms/cases that need no shell. |
| K0-ac10018182 | failure | skill-foundry@2bf2006:HANDOFF.md:54 | Same finding, re-recorded in a second repository. |
| K0-899caa909f | failure | ai-income@2386ddf:공개스킬/HANDOFF.md:37 | PC run needs a PATH with the access-denied folder `systemprofile\...\WindowsApps` removed; Bash grant errors every run; `--keep-temp` leaves `claude-eval-*` folders - delete only the names printed in the log. |
| K0-47b3f0b3d2 | measured | claude@8180f12:workspace/다음작업.md:18 | Store stub `python3` 166 ms + `python` 124 ms per call (Git Bash, 5-run mean); filtering by path (`command -v` then `case $q in *WindowsApps*) continue`) brings it to about 29 ms. |
| K0-8d5ba38554 | measured | claude@8180f12:workspace/앎배달-PC/인계.md:5 | The path-filter form of the command works on the PC (exit 0, 6,322-byte UTF-8 output). |
| K0-d4a4bee8ce | measured | claude@0f5c67b:workspace/앎배달-PC/인계.md:5 | Same as K0-8d5ba38554. |

## B. Cloud session / Linux container / CI

| id | kind | source | pitfall |
|---|---|---|---|
| K0-8ad270c2f3 | measured | ai-income@8c2a460:공개스킬/HANDOFF.md:35 | Shell-needing evals go to the cloud: `apt-get install -y bubblewrap socat` then `--allow-tools Bash Write Edit`. The shell inside the run is read-only, so file-writing steps are tested by unit tests instead. |
| K0-fd42ca560e | measured | ai-income@7eb5a42:docs/기획-공개스킬.md:44 | Cloud run works: 6 cases x 3 runs x two arms estimated $8.54-9.48 (`costUsd`, list price), 286-335 s; subscription login is not billed separately, it draws on the plan's usage limit; bubblewrap/socat required; shell read-only (6 runs, 2026-10-23). |
| K0-e4b4ff95dd | measured | ai-income@1108d73:docs/기획-공개스킬.md:45 | Same: sandbox packages required; shell read-only. |
| K0-5d69015121 | measured | ai-income@128a77f:docs/기획-공개스킬.md:45 | Same as K0-fd42ca560e. |
| K0-d8d3d7b5e7 | measured | ai-income@5e97e36:docs/기획-공개스킬.md:45 | Same as K0-fd42ca560e. |
| K0-ecf78b5946 | failure | ai-income@1108d73:docs/기획-공개스킬.md:71 | With the same `--allow-tools`, OS isolation blocked shell writes; the with-arm created files with the Write tool, and in 3 runs the skill's scripts did not run. |
| K0-9031c000bc | failure | ai-income@128a77f:docs/기획-공개스킬.md:71 | Same as K0-ecf78b5946. |
| K0-737da892bc | failure | ai-income@5e97e36:docs/기획-공개스킬.md:71 | Rule adopted: count from the trace, per with-arm run, whether the post-check script actually ran, and report it with the score. |
| K0-2bd1d79e6d | measured | ai-income@2386ddf:공개스킬/HANDOFF.md:35 | One gate-probe run of a long case (111-165 transcript lines in the prompt) cost about $6.26, as much as a formal 3-run suite. Cloud runs as root, so the tool warns it cannot seal `--keep-temp` folders; delete by logged name (wildcard delete of `/tmp/claude-eval-*` is blocked in automatic mode). |
| K0-746fea9325 | failure | skill-foundry@2bf2006:docs/기획-grounded-handoff.md:50 | Discarded option `--allow-tools Bash`: the baseline agent tried `git` in a repository that did not exist and wasted turns, so the arms were no longer like-for-like. |

## C. Cost

| id | kind | source | pitfall |
|---|---|---|---|
| K0-bfa92c4008 | measured | skill-foundry@2bf2006:HANDOFF.md:23 | Concurrency double-counts judge cost: the same 2 judge items cost $0.079 at `-j 1` and $0.147 at `-j 2`; all `-j 8` figures have an inflated judge share. |
| K0-dea4b2d738 | measured | skill-foundry@2bf2006:docs/기획-벤치마크꾸러미.md:46 | Mechanism: per-run `judgeCostUsd` is the difference of a global running total (`dy()-r` in the binary), so concurrent runs' judge calls are included; 1.86x at `-j 2`. Real values need a `-j 1` sample. |
| K0-e919bd6e8e | measured | skill-foundry@2bf2006:docs/기획-벤치마크꾸러미.md:127 | Symptom that triggered the test: a second judge cost reported at about 7x the expected value. |
| K0-7eba9c130c | measured | skill-foundry@69099ca:HANDOFF.md:23 | Same as K0-bfa92c4008. |
| K0-32644f32ff | measured | ai-income:공개스킬/HANDOFF.md:99 | A whole-workflow skill: 7 cases x 3 runs x two arms, `-j 8`: $15.43-15.49, 636-1,271 s. |
| K0-cd53c94ba0 | measured | ai-income@7eb5a42:공개스킬/HANDOFF.md:92 | Same as K0-32644f32ff. |
| K0-a4bcfdeec3 | measured | skill-foundry@2bf2006:docs/기획-앎우선공정.md:120 | A bundle arm: $21.20-31.31 per arm (tool-reported, `-j 8`, judge share inflated). |
| K0-9f3c9c0606 | measured | skill-foundry@2bf2006:docs/기획-벤치마크꾸러미.md:40 | One haiku run of a one-case probe: $0.006. (Also in section F.) |
| K0-6f95041daf | measured | ai-income@5e97e36:docs/기획-스킬양산.md:91 | Scaffold smoke test (download, compare, unpack; without-arm read `node_modules/effect/package.json` and answered 4.0.7): $0.07. |
| K0-32bbba8125 | measured | claude:workspace/스킬-연구소/진행/U9.md:30 | Context: the investigation itself - subagent tokens 98k (plugin eval research), 209k (pre-autopsy), 94k x 2 (judges), 207k/204k (full reviews); four CLI child flows about $7.2 (0.80, 2.01, 1.95, 1.96). |

## D. Judge verdicts

| id | kind | source | pitfall |
|---|---|---|---|
| K0-3aee184a4b | failure | ai-income:docs/기획-공개스킬.md:70 | The judge sees only the final reply (llm `focus` default `last_message`), so it did not know the user's own statement ("regulars say we're no. 1") and failed it as a fabricated source, while the same case's no-fake-source rubric held that wording as correct - two rubrics in conflict. |
| K0-1c9f5ca9bb | failure | ai-income:공개스킬/HANDOFF.md:72 | Case 01 "keep tone" with 0/3 vs without 3/3 was a judge artefact, not a skill fault; reproduction files kept. |
| K0-f3b8cba76a | failure | ai-income@7eb5a42:docs/기획-공개스킬.md:70 | Comparing the 6 stored replies showed with-arm runs 2-3 edited only flagged spots yet got FAIL x3; same-model reproduction gave the "invented source" reason. |
| K0-cd529f487d | failure | ai-income@5e97e36:docs/기획-공개스킬.md:71 | Same as K0-3aee184a4b. |
| K0-556fdffaf0 | failure | ai-income:docs/다음작업.md:22 | Fix: paste the request's original text into the rubric of every grader that compares against it. |
| K0-8f90233376 | measured | ai-income:공개스킬/앎체계/원자료/1-다른세션-전달-2026-10-23.md:55 | Six source-comparison rubrics failed the with-arm for that reason (case 01 "new facts" with 1/3, without 3/3); `examples/` containing answers is a contamination channel. |
| K0-83124cdcc1 | measured | ai-income@2386ddf:공개스킬/HANDOFF.md:39 | Judge sees reply + rubric only; paste the original into comparison rubrics; no reasons in results (votes only), `evidence` per grader; re-read divergent cells blind across arms; common-sense sentences can be called "invented". |
| K0-143fea691e | failure | skill-foundry@2bf2006:docs/기획-스킬양산.md:90 | The judge cannot see files the agent wrote: a without-arm wrote code to a file and summarized in the reply, the code rubric failed, and the with-arm's 0.886 was the inflated side. Rule: tools per case, default none; `write` only for file deliverables; `shell` only for execution. |
| K0-dc517e4f1a | measured | ai-income@b217699:공개스킬/HANDOFF.md:103 | Sonnet 3-vote judge fails correct long replies; only votes are stored, so re-read divergent cells from the kept trace's final reply with arm labels hidden and order shuffled, identically for both arms. |
| K0-b62db52986 | measured | ai-income@7eb5a42:공개스킬/HANDOFF.md:98 | Same as K0-dc517e4f1a. |
| K0-c11d398397 | measured | ai-income@b217699:공개스킬/HANDOFF.md:45 | Results hold votes only, no reasons; keep traces with `--keep-temp` to see what was produced. |
| K0-75dffd95ab | measured | skills:공개스킬/조사/3호-판정관-재현/README.md:3 | A `claude -p --model sonnet --tools ""` reproduction with the same rubric and reply is not the tool's judge prompt; it only indicates a cause. |
| K0-8c5c9fcd98 | measured | skill-foundry@2bf2006:docs/기획-벤치마크꾸러미.md:44 | `claude -p` re-judge of 36 grader-runs agreed 0.72; all 10 mismatches were without-arm FAIL -> PASS. Seeding the same reply (5,824 chars, byte-identical) as a workspace file and grading it with `focus: {source: file, path: seed.md}` reproduced the original FAIL x3. |
| K0-51517dfab6 | measured | skill-foundry@2bf2006:docs/기획-벤치마크꾸러미.md:44 | The tool's judge call has `thinkingConfig: {type: "disabled"}`; `claude -p` still used 174-364 thinking tokens despite `CLAUDE_CODE_DISABLE_THINKING=1`, `alwaysThinkingEnabled: false`, `MAX_THINKING_TOKENS` cleared - so `claude -p` cannot reproduce the judge; the file route can. |
| K0-633ba95907 | measured | skill-foundry@07c0967:HANDOFF.md:23 | Judge answers without thinking, one word. Via the file route: same-model agreement 0.97, opus 0.81; 6 of opus's 7 mismatches were without-arm FAIL -> PASS. The original judge may rate skill-less replies harshly, inflating with-minus-without. |
| K0-f451780ea5 | measured | skill-foundry@2bf2006:docs/기획-벤치마크꾸러미.md:45 | A without-arm reply containing GPSR art. 20, "without undue delay", Safety Business Gateway and Belgium still got FAIL x3 on `accident-notify-belgium-sbg`; a thinking sonnet passed it. Rubric length 9,500-10,000 chars. One case, not a conclusion. |
| K0-006a6842e2 | measured | ai-income@8c2a460:공개스킬/조사/grounded-handoff/관문-1/README.md:24 | Blind re-read, gate 1: case 07 judged per rubric (reply hit a FAIL clause); cases 05 and 06 met the PASS condition yet got FAIL. Correcting would raise the without-arm (about 0.96) and only strengthen the "baseline wins" conclusion, so no re-registration. |
| K0-054bfc4e7e | measured | ai-income@8c2a460:공개스킬/조사/grounded-handoff/관문-2/README.md:24 | Gate 2: case 06 judge wrong (old value marked as old, not current); case 01 arguably a real FAIL (told the user to enable a prod flag); case 04 undecidable from `evidence`. |
| K0-95b7c29844 | measured | ai-income@8c2a460:공개스킬/조사/grounded-handoff/관문-3/README.md:24 | Gate 3: cases 05 and 06 met PASS conditions yet failed; case 07 undecidable. Same decision rule. |

## E. Results JSON

| id | kind | source | pitfall |
|---|---|---|---|
| K0-a446e4e46d | measured | ai-income@7eb5a42:docs/기획-공개스킬.md:71 | Per grader: `evidence` (final reply) and `judgeVotes` are present; `explanation` is only `judge votes: PASS PASS PASS`. |
| K0-dc11561567 | measured | ai-income@7eb5a42:공개스킬/조사/1호-끔-다시/README.md:33 | Same. |
| K0-1a53242e1b | measured | ai-income@7eb5a42:공개스킬/HANDOFF.md:64 | `evidence` per grader holds the final reply; re-reading divergent cells can be done from the JSON. |
| K0-5f501a82d7 | measured | ai-income@7eb5a42:docs/기획-앎1단계.md:89 | 5.3 MB result file, 4.66 MB of which is the same reply repeated per grader (366 runs, all identical across graders); flattened: 1.73 MB with both arms, 0.95 MB without-arm only. |
| K0-77feda6feb | measured | knowledge-base@eee6509:docs/기획-앎1단계.md:89 | Same as K0-5f501a82d7. |
| K0-ee431a12e2 | measured | skill-foundry@2bf2006:docs/기획-벤치마크꾸러미.md:23 | Full census of one repository's results: 1,331 replies, longest 11,582 chars, zero `chars elided` markers - `evidence` is not truncated. |
| K0-e10a4d1272 | failure | skill-foundry@2bf2006:docs/기획-스킬양산.md:95 | The agent model is not in the results JSON; the 57 kept transcripts all showed `claude-sonnet-5-5`. A `claude -p --model claude-opus-4-8` decomposition gave iced 0.13 while the eval without-arm used 0.14 - outputs from outside the eval do not stand in for an arm. |
| K0-eb000acfb4 | measured | ai-income@5e97e36:docs/기획-앎우선공정.md:26 | `claude plugin eval --help` (2.1.312) has `--model`, `--judge-model`, `--runs`, `--case`, `--json`, and no option that forces a skill to fire. |

## F. With/without design, contamination, forced invocation

| id | kind | source | pitfall |
|---|---|---|---|
| K0-afe8cc2f9b | failure | ai-income:공개스킬/앎체계/원자료/1-다른세션-전달-2026-10-23.md:47 | A +0.128 delta (with 0.854, without 0.726) was not publishable: rubrics written by the skill author (the skill's own habit, "says bytes", became the pass condition); six rubrics the judge could not evaluate without the original (fixed later, not re-measured); no contamination check (`--keep-temp` unused; `examples/science/최종.txt` was case 01's answer); no pre-registered expectation or re-read rule. |
| K0-a12ba2a051 | failure | skill4:공개스킬/HANDOFF.md:45 | Same four defects, recorded in the skill's own repository. |
| K0-0bdfddd087 | measured | skills:공개스킬/스킬/bizplan-score-loop/docs/평가-결과.md:3 | Standard run: `claude plugin eval . --runs 3 --ablation with-without --judge-model sonnet --allow-tools Bash Write Edit` (2.1.309); invocation counted from tool records; judge = sonnet 3-vote majority on `evals/*/graders/*.md`. |
| K0-275ffea9fd | measured | skills:공개스킬/스킬/contract-redline-loop/docs/평가-결과.md:3 | Same run shape with `-j 8`. |
| K0-5e2858b878 | measured | skills:공개스킬/스킬/bizplan-score-loop/README.md:27 | Published table form: trigger counts (12/12 should-fire, 0/6 should-not) plus per-criterion with/without fractions; mean 0.90 vs 0.62 (+0.28). |
| K0-7b5553cac4 | measured | skills:공개스킬/스킬/contract-redline-loop/README.md:27 | Same form over three measurements (0.938 -> 0.974 -> 0.989 vs 0.884 -> 0.903 -> 0.873), including a cell where without beat with (2/3 vs 3/3). |
| K0-7186e55325 | measured | skills:공개스킬/스킬/naver-blog-draft-check/README.md:63 | 7 cases, same shape; failures recorded as they are. |
| K0-f68f558a5b | measured | ai-income@7eb5a42:docs/기획-공개스킬.md:67 | Two runs: +0.054 then +0.071, both under the project's 0.1 design bar; the gap sat in numeric cells (3/3 vs 1/3) and the full redline (2/3 vs 0/3); cells with both arms at 1.0 diluted the mean; one cell lower with the skill (2/3 vs 3/3). |
| K0-89d4ae0e5b | measured | ai-income@1108d73:docs/기획-공개스킬.md:68 | Same as K0-f68f558a5b. |
| K0-4c4e12a57d | measured | ai-income@5e97e36:docs/기획-공개스킬.md:68 | Same as K0-f68f558a5b. |
| K0-dab7a24aac | failure | ai-income@2386ddf:docs/기획-grounded-handoff.md:76 | "No room": the base model won three of four probes for handoff-from-pasted-transcript (delta -0.091, -0.088, -0.077). Reopen when the task becomes a real repo + shell eval, when a new base model drops below 0.8 on the same gate, when a top-installed rival beats the base, or when the map shows the task type losing. |
| K0-fb3b09addf | failure | skill-foundry@2bf2006:docs/기획-grounded-handoff.md:76 | Same reopen conditions, second repository. |
| K0-9f3c9c0606 | measured | skill-foundry@2bf2006:docs/기획-벤치마크꾸러미.md:40 | Forced invocation works via a `/skill-name ...` prompt (with-arm reply contained the skill's wording); the without-arm replied that `/skill-name` is not installed, so the name leaks. Run the forced arm with `--ablation none` and pair it with the natural prompt's without-arm. |
| K0-38e8f21712 | measured | skill-foundry@2bf2006:docs/기획-벤치마크꾸러미.md:40 | A slash prompt produces no `Skill` tool call (the slash is expanded); the trace's first line (`system`/`init`) lists `skills` and `slash_commands` including `<plugin>:<skill>` - count forced invocation by that entry. Regex grader default target is `last_message`. |
| K0-cb995b3ced | measured | skill-foundry@2bf2006:docs/기획-앎우선공정.md:121 | Forced arm fired 21/21; scores like the natural arm (gate 0.828 vs 0.838, confirm 0.934 vs 0.884). Rival forced arm skipped because the docs-only rival already decided the verdict. |

## G. Adjacent (not about `claude plugin eval`, kept for completeness)

| id | kind | source | note |
|---|---|---|---|
| K0-15836d013c | measured | claude@49cc4f5:workspace/에이전트-조직/effort.md:22 | External measurement (Stet, an eval-tool author): Opus 4.7 on 29 Go tasks, test pass low 79% / medium 97% / high 90% / xhigh 86% / max 93%, cost $2.50 -> $8.84. Not from `claude plugin eval`. |
| K0-9344da0659 | measured | claude@ab4c1bd:workspace/에이전트-조직/effort.md:22 | Same. |
