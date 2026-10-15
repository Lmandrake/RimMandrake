# Last-mile full-file review (BENCH reviewer, 2026-10-15)

Scope: every DIRTY file under src/RimMandrake/{GimmeSomeSlack,FlowWorks,Pyrelands,_Shared} and src/RimUtinni/EmpirePursuit
(EmpirePursuit lives in the RimUtinni tier, not src/RimMandrake) that ships or is read by a test. Every row is a FULL-FILE
read, every line (lesson d75b357e0c2d). Before: 806 DIRTY of 1407 tracked; after: 781, none of them shipped code or test-read code.

Generator: `generate_liquid_suite.py` re-run against the frozen dump: all 23 outputs byte-identical (git saw no change), so
the generated `RM_LiquidDefRegistry.xml` cleans with it.

Selftests after the fixes (run_selftests --only): review_map, extensions, flowworks_northstar, call_sites, fuel_moat,
settings_registry, empire_ladder 7/7 GREEN; selftest_empirepursuit_fuzz rebuilt and OK (16000 cases). No compiled mod
source changed, so no DLL rebuild.

| file | state | review | notes | fix sha |
|---|---|---|---|---|
| `src/RimMandrake/FlowWorks/Tools/generate_liquid_suite.py` | CLEAN | full-file read, regenerated | no significant finding; outputs byte-identical |  |
| `src/RimMandrake/FlowWorks/Defs/LiquidTypes/LiquidDefs/RM_LiquidDefRegistry.xml` | CLEAN | generated | byte-identical on regeneration |  |
| `src/RimMandrake/FlowWorks/Source/RimMandrakeFlowWorksMod.cs` | CLEAN | full-file read | no significant finding (static-init order of shippedDefaults checked: every public static field precedes it) |  |
| `src/RimMandrake/FlowWorks/Source/SelfTest/Program.cs` | CLEAN | full-file read | no significant finding (observation: Liquid_unit_contract_roundtrip is close to a tautology; not changed) |  |
| `src/RimMandrake/FlowWorks/northstar/extensions.py` | CLEAN | full-file read | no significant finding |  |
| `src/RimMandrake/FlowWorks/review_map.py` | CLEAN | fixed | R1: station fire_astrofuel staged a wild muffalo without keep=True, so the build's sweep (kill per id when keep rects exist) removed it: a corpse on the card that promises a muffalo, and verify_gallery read the station short. keep=True added; layout_check now refuses any non-colonist pawn without keep (probe: dropping keep goes red) | f5ca06ffd5 |
| `src/RimMandrake/FlowWorks/review_map_coverage.py` | CLEAN | full-file read | no significant finding |  |
| `src/RimMandrake/FlowWorks/northstar/site_spec.py` | CLEAN | full-file read | no significant finding |  |
| `src/RimMandrake/FlowWorks/northstar/selftest_flowworks_northstar.py` | CLEAN | full-file read | no significant finding |  |
| `src/RimMandrake/FlowWorks/selftest_flowworks_call_sites.py` | CLEAN | full-file read | no significant finding |  |
| `src/RimUtinni/EmpirePursuit/Source/SelfTest/Fuzz/EmpirePursuitFuzz.cs` | CLEAN | fixed | E1: `d.warnHours = ...` sat inside the end-of-line comment of the line above, so every ladder case ran with warnHours 0 and the warning-letter path (warn tick before raid tick) was never fuzzed; E2: the "live contact on a terminal ladder" invariant was a tautology (`... \|\| k.active >= 0` inside `if (k.active >= 0)`), now `!t.terminal`. Fuzz green after both | f5ca06ffd5 |
| `src/RimUtinni/EmpirePursuit/Source/SelfTest/Fuzz/Program.cs` | CLEAN | fixed | E3: header named selftest_explosivegrowth_fuzz.py as its wrapper (it is selftest_empirepursuit_fuzz.py) | f5ca06ffd5 |
| `src/RimUtinni/EmpirePursuit/Defs/Scenarios/ScenParts_EmpirePursuit.xml` | CLEAN | fixed | E4: surveyShadowBiomes named RUT_Abyss / RM_Abyss / AB_RockyCrags bare; on a list without mandrake.rut.patches, mandrake.rm.biomes (RM_Abyss ships composed there) or sarg.alphabiomes each is a cross-reference error. MayRequire added. E5: header claimed upstream's defName (Rename Phase 2a aa759446e4 changed it; the defName itself is left alone: a save-compat call, not a review fix) | f5ca06ffd5, d17a314e67 |
| `src/RimUtinni/EmpirePursuit/About/About.xml` | CLEAN | fixed | E5: description claimed the same ScenPartDef defName as the original | d17a314e67 |
| `src/RimUtinni/EmpirePursuit/validation.py` | CLEAN | fixed | E6: docstring said printDebug was the ONE settings field and ShadowMultiplier the ONE fork-own piece; the ladder and fuel-blast settings and code exist | f5ca06ffd5 |
| `src/RimUtinni/EmpirePursuit/Defs/EmpireRungDefs/RUT_EmpireRungs.xml` | CLEAN | full-file read | no significant finding |  |
| `src/RimUtinni/EmpirePursuit/Source/EmpireLadderLords.cs` | CLEAN | full-file read | no significant finding |  |
| `src/RimUtinni/EmpirePursuit/Source/HarmonyPatches.cs` | CLEAN | full-file read | no significant finding |  |
| `src/RimUtinni/EmpirePursuit/Source/Kernel/EmpireLadderKernel.cs` | CLEAN | full-file read | no significant finding |  |
| `src/RimUtinni/EmpirePursuit/Source/RUT_EmpireRungDef.cs` | CLEAN | full-file read | no significant finding |  |
| `src/RimUtinni/EmpirePursuit/Source/RuthlessPursuingMechanoids.cs` | CLEAN | full-file read | no significant finding (upstream port; EndlessWavesHours 0 from a hand-edited scenario would divide by zero, but the editor floors it at 1) |  |
| `src/RimUtinni/EmpirePursuit/Source/SelfTest/EmpireLadder.SelfTest.csproj` | CLEAN | full-file read | no significant finding |  |
| `src/RimUtinni/EmpirePursuit/Source/SelfTest/Fuzz/EmpirePursuitFuzz.csproj` | CLEAN | full-file read | no significant finding |  |
| `src/RimUtinni/EmpirePursuit/LICENSE.txt` | CLEAN | diffed | identical to /usr/share/common-licenses/GPL-3 apart from CRLF |  |
| `src/RimUtinni/EmpirePursuit/.naming-vendored` | CLEAN | full-file read | lint exemption list; no finding |  |

## Skipped (not reviewed), and why

- **Binaries:** the four mod DLLs and their `.srchash` (FlowWorks, GimmeSomeSlack, Pyrelands FireEcologyHook, EmpirePursuit):
  build outputs, never mark-cleaned anywhere in the repo; their source is what is reviewed.
- **Run records:** 222 result JSONs under FlowWorks/northstar and GimmeSomeSlack/northstar (extension_result_*, validation_*,
  proof_*, matrix_live_*), plus `FlowWorks_review.decisions.json` (the owner's own review decisions, data).
- **Generated human-review docs, read by no test** (the selftests regenerate their own copies in temp dirs):
  FlowWorks `northstar/review/{FlowWorks_review.html, FlowWorks_status_board.html, README.md, map/COVERAGE.md,
  map/KEYSHEET.md, map/keysheet.html}`, GimmeSomeSlack `review/{COVERAGE.md, KEYSHEET.md, README.md, keysheet.html}` and
  `northstar_matrix/README.md`, Pyrelands `review/{COVERAGE.md, KEYSHEET.md}`, FlowWorks `northstar/player_missions_BRIEF.md`.
- **Art:** 505 textures/gifs/jpgs and everything under `art_source/` (incl. TankTall `restyle.sh`, `fit_all.sh`,
  `jobs.txt`, `pipe/.gitignore`, `visual_principles_sheet.html`).

## Final count

DIRTY remaining in the five folders: 781, every one in the skip classes above. Shipped or test-read code DIRTY: **0**.
