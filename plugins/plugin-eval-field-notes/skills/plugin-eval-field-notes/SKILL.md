---
name: plugin-eval-field-notes
description: Field-measured pitfalls of `claude plugin eval` (the Claude Code CLI that runs eval cases against a plugin/skill and grades them) that the official docs do not cover. Load this whenever a user is writing, running, debugging, or interpreting plugin or skill evals - running on native Windows (PowerShell, PATH, no sandbox) or in a cloud/CI container (bubblewrap, root, read-only shell), granting Bash/Write/Edit with --allow-tools, reading COST or costUsd under concurrency (-j), making sense of llm judge/grader verdicts, judgeVotes and PASS/FAIL that look wrong, parsing aggregate-result.json or --json output (evidence, explanation, arms.with/without), designing with/without (ablation) skill comparisons and reading delta, forced invocation of a skill via a /name prompt, rival-skill arms, contamination checks, and the evals/ folder, prompt.md and graders/*.md format. Also triggers on "plugin eval", "skill eval", "--ablation", "--keep-temp", "--judge-model", "eval cost", "judge failed a correct answer".
---

# plugin eval field notes

The official page (code.claude.com/docs/en/plugin-evals) covers the format, flags, scoring and exit codes. This skill holds only what was learned by running the tool (Claude Code 2.1.309-2.1.312, Oct 2026) and is not on that page. Every claim carries an id (`K0-...`); `references/pitfalls.md` maps each id to its source line, `references/recipes.md` has paste-ready scripts.

How to answer: name the situation, say what goes wrong and how it shows in the output, then give the command or script. Quote numbers as single measurements from one project, not as rules. If the docs already answer, give the one-line answer and point to the docs section.

## 0. Before the first paid run

Each item below prevented a wasted run.

- Choose the tool grant per case, default **none** (section 3). A grant is suite-wide, so one Bash case forces the whole run onto a sandboxed host.
- Check the host: native Windows cannot run a Bash-granted case (section 1); a fresh Linux container needs `bubblewrap` and `socat` first (section 2).
- Pin `--model` and `--judge-model`. The agent model is **not recorded in the results JSON**; it was found only in `--keep-temp` transcripts, where 57 kept folders all showed the same default model (K0-e10a4d1272).
- Set `--max-cost-usd`, and expect inflated COST whenever `-j` > 1 (section 4).
- Grep the plugin for contamination: any plugin file (especially `examples/`) holding a case's expected answer loads into the with-arm and inflates delta. In one suite `examples/science/최종.txt` was literally case 01's answer (K0-afe8cc2f9b, K0-8f90233376, K0-a12ba2a051). Recipe 7.
- Write down the expected delta and the re-read rule (section 5) before running. A +0.128 measured without these was later judged unpublishable (K0-afe8cc2f9b).

## 1. Native Windows (PowerShell / Git Bash on the PC)

**Bash grant = every run errors, judges still bill.** Windows has no sandbox backend, so with `--allow-tools Bash` every agent run ends in a run error, yet the judge graders still execute and the cost is spent: one without-arm-only run of a 7-case suite burned an estimated $2.49 for nothing (K0-b612491c13, K0-f80dac9b21, K0-ac10018182, K0-899caa909f). Recognize it: every progress line shows `error:` and the summary still prints a COST.

Do instead: run on the PC only the cases and arms that need no shell. The split that emerged: **without-arm and shell-free cases on the PC, shell-needing with-arm in a Linux container** (K0-8ad270c2f3, K0-899caa909f) or WSL2 (docs). Never grant Bash on Windows "to see what happens".

**PATH holds an access-denied folder.** The PC run only started cleanly after removing `...\systemprofile\...\WindowsApps` from PATH for that shell (K0-899caa909f). Recognize it: access-denied errors before any case starts. Recipe 1 builds a filtered PATH.

**WindowsApps stub `python`/`python3`.** The Store stubs cost about 166 ms + 124 ms per call and fool `command -v python3` in hooks and helper scripts (K0-47b3f0b3d2, K0-8d5ba38554, K0-d4a4bee8ce). Filter by path, not name: `q=$(command -v "$p") || continue; case $q in *WindowsApps*) continue;; esac`.

**`--keep-temp` leftovers** are `claude-eval-*` folders; delete only the names printed in the log, never a wildcard (K0-899caa909f, K0-2bd1d79e6d).

## 2. Cloud session, Linux container, CI runner

**Shell needs the sandbox packages first.** What worked: `apt-get install -y bubblewrap socat` then `claude plugin eval . --allow-tools Bash Write Edit` (K0-8ad270c2f3, K0-fd42ca560e, K0-e4b4ff95dd). Without them the grant is refused as on Windows.

**The shell inside a run was read-only.** Across 6 measured runs the sandboxed shell could not write files; the with-arm created files with the Write tool instead, and in 3 runs the skill's scripts never executed (K0-e4b4ff95dd, K0-ecf78b5946, K0-9031c000bc). So: test a skill's file-writing steps with unit tests, not evals (K0-8ad270c2f3); and for any with-arm that depends on a script, **count from the trace how many runs actually executed it** and print that beside the score, which alone hides it (K0-737da892bc). Recipe 4.

**Granting Bash changes the without-arm too.** With Bash available, one baseline agent tried `git` in a repository that did not exist and spent its turns there, so the arms were no longer the same task (K0-746fea9325). If only the with-arm needs a shell, run the arms separately (`--ablation none` with the grant; the baseline without) and pair them by hand.

**Running as root.** The tool warns it cannot seal `--keep-temp` folders; delete them by exact logged name, because a wildcard `rm /tmp/claude-eval-*` is blocked in automatic mode (K0-2bd1d79e6d).

**What a cloud run cost.** 6 cases x 3 runs x two arms: estimated $8.54-9.48 (`costUsd`, list price), 286-335 s (K0-fd42ca560e). With a subscription login nothing is billed separately; the calls come out of the plan's usage limit (K0-fd42ca560e). A one-run scaffold smoke test cost $0.07 (K0-6f95041daf).

## 3. Tools and what the judge can see

An `llm` grader's judge reads the final reply only (`focus` default `last_message`). Two consequences the docs do not spell out:

**Files the agent wrote are invisible.** A without-arm wrote its code to a file with Write and left a summary in the reply; the code rubric failed although the code was right, which inflated the with-arm's lead (its 0.886 was "the inflated side") (K0-143fea691e). Rule that fixed it: tools **per case**, default **none** so the answer must carry the code or document; `Write` only where the deliverable is a file, then grade the file with `focus: {source: file, path: ...}`; `Bash` only where something must execute (K0-143fea691e).

**The user's context is invisible.** The judge sees reply and rubric, not the user's draft or facts. A correct reply that kept the user's own sentence ("regulars say we're the no. 1 scone place") got FAIL x3 as a fabricated source, while the same case's keep-the-tone rubric required exactly that sentence; the skill scored 0/3 on tone for a judge reason, not a skill reason (K0-3aee184a4b, K0-1c9f5ca9bb, K0-f3b8cba76a, K0-cd529f487d). Fix: paste the relevant original (draft, facts, constraints) into the body of every rubric that compares against it (K0-556fdffaf0, K0-83124cdcc1). Expect plain common-sense statements to be called "invented" too (K0-83124cdcc1).

## 4. Reading COST

**Concurrency double-counts judge cost.** The same two judge items reported $0.079 at `-j 1` and $0.147 at `-j 2` (1.86x). Per-run `judgeCostUsd` is the difference of a global running total, so judge calls from concurrently running cases land in each other's figure (K0-bfa92c4008, K0-dea4b2d738, K0-e919bd6e8e, K0-7eba9c130c). The symptom that exposed it: a second judge figure about 7x the expected value (K0-e919bd6e8e). Treat any COST from `-j` > 1 as an upper bound with an inflated judge share; when the number is the claim, re-measure a sample at `-j 1` (recipe 5).

**Reference points** (tool estimates, list price, `-j 8` unless stated):
- 7 cases x 3 runs x two arms, a whole-workflow skill: $15.43-15.49, 636-1,271 s (K0-32644f32ff, K0-cd53c94ba0).
- 6 cases x 3 runs x two arms in a container: $8.54-9.48, 286-335 s (K0-fd42ca560e).
- One arm of a large bundle: $21.20-31.31 (K0-a4bcfdeec3).
- One run of a long-transcript case (111-165 lines pasted into the prompt): about $6.26, as much as a normal 3-run suite (K0-2bd1d79e6d).
- One haiku run of a one-case probe: $0.006 (K0-9f3c9c0606). Use haiku with `--runs 1 --ablation none` for mechanics probes (does the grader fire, does the prompt parse), never for a score.

## 5. Judge verdicts that look wrong

**No reasons are stored.** Per grader per run the JSON keeps `judgeVotes` (three votes) and `evidence` (the final reply); `explanation` is only `judge votes: PASS PASS PASS` (K0-a446e4e46d, K0-dc11561567, K0-c11d398397). Do not promise the judge's reasoning; it must be reconstructed.

**The judge is harsh on long replies and long rubrics, mostly against the baseline.** A sonnet judge failed replies a human reading the rubric would pass (K0-dc517e4f1a, K0-b62db52986). Re-judging one case's 36 grader-runs on the same stored replies: `claude -p` with the same model agreed only 0.72, all 10 disagreements being without-arm FAIL to PASS (K0-8c5c9fcd98); through the eval tool as files, the same model agreed 0.97 and an opus judge 0.81, with 6 of opus's 7 disagreements again without-arm FAIL to PASS (K0-633ba95907). A without-arm reply containing every element the rubric asked for (regulation article, deadline wording, portal name, country) still got FAIL x3 from the no-thinking judge while a thinking sonnet passed it; the rubric was 9,500-10,000 characters (K0-f451780ea5). Net: **delta is biased upward**. Say so when a user wants to publish one.

**`claude -p` cannot reproduce the judge.** The eval's judge call runs with thinking disabled and answers in one word; `claude -p --model sonnet` still spent 174-364 thinking tokens with `CLAUDE_CODE_DISABLE_THINKING=1`, `alwaysThinkingEnabled: false` and `MAX_THINKING_TOKENS` cleared, and its verdicts diverged (K0-51517dfab6, K0-75dffd95ab). What does reproduce it: seed the stored reply into a case workspace as a file and point the same rubric at it with `focus: {source: file, path: seed.md}`; that returned the identical FAIL x3 (K0-8c5c9fcd98). Recipe 6.

**Re-read divergent cells, blind and symmetrically.** For every grader cell where the arms differ, take both arms' `evidence`, strip the arm label, shuffle, and read each against the rubric's literal PASS/FAIL wording (K0-dc517e4f1a, K0-1a53242e1b). Recipe 3. Outcomes seen: cells where the judge contradicted the rubric (reply met PASS, judge said FAIL), one where the judge was right and the reader had missed a FAIL clause, and some undecidable from the reply (K0-006a6842e2, K0-054bfc4e7e, K0-95b7c29844). Decision rule used: if correcting the judge would only strengthen the conclusion already reached, record it and do not re-run; re-run only when it could flip the conclusion (K0-006a6842e2).

**Author-written rubrics encode the skill's habits** as pass conditions ("mentions bytes" was the skill's method, not a user need) (K0-afe8cc2f9b, K0-a12ba2a051). State the user's outcome, and have someone who did not write the skill read the rubric once.

## 6. The results JSON (`aggregate-result.json`, `--json`)

- Each grader entry repeats the **whole final reply** in `evidence`. One 5.3 MB file was 4.66 MB of that repetition; across 366 runs the reply was identical between graders in every run (K0-5f501a82d7, K0-77feda6feb). Flatten to one reply per run first (recipe 2): the same file became 1.73 MB with both arms, 0.95 MB without-arm only.
- `evidence` is complete: 1,331 replies, longest 11,582 characters, zero `chars elided` markers (K0-ee431a12e2). Re-read from the JSON; `--keep-temp` is needed only for tool calls and the init line.
- Baseline runs are `cases[].arms.without[]`, with-arm `cases[].arms.with[]`; the agent model is absent (K0-e10a4d1272).
- `claude plugin eval --help` (2.1.312) lists `--model`, `--judge-model`, `--runs`, `--case`, `--json`, and **no flag that forces a skill to fire** (K0-eb000acfb4); see section 8.

## 7. Designing the with/without comparison

- **Standard shape reused across skills:** `claude plugin eval . --runs 3 --ablation with-without --judge-model sonnet [--allow-tools ...] [-j 8]`; invocation counted from tool records; results as a table "what was measured / with / without" with raw fractions (3/3, 1/3) and failures left in (K0-0bdfddd087, K0-275ffea9fd, K0-5e2858b878, K0-7b5553cac4, K0-7186e55325).
- **Dilution.** Cases where both arms score 1.0 pull the mean delta toward zero. A contract-review skill stayed at +0.054 and +0.071 (under the project's own 0.1 bar) because the base model already did the task; the real gap sat in two cells (penalty computation 3/3 vs 1/3, full redline 2/3 vs 0/3) and one cell went the other way (2/3 vs 3/3) (K0-f68f558a5b, K0-89d4ae0e5b, K0-4c4e12a57d). Report per-cell fractions, not only the mean.
- **The baseline can simply win.** For "write a handoff from this pasted transcript" the base model beat the skill in three probes (delta -0.091, -0.088, -0.077); the honest conclusion was "no room for a skill here" with written reopen conditions: a real repo plus shell instead of pasted text, a new base model falling below 0.8 on the same gate, a rival with installs beating the base (K0-dab7a24aac, K0-fb3b09addf). Offer that as a legitimate outcome.
- **Do not compare across tools.** The same prompt to `claude -p --model <opus>` and to the eval's without-arm gave different library versions (iced 0.13 vs 0.14); decompositions done outside the eval are not a without-arm (K0-e10a4d1272).
- **A positive delta is publishable only when** the rubric is not author-biased, every comparison rubric carries the original text, contamination was checked (plugin files and `--keep-temp`), and the expected delta and re-read rule were written before the run (K0-afe8cc2f9b, K0-a12ba2a051). Name which of the four is missing.

## 8. Forced invocation and rival arms

- **Force by prompt, not by flag.** A prompt starting `/skill-name ...` expands the slash into the skill's instructions in the with-arm; a haiku probe showed the skill's own wording in the reply ($0.006) (K0-9f3c9c0606).
- **The without-arm leaks the name.** Given the same `/skill-name` prompt, the baseline answered that `/skill-name` is not installed in this session, so the skill's name entered its context (K0-9f3c9c0606). Run the forced arm with `--ablation none` and pair it with the baseline of the **natural-phrasing** case, never a baseline that saw the slash. Recipe 8.
- **Counting forced invocations.** A slash prompt produces no `Skill` tool call, so `tool_used: Skill` reads 0. The run's first trace line (`type: system`, `subtype: init`) lists the plugin's skills and slash commands as `<plugin>:<skill>`; count a run as invoked when that entry is present (K0-38e8f21712). Recipe 4. A regex grader's default target is also `last_message`, so a pattern for the skill's wording must be in the reply (K0-38e8f21712).
- **Forced vs natural scores were close**: forced fired 21/21 and scored 0.828 vs 0.838 on one gate set, 0.934 vs 0.884 on another (K0-cb995b3ced). Use forced arms for the skill's content, natural arms for triggering; never mix them in one delta.
- **Rival skills.** One team skipped the rival-skill arm whenever the docs-only rival (official docs pasted as context, no skill) had already decided the verdict (K0-a4bcfdeec3, K0-cb995b3ced). Run the cheapest rival first.

## 9. Eval folder and grader format gotchas

- `graders/*.md` body is the rubric; keep PASS/FAIL conditions literal, because section 5's re-read is done against those exact words (K0-006a6842e2).
- To re-judge a stored reply, make a throwaway case whose workspace holds the reply as `seed.md` (`context.scaffold_script` plus `--scaffold`) and a grader with `focus: {source: file, path: seed.md}` (K0-8c5c9fcd98). Recipe 6.
- A scaffold can seed real dependencies: after one that downloaded, compared and unpacked a package, the without-arm read `node_modules/effect/package.json` and answered the version (K0-6f95041daf).
- Keep `examples/` and any fixture that doubles as an answer out of the plugin under test, or under the case directory, which the agent cannot read (K0-8f90233376).
- A 100+ line transcript pasted into `prompt.md` costs per run about what a small suite costs (K0-2bd1d79e6d); prefer a scaffolded repo plus a short prompt.

## 10. Reporting

Use the lines in recipe 9: command and host, per-cell fractions with script-execution counts, cost with the `-j` caveat, blind re-read buckets, the four publishability checks, and - if delta <= 0 - "baseline wins" with reopen conditions.
