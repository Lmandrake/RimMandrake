# PYRELANDS_SHIP_READINESS_1 — the SHIPPED rung for Pyrelands: art, review, settings, deploy

**For:** FOUNDRY. **Parent:** PYRELANDS_NORTHSTAR_TRIAL_1. **Plan:** `design/RimMandrake/northstar_trials/Pyrelands_trial_plan.md` §5.
**Depends on:** BIOME_MOD_UNIFICATION_1 (it ships as part of `mandrake.rm.biomes`; the per-biome
toggle must gate mechanics, not only worldgen).

## acceptance (gaps MEASURED 2026-09-30)

- [ ] **`RUT_Ashwallow` gets art.** Its texPath `Things/Pawn/Animal/Pyrelands/Ashwallow/Ashwallow`
      has no file in the repo or in the deployed UtinniPatches. Search `_artsrc`/`done/` first.
- [ ] **`RUT_Emberscythe` off placeholder vanilla Megascarab art.** `emberscythe_v1_*` already
      sits in `infrastructure/artpipe/done/`; check for an owner ruling before any regen.
- [ ] `BARBSLINGER_SCORPION_REDESIGN_1` closed. The FireHawk flight frames are judged in an
      owner-present session (`FIREHAWK_FLIGHT_BEHAVIOR_1`), never by an unattended hunt.
- [ ] Code review CLEAN. Currently DIRTY:
      - `RM_PyrelandsMod.cs`, `RM_JobGiver_BurrowOnFire.cs`, `RM_JobDriver_Burrow.cs`,
        `RM_BurrowOnFireExtension.cs`, `PyrelandsTuning.cs` and `PyrelandsMechanicsDefOf.cs`
        (`src/RimMandrake/Pyrelands/Source/`);
      - `src/RimMandrake/BiomesShell/Source/RM_BiomesMod.cs`;
      - `validation.py`, after wiring.
- [ ] Mod Settings are superb (`MOD_OPTIONS_RETROFIT_1`): every toggle is labelled and
      worldgen-affecting ones are marked. `RM_BiomesSettings.Enabled("Pyrelands")` gates the
      mechanics too, not only placement.
- [ ] The composed `mandrake.rm.biomes` deploys at 0 diff, with `.srchash` matching.
- ⛔ 0 tiles on Ash'karr is expected (painted once at the end). It is not a gap.
