# Recipes - paste-ready commands and scripts

Written so they can be handed to a user in a text reply. Each names the pitfall it answers (ids in `pitfalls.md`). Scripts avoid assuming undocumented key names: they walk the JSON and look for the documented/observed keys `cases`, `arms`, `with`, `without`, `evidence`, `judgeVotes`, `passed`, `scored`, `costUsd`, `judgeCostUsd`.

## 1. Windows: clean PATH for the eval shell (K0-899caa909f, K0-47b3f0b3d2)

PowerShell:

```powershell
$env:PATH = ($env:PATH -split ';' | Where-Object { $_ -notmatch 'WindowsApps' }) -join ';'
claude plugin eval . --ablation none --runs 3 --judge-model sonnet --no-publish
```

Git Bash:

```bash
clean=""
IFS=':' read -ra parts <<< "$PATH"
for p in "${parts[@]}"; do
  case "$p" in *WindowsApps*) continue;; esac
  clean="${clean:+$clean:}$p"
done
PATH="$clean" claude plugin eval . --ablation none --runs 3 --judge-model sonnet --no-publish
```

Picking a real Python in hooks or helper scripts on the PC (skips the Store stubs):

```bash
for p in python3 python py; do
  q=$(command -v "$p") || continue
  case $q in *WindowsApps*) continue;; esac
  PY=$q; break
done
"$PY" -I your_script.py
```

Do not add `--allow-tools Bash` on native Windows: every run errors and judges still bill (K0-b612491c13).

## 2. Flatten the results JSON to one reply per run (K0-5f501a82d7, K0-ee431a12e2)

```python
# flatten_results.py  <aggregate-result.json>  -> runs.jsonl (one line per run)
import json, sys
doc = json.load(open(sys.argv[1], encoding="utf-8"))

def graders_in(obj, out):
    if isinstance(obj, dict):
        if "evidence" in obj:
            out.append(obj)
        for v in obj.values():
            graders_in(v, out)
    elif isinstance(obj, list):
        for v in obj:
            graders_in(v, out)
    return out

with open("runs.jsonl", "w", encoding="utf-8") as f:
    for case in doc.get("cases", []):
        for arm, runs in (case.get("arms") or {}).items():
            for i, run in enumerate(runs or []):
                gs = graders_in(run, [])
                replies = {g.get("evidence") for g in gs}
                row = {
                    "case": case.get("name"), "arm": arm, "run": i,
                    "error": run.get("error"),
                    "graders": [{k: g.get(k) for k in ("name", "passed", "scored", "judgeVotes", "explanation")} for g in gs],
                    "reply": gs[0].get("evidence") if gs else None,
                    "reply_variants": len(replies),   # expected 1; >1 means graders saw different text
                }
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
print("wrote runs.jsonl")
```

`reply_variants` was 1 for all 366 runs measured; if it is not, the graders used different `focus` values and you must keep them apart.

## 3. Blind re-read of divergent cells (K0-dc517e4f1a, K0-006a6842e2)

Produces `reread.md` with arm labels removed and order shuffled, and `reread-key.json` to open only after judging.

```python
# blind_reread.py  runs.jsonl  -> reread.md, reread-key.json
import json, random, collections
rows = [json.loads(l) for l in open("runs.jsonl", encoding="utf-8")]
cells = collections.defaultdict(lambda: {"with": [], "without": []})
for r in rows:
    for g in r["graders"]:
        if r["arm"] in ("with", "without"):
            cells[(r["case"], g["name"])][r["arm"]].append((r["run"], bool(g["passed"]), r["reply"]))

items, key = [], {}
for (case, grader), arms in cells.items():
    pw = sum(p for _, p, _ in arms["with"]); po = sum(p for _, p, _ in arms["without"])
    if not arms["with"] or not arms["without"] or pw == po:
        continue
    for arm in ("with", "without"):
        for run, passed, reply in arms[arm]:
            items.append((case, grader, arm, run, passed, reply))
random.shuffle(items)
with open("reread.md", "w", encoding="utf-8") as f:
    for n, (case, grader, arm, run, passed, reply) in enumerate(items, 1):
        label = f"R{n:03d}"
        key[label] = {"case": case, "grader": grader, "arm": arm, "run": run, "judge_passed": passed}
        f.write(f"\n\n# {label}  case={case}  grader={grader}\n\n{reply}\n")
json.dump(key, open("reread-key.json", "w", encoding="utf-8"), indent=1)
print(len(items), "replies to read; verdicts go next to each label, then open reread-key.json")
```

Read each reply against the rubric's literal PASS/FAIL wording and write PASS/FAIL beside the label. Then compare with `judge_passed` in the key. Report three buckets: judge contradicted the rubric, judge was right, undecidable from the reply. Re-run the suite only if correcting the judge could flip the conclusion.

## 4. Count tool calls and forced invocations from `--keep-temp` traces (K0-737da892bc, K0-38e8f21712)

```python
# trace_counts.py  <skill-name>  <kept-dir> [<kept-dir> ...]
# For each transcript: tool-call counts by tool name, and whether the init line lists the skill.
import json, sys, pathlib
skill = sys.argv[1]
for root in sys.argv[2:]:
    for path in pathlib.Path(root).rglob("*.jsonl"):
        tools, init_has_skill = {}, False
        with open(path, encoding="utf-8", errors="replace") as f:
            for i, line in enumerate(f):
                try:
                    msg = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if i == 0 or (msg.get("type") == "system" and msg.get("subtype") == "init"):
                    blob = json.dumps(msg, ensure_ascii=False)
                    init_has_skill = init_has_skill or (skill in blob)
                def walk(o):
                    if isinstance(o, dict):
                        if o.get("type") == "tool_use" and "name" in o:
                            tools[o["name"]] = tools.get(o["name"], 0) + 1
                        for v in o.values(): walk(v)
                    elif isinstance(o, list):
                        for v in o: walk(v)
                walk(msg)
        print(path, "| init lists skill:", init_has_skill, "| tools:", tools)
```

Use it for two counts the score hides: (a) per with-arm run, did `Bash` (or the skill's post-check script) actually execute; (b) in a forced-invocation arm, which runs had the skill loaded (`init lists skill: True`), since `tool_used: Skill` reads 0 for a slash prompt.

## 5. Check how much `-j` inflates the judge share of COST (K0-dea4b2d738)

Run one small case twice, identical except for concurrency, then compare:

```bash
claude plugin eval . --case <one-case> --runs 2 --ablation none --judge-model sonnet -j 1 --json j1.json --no-publish
claude plugin eval . --case <one-case> --runs 2 --ablation none --judge-model sonnet -j 2 --json j2.json --no-publish
```

```python
# judge_cost.py j1.json j2.json
import json, sys
def sums(path):
    doc = json.load(open(path, encoding="utf-8")); total = doc.get("costUsd"); judge = 0.0
    def walk(o):
        nonlocal judge
        if isinstance(o, dict):
            if isinstance(o.get("judgeCostUsd"), (int, float)): judge += o["judgeCostUsd"]
            for v in o.values(): walk(v)
        elif isinstance(o, list):
            for v in o: walk(v)
    walk(doc); return total, judge
for p in sys.argv[1:]:
    print(p, "costUsd=%s  sum(judgeCostUsd)=%.3f" % sums(p))
```

Measured once: $0.079 at `-j 1` vs $0.147 at `-j 2` for the same two judge items. Quote `-j 1` figures when the cost itself is the claim.

## 6. Re-judge a stored reply with the real judge (K0-8c5c9fcd98, K0-51517dfab6)

`claude -p` does not reproduce the judge (thinking stays on). This does: a throwaway case whose workspace already contains the reply.

`evals/rejudge-01/case.yaml`
```yaml
schema_version: "1.1"
name: rejudge-01
context:
  scaffold_script: seed.sh
```

`evals/rejudge-01/seed.sh` (embed the reply verbatim; byte-identical text matters)
```bash
#!/usr/bin/env bash
cat > seed.md <<'EOF'
<paste the stored reply here, exactly>
EOF
```

`evals/rejudge-01/prompt.md`
```markdown
---
max_turns: 1
---
Reply with the single word: done
```

`evals/rejudge-01/graders/<same-grader-name>.md`
```markdown
---
type: llm
focus: { source: file, path: seed.md }
---
<paste the original rubric body, unchanged>
```

Run from the plugin root (Linux/macOS/WSL2; the scaffold is a Bash script):

```bash
claude plugin eval . --case rejudge-01 --runs 1 --ablation none --scaffold --judge-model <same judge as the original> --json rejudge.json --no-publish
```

Compare `judgeVotes` with the original. To test judge sensitivity, repeat with `--judge-model opus`; in the measured case opus flipped 6 of 7 disagreements toward PASS on without-arm replies (K0-633ba95907).

## 7. Contamination grep before a run (K0-afe8cc2f9b, K0-8f90233376)

For each case, take two or three distinctive phrases from the rubric's PASS condition or the expected answer and search the plugin tree excluding the eval directory:

```bash
grep -rIl --exclude-dir=evals --exclude-dir=.git --exclude-dir=results -e "phrase one" -e "phrase two" .
```

Any hit inside `skills/`, `examples/`, or a bundled fixture means the with-arm can read the answer. Move the file under the case directory (unreadable to the agent) or remove it, then re-run. Keep `--keep-temp` on that run and spot-check one with-arm transcript for the phrase.

## 8. Forced-invocation arm, paired correctly (K0-9f3c9c0606)

```bash
# natural phrasing, both arms (triggering + baseline)
claude plugin eval . --case <case> --runs 3 --ablation with-without --judge-model sonnet --json natural.json --no-publish
# forced: prompt body begins with "/<skill-name> ..."; with-arm only
claude plugin eval . --case <case>-forced --runs 3 --ablation none --judge-model sonnet --json forced.json --no-publish
```

Report: triggering = natural with-arm `tool_used: Skill`; content effect = forced with-arm vs natural without-arm; never a forced without-arm (it has seen the skill's name).

## 9. Reporting lines to copy

```
Run: claude plugin eval . --runs 3 --ablation with-without --judge-model sonnet -j 8 (Claude Code 2.1.312, Linux container, bubblewrap+socat)
Cost: $X.XX as reported by the tool (list price; -j 8, judge share inflated - see recipe 5)
Scripts executed in with-arm runs: N of M (trace count, recipe 4)
Divergent cells re-read blind: K judge-vs-rubric contradictions, L upheld, U undecidable
Publishability: rubric not author-biased [ ]  originals pasted into comparison rubrics [ ]  contamination grep + keep-temp check [ ]  expectation and re-read rule written before the run [ ]
```
