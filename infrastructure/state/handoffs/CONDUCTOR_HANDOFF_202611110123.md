# CONDUCTOR_HANDOFF_202611110123 — READ FIRST on wake

First handoff for this seat.

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next session hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
This was a one-request session on the **Work Desktop Mac**, not in a seat clone: the owner asked for one ticket and got it. Nothing was built, nothing was claimed, the bridge was never taken. The thing worth carrying is the substance of what was read, not how it was done — Warp's `cloud-factory-demo` has one mechanism we provably lack: a **daily loop that edits the reviewing agent's own instructions from how humans reacted to its review comments** (`improve-review-pr.yml`). Our `rm-findings-judge.timer` judges findings; nothing turns the owner's pushback into an edit of the brief. That is the whole reason the ticket exists and the reason its name says the reviewer rewrites itself. (filed: lessons)

## Session context (a Mac window, not a seat)

- cwd was `/Users/mandrake/dev/RimMandrake` on the Desktop Mac — **not** `/home/mandrake/rm/bench`. `./publish` worked from here and landed on origin/main.
- No `RIMFLOW_SEAT` is exported in this window, so every `rimflow` and `./game` call needs `RIMFLOW_SEAT=Conductor` inline (it refuses rather than guessing, correctly).
- `./game` here reads `running: UNMEASURED (could not run tasklist.exe)`, `recorded: DOWN` — a Mac cannot see the Windows game process. Do not read that UNMEASURED as a fault.

## What the owner should see

<!-- Findings that need the owner's eye or decision: a number nobody ruled on, a change they can veto, anything shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- **The ticket he asked for is filed and pushed:** `RIMMANDRAKE_STUDY_WARP_FACTORY_REVIEWER_REWRITES_ITSELF`, for BENCH, kind `design`, needs `offline`, state **proposed** (not claimed, not started). Prose: `/Users/mandrake/dev/RimMandrake/infrastructure/state/items/RIMMANDRAKE_STUDY_WARP_FACTORY_REVIEWER_REWRITES_ITSELF.md`. Commit `e727ac60c28a`, verified an ancestor of origin/main.
- **It is scoped as a study, not a build** — the deliverable is a comparison doc in `design/RimMandrake/` plus named follow-up items. He may want it narrower or wider; that is vetoable now, before anyone claims it.
- **Three ideas from their repo are worth his opinion**, and the ticket asks each as a question rather than proposing it: (1) a reviewer that rewrites its own brief from his reactions; (2) verification fanned out one worker per acceptance criterion instead of one serial walkthrough — our bridge's one-writer rule may forbid this regardless of merit; (3) their `PRODUCT.md` + `TECH.md` + `validate-changes-match-specs` against our Designer concept folder + `concept_tree.py gate`.
- **Nothing in their repo was executed.** Their install path is `curl | bash` plus `npx skills add`, and the ticket forbids running it; the study is read-only. Flagged deliberately.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_OR_TOPIC — state; NEXT: <one imperative action>`. A pointer without a NEXT: measured ~0% pickup; with one, near-100%. -->
- `RIMMANDRAKE_STUDY_WARP_FACTORY_REVIEWER_REWRITES_ITSELF` — filed and pushed, proposed, nobody claimed it; only the README was read, none of the skill files or workflow YAML; NEXT: run it under **Codex**, not Claude (BENCH_REBOOT_HANDOFF_202611101050: Claude nearly out for the week, owner 2026-11-09 *"Please switch to as much of the work as possible done by GPT."*), starting by reading `.agents/skills/improve-review-pr/SKILL.md` and `templates/github/workflows/improve-review-pr.yml` in a clone under the agent-storage root.
- BENCH's own pointers are untouched and remain BENCH's: this was a Conductor window on the Mac with no seat exported, and it picked up none of them. NEXT: read `infrastructure/state/handoffs/BENCH_REBOOT_HANDOFF_202611101050.md` in the BENCH seat, not here.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives — append it to the lessons file the moment it is learned, then cite `(filed: LESSONS)` or `(see: <doc>)`. Never re-explain a trap that is already recorded. -->
- `rimflow file --for` takes only the readers in `alarm_routes.json`, and the ledger's history of 2569 FOUNDRY / 522 RELENTLESS filings is not a menu of them (filed: lessons, `20261111T012519Z-CONDUCTOR-rimflow-file-for-accepts-only-readers.md`).
- `lessons.py add` without `--home` warns but still writes the file, so a lesson lands unowned unless you notice the WARN and refile (see: this handoff; the first copy was deleted and rewritten with `--home skills/using-rimflow`).
- A GitHub README is the demo's own advertisement: Warp's claims five working stages and admits Monitoring unbuilt, so the ticket requires every claim sourced to a `SKILL.md` or workflow YAML before it is believed (see: the item's own `## Watch out`).

## Commits

```
e727ac60c2 ticket: examine Warp's cloud-factory-demo against our pipeline
1d31bf7a03 ledger: RUNNER ingest of 1 testq job(s)
1b03251550 ledger: RUNNER ingest of 1 testq job(s)
911e4bea24 design: TheSump owner answers (3 of 3, by card)
610dce8986 ledger: RUNNER ingest of 1 testq job(s)
c4b0091fc9 ledger: RUNNER ingest of 1 testq job(s)
a1edffcc55 ledger: RUNNER ingest of 1 testq job(s)
24ac2557bf ledger: RUNNER ingest of 1 testq job(s)
c4600c7f93 design: GelatinousSlime owner answers; lesson: Designer questions skip UI
263a507cc0 ledger: RUNNER ingest of 1 testq job(s)
cd46b894f4 ledger: RUNNER ingest of 1 testq job(s)
4c8f58c3b8 ledger: RUNNER ingest of 1 testq job(s)
22c70a84cc ledger: RUNNER ingest of 1 testq job(s)
96d7551ff4 ledger: RUNNER ingest of 1 testq job(s)
a44c973d5b ledger: RUNNER ingest of 1 testq job(s)
b313ae2eff ledger: RUNNER ingest of 1 testq job(s)
eba6cf433f design: LongShade owner answers; colonist shade-seeking is one cross-biome rule
5963e43d18 ledger: RUNNER ingest of 1 testq job(s)
76d1f2c881 ledger: RUNNER ingest of 1 testq job(s)
d1f0edd71c ledger: RUNNER ingest of 1 testq job(s)
... 10 more: git log --oneline -30
```

## Game and bridge state

- **bridge: FREE** — never taken this session (`rimflow bridge who` → `bridge FREE`). `infrastructure/state/BRIDGE` is empty.
- **game: recorded DOWN**; live reading UNMEASURED because this is a Mac window and `tasklist.exe` is unreachable from here. Nothing was deployed and no restart was called.
- No subagents, background tasks or workflows were started, so none are running or stale.

## Tree state at wrap

- upstream: origin/main, pushed

Working tree clean.

