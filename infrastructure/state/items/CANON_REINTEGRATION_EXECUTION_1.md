# CANON_REINTEGRATION_EXECUTION_1 — continuity handoff for agent reboot

BENCH, 2026-09-04, written at the owner's "prepare for agent reboot" after a
single very long design sitting. **No session context is load-bearing** —
everything ruled is committed; this file is the short map.

## Where truth lives (all current as of this commit)

- `design/Jawa/canon_reintegration_plan.md` — THE master doc. **All fourteen
  §G decision points RULED by owner card**, several expanded beyond the
  offered options; read every §G entry as the ruling of record.
- `infrastructure/state/canon.yml` — caught up (F1, +234 lines);
  `design/Jawa/reconciled_lore/` current through 2026-09-04;
  `narrator_corpus/the_knowing.md` new.
- `design/Jawa/antiquities_design.md` (ruled + owner comment pass),
  `waking_mind_ai_deep_dive.md`, `faction_semipermanent_bases_seed.md`,
  `research_deck_FROZEN_20260904.json` (+ flame amendment recorded in the
  plan, applied to the manifest).
- `infrastructure/output/research_manifest_draft.csv` — **schema v2** (F2):
  532 rows (522 live + 5 Rites pending-restart + 5 planned Antiquities),
  access/holder/theology/stage_gate/live columns; validator + selftests
  extended, 23/23.

## The sequence — F1 ✅ F2 ✅ → next

1. **F3 — the C# manifest pass** (ruled all-C#, G1): StaticConstructor
   loader reads the v2 manifest, rewrites tabs/tiers/costs/prereqs/gates/
   hidden reveals, LOGS LOUDLY on unmatched rows; ResearchRetag (live,
   deployed, active) retires only at proven parity — planned obsolescence,
   dated. Minimal-list restart proves the load; full-list proves content.
2. **F4** — unblock + build `ANTIQUITIES_TREE_BUILD_1` (blocked on owner's
   "do not build yet"; the reintegration sitting has since ruled everything —
   still ask him before unblocking, the hold was his).
3. **Art program** — Urn Reading Station (animated centerpiece) + 8 factory
   modules × 3 restoration states, FIXED order Mill→Loom→Galley→Farm→Press→
   MachiningBay→Apothecary→Assembler ("the urns lock what they unlock").
4. **Three balance letters** (Armoury, xenotype, ideoligion) — approved as
   DRAFTS; his review of each diff still gates deployment.
5. FOUNDRY has four freshly-unblocked items (canal BOTH mechanisms, bespoke
   building shields, MapParent rebase, techprint gating answered by the
   plan's §E grammar).

## Deploy state / restart debt

- `mandrake.rut.rites` + `mandrake.rut.researchretag` deployed AND active
  (ModsConfig 591); **first full-list load not yet taken** — signatures
  waiting in `infrastructure/state/EXPECTED_FAILURES_next_load.md`. The dump
  (589) trails the config (591) until that load's capture; the validator
  says so itself.
- Game DOWN (measured), bridge free.

## Traps learned this sitting (do not relearn)

- rimflow CLI selftests: the probe reads the REAL machine; the
  `RIMFLOW_PROBE=no-reading` seam (probe.py) keeps fixtures sovereign. The
  suite was flipping green/red with the owner's play sessions.
- The validator's check-1 used any-type `cut_name()` and re-reported
  ThingDef/GravForge as a cut research project — now typed; the same trap
  bit two earlier passes.
- refresh.py judges the frozen dump in its own capture dir now
  (design_target_state); the old REPLACED scream was a false alarm.
- `code_review_status.py`, `codebase_health*.py`, `rimflow/cli.py` were
  mid-edit by FOUNDRY at handoff — not committed here, not mine.

## How the owner worked this sitting (worth keeping)

Question cards with trade-offs spelled out, free text always honored — his
free-text answers repeatedly BEAT the offered options and became canon
verbatim (fractal re-reading, the Reclamation, the cast-off grandchildren,
the Cathedral's "I am bound to an Empire that no longer reigns"). Draft his
decisions, never re-derive them; record his words the hour he says them.
