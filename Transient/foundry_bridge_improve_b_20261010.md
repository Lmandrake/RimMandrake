# FOUNDRY bridge improve B — 2026-10-10

Offline preflight, effective-def lint, experiment manifest, docs.

## Progress
- 12:44 started
- 12:44 read briefs; reading docs
- 12:44 docs read; surveying reusable tools
- 12:46 survey: reusing costlist_resolve_check Sim, run_identity, launch_gate, belt_watchdog KNOWN_LOOPS, check_load
- 12:47 rimsage: costList miss on recipeMaker def = NRE in RecipeDefGenerator.SetIngredients (SetAllow(null).virtualDefs) -> crash path; PlantPurpose={Food,Health,Beauty,Misc}
- 12:49 wrote effective_def_lint.py; testing --src-only
- 12:49 full-list lint run 1 started (python.exe) -> Transient/.edl_full_run1.txt
- 12:50 filed+claimed 4 tickets: PREFLIGHT_BUILD_85_ROWS_OF_HINDSIGHT, EFFECTIVE_DEF_LINT_WIDEN_PAST_DURASTEEL, EXPERIMENT_MANIFEST_BUILD_FREEZE_SIX_CELLS, PREFLIGHT_DOCS_WIRE_ONE_LINE_EACH
- 12:51 run1 restarted after dir-named-*.xml fix; writing preflight.py
- 12:52 run1 finished; reading
- 12:54 triaging run1: biome_worker FP on pocket biomes; AM prestige VPE_Eltex provenance
- 12:55 run2 (fixes: live-iter removal bug inherited from costlist_resolve_check, biome_worker gating, patch-added def provenance)
- 12:55 writing preflight.py
- 12:57 preflight.py written; first offline run
- 13:01 experiment_manifest.py written
- 13:01 run2 done: removal-bug fix erased the 10 old AM/dacrypts costList misses (MayRequire-guarded, tool artifact). Calibrating op_mayrequire/member/removed_refs; run3 with Armoury override
- 13:02 selftest_effective_def_lint written; running
- 13:02 member_mayrequire moved before MayRequire stripping (selftest caught it failing-first); 28/28
- 13:03 selftest_preflight written
- 13:04 docs written (references/preflight.md, SKILL row, GAME_STATE_WORKFLOW gate row)
- 13:05 PUBLISHED e45bd904f (land.sh)
- 13:06 run3(override) clean of costList; residual removed_refs LKDurasteel_Ore mineableThing + WorkSite_Mining thing -> fixed in RSW_DurasteelConvert_OuterRim.xml (false 'not found' comment corrected). run4 override + run5 deployed started
- 13:06 Armoury validation durasteel_outerrim_static extended; selftest_armoury passes
- 13:07 preflight fixes: About.xml parsed (regex took a dependency's packageId), tasklist for presence, flush; O13 deploy_match timing run
- 13:09 waiting run4/run5/O13
- 13:11 PUBLISHED 27edb8a0e (Armoury/Utinni content fixes) + preflight fixes; filed RAKATA_PATCHES_PROBE_THREE_OPS_MATCH_NOTHING
- 13:12 edl accepts manifest.<NAME>.json; run6 (deployed, manifest.FULL.json) started
- 13:14 O13 deploy_match is drvfs-bound (D state, >7 min); run_selftests started
- 13:18 fixed: gp.resolve falls back to Windows spelling for not-yet-existing dirs -> literal 'D:\...' dir in repo (removed). run7 final deployed lint started
- 13:21 renamed preflight.py -> preflight_bridge.py (shadowed live_queue/preflight.py; selftest_live_queue preflight checks restored; its other FAILs pre-exist at e45bd904^)
- 13:23 O13 rebuilt as hybrid (WSL hashes ext4 repo, python.exe hashes NTFS deploy): 14+ min -> 3.7 s; agrees with deploy_custom_mods plan on Armoury
- 13:24 implemented x4 (3815260a2 / b80e7accf); final run_selftests started

## Result (2026-10-10)

Tickets: PREFLIGHT_BUILD_85_ROWS_OF_HINDSIGHT, EFFECTIVE_DEF_LINT_WIDEN_PAST_DURASTEEL, EXPERIMENT_MANIFEST_BUILD_FREEZE_SIX_CELLS
(all `built`, criteria owed L1/L2), PREFLIGHT_DOCS_WIRE_ONE_LINE_EACH (done); filed RAKATA_PATCHES_PROBE_THREE_OPS_MATCH_NOTHING.
Published: e45bd904f, 27edb8a0e (content), 0e4bb3b6e, b80e7accf (rename preflight.py -> preflight_bridge.py), 3815260a2.

Tools: `src/RimMandrake/Utils/preflight_bridge.py` (renamed: `preflight.py` shadowed modcheck/live_queue/preflight.py),
`effective_def_lint.py`, `experiment_manifest.py`; selftests selftest_preflight_bridge.py 35/35, selftest_effective_def_lint.py 29/29.

Full-list lint (manifest.FULL.json == FULL.LATEST, 551 ids, 55,392 defs, 10,959 patch ops, ~1-4 min python.exe, cache hit ~30 s):
- DEPLOYED tree: 6 crash = OuterRim doors on the Minify Mass path (Armoury fix 67153b072 committed, not deployed); 9 more
  OuterRim costList misses (error, no load consumer); removed_refs 13; member_mayrequire 1; failed_ops 3.
- With the repo Armoury as override (models the deploy): costList 0, crash 0, removed_refs 0 after 27edb8a0e.
- The "11 older apparel/van.dacrypts misses": 10 were NOT misses. costlist_resolve_check removed MayRequire children while
  lxml iter() was live, ending the walk early, so guarded entries survived (AM prestige VPE_Eltex, DA_* DankPyon_*).
  The 11th, Meat_Human, is implied. Nothing to fix in our patches for them.
- New real finds, fixed in 27edb8a0e: LKDurasteel_Ore <mineableThing> and Ideology WorkSite_Mining <thing> still named the
  removed OuterRim_Durasteel (the patch comment said the ore "was not found"); RM_Stillsand in the phrikite GenStep
  gated on a composed-member id (never loaded) -> MayRequireAnyOf.
- op_mayrequire: 0 of ours; 32 donor top-level <Operation MayRequire> (warn).
- UNSUPPORTED: 237 custom-class patch ops (8 mention costList); donor-assembly types.

Offline preflight on the current machine (~37 s): NO-GO, every FAIL true: RealFoW on a test run; 38 built mods absent
from FULL; live ModsConfig is a 67-mod tier; companion deployed != repo artifact (no .srchash); vlvop.tormentmaster.expansion
not installed; 6 crash findings; 6 of 64 mods drifted (FlowWorks/WreckedMachines textures, Armoury patches, ...).

Weak: --live not exercised (no bridge/game this pass); live L01-L07 read files/OS only (no main-thread round trip, no
RunInBackground, no resolved-def audit in game); O10 has no baseline yet; experiment_manifest complete has never seen a
real C0-C5 run; the lint is a simulator (custom ops, C# generators unseen); ledger_lint selftest red in this clone because
the shared HEAD is behind origin (land.sh publishes without rebasing).
- 13:28 run_selftests: 374/380, FAIL = 3 known (hugethings_footprint, one_path_seam, items_glob_live) + selftest_ledger_lint (clone HEAD behind origin; not code)
