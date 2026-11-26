# Maturation Pipeline: no step waits on the Conductor's hand (section to fold into maturation_pipeline.md)

Item `RIMMANDRAKE_AUTOMATE_MATURATION_HAND_STEPS_MODS_SAT_WAITING`. The owner, 2026-11-15: *"we're not going to just
manually frog walk things along anymore. It's taking days because you let things sit. Get the automation going so things
can keep moving even if that means we have to pause them to fix something. But at least then it's paused animation
instead of manual replication of no automation."*

Code: `src/RimMandrake/rimflow/maturation_autonomy.py`, run inside `maturation_dispatch.py tick` (rm-maturation-dispatch.timer,
60 s). Test: `src/RimMandrake/rimflow/selftest_maturation_autonomy.py`. `design/RimMandrake/maturation_pipeline.md` did not
exist when this was written; whoever writes it folds this section in and deletes this file.

## The four classes

Every mod on every tick is exactly one of:

- **launch**: a builder, blind judge or live driver (the per-stage decision), a **steward run** (the Conductor's old hand
  step, one opus run per state, `steward_cap_tokens`), or a **fixer run** on a road-back item (`fix_cap_tokens`).
- **wait**: on a named live unit, the one game driver (queue position recorded; the longest waiter gets the free game),
  a held bridge, full slots, an account hold, a settling run, or the Designer's own launcher.
- **paused**: stopped, with why and what un-pauses it; `OPS_MATURATION_MOD_PAUSED` (one fixed id) while any mod is paused.
- **owner**: his walk, opening the next version, a Designer turn or owner hold waiting on him; a ready-to-ask card text
  is appended to the Conductor log once per card.

A steward or fixer run is tried once per state key; if it ends and the state has not moved, the mod is PAUSED (no loops:
*"As long as we don't have automated loops rejecting/cycling things, we can't get into too much trouble."*, 2026-11-14).
A wait on nothing named for `stalled_min` (10) raises `maturation.stalled` (`OPS_MATURATION_MOD_STALLED`).
Designer concepts (a `stage.json` under `design/concepts/`) are discovered and seeded; a folder holding
`.maturation-exclude` (test fixtures such as `_dry_walk`) is never discovered.

## Every NEXT string `maturation.py next` emits, and its class

| NEXT (as of 2026-11-15) | class |
|---|---|
| no record: seed it | launch (the tick seeds a Designer concept and lands it) |
| passed: open the next version | owner |
| in-game acceptance blocked | paused |
| launch in-game visit N when the game is free | launch, or wait on the driver/bridge (queued fairly) |
| visit N recorded without an exit block | wait on its live run, else paused |
| visit N exit met | launch (steward confirms and advances to pre_human) |
| visit N exit not met | launch (steward files each failed line, routes back; a fixer per item; visit N+1 when they close) |
| blind challenge blocked | paused |
| launch blind cycle N | launch (up to his CYCLE_LIMIT, 3 per visit) |
| cycle N recorded without an exit block | wait on its live run, else paused |
| cycle N exit met | launch (steward confirms, advances to in_game) |
| cycle N exit not met | launch (steward routes, opens the next cycle); paused at three cycles (the Conductor decides) |
| offline build: build the missing checks | launch (capped builder) |
| designer/intake: version or lock refusal | owner (lock, his turn) or wait (the Designer's launcher) |
| preflight / pre-human refusal | launch (steward runs the stage) |
| any other refusal (hold, version mismatch) | paused |
| hand step steward_confirms / walk_bars_confirmed | launch (steward) |
| hand step owner_said | owner |
| hand step conductor_decision (fourth cycle) | paused |
| every exit test passes | launch (steward advances) |
| locked change with no look after it (stage.json) | launch (steward chain: re-pin, exam retake, one coverage look) |

Counts over the 21 rows: launch 12 (the visit launch can first wait on the game, any launch on a slot), wait-else-paused 2, paused 4, owner 3 (the designer row can instead wait on the Designer launcher). No row is a Conductor hand step.

## Not done here

- SteveDesktop running pipeline in-game checks in parallel: `RIMMANDRAKE_FEED_STEVE_GAME_PIPELINE_VISITS_SECOND_DRIVER`.
- An owner card answer (`--by-card`) usable by `concept_tree certify` / `designer_stage repin`: the Knockback refusal is
  diagnosed on `RIMMANDRAKE_RECERTIFY_KNOCKBACK_TREE_AFTER_HIS_OWN_REWORDING` (closed); the rule change is the Divergent
  item `RIMMANDRAKE_CARRY_OWNER_CERTIFICATE_THROUGH_HIS_OWN_CARD_EDIT`, left to him. Until then that state is OWNER: the
  steward brief writes the card text, never certifies.
