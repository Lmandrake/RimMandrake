# Solar Mirrors — full build to deploy-ready (FOUNDRY, 2026-10-08, offline)

Owner order 2026-10-08: *"Fully build Solar Mirrors to full deploy ready status."* No bridge, no game, no deploy.
Items: `SOLAR_MIRRORS_MOD_DESIGN_1` (superseded by) → `SOLAR_MIRRORS_BUILD_1` (built at `f22b94f84`, live criteria owed).

## Phase 1 — measured built vs design; stale prose corrected (`315907cee`)

Already built before this pass: P0 hook, P1 layer/comps/kernel+fuzz, P2 signal/static/heliostat/sun-stone/re-aim,
P3 spot+shaft render and glow postfix, E1 furnace bill gate, E4 glare-blind, E13 power freeze.
Corrected in the design doc: "Nothing is built" (false), §6.1 now has a Status column, §6.2 line 4 contradicted §2.2
on roofs along the path, §7 still listed four questions the owner ruled on 2026-10-04 (now recorded as rulings).
`SOLAR_MIRRORS_MOD_DESIGN_1` had no item prose file, so there was nothing there to correct.

## Phase 2 — build (`b81a9b6a4` probe, `f22b94f84` mod)

- `jawa/shade_probe` (RM_ShadeProbe), JawaBench companion: shade/exposure/grid light/mirror light/ground glow per cell,
  mirrors, receivers, field report; reflection, reports missing members. Built (`build.py --gm`, plan only), not deployed.
- §3.4 ancient mirror field: `RM_MirrorFieldExtension` reaching `RM_LongShade` by a Conditional patch in this mod;
  `RM_GenStep_AncientMirrorField` (order 955) lays a 5x5 sealed vault, 2–4 sun-stones, 4–6 seized `RM_AncientHeliostat`s
  on the downsun arc with 3 detents each (brass pins), and SOLVES it with the real light pass before keeping it
  (`RM_MirrorFieldKernel`: exhaustive, start ≥ difficulty re-aims from the nearest solution, chain ≤ cap); failed sites
  are torn down and roofs restored. Repair = one component + Construction; each turn is a job; detent ghosts on select;
  latched vault (seal destroyed + letter) holding loot and a minified heliostat; escalating hints on the seal.
- §3.2 dust: `RM_MirrorDust` def (weathers by defName), dust in reflectivity, Cleaning work giver/job.
- §2.6 concentration heat: postfix after CreatureBehaviors on `Thing.AmbientTemperature`, vanilla offset, capped.
- E2: `RM_GlazedAperture` (glazed wall) — the kernel lets a beam under roofs once it passes glass; lit enclosed cells
  `PushHeat` their room (covers the furnace indoors).
- E3: heliograph comp on the signal mirror — float menu per friendly faction with a settlement in reach (range × daylight),
  job opens `Faction.TryOpenComms`.
- E4: `RM_StatPart_MirrorDazzle` on ShootingAccuracyPawn for hostiles in a beam (eyes protection honoured).
- Settings: 25 fields (14 new), sections, Reset and an "all off" button; heliostat power dial written into the def.
- Keyed strings, About.xml description; dependency URLs were already present.

## Phase 3 — build, selftests, validation

- `winbuild.py SolarMirrors`: 0 warnings, 0 errors, DLL + `.srchash` committed.
- Fuzz (`selftest_solarmirrors_fuzz.py`): math / pass / sequence / field families, 10,700 cases, 0 failures, blind
  check reached glazed beams, solvable/accepted/oversized fields and hint walks.
- Mutations: 42 (23 old + 19 new: aperture, dust, concentration, room heat, dazzle, heliograph, solver, hints) — 42 caught.
- Lint 0 ERROR 0 WARN; `validation.py` static PASS (failure path proven); `validate_patch.py` 0 errors.
- New `selftest_solarmirrors.py` (lint + static) is picked up by `run_selftests.py`.
- `run_selftests.py`: 330/337. Failing ones belong to other mods/agents: abyss, creaturebehaviors and inhabited fuzz,
  `selftest_sun_heat.py` (dash-range clamp in CreatureBehaviors, untouched here), `selftest_items_glob_live.py`
  (`HUGE_THINGS_GPT_REVIEW_1.md` has no ledger row), `modcheck/selftest.py` timeout. The walklint failure this pass
  caused (walk `subject:`) was fixed and passes.
- validation.py: new `probe.answers`, `field.solvable` chains on `jawa/shade_probe`; 10 more live lines owed.
- Walk: `design/validation_walks/RimMandrake/SolarMirrors.md` (new).

## PROVISIONAL numbers

Field: stones 2–4, mirrors 4–6 (setting 5), detents 3, min re-aims 3 (setting 2–4), ring radius 9–15, ancient
reflectivity 0.75, repair 1500 ticks + 1 component, re-aim 900 ticks, vault loot silver 250–500, gold 20–50,
components 4–8, plasteel 20–40, seal 6000 HP, wall 3000 HP, shadow height 0.3. Dust: 1/day of storm, max loss 0.6,
clean at 0.25, clean job 300 ticks. Concentration cap 3x. Room heat 2 per light per cell per second. Heliograph
12 tiles × daylight, 300 ticks, mirror must stand in ≥ 0.5 sun, non-hostile humanlike factions only. Dazzle up to
−40% accuracy at light ≥ 0.5. Heliostat 150 W. Glazed aperture: steel-type stuff 10 + silver 5, 120 HP.
Interpretation calls: §3.5 "detents 4/5/6" read as the field's mirror count; E2 built as a glazed wall, not a
glass roof; the vault's repaired heliostat is the reward, so field mirrors stay detent-bound after repair.

## Art owed

`artpipe_state.py find` (sanity probe "hawkbat" = 23 hits) found no art for any of the 10 subjects. Queued 12 jobs
(`D:\Luke\dev\_artpipe\pending\`, item SOLAR_MIRRORS_BUILD_1, target `Things/Building/RM_SolarMirrors/<defName>`):
signal mirror, static mirror (greyscale for stuff), heliostat, ancient heliostat, sun-stone + `_Lit`, solar furnace
(north/east/south), mirror detent, vault seal, glazed aperture. Not queued: `RM_SunVaultWall` (the pipeline cannot do
linked atlases). The defs still point at vanilla placeholders and must be repointed when the art installs.

## Only a live run can prove

Everything behavioural: the probe itself answering; light un-shading, blocking, roofs, relays, glow 0.8→1.0, GridVersion
and patch count moving, save/load; mapgen actually laying a field on a Long Shade map (Recompute and the pinned sun at
GenStep time are expected to work, as the crawler road relies on the same Recompute); the vault latch; repair and detent
jobs; dust and cleaning; glazed room heat; heliograph comms by day and refusal at night; dazzle in the stat explanation;
concentration heat. Legibility of the lit patch and the herd re-route need the owner watching.
