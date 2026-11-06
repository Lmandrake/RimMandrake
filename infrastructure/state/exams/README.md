# Acceptance exams (RELENTLESS_BUILD_EXAM_BEFORE_BUILDER)

An exam is written BEFORE an item is built, by a Setter that is not its builder (redesign_final.md §2 G3/G4, §3.2).
The builder sees it and may not edit it. Code: `src/RimMandrake/rimflow/relentless_exam.py`; config: `relentless_exam.json`.

## Where exams live

- **shadow** (now): in the supervisor store, never in a builder's clone:
  `/home/mandrake/rm/relentless/store/exams/<ITEM>/`
  - `owed.json`: state `owed | setting | validated | arbiter_owed | setter_failed`, base sha, refusals, `origin` (`first_contract`, or `start_backfill`: an item contracted before the hook, owed at its next start).
  - `setter/exam.json`, `setter/files/`: what the Setter wrote. `setter.out`: its run.
  - `validation.jsonl`: one VALIDATE verdict per attempt (refusals and every run's exit and kind).
  - `exam.json` + `files/`: the frozen exam once validated, with `exam_hash`, `base_sha` and the Setter's session.
  - `catch.jsonl`: the exam run at each candidate a Marker returned, and at the done sha.
- **live** (later, after the shadow sample): this directory, one `<ITEM>.json` per item.

## exam.json

```json
{"item": "X_Y_Z", "base_sha": "...", "exam_hash": "<sha256>", "setter": {"session": "...", "model": "opus"},
 "clauses": [{"id": "c1", "says": "<the clause, quoting the item>", "kind": "behaviour | artifact | live | owner",
              "check": {"argv": ["python3", ".exam/test_x.py"], "timeout_s": 300, "red": {"exit": [1], "marker": "FAIL"}},
              "break": {"kind": "base_red"}}],
 "maps": {"<sentence copied verbatim from the item>": ["c1"]}, "no_code": false}
```

`.exam/<name>` in an argv is a Setter file, copied into the tree at `.exam/` for every run.
`break.kind`: `base_red` (new behaviour: the check fails on the base sha) or `patch` (preserved behaviour: green on base,
red once the planted unified diff is applied).

## VALIDATE refusals (no agent; a refused exam gets one resumed Setter turn, a second refusal goes to the arbiter)

| code | meaning |
|---|---|
| `EXISTENCE_ONLY` | a behavioural clause checked by existence/grep only (test, ls, grep, cat, a python -c that only tests a path) |
| `ARTIFACT_NOT_ASKED` | `kind: artifact` where the item asks for no artifact |
| `RED_NOT_ASSERTION` | the red was an ImportError, missing file/tool, SyntaxError, timeout, exit 2/124/126/127, an undeclared exit, or a missing marker |
| `STAYS_GREEN` | `base_red` passes on base, or the check passes under its planted break |
| `BASE_NOT_GREEN` / `PATCH_FAILED` | a `patch` clause not green on base / a break that does not apply |
| `BREAK_DELETES` | the break deletes the file the check names, or only deletes files |
| `MAP_UNKNOWN_SENTENCE` / `MAP_UNMAPPED_CLAUSE` / `MAP_DONE_WHEN` | maps not the item's words / a clause no sentence maps / a `## Done when` bullet unmapped |
| `SCHEMA` / `BREAK_KIND` | malformed clause / break kind, or a break editing `.exam/` |

`exam_hash` = sha256 of the clauses + maps JSON, the item text, and the sha256 of every file a check argv names.

Hold-outs are not here: the Marker writes them at mark time (G4).

## Reading the shadow

`python3 src/RimMandrake/rimflow/relentless.py reading` → `exam_shadow`: items, states, refusal codes, items with a
Marker verdict against `target` (30), `returns_run` / `returns_caught` (Marker returns the exam would have caught), and
`done_green`. `python3 src/RimMandrake/rimflow/relentless_exam.py summary` prints the same block.
