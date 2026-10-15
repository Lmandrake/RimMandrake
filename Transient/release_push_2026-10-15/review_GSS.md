# GimmeSomeSlack release review — 2026-10-15 (BENCH reviewer)

Owner, 2026-10-15: "please ensure that full clean/dirty code reviews are provided for these files before then"

Scope: every tracked file under `src/RimMandrake/GimmeSomeSlack` plus code compiled into the GSS DLL from
`_Shared/` and tooling that tests GSS. Census: 256 tracked non-art files; 95 CLEAN at start (all .cs Source,
About.xml, Defs, Patches already CLEAN).

| path | reachable | verdict | defects found/fixed | sha |
|---|---|---|---|---|
| `src/RimMandrake/GimmeSomeSlack/Source/RimMandrake_GimmeSomeSlack.csproj` | yes (the GSS build) | CLEAN | 0 (every Compile Include exists; every non-SelfTest .cs is compiled) | d794e8037c |
| `src/RimMandrake/_Shared/SlackGeometry/CordMath.cs` | yes (compiled into GSS + FlowWorks) | CLEAN | 0 | d794e8037c |
| `src/RimMandrake/_Shared/SlackGeometry/CordWorld.cs` | yes | CLEAN | 0 | d794e8037c |
| `src/RimMandrake/_Shared/SlackGeometry/CordPlanner.cs` | yes | CLEAN | 0 (dive-span indexing checked: a barrier run never reaches the goal cell) | d794e8037c |
| `src/RimMandrake/_Shared/SlackGeometry/CordLayer.cs` | yes | CLEAN | 0 | d794e8037c |
| `src/RimMandrake/_Shared/SlackGeometry/DrawOrder.cs` | yes | CLEAN | 0 | d794e8037c |
| `src/RimMandrake/_Shared/StylePicker/StylePickerCore.cs` | yes (GSS anchors) | CLEAN | 0 significant; minor: a second `Register` on one instance (FlowWorks' PipeLook does this) re-logs earlier missing style defs. Not fixed: shared with FlowWorks, which another agent is building | d794e8037c |
| `src/RimMandrake/_Shared/HarmonyResilience/PatchApplier.cs` | yes (GSS `Apply`) | CLEAN | 0 | d794e8037c |
| `src/RimMandrake/_Shared/SettingsKit/SettingsKitCore.cs` | yes (GSS settings search, scope tags) | CLEAN | 0 | d794e8037c |
| `src/RimMandrake/_Shared/SettingsKit/SettingsKitDrawer.cs` | yes (GSS SearchBox, ResetButton) | CLEAN | 0 | d794e8037c |
| `src/RimMandrake/_Shared/SlackGeometry/selftest_slackgeometry_internal.py` | yes (gate) | CLEAN | 0; ran PASS (6 files, 23 decls) | d794e8037c |
| `src/RimMandrake/Utils/selftest_gimmesomeslack.py` | yes | CLEAN | 0; ran 631/631 | d794e8037c |
| `src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchGssPlaytest.cs` | yes (companion; gss_playtest_* / gss_stage) | CLEAN after fix | **2 found, 2 fixed (36df5dcdee)**: (1) the reel's look was read through GSS's `StylePicker`, which has not known the reel since the hose port, so the ui "Choose style" check could never pass and save_reload's reel `style` line compared GSS's default on both sides (blind). It now uses FlowWorks' `HoseLook` / `HoseStyles`. (2) A repeated key in a `gss_stage` op line threw outside the per-op try and dropped every op. The companion compiles with 0 errors; closure_scan and the runner selftest pass. NOT deployed (plan only) | d794e8037c |
| `src/RimMandrake/GimmeSomeSlack/northstar/gss_playtest_runner.py` | yes (launcher) | CLEAN | 0 significant | d794e8037c |
| `src/RimMandrake/GimmeSomeSlack/northstar/selftest_gss_playtest_runner.py` | yes | CLEAN | 0; ran 12/12 | d794e8037c |
| `src/RimMandrake/GimmeSomeSlack/Source/SelfTest/oracle_scenes.json` | yes (SelfTest input) | CLEAN | 0: `export_oracle.py` regenerates it byte-identical | d794e8037c |
| `src/RimMandrake/GimmeSomeSlack/Source/SelfTest/matrix_det_scenes.json` | yes (SelfTest input) | CLEAN | 0: `det_export.py` regenerates it byte-identical | d794e8037c |
| `src/RimMandrake/GimmeSomeSlack/art_source/tapclamp_v3_2026-10-11/build_tapclamp_v3.py` | provenance only (done art round, no caller) | CLEAN | 0 | d794e8037c |
| `src/RimMandrake/GimmeSomeSlack/art_source/tapclamp_v3_2026-10-11/fetch_master.py` | provenance only | CLEAN | 0 | d794e8037c |

## Pending, under edit (skipped by instruction)
- `src/RimMandrake/GimmeSomeSlack/human_review.py`, `save_review_map.py`, `review/*`

## Not code (run records / data)
- `src/RimMandrake/GimmeSomeSlack/northstar/*.json`: about 140 live run records (matrix_live, proof_all, validation_*), output of past runs and never read by the mod.
- `src/RimMandrake/GimmeSomeSlack/art_source/tapclamp_v3_2026-10-11/{artpipe_jobs,manifest}.json`: art-job records.
- `src/RimMandrake/GimmeSomeSlack/northstar_matrix/README.md`: documentation.

These remain DIRTY by design: none is code the game loads or a test reads.

## Already CLEAN at start
Every `.cs` under `GimmeSomeSlack/Source` (including SelfTest), `About/About.xml`, `Defs/**`, `Patches/RM_ConduitStyleable.xml`, the SelfTest csproj, and `_Shared/SettingsKit/SettingsKitMasters*.cs`.

## Not reviewed
- `src/RimMandrake/_Shared/StylePicker` minor: listed above, left for FlowWorks' owner.
