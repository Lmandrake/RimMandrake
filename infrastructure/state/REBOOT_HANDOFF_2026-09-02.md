# BENCH reboot handoff — 2026-09-02

> **LOAD-HEALTH SWEEP: DONE 2026-09-02 (BENCH).** All 25 believed-clean mods scored
> in 2 minimal loads: zero recovery resets, all sentinel defs resolve. WreckedMachines
> clean with VEF+VFE-furniture+Factory. Campaign-real findings:
> PAWNFLAVOR_BREAK_LABEL_FIX_1 (fixed+deployed), sonic forcedMiss (noted on
> SONIC_WEAPONS_EXPANSION_1), ARMOURY_ABSORBED_FRAMEWORK_DEPS_1 (filed —
> Armoury is NOT self-contained; donor-sunset risk). FireEcology burnedDef x6
> already known in FIRE_ECOLOGY_LOOP_1. Full 592 restored + relaunched, dump armed.

Session paused by owner ("stop / prepare for agent reboot") mid load-health sweep.
Machine state: full 592-mod config restored (md5 c9d20db5, verified); game is
running on an 11-mod isolation list (harmless — relaunch picks up full). No
background jobs. All prior work committed+pushed except what this handoff commits.

## In flight when stopped: LOAD-HEALTH SWEEP (not started, census done)

Plan: put each SELF-CONTAINED custom mod on a clean dependency-complete minimal
list, check (a) no "Resetting mods config" in Player.log (recovery reset =
load-crash), (b) ConfigError sweep, (c) get_defs confirms defs loaded. Batch
believed-clean mods; bisect any group that resets.

🔴 EXCLUDE from test lists (break mapgen or need absent donors):
- `mandrake.jawa.patches` (3 biome injectors), `mandrake.rsw.seaswaterline`
  (1 biome injector) — ecosystem patches, unresolved BiomeAnimalRecord → mapgen NRE.
- Any mod whose deps column named a non-mandrake mod NOT in the test list
  (BeastNorm→Mlie, Droidworks→HAR, IonWeapons→OuterRim, StarWarsRaces→VFE/genetics,
  etc.) — include the dep or skip the mod.

TRUE self-contained (deps: none, no biome inj) — safe first batch:
Armoury, AshkarrLandmarkArt, EmpirePursuit, FactionSlate, FireEcology,
FluidCanals, Graffiti, HelixTellurox(⛔known crasher — keep OUT), JawaRules,
IshkoDarkLandmarks, Livestock(fixed), Ninefold, Oracle, PawnFlavor, Pits,
PlanetPresetPrime, PlantGrowth, Property, RimDefDump, RiverSteam, SWBestiary,
StickCuisine, StrandedQuest, Visibility, WeatherSuite, WreckedMachines(→VFEFactory).

Clean minimal base (proven this session): harmony, core+5 expansions,
imranfish.xmlextensions, brrainz.rimbridgeserver + the mods under test.
After any RimWorld recovery-reset, the disk config is wiped to Core-only(6) —
REWRITE the intended list before relaunching.

## Proven this session (all committed)
- Rapid-minimal loop works end-to-end: found+fixed a load-crash in Livestock
  (ForsakenCrags <wildness>/<leatherLabel> invalid RaceProperties fields →
  corpse-gen NRE → recovery reset), spawned Cindermare/Skarnix live, custom art
  renders (not magenta). Offline validate_patch was blind to it.
- hot_reload_defs: PROVEN 0.04s on minimal; HANGS/unresponsive-for-minutes on
  full 592 (recovery unmeasured — do NOT fire under owner mid-play).

## Open items filed
- HELIX_TELLUROX_SHELL_LOAD_CRASH_1 — shell def parse error (MissingMethodException
  System.String ctor) → null butcherProducts → corpse NRE. Keep Tellurox OUT of loads.
- JAWA_SPAWN_KINDS_NO_RACE_1 — Zygerrian/Yoder/Taung raceless + 2 weapon bugs.
- BIOME_CAST_REFS_BREAK_MAPGEN_1 — donor-sunset forward risk.

## Owed (design)
- god_modes_deep_design.md §5.0 LAW OF WRATH written; the FOUR angry-mode
  rewrites it calls for (①Ishko ②Ohm ④Mob ⑤Rekko → withhold-not-invert) are
  NOT yet done. Evil-god slumber-pressure clause ruled, not yet applied to ⑦⑧.
- Sea-monster fanout: Opee pilot PIPELINE-PROVEN (src/RimStarWars/SeaBeasts/art/final/);
  17 more creatures ready to fan out; FIX codex_image.py harvest-on-timeout first.
