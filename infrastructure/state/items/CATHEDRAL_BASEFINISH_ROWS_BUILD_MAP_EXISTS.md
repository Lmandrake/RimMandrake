## spec
Re-filed from UNPROVEN_LIVE_LEGS_TRIAGE_1 (triage of RUSTCATHEDRAL_BASE_FINISH_BUILD_1 A5-A9, verdict NEEDS A TOOL;
the map is NOT the blocker any more).
The item that filed the triage assumed A5-A9 needed a generated Cathedral map that could not exist until the repaint.
It can exist today: `python.exe src/RimMandrake/Utils/live_site.py --biome RM_RustCathedral` sets the current
quicktest tile's biome, commits, and runs `Actions\Regenerate Current Map` (which honours the tile's biome), the
recipe proven live 2026-10-01 for Stillsand. A live_proofs line `live-site A<n>: <that command>` makes the supervisor
stage it before the proof. What is missing is the proof: `src/RimMandrake/RustCathedral/validation.py` has no live
component for any of A5-A9 (only the STATIC basefinish_problems check and selftest_rustcathedral_basefinish), and its
`map_mechanics` chain still says "the bridge cannot generate one" (line ~1198), which live_site.py made false: fix
that text in the same change.

Build: validation.py components on a live_site Cathedral map, each with its toggle-off arm (A9):
- A5 line_cycle_lowers_band: `jawa/fire_incident RM_LineCycle`; band 1-3 drops one, worst unchanged (read via the
  attitude tools in JawaBenchCathedralAttitudeTools.cs; check what they can seat before writing a new one).
- A6 hum_reading_follows_trait: add RM_HumReader to a colonist -> RM_HumReading.Readout non-empty; remove -> empty.
- A7 eels_stay_on_water: canal-water map, RM_CoolantEel count > 0, every eel on water after 5000 ticks.
- A8 strays_toggle: desiccated corpses within 8 cells of the edge > 0 with the toggle on, 0 off (a map regen per arm),
  no live pawn from the GenStep.
- A9: each toggle off removes exactly its effect (the four arms above).

## criteria
A1 L0: the components exist, the mock suite lists them, the false "cannot generate" text is gone, validation.py and the basefinish selftest green.
A2 L2: live on a live_site.py --biome RM_RustCathedral map, the five rows read PASS, proving RUSTCATHEDRAL_BASE_FINISH_BUILD_1 A5-A9.
