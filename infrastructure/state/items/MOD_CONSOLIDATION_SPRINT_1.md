# MOD_CONSOLIDATION_SPRINT_1

## Spec
Execute `infrastructure/state/mod_consolidation_map.csv` (103 rows, the
single source of truth — patch it, never re-derive) per
`design/MOD_CONSOLIDATION_PLAN.md` §4 (v3, SIGNED OFF 2026-09-08 on
MOD_NAMING_CONSOLIDATION_AUDIT_1). 77 → 53 mods; RM 21 / RSW 12 / RUT 20.

🔴 The game-down window is MECHANICAL ONLY: git mv, About merges,
packageId consolidation, MayRequire rewrite from the map, tier-move
defName re-prefix (R4, Phase-2 machinery), ModsConfig swap, redeploy,
refresh.py, naming_lint zero, validate_patch --live/--defs, magenta
sweep, minimal-list load. NO authoring in-window.

GATES (must be closed before the Chronicle/Property/Pursuit/Graffiti/
Pyrelands rows execute; the rest of the map does not wait):
- CHRONICLE_EVENT_SPINE_1 (hook points named before those merges)
- GRAFFITI_GENERIC_MARKS_1 (RM Graffiti needs default content to ship)
- PYRELANDS_GENERIC_TEXT_1 (self-contained biome text + donor BiomeDef)

Write-freeze during the window: rimflow blocking item + the temporary
PreToolUse src/ hook (NAMING_SCHEME_PLAN §5 Phase 2 precedent).
Hard ordering: this sprint → regenerate .rid/.xtp → world re-import →
only then any world freeze.

## Verify
Per-destination def-count reconciliation vs sources (plan §4's
lost-nothing check); naming_lint 0 violations; MayRequire checker 0;
minimal-list load clean; every VERIFY row on the map resolved or
explicitly re-parked with reason.

## Criteria
All 103 map rows executed or re-parked; counts reconcile; owner told
scheduling was his call — do not start without his go.

## Game-down window runbook — prepared 2026-09-08 (BENCH)

15 dying ids are ACTIVE in live ModsConfig (MEASURED against the live file).
Swap old→new (dedupe after — several map to one destination):
```
mandrake.rut.factionslate -> mandrake.rut.patches
mandrake.rsw.beastnorm -> mandrake.rsw.swbestiary
mandrake.rsw.seabeasts -> mandrake.rsw.swbestiary
mandrake.rm.sauridfrillfix -> mandrake.rm.patches
mandrake.rm.gravshipastronautfix -> mandrake.rm.patches
mandrake.rm.toolbeltfix -> mandrake.rm.patches
mandrake.rsw.blastdoorframeasyncfix -> mandrake.rsw.patches
mandrake.rm.researchkiteastfix -> mandrake.rm.patches
mandrake.rm.desertvehiclereskin -> mandrake.rsw.desertvehiclereskin
mandrake.rsw.jawaikee -> mandrake.rsw.swbestiary
mandrake.rsw.fireecology -> mandrake.rm.pyrelands
mandrake.rut.fireecology -> mandrake.rut.fireecology
mandrake.rm.salvageclaim -> mandrake.rm.property
mandrake.rm.theft_hauler -> mandrake.rm.property
mandrake.rut.shell -> mandrake.rut.menushell
```
Then: deploy_custom_mods.py plan → --apply; refresh.py; minimal-list load proof.
Game must be DOWN for the swap+deploy (ModsConfig describes the NEXT load).

## Repo-side execution COMPLETE — 2026-09-08 (BENCH, waves A+B)
Executed: 5 wave-A cluster merges · global pass (23 ids, 32 files) ·
Armoury extractions · R4 re-prefix (120 defs + RSW_WS_/RSW_FE_) · 4+1
assemblies rebuilt 0W/0E · tombstone removed · selftests 45/45 ·
def-count differential 4430→4433, the +3 attributed to FOUNDRY's swept
ModulePersonality WIP (sprint net ZERO — lost nothing).
src/ write freeze CLOSED — repo-side moves done.

STILL OPEN on this item:
- Game-down runbook above (ModsConfig 15-id swap, redeploy, refresh.py,
  minimal-list load proof) — needs the next real down-window.
- Gated rows: Chronicle/Pursuit renames (CHRONICLE_NINEFOLD_DECOUPLE_1),
  Graffiti/Salvation split (GRAFFITI_GENERIC_MARKS_1), Pyrelands
  finish (PYRELANDS_GENERIC_TEXT_1).
- VERIFY rows: Absorbed_SovSith_Misc duplicate-species compare;
  SeasWaterline + BirthHatchDemo fates (owner-parked, R14).
- Incident recorded: DROIDWORKS_WIP_SWEPT_NOTICE_1 (BENCH directory-add
  swept FOUNDRY's uncommitted Droidworks WIP into 0f7da95c; preserved,
  misattributed; explicit file lists used from then on).

## PROOF LOAD PASSED — 2026-09-09 (BENCH game window)
Root cause of the first failed load: the ModsConfig dedupe kept DONOR
slots — all three load-last patch catch-alls fell to mid-order
(UtinniPatches 582→188), aborting play-data load in AlphaGenes'
implied-gene pass. Lists rebuilt (destination keeps own slot, else last
donor's; fc103b59). Second full load: UP in ~17 min, 590 active, zero
texture errors (was 3,260), zero play-data exceptions, harvest at
baseline everywhere except +6 config-error lines belonging to FOUNDRY's
DW armor modules (filed DROIDWORKS_MODULE_SMELT_CONFIG_1). Fresh dump
captured (2026-09-09T01-54-07Z). Karrask latent bugs fixed and proven
(0 hits). Runbook CLOSED; bridge released; FOUNDRY safe to restart.

⚠️ R9 fork escalated to owner (Pyrelands agent, 2026-09-09): Pyrelands
has NO BiomeDef of its own — the "biome" is the donor's ZBiome_Grasslands
(zylle.morevanillabiomes) patched in place by the RUT wiring. "Self-
contained" requires authoring/absorbing a BiomeDef — owner picks: absorb
now (donor-retirement coordination) or keep the dep and amend R9's
promise. About.xml's "self-contained" claim is currently wrong; held for
the ruling.

## World + gravship saves MIGRATED to the new names — 2026-09-08 evening (BENCH, bridge window)
Offline migration (Transient/load_verify_save.py pattern): text defNames
word-boundary, meta packageIds, and grid shortHashes remapped via the
pre/post-rename dump pair (old 00-19Z / new 01-54Z captures). V23→V24:
63 text + 15 meta + 492 topGrid terrain cells (RM_FE_Ground_*);
gravship e→f: 83 text + 15 meta, no grid hits. Both loaded live
(RUT_Jawa_* factions PRESENT, old names absent), canonically re-saved
in-game, slot audits clean (only their own files changed; gravship
identity proven by GravEngine content check). Saves dir pruned to the
4 keepers on the owner's order (deleted-unverified until next-launch
count, per the Steam Cloud lesson). Pre-migration originals in
Transient/. STILL OWED: .rid/.xtp regeneration before worldgen/freeze
(build_salvation_rid.py) — unchanged by this.
