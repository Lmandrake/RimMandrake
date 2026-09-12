# MOD_OPTIONS_RETROFIT_1 — superb mod-options support, every mod, forever

Owner, 2026-09-12 (verbatim on the filing event): every one of our mods gets
"superb mod options support to tailor behavior and turn certain options on and
off" — retrofit all mods so far, requirement on all future mods. Trigger case:
the Greentide standalone mod must let a player enable individual special
contents (the Greatbole, sinking mud/churnmud, etc.) in OTHER biomes without
inserting the whole biome.

## spec
- Inventory every shipped/in-progress mod under `src/RimMandrake/`,
  `src/RimStarWars/` (if any), `src/RimUtinni/` that has player-facing
  behavior. For each: a `Mod` subclass + `ModSettings` with a real settings UI
  (`DoSettingsWindowContents`), not a stub.
- Per mod, expose at minimum: on/off per major feature/mechanic, and tuning
  where a number is the experience (spawn rates, intervals, damage scalars).
  Defaults = current shipped behavior; all-off must degrade gracefully (no
  NREs, no orphaned defs — features gate at the comp/mapcomponent/patch level).
- Greentide (rides `GREENTIDE_STANDALONE_MOD_1`): per-feature biome opt-in —
  Greatbole spawning, churnmud/mire, buried caches, each enableable in other
  biomes via settings (biome allowlist or "everywhere" toggle) without the
  Greentide biome itself.
- Settings that alter map generation vs live behavior must say which they are
  in the UI (worldgen-frozen campaign: some toggles only affect new maps).
- The requirement is DOCTRINE for future mods — recorded in project CLAUDE.md
  (this change) and folded into the rimworld-modding skill at next curation
  (LESSONS_INBOX line filed).

## verify
Every mod in the inventory has a settings screen listing its features;
toggling a feature off provably disables it live or at next map-gen (say
which) with no errors; Greentide features work in a non-Greentide biome when
opted in.

## criteria
Owner can open Mod Settings on any of our mods and meaningfully tailor it.

## progress — FOUNDRY 2026-09-12 (this pass)

Inventoried every folder with a `Source/` dir under `src/RimMandrake/`,
`src/RimStarWars/`, `src/RimUtinni/` (101 top-level mod folders total across
the three trees; ~59 carry a `Source/`+`.csproj`). Retrofitted via one
hand-built exemplar (Greentide) + 9 parallel Sonnet subagents, one cluster of
mods each, all following the same pattern (precedent:
`src/RimMandrake/GelatinousSlime/Source/SlimeMod.cs`): a `<Mod>Settings :
ModSettings` + `<Mod>Mod : Mod` class, `Scribe_Values` defaults = shipped
behavior, real gates wired into the actual mechanism (not stubs).

**DONE (compile-verified, real gates wired) — 45 mods this pass, plus
Greentide (hand-built) = 46, plus 3 that already had settings before this
item (GelatinousSlime, Oracle, EmpirePursuit) = 49 mods now carry a real Mod
Settings screen:**
RimMandrake: Aftermath, CreatureBehaviors, EnvironmentalHazards, FluidCanals,
Graffiti, Greentide, Inhabited, LoreStages, ManyWaters, MovingDunes, Ninefold,
Pits, ProximityHatch, Pyrelands, RaidRedesigner, RimProperty, RustChrome,
SacredGraffiti, ShipVermin, StructureInjections, TitanicCreatures, Visibility,
WeatherSuite.
RimStarWars: Armoury, BrainWorms, DesertVehicleReskin, Droidworks,
JawaIonWeapons, JawaRules, SWBestiary (two settings entries, JawaIkee +
Livestock — mirrors the mod's own already-unmerged assembly split), Shokk.
RimUtinni: Antiquities, DroidRepairJobs, FungalSoilTrade, LanternDeeps,
LongHunger, PlantGrowth, PyrelandsMechanics, RestrainingBolts, RiverColors,
RustCathedralWalls, ScavengerEvents, ShipMemory, ShipShields,
StructureInjectionsRUT, UtinniPatches.

Greentide specifically ships the item's own named trigger case: churnmud/mire
is now a settings-gated master toggle + severity slider, AND a genuine
cross-biome opt-in (`RM_MapComponent_CrossBiomeChurnmud`, mirrors the biome's
own `<mudTerrain>` trick) that repaints a settings-chosen fraction of a
NON-Greentide map's ordinary Mud terrain to RM_Churnmud once at
FinalizeInit — labeled worldgen-affecting/new-maps-only in the UI. The
Greatbole itself does not exist yet (About.xml: gated on
`ALPHA_MECHANICS_KIT_1`/`EXPLOSIVE_PLANT_GROWTH_1`) — nothing to gate there.

**Every touched `.csproj` rebuilds clean** (`Build succeeded, 0 Errors`),
re-verified independently by the coordinator after all 9 clusters landed —
including 3 satellite SelfTest projects that reach into a mod's parent
directory and needed their own `<Compile Include>` fix
(`RimMandrakeVisibility.SelfTest.csproj` was missing the new
`RM_VisibilityMod.cs`, found and fixed by the coordinator; Aftermath/
LoreStages/RaidRedesigner/Pits/RimProperty/JawaIonWeapons SelfTest projects
were unaffected).

**EXEMPT (checked, genuinely no runtime-tunable behavior — not skipped on
guess):**
- `Pyrinth` — pure XML content pack, no `.csproj`/`Source` C# at all.
- `Cuisine` — DefOf boilerplate + a divide-by-zero guard, no balance number.
- `KotORBandolierNorthFix`, `MSEDroidFix` — loose PNG sprite fixes, zero C#/Defs.
- `StarWarsPatches` — XML-only PatchOperations (load-time def transforms, no
  live mechanism a ModSettings toggle can gate without building a new
  Harmony-patched assembly from scratch).
- `Doctrine` — its XML is owner-ruled campaign doctrine, not a rebalance
  knob; its one C# file is a crash-fix Harmony postfix (a toggle would just
  reintroduce the crash).
- `MandrakePatches` — no `.csproj`/no compiled DLL; `Source/` holds one-off
  Python art-generation helper scripts, not runtime mod code.
- `PlanetPresetPrime` — dev-ergonomics tool, explicitly not player-facing
  per its own About.xml (players never see the world-creation page).
- `LoadTracer`, `RimDefDump`, `bridgetools/*` — dev tooling, never shipped
  to a player's game.
- Every `*ArtOverride` mod and `WreckedMachines` — pure texture reskins, no
  `Source/` dir, nothing to toggle beyond enabling/disabling the mod itself.

**NOT YET DONE — owed, and why this is BLOCKED not CLOSED:**
1. **Live in-game verification.** Everything above is compile-verified only.
   The item's own `## verify` section demands "toggling a feature off
   provably disables it live... with no errors" — that has NOT been run.
   ~46 assemblies changed in one pass across nearly the whole mod roster;
   before trusting this at the owner's table, deploy
   (`deploy_custom_mods.py --apply`, scoped to the mods actually touched —
   see caveat below) and run at least one full-modlist cold load (or a
   quicktest against a mod list wide enough to cover a representative
   sample), confirming: Mod Settings opens with no red errors for each mod,
   and one or two toggles genuinely change live behavior.
2. **Deploy is not yet applied.** A concurrent FOUNDRY window worked
   `WRECKAGE_VERMIN_SPAWN_1` in this same tree at the same time (shares
   `ShipVermin/Source/RM_ShipVerminMod.cs`, which now carries both items'
   settings — see that file's own header comment) and left its own Defs
   changes uncommitted in `StructureInjectionsRUT` and `UtinniPatches`
   (`Absorbed_Cephaloids_Defs.xml`, `RUT_Scarlands.xml`,
   `StructureLayoutDefs_Vaults.xml`) that are OUT OF SCOPE for this item. A
   plain `deploy_custom_mods.py --apply` (no `--mod` filter) would deploy
   their uncommitted work too — re-run the plan once their item lands and
   deploy explicitly `--mod`-scoped, or wait for them to commit first.
3. **Doctrine bullets already satisfied, no further action needed:** the
   CLAUDE.md "Every mod ships superb Mod Settings" section already exists;
   the LESSONS_INBOX line for folding this into the `rimworld-modding` skill
   at next curation is already filed (`"Mod options are mandatory on every
   mod (owner 2026-09-12, MOD_OPTIONS_RETROFIT_1)..."`).
4. **Any BRAND NEW mod filed after this pass** (none currently pending)
   still needs its own settings screen at build time per the standing
   doctrine — this item's closure will not retroactively cover it.

Next FOUNDRY pass: re-verify this list is still current (another window may
have added mods or closed WRECKAGE_VERMIN_SPAWN_1 in the meantime), then run
the live verification pass above. Close only once that live check is
clean.
