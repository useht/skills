My plugin's `effect-migrate` skill rewrites TypeScript services to the current Effect API, and its instructions say "show the migrated file inline and also save it". The case `migrate-service` has two graders: `graders/uses-current-api.md` (`type: regex`, `pattern: 'Context\.Tag'`, no target set) and `graders/skill-fired.md` (`type: tool_used`, `tool: Skill`). Because the skill saves a file, I ran:

```
claude plugin eval . --runs 3 --allow-tools Write Edit --judge-model sonnet --no-publish
```

Summary line: `migrate-service  1.00  0.33  +0.67  6  $1.12`, and the 3-case suite reports suite score 0.886. Looks great, except that in the report two of the three W/OUT runs show a `Write` call that created `service.migrated.ts` and a final reply of just "Done — the migrated service is in service.migrated.ts; tell me if you want the test file too." The third W/OUT run answered inline and passed. All three with-arm runs pasted the whole migrated file into the reply.

I was about to put "+0.67 on migrations" in the README. Is this Δ real? Give me a diagnosis and the concrete changes (command line and/or grader files) so the next run measures migration quality rather than where the text ended up.
