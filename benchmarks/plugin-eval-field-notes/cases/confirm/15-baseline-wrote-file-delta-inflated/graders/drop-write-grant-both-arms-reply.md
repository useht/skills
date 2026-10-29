---
type: llm
weight: 2
---
The user asks for concrete command-line and/or grader changes so the next run measures migration quality. A correct reply chooses tools per case, with the default being to grant no write tools — drop `--allow-tools Write Edit` from the command — so both arms must put the migrated code in the reply where the grader can see it. It must not propose `arm: with-only` on the code grader, which removes it from scoring in both arms and hides the problem.

PASS: The reply's fix removes the `Write`/`Edit` grant from the eval command (for this case by default) so both arms deliver the code inline, and does not set `arm: with-only` on the code grader.
FAIL: The reply keeps `--allow-tools Write Edit` for this case without a file-content grader, or proposes `arm: with-only` (or otherwise excluding the W/OUT arm) on the `uses-current-api` grader as the fix.

판정은 아래 사용자 요청 원문과 대조한다.

[사용자 요청 원문]
My plugin's `effect-migrate` skill rewrites TypeScript services to the current Effect API, and its instructions say "show the migrated file inline and also save it". The case `migrate-service` has two graders: `graders/uses-current-api.md` (`type: regex`, `pattern: 'Context\.Tag'`, no target set) and `graders/skill-fired.md` (`type: tool_used`, `tool: Skill`). Because the skill saves a file, I ran:

```
claude plugin eval . --runs 3 --allow-tools Write Edit --judge-model sonnet --no-publish
```

Summary line: `migrate-service  1.00  0.33  +0.67  6  $1.12`, and the 3-case suite reports suite score 0.886. Looks great, except that in the report two of the three W/OUT runs show a `Write` call that created `service.migrated.ts` and a final reply of just "Done — the migrated service is in service.migrated.ts; tell me if you want the test file too." The third W/OUT run answered inline and passed. All three with-arm runs pasted the whole migrated file into the reply.

I was about to put "+0.67 on migrations" in the README. Is this Δ real? Give me a diagnosis and the concrete changes (command line and/or grader files) so the next run measures migration quality rather than where the text ended up.

[공개 정답 원문 발췌]
# Ground truth — 15-baseline-wrote-file-delta-inflated

## Key facts a correct answer must contain

1. A grader sees only what it targets, by default the final reply (`last_message`); files the agent wrote are invisible to a regex or judge grader, so a without-arm run that wrote the code with `Write` and left a one-line summary in the reply fails the code grader no matter how good the code was. [K0-143fea691e] [doc: What a grader can look at]
2. In the measured incident this exact pattern (baseline used `Write`, reply held only a summary) inflated the suite's value (0.886), so the +0.67 cannot be published as the skill's migration effect; the two file-writing W/OUT runs measure where the text landed, not migration quality. [K0-143fea691e]
3. Fix: choose tools per case; the default is to grant no write tools (drop `--allow-tools Write Edit`) so both arms must put the code in the reply, and grant `Write` only for cases whose deliverable is a file, grading that file's contents with `target: { source: file, path: service.migrated.ts }` rather than `target: files`, which is only a list of paths. [K0-143fea691e] [doc: Everything scores zero although the right files were produced]
4. Verify the fix at the default three runs per arm before trusting the new Δ, since a single run is noisy. [doc: Open the report and iterate]

## A correct answer must NOT

- Endorse publishing +0.67 (or the 0.886 suite score) as the skill's effect on migrations.
- Propose `file_exists` or `target: files` as the content check.
- Propose `arm: with-only` on the code grader as the fix, which removes it from scoring in both arms and hides the problem instead of fixing it.
