# The criteria ledger — how a miss becomes a better check

Owner, 2026-10-23: *"If Human live walk notices a problem, look back and improve evaluation criteria or process
that generated the issue."*

The Artist (`src/RimMandrake/rimflow/roles/artist.md`) studies these entries and keeps what they show in
`design/RimMandrake/art_style_memory.md`. This procedure is unchanged: it is how a pattern there reaches the pipeline.

`infrastructure/state/art_eval/criteria_ledger.jsonl`, append-only events, written only by `ledger.py`:

```json
{"event": "add", "id": "CL-001", "at": "<iso>", "subject": "RM_Shadefern", "template": "plant",
 "source": "owner_override | live_walk | owner_key | agent_review", "owner_said": "<his words, required for
 owner_override and live_walk>", "missed": "<what the pipeline got wrong, concretely>",
 "pipeline_decision": "REGEN", "run": "<run id>"}
{"event": "fix", "id": "CL-001", "at": "<iso>", "change": "<which check / prompt line / policy row changed, and how>",
 "files": ["<paths>"], "versions_after": {"preamble": "preamble@v1", "...": "..."},
 "regression": "RM_Shadefern:B", "expect": "ACCEPT"}
```

Sources: `owner_override` (his answer on a shadow sheet — `shadow.py ingest` writes these), `live_walk` (he saw it
in game), `owner_key` (the pipeline disagrees with a verdict he already gave on an older sheet), `agent_review`
(a seat found it; never enough alone to change a blocking rule).

## The procedure (same day)

1. `ledger.py add …` — the miss, in concrete words, with his words when he gave them.
2. Find the cause. Exactly one of:
   - **a missing constraint** → a new line in `design/RimMandrake/art_judge_brief.md` sourced to his words, and a
     code in `severity_policy.md`;
   - **a constraint no question asked** → a new checklist item in the template;
   - **wrong severity** → move the code or add a `polish_when` fact in `severity_policy.md`;
   - **a card defect** (a panel missing, a reference unlabelled, a fact not given) → `cards.py`;
   - **a prompt that misled** → the prompt, version bumped.
3. Bump the `<!-- version -->` / `"version"` of every file changed.
4. `ledger.py fix CL-NNN --change … --files … --regression DEF:LETTER --expect ACCEPT|NOT_ACCEPT`.
5. `runner.py regress` — every row passes on the new versions, or the change does not ship.
6. Commit the ledger, the regression row, the changed files and the regression run together.
Criteria-ledger ids (CL-NNN) collide across seats (two clones minted the same id and `./publish` refused the replay): mint the id from origin/main's tail right before committing, or key it by seat. A ruling that changes how art is MADE (prompt template, house register) must change how it is JUDGED in the same change: a no-outlines ruling reached the generator prompt but the judge brief (B1/B2) and `art_checks.outline_coherence` kept the outline clause for a month, so compare picked keyline-free regens while outline_coherence flagged them (guard: `selftest_art_judge_no_keyline.py`).

## Restraint

One owner verdict is one data point. When a fix would flip other subjects he ruled the other way (pilot §6: a blunt
"Earth animal → REDO" also flips Burrak and Vobbal), leave the entry OPEN with what is known and wait for the
second case, or ask him on the shadow sheet. Never tune a prompt until it agrees with one sitting's key —
`evaluation-independence`.

## Entries so far

`python3 src/RimMandrake/Utils/art_eval/ledger.py list` — the ledger is the record; this file never copies it.
