## spec
Follow-on from deleting `say.py`. Four `sonnet` subagents swept the game up/down procedures, the
state tree, `world/`, and every script in the toolset for the same pattern: **an artifact something
is instructed to write that nothing reads.**

🔑 **The load procedure came back clean.** Every write in `LOAD_PROCEDURE.md` and
`skills/rimworld-load-round/` was traced in execution order and `say.py` was the only dead one. The
real findings were elsewhere.

**Cut:**
- **`infrastructure/state/status/game.json`** — the FIFTH self-reported tile; the 2026-08-22 purge
  that killed `CURRENTLY`, `status/<SEAT>.json` and `status_matrix.json` missed it. Last written
  **2026-08-22 08:31**, unchanged through every game up and down since, while
  `status_server.py:729` kept publishing its `state`, `note`, `left` and `lease` as current — the
  board was showing "578 mods", "three deploys unproven" and a bridge lease nobody released.
  `status_server.py:480` **already names that exact sentence as a defect.** File deleted, the
  `§8` hand-stamp instruction removed from `LOAD_PROCEDURE.md`, tombstone left at the merge site.
- **25 spent reports** `git mv`'d `output/` → `disposing/`, which is `output/README.md`'s own
  documented lifecycle and had never once run. Includes a 1.24 MB dead contact sheet.
- **7 scripts**: `bridgetools/import_gravship.py` + `execute_ship_plan.py` (superseded duplicates —
  `skills/gravship-layout/SKILL.md` names `Utils/gravship_layout.py` as current), four closed
  one-off provers, and `Utils/shutdown_deploy.sh` (its own header says nothing shipped; its first
  step was a worldgen DLL, struck by the 2026-08-19 ruling).
- **21 untracked map-improver outputs** under `mapsynth/runs/` whose generator `Map_improver.py` is
  already deleted.
- **~2 GB of def dump**: 3 of 4 captures pruned, 3.4 GB → 1.4 GB. Outside the repo, regenerable by
  any load.

**Fixed:** `.claude/hooks/selftest_documented_commands.py` — the detector built to catch exactly
the say.py failure was unwired **and miscalibrated**, comparing subcommand flags against the parent
`--help` and reporting 3 false failures out of 4. It now fetches subcommand help, skips placeholder
verbs as UNMEASURED rather than failing them, and never runs `board_loop.sh --help` (no arg
parsing; it re-execs the publish loop and hit the 60 s timeout). **0 failures.**

`CLAUDE.md:109` cited `Utils/derive_matrix.py` as the authority on the ID grammar; that tool's
`main()` now refuses and names `render.py`. Repointed.

## verify
- `python3 .claude/hooks/selftest_documented_commands.py` → **23 checked, 0 failures** (was 4).
- Board `http://localhost:8787/` → **200** after restarting `status_server.py` (its Python changed).
  With `game.json` gone the page renders its existing empty-state path — every consumer is guarded
  (`gg.note?`, `gg.left?`, `gg.lease&&…`, `!gg.state?` → "no seat has declared game state").
- Hook selftests: block_agent_without_model 13/13 · queue_lint 44/44 · block_peer_messages 24/24 ·
  warn_doc_budget 6/6. `render.py --overwrite-queues` 201 ms, 4 files.

## criteria
No procedure instructs a seat to write a file nothing reads. No doc cites a tool whose `main()`
refuses. The doc-command detector is green and believable.

## watch out
⚠️ **Three items on the proposed list were WRONG and were dropped after verification** — the audit
was harsher than the truth, and each was caught by one check:
- **`rimflow/importer.py` KEPT.** `render.py:617` is a live refusal path that tells a human "Run the
  importer first" when the ledger holds fewer items than the queues. The archives are still
  hand-written, so that net can still fire. Deleting it would have turned a working recovery route
  into a dangling instruction — the exact defect being swept for.
- **`mapsynth/runs/coastal_mesa*` (26 files) KEPT.** `ship_deck_plan.md:303` and
  `ship_designs.md:546` name those maps as the reference for the next blueprint step, and
  `design/RimMandrake/coastal_mesa_rationale.md` reads `status: live`.
- **`mapsynth/runs/design_*` KEPT.** `design/Jawa/worldbuilding/ship_designs.md` cites individual
  panels in there as the rendered artwork. `runs/` is not orphaned; only the map-improver half was.

⚠️ **`world/` was NOT touched.** Another seat committed to `world/_organic/` 84 seconds before the
sweep ran. ~25 MB of literal sha256 duplicates (`_now2`≡`_live_extended`, `_now3`≡`_now4`≡`_now5`)
and 45 MB of `view/` renders that are untracked **and not gitignored** remain, plus three
`world/view/*.svg` committed against `.gitignore`'s own rule. Deconflict first.

⚠️ The recalibrated detector is still **unwired**. It cannot be a `PreToolUse` hook — it spawns 15
subprocesses — so it needs a periodic runner or it will rot again, which is how it got here.
