# RimMandrake: Solar Mirrors — validation walk
subject: src/RimMandrake/SolarMirrors  (own About.xml packageId `mandrake.rm.solarmirrors`)
deps: `brrainz.harmony`, `mandrake.rm.biomes` (CreatureBehaviors' shade grid, pinned sun, glare-blind hediff; the Long Shade biome)
status-hint: SOLAR_MIRRORS_MOD_DESIGN_1 + SOLAR_MIRRORS_BUILD_1; script = `src/RimMandrake/SolarMirrors/validation.py`; probe = `jawa/shade_probe` (JawaBench companion)

Sources: `design/RimMandrake/solar_mirrors_mod_design_2026-10-04.md` (§2.2–§2.7, §3, §5 E1–E4/E13, §6.2, §7 rulings),
`About/About.xml`, the defs, `Source/`.

## must be true
Every line ends in `→ chain.component` (a suite component that reads the state back) or `→ UNCOVERED: why`.
- No error in Player.log names this mod or the CreatureBehaviors light hook it needs. → load.no_errors_naming_this_mod
- Every SolarMirrors def loads with its comps (a comp class that cannot resolve throws the whole def away), the field's GenStepDef included. → defs.present
- The probe reads the shade grid, the mirror layer and the field on a map, with no member missing. → probe.answers
- The shade grid pulls mirror light through `IRM_LightLayer` (design §2.3). → live_owed.hook.registered
- A mirror aimed at a shaded cell lowers ShadeAt and raises ExposureAt there; un-aimed, both restore (design §6.2 line 2). → live_owed.light.unshade
- A wall built on the beam line takes the light within one pass (§6.2 line 3). → live_owed.light.blocked
- A roof over the target, or along the path, takes the light (§2.2, §6.2 line 4). → live_owed.light.roof
- A mirror in shadow throws nothing; lit by a second mirror it relays (§6.2 line 5). → live_owed.light.chain
- On a Long Shade map a lit cell's GroundGlowAt reads 1.0 against 0.8 beside it (§6.2 line 6). → live_owed.glow.postfix
- Re-aiming bumps the grid's GridVersion and changes the patch count (§6.2 line 7). → live_owed.herd.patchgraph
- Save and load keep every mirror's target, normal, dust and detent; the rebuilt layer hashes equal (§6.2 line 8). → live_owed.save.roundtrip
- A heliostat that loses power under a moving sun drifts (E13). → live_owed.heliostat.power_freeze
- The solar furnace takes no bill under one mirror and works under two (E1). → live_owed.furnace.gated
- A hostile in a beam gains glare-blind; goggles stop it (E4). → live_owed.blind.hostile_gain
- A hostile shooter in a beam aims worse, shown in the stat explanation (E4). → live_owed.dazzle.accuracy
- A Long Shade map made with the setting on carries a field mapgen solved: ≥ 1 solution, a start ≥ 2 re-aims away (§3.4, §6.2 line 10). → field.solvable
- Lighting every stone opens the vault, and it stays open (§3.4 latch). → live_owed.field.latch
- A seized ancient mirror turns only after "Free the bearings" spends a component. → live_owed.field.repair
- A dust storm dulls an open mirror; a cleaning job restores it (§3.2). → live_owed.dust.storm, live_owed.dust.clean
- A beam through a glazed aperture lights and warms a roofed room (E2). → live_owed.glazed.room
- A lit solar furnace in a closed room warms it (E1). → live_owed.furnace.room_heat
- By day a heliograph opens comms with a friendly faction in reach; at night it says why not (E3). → live_owed.helio.comms, live_owed.helio.night
- Two overlapping beams feel hotter than one, never past the biome's maxHeatOffsetC (§2.6). → live_owed.concentration.heat
- Each Mod Settings toggle off removes its effect (`suite.toggles`). → toggles.*
- The lit patch reads as light inside a rendered shadow, and a herd visibly re-routes. → UNCOVERED: needs the owner's eyes (design §2.8 risk 1); the state half is herd.patchgraph

## the walk
1. [B] Tier: minimal list with `mandrake.rm.biomes` (CreatureBehaviors + Long Shade), `mandrake.rm.solarmirrors`, the bridge and all five DLCs; deploy the JawaBench companion first so `jawa/shade_probe` exists.
2. [B] A fresh Long Shade quicktest map (the field is laid at map generation, so an old map has none).
3. [B] `python.exe src/RimMandrake/Utils/modcheck/cli.py run SolarMirrors`.
Offline: `python3 src/RimMandrake/SolarMirrors/validation.py` (static), `python3 src/RimMandrake/Utils/selftest_solarmirrors.py`
(lint + static), `python3 src/RimMandrake/Utils/selftest_solarmirrors_fuzz.py` (kernel fuzz), and the 42-mutant set
`python3 src/RimMandrake/Utils/mutate_kernel_fuzz.py selftest_solarmirrors_fuzz.py src/RimMandrake/Utils/mutations_solarmirrors_fuzz.json`.

## north star
state: DRAFT
validated-hash:

Experience bars here are the owner's to write and rule; the functional lines above are agent-owned.

## anti-guessing notes
- RULED OUT: "a roof on the beam's path does not block" (the old §6.2 line 4) — §2.2's rule is that it does; the kernel, the fuzz oracle and the design now agree, and a glazed aperture is the one way under a roof.
- RULED OUT: "the probe must live in the SolarMirrors DLL" — a shipping mod must not depend on the bridge SDK; the probe is in the JawaBench companion and reads by reflection.
- UNPROVEN at mapgen: the shade grid's Recompute and the pinned sun both answering during a GenStep (the Long Shade's own crawler road relies on the same Recompute, so it is expected to work). A field that could not be laid records why in `SolverReport` ("no field: …"), which field.solvable prints.
- The solver's "every re-aim reaches every configuration" is structural (one job turns one mirror to any detent), so the design's "reset path exists" needs no search; the fuzz pins the hint walk taking exactly the Hamming distance.
- RULED OUT (2026-10-08 offline validation): "the sun-stones' hysteresis cannot affect the puzzle's difficulty". The old solver counted only configurations lighting every stone from dark; with the stones held lit down to unlitBelow, the fuzz's exhaustive job-order walk latched the vault after 1-3 jobs on fields promised 2-4. The solver now bounds the start by the HELD set; guard: the `generate` fuzz family (held-distance, PickStart, minReAims and early-latch oracles) and mutations "D3".
- RULED OUT: "a field stone is fixed in place". Field stones are claimable and minifiable; the vault now counts a stone only on the cell mapgen laid it on (static guard D2).
- WATCH (live only): mapgen re-solves the laid field at `MapGenerated` and logs `[RM SolarMirrors] the ancient mirror field changed after it was solved at mapgen` if a later step broke it. A Long Shade load whose log carries that line is a SITE/MOD finding, not noise.
