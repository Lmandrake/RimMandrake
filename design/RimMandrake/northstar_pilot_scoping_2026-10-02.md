# Northstar pilot scoping (2026-10-02, read-only)
## 1 Chain
- modset tier: modset_builder.py TIERS (src/RimMandrake/Utils/modset_builder.py:92) has graffiti_solo, luminouspigment(_ns), weepingstones_solo, leaningscrub, explosivegrowth_solo... PROVEN in past use (Graffiti live run 2026-10-01 on graffiti_solo per commit e148bae1e).
- path A `modcheck run` (modcheck/runner.py:553): swap MINIMAL + deploy + compose, but NO restart (runner.py:579 comment "caller owns the game restart") -> ensure_playing_map on whatever game is up. Orchestration UNRUN since fix (runner.py:11-23). Last runs: 13 mods all RED within 45 s on 2026-09-13 (modcheck_status.json) = harness wave failure.
- path B northstar_driver/live_session.py (be910cd62, 2026-10-01): stop game -> modset tier -> deploy -> Steam launch -> quicktest -> driver run. UNRUN as a whole (no ledger mention).
- driver run (northstar_driver/cli.py:118): PROVEN live — Graffiti_20261001T161209Z (PASS0 FAIL1 UNM9), Pyrelands_20261001T220547Z (PASS0 FAIL1 UNM19). Never green.
- visual judge judge_cli.py: run once (Graffiti _judged.json).
- record: driver does NOT call record_run (grep empty) -> MISSING: NORTHSTAR_DRIVER_RECORD_STATUS_1 open. modcheck run path records (runner.py:616,637).
- owner layer: modcheck validate/review verbs exist (cli); only needed if walk has hashed north star.
## 2 Candidates (measured by ET parse over src/*/*/About/About.xml, 116 non-ArtOverride mods)
| mod | packageId | defs/patchops/.cs | deps | script state | bars |
|---|---|---|---|---|---|
| IshkoDarkLandmarks | mandrake.rut.ishkolandmarks | 3/0/0 | Odyssey (DLC) + ashkarrlandmarkart (loadAfter) | validation.py 2 chains (get_defs readback, world_landmarks_get); walk 5 must-be-true, 0 arrows, no north star; no tier, no plan | 3 defs resolve w/ category, commonality, Required mutator, icon path |
| Rites | mandrake.rut.rites | 6/0/0 | Antiquities (RED) | validation.py; walk 4 lines/1 arrow | research chain prereqs + research_availability before/after finish |
| StrandedQuest | mandrake.rm.strandedquest | 2/0/0 | none | validation.py 2 chains; walk 7/0 | fire_quest -> lodger arrives; recruit -> goodwill -12. Needs settlement <=32 tiles; random asker |
| BirthHatchDemo | mandrake.rut.birthhatchdemo | 1/0/0 | Biotech (+hidden RSW_Jawa kind) | validation.py; walk 4/0 | egg spawn, 6100 ticks, newborn pawn, egg consumed |
| MSEDroidFix | mandrake.rsw.msedroidfix | 0/0/0 (texture) | OuterRim DroidDepot donor chain | validation.py; walk has DRAFT north star | texture_audit 4 facings — visual-adjacent |

## 3 Recommendation: IshkoDarkLandmarks
Mod status rule (status.py:185-198): no `## north star` -> all-green run records GREEN with no owner step; with a north star: DRAFT-CHECKLIST until `validate --owner-said`, PENDING-OWNER-REVIEW until `review --owner-said`.
1 agent: add arrows to walk must-be-true (§2.3); replace the 'not placed' absence bar with a real behaviour bar if a world landmark set tool exists (else UNCOVERED w/ reason).
2 agent: modset_builder tier `ishko` = Core+DLCs+ashkarrlandmarkart+ishkolandmarks; northstar_plan.py USE_SUITE=True.
3 agent: `run --mock` clean; lint_calls clean.
4 agent: land NORTHSTAR_DRIVER_RECORD_STATUS_1 (driver -> status.record_run) OR use modcheck run (but runner has no restart step, runner.py:579).
5 (optional owner layer) agent drafts 1-2 north-star lines; owner `modcheck validate IshkoDarkLandmarks --owner-said`.
6 agent: bridge take; live_session.py --mod IshkoDarkLandmarks --tier ishko --plan ... (first live use of live_session).
7 agent: rerun until green per debug ladder; record.
8 owner (only if step 5): `modcheck review --owner-said` -> GREEN.

