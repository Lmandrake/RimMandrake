# GimmeSomeSlack ship path — 2026-10-22 (FOUNDRY helper, offline)

Ranked #1 in `design/RimMandrake/release_proximity_2026-10-22.md`. This file is the per-row disposition of the stored
run's 1 FAIL and 5 UNMEASURED rows, the deploy dry run, and the one bridge sitting that takes GSS to a recordable result.
Offline only (BENCH held the bridge).

## Source of truth, and the headline

- `modcheck status GimmeSomeSlack` reads `RED (last run failed)`. The recorded run is
  `Transient/bench_live_20261015_l2/live/gss_proof_all_1.json` (started 2026-10-15T12:52, mod hash `52b7c6c9…`,
  tier `ratchet_pilot`): PASS 113, FAIL 1, UNMEASURED 5.
- **That run is stale twice over.** Every one of its six rows was fixed or built on the afternoon of 2026-10-15, and two
  later full live runs, never recorded, show it:
  - `Transient/bench_live_20261015_c1/gss_proof_all_c1.json` (2026-10-15T17:20, hash `0937b01e…`): PASS 118, UNMEASURED 1.
  - `src/RimMandrake/GimmeSomeSlack/northstar/proof_all_20261016T192502.json` (2026-10-16T19:25, hash `072aeeda…`): PASS 118,
    UNMEASURED 1. That one UNMEASURED was `S12d` in both runs.
- The mod's hash NOW is `cd82595b39e0…` (`status.mod_hash` on the mod folder). It has moved since 2026-10-16: the pipe-pole
  C# work (681d39c09, ee633ed66, f511ec319, eb1065191) and the aerial switch text (6e3a81554). So **no stored run is at the
  current hash**, and a fresh full `proof_all` is owed whatever the rows say.
- Two findings stopped that run from ever being recordable as GREEN. Both are fixed in this pass (sections below):
  1. `S12d` was UNMEASURED **by construction** in every full `proof_all`, and `modcheck record` reads any UNMEASURED row as RED.
  2. The offline gate was **red** (`validation:O7_gpt_read_fixes`), so `proof_all --live` would have printed
     `REFUSED: offline red -- not going live` before touching the game.

## The six rows

| row | class (stored) | cause | disposition | evidence | owner-needed? |
|---|---|---|---|---|---|
| `S12a_D1_legacy_run_one_look` | FAIL, MOD | **A real defect (D1).** A styled mast built onto an unstyled run, followed by a default-look change, split the run into two looks (`looksAfterDefaultChange: [Industrial, Scrapper]`). | (a) **Already fixed**: bb6825c7e (2026-10-15 16:16), "a run whose winner is legacy stays legacy (joiners and bridge losers are cleared, not stamped with the default)"; DLL 414b6a825. | PASS in c1 (17:20) and 2026-10-16 (`looksAfterDefaultChange: [Industrial]`, one look). No C# kernel test covers the map-component application, only `PlanPlacement` (`SelfTest/StyleStage2Checks.cs` "legacy:" check); the live row is the guard. | no |
| `B12_shader_sway_far_zoom_drawn_once` | UNMEASURED, HARNESS | The scene was not written yet: the row was a placeholder. | (b) **Already built**: d3d33e25b (scene), 25ca9dd96 and f8695482d (review fixes). | PASS 2026-10-16 (near and far zoom, shader submeshes 2 of 2 enabled). | no |
| `B13_hidden_conduit_hookup_not_drawn` | UNMEASURED, SITE | `printed: [null, null]`: the census did not report `hookupCablesPrinted`, so the row could not tell zero from blind. | (b) **Already fixed**: d3d33e25b (B13 reads `hookupCablesPrinted` from census), 1b9ce1302 (requires a hookup print, so a blind census cannot pass). | PASS 2026-10-16 (`printed [0,0]`, `hookupPrints 2`: the instrument can see). | no |
| `A8_same_frame_dirty_not_dropped` | UNMEASURED, HARNESS | Scene not written yet. | (b) **Already built**: d3d33e25b, cf3ce5b91, f8695482d (needs fresh edges > 0). The mod fix it guards landed the same afternoon: e77b93062 (a dirty event landing after this frame's rebuild defers one rebuild instead of being dropped). | PASS 2026-10-16 (`inFrameStale: true`, fresh hash differs, one frame). | no |
| `S12c_D5_multilink_one_frame` | UNMEASURED, HARNESS | Scene not written yet. | (b) **Already built**: d3d33e25b, 1b9ce1302 (requires two different staged looks), 80de79ba6 (Modern takes a colour key). | PASS 2026-10-16. | no |
| `S12d_D4_pending_queue_save` | UNMEASURED, HARNESS | **Structural harness gap.** In `proof_all` (SHARED mode) the style block always wrote this row UNMEASURED, because a member staged pending in the ONE census save would change SL3's M4/S7/S9e sets. It was left to a standalone `validation_style.py --live --save`, which has **never been run** since the D4 scene and fix landed (no result file holds a measured S12d). And because `modcheck record` makes any UNMEASURED row RED, no full `proof_all` could ever be recorded GREEN. | (b) **Fixed this pass**: 6fa5cc14c. `proof_all` gets a `d4_save` block AFTER SL3: it stages D4, writes a SECOND save by `csavenow` (one member still pending), reloads and reads it against the control. It uses validation_style's own `s12d_stage` / `_save_load(stage=True)` / `s12d_after_load` unchanged. It replaces the SHARED placeholder. A failed save or load reads UNMEASURED and says why, never PASS, and an aborted session keeps the placeholder. S12d is now a declared `save_load` row. The mod fix it guards: dbd430c6c (drain the conduit-run queue before every save). | `northstar/selftest_proof_all.py` check 9: 7 new checks, with controls for a failed save/load, an aborted session and a FAIL verdict. ALL PASS. **Live-untested**: the first live run is the real test of the new block. | no |

### Two harness states surfaced (never edited to pass)

- **O7 offline gate, before and after.** Before: FAIL with `['A18 span meshes destroyed', 'C11 placement ghost picks like
  auto-link']`. The pipe-pole commits (681d39c09, f511ec319, 2026-10-21) rewrote both sites, so the literal source shapes no
  longer matched. I read both sites, and the fixes still stand:
  - A18: `Notify_SpansChanged()` is now a block whose first line is `ClearSpanMeshes();`, and `ClearSpanMeshes` still calls
    `UnityEngine.Object.Destroy` on each mesh.
  - C11: the ghost now calls `AutoLinkCandidates(AerialLineProfiles.LookOfPick(def, picked), null, center, kind)`.
    `LookOfPick` returns `StylePicker.LookOfStyle(picked) ?? StylePicker.DefaultLook` for power poles, the same as before,
    and a pipe-specific look for pipe poles.

  After (191964b06): the shapes point at the new text, plus A18b (the destroy) and C11b (the power branch of `LookOfPick`).
  The old A18 literal still reads missing against the current source (a control). The gate is now `red: []` and the matrix
  selftest reads 58/58.
- **The 2026-10-16 run was never recorded.** Its only non-PASS row was S12d, so it would have recorded RED anyway. It is
  now stale (hash `072aeeda…`), so recording it would be refused.

## Deploy dry run (`deploy_custom_mods.py --mod GimmeSomeSlack`, no `--apply`)

`in sync (133 files, 160 held)`, `Everything in sync.`: **nothing would change.** The 160 held files are proof and
validation result JSONs (`src/DEPLOY_HOLD.txt`). The release doc's "DLL rebuilt 2026-10-22 and undeployed" no longer
holds: the deployed copy matches the repo. Whether the RUNNING game loaded that DLL depends on when it launched. P2 and
the result's `env.assembly_sha256` will say.

## One-sitting live sequence (one minimal-list load, cheapest first)

Everything below fits one cold load of tier **`fw_gss_sitting`** (FlowWorks + GSS + composed biomes + VEF core + DLCs).
I chose it over the walk's `gimmesomeslack` tier because the batched riders (pipe-pole switch A2/A3) need FlowWorks.
`proof_all`'s P2 does not check the tier: it records `env.running` (read via `jawa/running_mods`) and checks the startup
log. The 2026-10-16 run passed P2 on a 22-mod list. **The record must name the tier that actually loaded**, because `modcheck record` refuses any
`env.running` set that is not that tier's. If the sitting is GSS-only, use `--tier gimmesomeslack` in steps 0 and 4 and
drop step 1.

0. Bridge free, game down: `python3 src/RimMandrake/Utils/modset_builder.py --tier fw_gss_sitting --apply`, launch via Steam
   (a cold load on a minimal list takes seconds, not minutes).
1. (rider, ~2 min, cheapest) `PIPE_POLE_SWITCH_DECIDE_HOSTAGE_TO_WIRES` A2 and A3 (L1), with the deployed DLLs:
   - A2: GSS power master OFF and FlowWorks pipe poles ON. Expect `RM_PipePole` in the architect menu and its built spans
     drawn.
   - A3: pipe poles OFF and power master ON. Expect the pole to leave the build menu.

   Restore both defaults afterwards. (The ledger item's own A-lines are the bar. Read them with `rimflow show` at the
   sitting.)
2. (the gate, ~7 min) `timeout 1200 python.exe src/RimMandrake/GimmeSomeSlack/northstar/proof_all.py --live --no-shots`
   from the repo root. It runs the offline gate first (now green), loads the calm site save, and runs P1 to P3, the
   reduced matrix, core, aerial and style. Then come D1/D2, the census save and load (SL1 to SL3), the **new S12d second
   save and load**, and Z. Pre-registered expectations:
   - S12a, B12, B13, A8 and S12c PASS, as on 2026-10-16.
   - S12d PASS, with detail `csavenow.pendingAtSave` truthy and `afterLoad.staged` equal to `afterLoad.ctrl`, both of length 1.
   - Z PASS across both loads.

   If S12d reads UNMEASURED with `why: the D4 save/load did not complete`, the new block failed. That is a HARNESS problem:
   fix it, don't record.
3. If a row fails: classify it MOD, SITE or HARNESS from its detail before re-running anything (the
   `live-debugging-proof-harness` skill). A re-run is one `proof_all` (about 7 min), not a reload.
4. Offline, right after:
   `python3 -m modcheck.cli record GimmeSomeSlack --result src/RimMandrake/GimmeSomeSlack/northstar/proof_all_<stamp>.json --tier fw_gss_sitting`.
   The checklist is VALIDATED, so an all-PASS run records as PENDING-OWNER-REVIEW or GREEN.
5. (optional riders, same map, only if time) `FALLEN_WIRE_SHOCK_1` A5 (L2: a live end in a chemfuel puddle starts a fire)
   and `CORD_GRAPH_TOPOLOGY_REVISION_1` A2 (L2: SwayHash and RippleHash match before and after on a busy map). I found no
   standing script for either. They need an exact bar written before the sitting, so they are not part of this
   sequence's promise.

## Still owed, offline

- `src/RimMandrake/GimmeSomeSlack/northstar/proof_all.py` and `src/RimMandrake/GimmeSomeSlack/northstar/selftest_proof_all.py`
  are DIRTY (`code_review_status.py`) after 6fa5cc14c, and `src/RimMandrake/GimmeSomeSlack/validation.py` is DIRTY after
  191964b06. Each needs a full-file review before `mark-clean`. I left them DIRTY: I reviewed only my diff.
- `src/RimMandrake/Utils/modcheck/required_checks.json` lists GSS checkout rows from `declared_rows()`. It will pick up
  `S12d_D4_pending_queue_save` as a required checkout row when it is next regenerated.

## Owner-needed

None for these six rows. The open owner decision on GSS stays `PIPE_POLE_SWITCH_DECIDE_HOSTAGE_TO_WIRES` (built; L1 owed
live), and the human look pass stays walk step X, which is never a pass bar.
