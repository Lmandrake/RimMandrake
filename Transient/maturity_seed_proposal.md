# PROJECT_MATURITY_DASHBOARD_1 — proposed seed

**A PROPOSAL for BENCH+owner review. Nothing here has been written through
`rimflow capability set` — the registry is EMPTY. This doc is the survey that
would feed it, not the seeding itself.**

## Scope and method

**Systems = mod folders.** The ruling's own worked examples — "pits, ocean
biomes, trenches, water types, droids, cuisine, reset tenders, the Rust
Cathedral kit" — map one-to-one onto `Pits`, `SeaBeasts`/`SeasWaterline`,
`Droidworks`, `Cuisine`, `RustChrome` in this survey, which confirms the mod
folder is the right granularity, not something finer (a single def) or
coarser (a whole tier).

Surveyed: every mod folder under `src/RimMandrake/`, `src/RimStarWars/`,
`src/RimUtinni/` — 78 in total, dev tooling (`Utils/`, `rimflow/`,
`bridgetools/`, `mapsynth/`) excluded as not game systems. `Jawa/` (art bench,
ideoligion prose) is not a mod folder and is not in this survey; it feeds
GOAL_SHEET section 3 instead. `infrastructure/state/items/` (395 files) and
`infrastructure/state/GOAL_SHEET.md` were read for corroborating evidence but
did not change the method — see "what this does NOT do" below.

**Every suggestion below is FOLDER-EVIDENCE ONLY** — About.xml presence, Def/
Patch/`.cs` file counts, a compiled Assembly, PNG counts under `Textures/`.
Nothing here comes from a game load, a screenshot, or a play session.

**Function ladder** (`planned -> designed -> implemented -> runnable ->
checked-out`) — suggestions never go past `implemented`:
- `planned` — an empty/stub folder: no About.xml, no Defs, no Patches, no C#,
  no art.
- `designed` — About.xml and/or a thin body (fewer than 3 def/patch/cs files
  each) — declared, not yet substantial.
- `implemented` — About.xml plus a real body (an assembly, or >=3 of any one
  of def/patch/cs files).
- `runnable` and `checked-out` are **never suggested here** — those need the
  lightest proof the ruling actually asks for (a load already paid for,
  read by `harvest_log.py`, or the owner's own decision) and a folder scan
  cannot manufacture either. That determination is BENCH/owner's, drawing on
  session history this survey did not attempt to mine.

**Content ladder** (`none -> placeholder -> authored -> final`) — suggestions
never go past `authored`:
- `none` — no PNGs under `Textures/` (marked "mechanism-only" in the
  rationale when the name/shape also suggests no art was ever due — a Fix,
  Patches, Injections or similar mod).
- `placeholder` — fewer than 8 PNGs — thin, likely placeholder-grade.
- `authored` — 8+ PNGs — a real art pass has plainly happened.
- `final` is **never suggested here** — that is a sign-off, not a count.

## What this does NOT do

- It does **not** claim `runnable` for anything, even mods visibly active in
  the current `ModsConfig.xml` — deployment is not the same evidence as "it
  loaded without errors and did something," and manufacturing that check here
  would be exactly the new-instrument-as-prerequisite the ruling forbids.
- It does **not** mine `events.jsonl` or `items/` for closed verify-runs per
  mod to promote individual systems further — that is real, valuable
  incidental evidence and it is left for BENCH/owner to apply when seeding,
  not guessed at here under time pressure.
- It does **not** invent systems beyond mod folders (no "the deploy
  pipeline", no "code review process") — the ruling's examples are all mods,
  and staying literal keeps this proposal falsifiable against the same
  evidence anyone else can re-run.

## Headline (of THIS proposal, not the seeded registry)

78 systems surveyed. Suggested function: 53 `implemented`, 25 `designed`, 0
`planned`. Suggested content: 48 `none`, 16 `placeholder`, 14 `authored`.

Re-run the survey any time — it is a folder scan, not a load:
`python3` against `src/RimMandrake/`, `src/RimStarWars/`, `src/RimUtinni/`,
counting About.xml / Defs / Patches / `*.cs` / `Textures/**/*.png` per folder.
No script was added to the repo for this one-off; the counts above are
reproducible from the same globs.

## The full table

| tier | system | function_rung | content_rung | rationale |
|---|---|---|---|---|
| RimMandrake | Aftermath | implemented | none | About.xml + a real body: 0 def file(s), 0 patch file(s), 20 .cs file(s), compiled assembly present; no PNGs under Textures/ found |
| RimMandrake | DesertVehicleReskin | implemented | authored | About.xml + a real body: 0 def file(s), 4 patch file(s), 9 .cs file(s); 30 PNG(s) under Textures/ — a real art pass has happened |
| RimMandrake | FluidCanals | implemented | none | About.xml + a real body: 6 def file(s), 1 patch file(s), 11 .cs file(s), compiled assembly present; no PNGs under Textures/ found |
| RimMandrake | Graffiti | implemented | placeholder | About.xml + a real body: 5 def file(s), 0 patch file(s), 12 .cs file(s), compiled assembly present; 6 PNG(s) under Textures/ — thin, likely placeholder-grade |
| RimMandrake | GravshipAstronautFix | designed | placeholder | About.xml and/or a thin body (0 def, 0 patch, 0 cs) — declared, not yet substantial; 3 PNG(s) under Textures/ — thin, likely placeholder-grade |
| RimMandrake | Inhabited | implemented | none | About.xml + a real body: 20 def file(s), 0 patch file(s), 31 .cs file(s), compiled assembly present; no PNGs under Textures/ found |
| RimMandrake | LoadTracer | implemented | none | About.xml + a real body: 0 def file(s), 0 patch file(s), 3 .cs file(s), compiled assembly present; no PNGs under Textures/ — mechanism-only |
| RimMandrake | MandrakePatches | implemented | none | About.xml + a real body: 0 def file(s), 9 patch file(s), 0 .cs file(s); no PNGs under Textures/ — mechanism-only |
| RimMandrake | Ninefold | implemented | none | About.xml + a real body: 0 def file(s), 0 patch file(s), 26 .cs file(s), compiled assembly present; no PNGs under Textures/ found |
| RimMandrake | Oracle | implemented | none | About.xml + a real body: 0 def file(s), 0 patch file(s), 10 .cs file(s), compiled assembly present; no PNGs under Textures/ found |
| RimMandrake | PhytokinBarkHeadFix | designed | placeholder | About.xml and/or a thin body (0 def, 0 patch, 0 cs) — declared, not yet substantial; 1 PNG(s) under Textures/ — thin, likely placeholder-grade |
| RimMandrake | Pits | implemented | none | About.xml + a real body: 7 def file(s), 0 patch file(s), 29 .cs file(s), compiled assembly present; no PNGs under Textures/ found |
| RimMandrake | PlanetPresetPrime | implemented | none | About.xml + a real body: 0 def file(s), 0 patch file(s), 3 .cs file(s), compiled assembly present; no PNGs under Textures/ found |
| RimMandrake | Property | implemented | none | About.xml + a real body: 0 def file(s), 0 patch file(s), 27 .cs file(s), compiled assembly present; no PNGs under Textures/ found |
| RimMandrake | RaidRedesigner | implemented | none | About.xml + a real body: 0 def file(s), 0 patch file(s), 18 .cs file(s), compiled assembly present; no PNGs under Textures/ found |
| RimMandrake | ResearchKitEastFix | designed | placeholder | About.xml and/or a thin body (0 def, 0 patch, 0 cs) — declared, not yet substantial; 4 PNG(s) under Textures/ — thin, likely placeholder-grade |
| RimMandrake | RimDefDump | implemented | none | About.xml + a real body: 0 def file(s), 0 patch file(s), 5 .cs file(s); no PNGs under Textures/ found |
| RimMandrake | RustChrome | implemented | authored | About.xml + a real body: 0 def file(s), 0 patch file(s), 5 .cs file(s), compiled assembly present; 14 PNG(s) under Textures/ — a real art pass has happened |
| RimMandrake | SacredGraffiti | implemented | placeholder | About.xml + a real body: 2 def file(s), 0 patch file(s), 3 .cs file(s), compiled assembly present; 1 PNG(s) under Textures/ — thin, likely placeholder-grade |
| RimMandrake | SalvageClaim | implemented | none | About.xml + a real body: 0 def file(s), 0 patch file(s), 4 .cs file(s), compiled assembly present; no PNGs under Textures/ — mechanism-only |
| RimMandrake | SauridFrillFix | designed | placeholder | About.xml and/or a thin body (0 def, 0 patch, 0 cs) — declared, not yet substantial; 1 PNG(s) under Textures/ — thin, likely placeholder-grade |
| RimMandrake | Spikes | implemented | none | About.xml + a real body: 0 def file(s), 0 patch file(s), 5 .cs file(s); no PNGs under Textures/ found |
| RimMandrake | StrandedQuest | designed | none | About.xml and/or a thin body (2 def, 0 patch, 0 cs) — declared, not yet substantial; no PNGs under Textures/ found |
| RimMandrake | StructureInjections | implemented | none | About.xml + a real body: 0 def file(s), 0 patch file(s), 7 .cs file(s), compiled assembly present; no PNGs under Textures/ — mechanism-only |
| RimMandrake | TheftHauler | implemented | none | About.xml + a real body: 1 def file(s), 1 patch file(s), 7 .cs file(s), compiled assembly present; no PNGs under Textures/ — mechanism-only |
| RimMandrake | ToolBeltFix | designed | placeholder | About.xml and/or a thin body (0 def, 0 patch, 0 cs) — declared, not yet substantial; 1 PNG(s) under Textures/ — thin, likely placeholder-grade |
| RimMandrake | Visibility | implemented | none | About.xml + a real body: 0 def file(s), 0 patch file(s), 9 .cs file(s), compiled assembly present; no PNGs under Textures/ found |
| RimMandrake | WreckedMachines | implemented | authored | About.xml + a real body: 3 def file(s), 0 patch file(s), 0 .cs file(s); 12 PNG(s) under Textures/ — a real art pass has happened |
| RimStarWars | Armoury | implemented | authored | About.xml + a real body: 251 def file(s), 20 patch file(s), 55 .cs file(s), compiled assembly present; 1058 PNG(s) under Textures/ — a real art pass has happened |
| RimStarWars | BeastLairs | designed | placeholder | About.xml and/or a thin body (1 def, 0 patch, 0 cs) — declared, not yet substantial; 1 PNG(s) under Textures/ — thin, likely placeholder-grade |
| RimStarWars | BeastNorm | designed | none | About.xml and/or a thin body (0 def, 1 patch, 0 cs) — declared, not yet substantial; no PNGs under Textures/ found |
| RimStarWars | BlastDoorFrameAsyncFix | designed | placeholder | About.xml and/or a thin body (0 def, 0 patch, 0 cs) — declared, not yet substantial; 6 PNG(s) under Textures/ — thin, likely placeholder-grade |
| RimStarWars | CereanManeFix | designed | placeholder | About.xml and/or a thin body (0 def, 0 patch, 0 cs) — declared, not yet substantial; 1 PNG(s) under Textures/ — thin, likely placeholder-grade |
| RimStarWars | Cuisine | implemented | authored | About.xml + a real body: 3 def file(s), 0 patch file(s), 5 .cs file(s), compiled assembly present; 9 PNG(s) under Textures/ — a real art pass has happened |
| RimStarWars | Droidworks | implemented | authored | About.xml + a real body: 15 def file(s), 1 patch file(s), 27 .cs file(s), compiled assembly present; 457 PNG(s) under Textures/ — a real art pass has happened |
| RimStarWars | FireEcology | implemented | none | About.xml + a real body: 8 def file(s), 0 patch file(s), 3 .cs file(s), compiled assembly present; no PNGs under Textures/ found |
| RimStarWars | HelixTellurox | designed | placeholder | About.xml and/or a thin body (1 def, 0 patch, 0 cs) — declared, not yet substantial; 1 PNG(s) under Textures/ — thin, likely placeholder-grade |
| RimStarWars | JawaIkee | implemented | none | About.xml + a real body: 1 def file(s), 0 patch file(s), 3 .cs file(s), compiled assembly present; no PNGs under Textures/ found |
| RimStarWars | JawaIonWeapons | implemented | placeholder | About.xml + a real body: 5 def file(s), 0 patch file(s), 11 .cs file(s), compiled assembly present; 2 PNG(s) under Textures/ — thin, likely placeholder-grade |
| RimStarWars | JawaRules | implemented | none | About.xml + a real body: 0 def file(s), 0 patch file(s), 3 .cs file(s), compiled assembly present; no PNGs under Textures/ found |
| RimStarWars | JawaVoice | implemented | none | About.xml + a real body: 0 def file(s), 11 patch file(s), 0 .cs file(s); no PNGs under Textures/ found |
| RimStarWars | KotORBandolierNorthFix | designed | authored | About.xml and/or a thin body (0 def, 0 patch, 0 cs) — declared, not yet substantial; 20 PNG(s) under Textures/ — a real art pass has happened |
| RimStarWars | Livestock | implemented | placeholder | About.xml + a real body: 7 def file(s), 1 patch file(s), 3 .cs file(s), compiled assembly present; 3 PNG(s) under Textures/ — thin, likely placeholder-grade |
| RimStarWars | MSEDroidFix | designed | placeholder | About.xml and/or a thin body (0 def, 0 patch, 0 cs) — declared, not yet substantial; 1 PNG(s) under Textures/ — thin, likely placeholder-grade |
| RimStarWars | SWBestiary | implemented | authored | About.xml + a real body: 14 def file(s), 0 patch file(s), 0 .cs file(s); 70 PNG(s) under Textures/ — a real art pass has happened |
| RimStarWars | SeaBeasts | implemented | authored | About.xml + a real body: 6 def file(s), 0 patch file(s), 0 .cs file(s); 72 PNG(s) under Textures/ — a real art pass has happened |
| RimStarWars | SeasWaterline | designed | none | About.xml and/or a thin body (0 def, 1 patch, 0 cs) — declared, not yet substantial; no PNGs under Textures/ found |
| RimStarWars | StarWarsPatches | implemented | authored | About.xml + a real body: 5 def file(s), 22 patch file(s), 0 .cs file(s); 54 PNG(s) under Textures/ — a real art pass has happened |
| RimStarWars | StarWarsRaces | implemented | authored | About.xml + a real body: 13 def file(s), 0 patch file(s), 0 .cs file(s); 876 PNG(s) under Textures/ — a real art pass has happened |
| RimStarWars | StructureInjectionsSW | implemented | none | About.xml + a real body: 8 def file(s), 0 patch file(s), 0 .cs file(s); no PNGs under Textures/ — mechanism-only |
| RimStarWars | WeatherSuite | implemented | none | About.xml + a real body: 5 def file(s), 0 patch file(s), 3 .cs file(s), compiled assembly present; no PNGs under Textures/ found |
| RimUtinni | AftermathRites | designed | none | About.xml and/or a thin body (2 def, 0 patch, 0 cs) — declared, not yet substantial; no PNGs under Textures/ found |
| RimUtinni | Antiquities | implemented | none | About.xml + a real body: 5 def file(s), 0 patch file(s), 8 .cs file(s), compiled assembly present; no PNGs under Textures/ found |
| RimUtinni | AshkarrFlora | designed | none | About.xml and/or a thin body (1 def, 1 patch, 0 cs) — declared, not yet substantial; no PNGs under Textures/ found |
| RimUtinni | AshkarrInhabited | implemented | none | About.xml + a real body: 6 def file(s), 0 patch file(s), 0 .cs file(s); no PNGs under Textures/ found |
| RimUtinni | AshkarrLandmarkArt | designed | authored | About.xml and/or a thin body (0 def, 1 patch, 0 cs) — declared, not yet substantial; 49 PNG(s) under Textures/ — a real art pass has happened |
| RimUtinni | AshkarrWeatherSuite | designed | none | About.xml and/or a thin body (1 def, 1 patch, 0 cs) — declared, not yet substantial; no PNGs under Textures/ found |
| RimUtinni | BirthHatchDemo | designed | none | About.xml and/or a thin body (1 def, 0 patch, 0 cs) — declared, not yet substantial; no PNGs under Textures/ found |
| RimUtinni | DesertFixtures | designed | placeholder | About.xml and/or a thin body (1 def, 0 patch, 0 cs) — declared, not yet substantial; 1 PNG(s) under Textures/ — thin, likely placeholder-grade |
| RimUtinni | Doctrine | implemented | none | About.xml + a real body: 0 def file(s), 3 patch file(s), 5 .cs file(s), compiled assembly present; no PNGs under Textures/ found |
| RimUtinni | EmpirePursuit | implemented | none | About.xml + a real body: 1 def file(s), 0 patch file(s), 7 .cs file(s), compiled assembly present; no PNGs under Textures/ — mechanism-only |
| RimUtinni | FactionSlate | designed | none | About.xml and/or a thin body (0 def, 1 patch, 0 cs) — declared, not yet substantial; no PNGs under Textures/ — mechanism-only |
| RimUtinni | IshkoDarkLandmarks | designed | none | About.xml and/or a thin body (1 def, 0 patch, 0 cs) — declared, not yet substantial; no PNGs under Textures/ found |
| RimUtinni | LanternDeeps | implemented | none | About.xml + a real body: 3 def file(s), 1 patch file(s), 3 .cs file(s), compiled assembly present; no PNGs under Textures/ found |
| RimUtinni | LongHunger | implemented | none | About.xml + a real body: 4 def file(s), 0 patch file(s), 4 .cs file(s), compiled assembly present; no PNGs under Textures/ found |
| RimUtinni | MenuShell | designed | authored | About.xml and/or a thin body (2 def, 0 patch, 0 cs) — declared, not yet substantial; 11 PNG(s) under Textures/ — a real art pass has happened |
| RimUtinni | PawnFlavor | implemented | none | About.xml + a real body: 8 def file(s), 4 patch file(s), 0 .cs file(s); no PNGs under Textures/ found |
| RimUtinni | PlantGrowth | implemented | none | About.xml + a real body: 1 def file(s), 0 patch file(s), 5 .cs file(s), compiled assembly present; no PNGs under Textures/ found |
| RimUtinni | PyrelandsFireEcology | implemented | none | About.xml + a real body: 0 def file(s), 3 patch file(s), 0 .cs file(s); no PNGs under Textures/ found |
| RimUtinni | ResearchRetag | implemented | none | About.xml + a real body: 1 def file(s), 3 patch file(s), 0 .cs file(s); no PNGs under Textures/ — mechanism-only |
| RimUtinni | RestrainingBolts | implemented | none | About.xml + a real body: 1 def file(s), 0 patch file(s), 4 .cs file(s), compiled assembly present; no PNGs under Textures/ found |
| RimUtinni | Rites | designed | none | About.xml and/or a thin body (1 def, 0 patch, 0 cs) — declared, not yet substantial; no PNGs under Textures/ found |
| RimUtinni | RiverSteam | implemented | none | About.xml + a real body: 0 def file(s), 0 patch file(s), 3 .cs file(s), compiled assembly present; no PNGs under Textures/ found |
| RimUtinni | ShipMemory | implemented | none | About.xml + a real body: 1 def file(s), 1 patch file(s), 3 .cs file(s), compiled assembly present; no PNGs under Textures/ found |
| RimUtinni | StructureInjectionsRUT | implemented | none | About.xml + a real body: 10 def file(s), 0 patch file(s), 0 .cs file(s); no PNGs under Textures/ — mechanism-only |
| RimUtinni | UtinniPatches | implemented | authored | About.xml + a real body: 28 def file(s), 37 patch file(s), 0 .cs file(s); 19 PNG(s) under Textures/ — a real art pass has happened |
| RimUtinni | UtinniShell | designed | placeholder | About.xml and/or a thin body (1 def, 0 patch, 0 cs) — declared, not yet substantial; 1 PNG(s) under Textures/ — thin, likely placeholder-grade |
| RimUtinni | VaultDungeons | implemented | none | About.xml + a real body: 7 def file(s), 0 patch file(s), 0 .cs file(s); no PNGs under Textures/ found |

## How to seed this, if the owner accepts it as-is or after edits

One `capability set` call per row, e.g.:

```
python3 src/RimMandrake/rimflow/cli.py capability set Droidworks \
  --function-rung implemented --content-rung authored \
  --evidence-ref "src/RimStarWars/Droidworks: 15 defs, 27 .cs, compiled assembly, 457 PNGs" \
  --date 2026-09-08
```

Left to the parent, deliberately: this doc proposes, it does not write.
