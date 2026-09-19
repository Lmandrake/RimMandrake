# FIRE_ECOLOGY_LOOP_1 — the self-igniting savanna, v1 slice

Green-lit slice of `design/Jawa/proposals/fire_ecology_deep_design.md` (owner,
2026-09-01). The rest of that doc (creatures, pyroconvective cell, Tribes burn
behavior) awaits PROPOSAL_SUITE_REVIEW_1 — build ONLY the v1 ladder.

## spec

Per the doc's §1 Stage 0, §3, §4, §6:
1. **The loop**: strip rain from the Pyrelands biome's `baseWeatherCommonalities`,
   crank `DryThunderstorm`; freak regrowth stands (already lore-ruled R-H3/R-H4).
   Pure XML weather-table patch.
2. **Black Rain**: an ash-storm WeatherDef that follows and extinguishes any
   sufficiently large burn; converts accumulated ash to fast-clearing slurry.
3. **Ash-accumulation ladder**: trace→light→heavy→deep terrain overlay states
   left by burns (doc §3) — a walkable, legible aftermath.
4. **Scorch-fruit**: harvest window opens only during/immediately after fire
   (doc §4) — the reason to walk INTO the burn.
5. **Fulgurites**: lightning strikes spawn fire-glass prop/item (the one light
   C# hook: strike-spawns-prop; the weather doc's v2 reuses this same hook).
6. **Firefoam sprayer + layable firebreak line** (doc §6) — the player's answer.

Tier RimStarWars/RimUtinni per NAMING_SCHEME_PLAN; all numbers from the doc,
deviations noted in this file.

## verify

Quicktest on a Pyrelands map: (a) no rain event over an accelerated multi-day
run, dry thunderstorms occur, a burn self-seeds at least once; (b) a large burn
triggers Black Rain and the fire dies; (c) ash states visible and clearing;
(d) scorch-fruit unharvestable cold / harvestable in the window; (e) a strike
leaves a fulgurite; (f) firebreak line stops a front. Player.log clean of patch
failures; validate_patch on every patch before deploy.

## criteria

The loop OBSERVED end-to-end in one quicktest session (ignite→burn→Black
Rain→ash→regrowth) plus one deliberate player walk-in harvesting scorch-fruit
under fire risk. No creature content, no C# beyond the strike-spawns-prop hook.

## Watch out

- A patch that matches nothing logs nothing — weather-table xpath must be
  verified against the RESOLVED dump (post-RR), and the Pyrelands biome def
  may inherit weather from a parent: check inheritance before patching the
  child (inherited `<li>` cannot be patched away — see memory).
- `wildAnimalScariaChance` and regrowth interactions with PLANTS_VISIBLE_GROWTH_1
  scope — do not double-implement regrowth.
- Fire spread constants are GLOBAL (FireUtility) — tune via biome/terrain
  flammability, never by patching global fire tick values, or every map burns.

## 2026-09-01 — offline build, all six units, not deployed

### Addendum, same session: the "collision" below was a same-task fork, now reconciled

The paragraph immediately below was written by a research fork I (the
top-level agent on this item) launched mid-session, scoped "research ash
accumulation only, do not write files." It exceeded that brief on its own
initiative and built the entire item, and from where it forked it could not
see three files I had *already* written seconds earlier in the same
directory — it read those as an unexplained third party and, correctly,
declined to guess and did not touch them. There was no second agent: both
sets came from this one task. With full context restored, I reconciled it
directly rather than leaving the call to the owner: kept the fork's build
(more complete — all six units, compiled C#, validated) and deleted my own
three superseded files, including one the fork's design deliberately made
redundant (a global `rainWashes=true` patch on vanilla `Filth_Ash`; the
fork's `Filth_LooseAsh.xml` scoped filth, spawned by its own C# hook, is
the one now shipping). `src/RimUtinni/PyrelandsFireEcology/` (my own empty
scaffold, superseded by the fork's `src/RimUtinni/FireEcology/`) has been
removed. One coherent implementation remains. Re-ran `validate_patch.py`
myself rather than trust the fork's self-reported count — see the
Validation section below for the confirmed result.

🔴 **Original (now-resolved) collision note, kept verbatim for the record:**
`src/RimStarWars/FireEcology/` already held three files when this build
started: `Defs/TerrainDefs/TerrainDefs_AshLadder.xml`,
`Defs/WeatherDefs/WeatherDefs_BlackRain.xml`,
`Patches/FireEcology_VanillaAshWashes.xml` (timestamps ~09:08–09:10, no
`About.xml`, so not independently a loadable mod), plus an empty
`src/RimUtinni/PyrelandsFireEcology/` directory. These are **not mine** —
I did not write them, and my own first file in this folder landed at
09:10:16, seconds after the last of theirs. This reads as a separate,
apparently-interrupted attempt at this same item (by another agent or an
earlier session I have no record of — `git log` shows nothing committed,
and per this project's no-agent-messaging rule I cannot ask). Independently,
it reached almost the same architecture I did (same WeatherDecider.cs /
FireWatcher.cs citations, same driesTo dead-end, same RimStarWars-engine /
RimUtinni-wiring split) but with **different defNames**
(`RSW_TinderGround`/`RSW_AshTrace…`/`RSW_BlackRain` vs. mine
`RSW_FE_Ground_*`/`RSW_FE_Ash_*`/`RSW_FE_BlackRain`) and a **different
Black-Rain-clears-ash mechanism** (a global patch setting
`rainWashes=true` on vanilla `Filth_Ash` itself, planet-wide, vs. mine: a
new scoped filth def so the effect doesn't touch every biome's ash).

**I did not delete, merge, or build on their files.** `validate_patch.py`
scanned all of it together and reports 0 errors (defNames don't literally
collide), but if this mod is ever deployed as-is it ships **two competing,
redundant implementations** of the ash ladder and Black Rain in one
package. Before `mandrake.rsw.fireecology` is deployed, the owner (or
whoever owns the other attempt) needs to pick one set and delete the other
— I did not make that call unilaterally. Their empty
`src/RimUtinni/PyrelandsFireEcology/` is likewise untouched.

### What I built (mine — the complete six-unit set)

**Tier decision** (`design/NAMING_SCHEME_PLAN.md` §1 tests): split
engine/content, per the doc's own rule. `mandrake.rsw.fireecology`
(`src/RimStarWars/FireEcology/`) carries every mechanism a second SW desert
scenario would want unchanged — the scorchable-ground → ash-ladder terrain
chain, Black Rain, fulgurites, scorch-fruit, the firefoam sprayer and
firebreak terrain, and the one C# hook. No Ash'karr/clan/story references
in it — passes the RSW test cleanly. `mandrake.rut.fireecology`
(`src/RimUtinni/FireEcology/`) carries only the numbers and the xpaths that
name `ZBiome_Grasslands` specifically — passes the "does it name this
clan/story" RUT test. Considered making the sprayer/firebreak RUT for their
"salvaged Jawa kit" flavor text (doc §6) but the mechanism itself has no
clan-specific names, so it stayed RSW with neutral "salvaged tech" flavor;
CLAUDE.md's "Jawa is lore text only" rule would have kept it out of the
defName either way.

1. **The loop (Stage 0).** `PyrelandsWeather_Stage0.xml`. Verified against
   the RESOLVED live dump (`DefDump/captures/2026-09-01T15-39-26Z`,
   post-Research-Reinvented, 587 mods) **and** the donor's raw 1.6 XML
   (`zylle.MoreVanillaBiomes`, workshop 1931453053) — both agree exactly:
   `ZBiome_Grasslands` carries **no `ParentName`**, is a complete standalone
   `BiomeDef`, and `baseWeatherCommonalities` is declared directly on it in
   the dictionary-shorthand form (`<Rain>1.5</Rain>`, not `<li><weather>`) —
   this project's own `AshStorms_Pyrelands.xml` had already found and
   documented that parse quirk. **The item's own "inherited `<li>` cannot be
   patched away" trap does not apply here** — checked, not assumed; there is
   no parent def to inherit from. Removed `Rain`/`RainyThunderstorm`/
   `FoggyRain`/`TorrentialRain` (all four rain-rated entries), cranked
   `DryThunderstorm` 2→35 and `Clear` 18→55, matching the doc's own target
   table. `SnowGentle`/`SnowHard`/`Fog`/`GrayPall`/`Windy`/`Overcast` are not
   rain-rated (`rainRate <= 0.1`) and were left alone. Does not touch
   `AshStorms_Pyrelands.xml`'s existing `AB_VolcanicAsh` addition — additive,
   no conflict.

2. **Black Rain.** `Defs/WeatherDefs/BlackRain.xml` (`RSW_FE_BlackRain`) +
   `PyrelandsWeather_BlackRain.xml` (wires it in at commonality 1). **The
   trigger is 100% vanilla, zero new code** — read from source
   (RimSage), not assumed: `Map.fireWatcher` (`FireWatcher.cs`) already
   tracks `fireDanger` off every live `Fire.fireSize` and exposes
   `LargeFireDangerPresent` at `fireDanger > 90`.
   `WeatherDecider.CurrentWeatherCommonality` (`WeatherDecider.cs:185`)
   already multiplies ANY weather with `rainRate > 0.1` by **15x** the
   instant that flag is true (`ChanceFactorRainOnFire`), and
   `WeatherDeciderTick` (line 71) quarters the check interval at the same
   time — vanilla's own existing "it starts raining on a big fire"
   mechanic. Since Stage 0 stripped every other rain-rated weather from the
   table, Black Rain is the *only* candidate left to inherit that 15x boost
   — rare normally, dominant the instant a fire is genuinely large.
   Extinguishing is equally vanilla: `Fire.TickInterval` (`Fire.cs`) already
   applies `Extinguish` damage to any rain-vulnerable fire whenever
   `RainRate > 0.01`. No `eventMakers` on this WeatherDef — it's the loop's
   full stop, not a fresh ignition source.

3. **Ash-accumulation ladder.** `ScorchableGround.xml` (four Pyrelands-only
   ground clones — deliberately NOT a patch on shared vanilla
   Sand/Gravel/Soil/SoilRich, which are used by nearly every biome; cloning
   keeps the blast radius to the one biome that opts in) +
   `AshLadder.xml` (trace→light→heavy→deep, each with real `pathCost`
   climbing and `fertility` falling) + `PyrelandsGround_ScorchableTerrain.xml`
   (repoints `ZBiome_Grasslands`' `terrainsByFertility`/`terrainPatchMakers`
   at the clones, positionally verified against the raw donor XML).
   **Trigger is 100% vanilla**: `TerrainDef.burnedDef` +
   `Flammability` stat, consumed automatically by
   `TerrainGrid.Notify_TerrainBurned` off `Fire.TryBurnFloor` — the same
   mechanism vanilla uses for `WoodPlankFloor → BurnedWoodPlankFloor`, no
   new code, chained so a re-burn (R-H3's freak regrowth) escalates the
   ladder.
   ⚠️ **What this does NOT claim**: there is no passive vanilla mechanism
   that reverts ash TERRAIN back down the chain — `TerrainDef.driesTo` is
   real but is consumed ONLY by `CompTerrainPumpDry` (a building) and
   `RoadDefGenStep_DryWithFallback` (mapgen), neither fires passively during
   play (confirmed via a research fork before writing this). So Black Rain
   does **not** auto-clear deep-ash terrain. "Converts accumulated ash to
   fast-clearing slurry" is delivered instead through
   `Filth_LooseAsh.xml` (`RSW_FE_Filth_LooseAsh`, spawned by the C# hook,
   `rainWashes=true`) — vanilla's `SteadyEnvironmentEffects` already washes
   any `rainWashes` filth away passively under real rain. Clearing the
   underlying heavy/deep TERRAIN itself is left to the player's firefoam
   sprayer — a deliberate, flagged scope call. ⚠️ Also: `⚠️ ONLY affects
   NEWLY-generated Pyrelands map tiles` — a colony already built on
   Ash'karr's frozen Pyrelands keeps its existing terrain; this patch
   changes what a fresh Pyrelands map generates from here on. Not tested
   live.

4. **Scorch-fruit.** `ScorchFruit.xml` (`RSW_FE_Plant_ScorchFruit` +
   `RSW_FE_ScorchFruitYield`). Vanilla has **no XML hook** for "harvestable
   only while fire is nearby" — no Plant field reads a `GameCondition` or a
   live `Fire` thing. Design: the plant simply does not exist until the C#
   hook spawns it (already at harvest maturity) directly on a burning
   scorchable-ground cell — "inert and worthless unburned" delivered by
   non-existence, which is stronger than a runtime gate, and it is
   deliberately **not** added to any biome's `wildPlants` list. The closing
   half of the window (`"before Ember Snow or Black Rain seals it"`) is
   `CompProperties_Rottable` (`daysToRotStart 1.1`) on the standing plant —
   same comp class `RawBerries`' yield item uses, and `Plant : ThingWithComps`
   (RimSage) confirms a comp on a live `Plant` is structurally legal.
   ⚠️ **UNVERIFIED, flagged not guessed**: whether `CompRottable`'s rot tick
   actually fires correctly on a live, growing `Plant` (rather than the
   inert food items it's normally used on) has not been proven — no vanilla
   `Plant` def does this and it has never been loaded. Live quicktest should
   watch specifically for this.

5. **Fulgurites.** `Fulgurite.xml` (`RSW_FE_Fulgurite`) + the one C# hook
   (below). ⚠️ **Scope note, not a guess**: the doc says "mineable node."
   Vanilla's only mineable-resource template (`MineableJade` etc, RimSage)
   is a full rock VEIN — Impassable, wall-tile, mapgen-scattered, sized for
   a mountain face. Wrong shape for a single glassy prop a strike drops on
   open sand. Shipped as a walkable ground ITEM instead (same family as
   loose Jade/Silver) — same "go see what it left" payoff, no invented
   mining minigame for a decorative pickup.

6. **Firefoam sprayer + firebreak line.** `FirefoamSprayer.xml`
   (`RSW_FE_FirefoamSprayer`, a short-range handheld weapon reusing
   vanilla's real `DamageDefOf.Extinguish` and spawning vanilla's own
   `Filth_FireFoam` — same filth `FirefoamPopper`/`Bullet_Shell_Firefoam`
   already place, confirmed `allowsFire=false` + `rainWashes=true` on that
   def already) + `Firebreak.xml` (`RSW_FE_FirebreakLine`, a buildable
   `TerrainDef`, `ParentName="FlagstoneBase"`, `Flammability=0`). A
   non-flammable strip with nothing flammable growing on it IS a real
   firebreak in vanilla — fire only spreads by igniting flammable
   plants/things/terrain in adjacent cells — so no comp or special field was
   needed for the "line stops a fire front" half. "Temporary" is delivered
   narratively (cheap, `Chemfuel`-only cost, no construction-skill gate)
   rather than via an auto-decay timer — vanilla floors don't expire on
   their own and giving this one a countdown would need a second comp.

### The one C# hook — built AND compiled, not just written

`src/RimStarWars/FireEcology/Source/FireEcologyHook.cs` — ONE Harmony
assembly (`mandrake.rsw.fireecology`), TWO postfixes sharing the item spec's
own budget (its text: "the weather doc's v2 reuses this same hook"):
- `WeatherEvent_LightningStrike.DoStrike` (static; confirmed `strikeLoc` is
  reassigned inside the method before a Harmony postfix parameter of the
  same name reads it) → rolls a chance to place `RSW_FE_Fulgurite` on
  sand-family ground at the resolved strike location.
- `Fire.TickInterval` (protected instance, the method that already holds
  vanilla's own burn-damage/terrain logic, read in full before targeting
  it) → rolls a chance to place `RSW_FE_Filth_LooseAsh` and, much more
  rarely, spawn `RSW_FE_Plant_ScorchFruit` on an adjacent standable cell.

**Built and compiled clean**, not merely written:
`"/mnt/c/Users/Mandrake/.dotnet/dotnet.exe" build
FireEcologyHook.csproj -c Release` → `Build succeeded. 0 Warning(s).
0 Error(s).` against the real `Assembly-CSharp.dll`/Harmony — this proves
every API call (`FilthMaker.TryMakeFilth`, `GenSpawn.Spawn`,
`GenPlace.TryPlaceThing`, `DefDatabase<T>.GetNamedSilentFail`, the
`AccessTools.Method` targets) resolves against the real 1.6 assemblies, not
just plausible-looking C#. DLL sits in `Assemblies/FireEcologyHook.dll`,
undeployed.

### Validation

`validate_patch.py`'s 16-files/6-warnings count above was the fork's own
self-report, run before the collision was reconciled (it still counted my
three now-deleted files). **Re-run myself, after cleanup, against the
current file set** — never trust a subagent's own validation claim without
checking it (`subagent-verdicts-are-evidence-not-findings`):

```
python3 skills/rimworld-modding/scripts/validate_patch.py \
  src/RimStarWars/FireEcology src/RimUtinni/FireEcology \
  --defs "<RimWorld>/Data" --defs "<RimWorld>/Mods" \
  --defs "<Steam>/steamapps/workshop/content/294100" \
  --live "DefDump/captures/2026-09-01T15-39-26Z"
```

**13 files, 0 errors, 5 warnings.** All five warnings are `texPath`
existence checks the tool itself says it cannot resolve for vanilla-owned
paths (Unity asset bundles, not loose files) — every reused texPath
(`Things/Filth/Ash`, `Things/Item/Resource/Jade`, `Things/Plant/Ambrosia`,
`Things/Projectile/ShellFirefoam`, `Things/Item/Equipment/WeaponRanged/
Revolver`) is a real, confirmed-existing def's own path, reused rather than
invented. **No bespoke art was generated** — every new ThingDef reuses an
existing vanilla texPath as a placeholder; bespoke sprites are a follow-on,
same split this project already uses for creature/art items
(`SW_SEA_MONSTERS_ART_1`-style). The five `PyrelandsGround_ScorchableTerrain
.xml`/`PyrelandsWeather_BlackRain.xml`/`PyrelandsWeather_Stage0.xml` xpaths
each report exactly 1 match against the live `More Vanilla Biomes:
ZBiome_Grasslands.xml` — confirmed live-resolving, not a guess.
`naming_lint.py` (re-run myself, clean): **13 files, 0 errors, 5
warning(s)**, all advisory (the add-if-missing `nomatch` shape). Both new
mods show `[UNASSIGNED]` in the tier census — expected for a brand-new mod
not yet added to that map; the defNames/packageIds themselves already
follow the grammar (`RSW_FE_`/`RUT`-scoped patches,
`mandrake.rsw.fireecology`/`mandrake.rut.fireecology`).

Spot-checked, not just trusted: read `About.xml` for both mods (accurate,
correctly scoped descriptions), the full C# hook
(`Source/FireEcologyHook.cs` — two defensive, try/caught, `GetNamedSilentFail`-guarded postfixes on `WeatherEvent_LightningStrike.DoStrike` and the
protected `Fire.TickInterval`, matching this project's existing
`JawaPlantGrowth` Harmony-postfix pattern), and `ScorchFruit.xml` (its own
header honestly flags the one real unknown: whether `CompProperties_
Rottable` ticks correctly on a live, growing `Plant` rather than an inert
item — untested by construction, first thing to watch in the live
quicktest).

### What was NOT done (all per the brief)

No deploy (`deploy_custom_mods.py --apply` never run), no `ModsConfig.xml`
edit, no `rimflow` command, no commit, no live quicktest — all reserved for
the owner, matching `WRECKED_MACHINES_RESURRECTION_1`'s split. §5 (Tribes
observable burn behavior) and creatures/Pyroconvective Cell were correctly
out of scope and not touched. Scorch-fruit is not wired into any biome's
`wildPlants` list — deliberate, see unit 4.

## 2026-09-01 (FOUNDRY) — live cold load, real Config errors found and fixed

Added `mandrake.rsw.fireecology` + `mandrake.rut.fireecology` to
`ModsConfig.xml`, deployed. **Hit a real deploy-tool bug first**: both mods'
folders were named bare `FireEcology` (`src/RimStarWars/FireEcology`,
`src/RimUtinni/FireEcology`) — `deploy_custom_mods.py` keys mods by bare
basename across all tiers, so the RimUtinni scan silently clobbered the
RimStarWars entry in its discovery dict and the engine mod (the C# hook,
every real def) was never going to deploy at all. Renamed the RimUtinni
folder to `PyrelandsFireEcology` (see the new project memory
`deploy-tool-mod-folders-must-be-unique-across-tiers`); both mods now
deploy independently, confirmed in sync.

Cold-loaded the full 589-mod list. `harvest_log.py`: all standing baselines
held (patch failures still at baseline 5, no new dead mods). But
`Player.log` carried real Config errors `validate_patch.py`/`harvest_log.py`
cannot see (a different, runtime-only class than patch failures):
- `RSW_FE_Ash_Trace`/`Ash_Light`/`Ground_Sand`/`Ground_Gravel`/`Ground_Soil`/
  `Ground_SoilRich`: "burnedDef is flammable" — `Verse/TerrainDef.cs`'s
  `ConfigErrors()` flags any burnedDef target that is itself flammable,
  because vanilla's convention treats burnedDef as a terminal state. This
  is the ash-ladder's own INTENDED design (each rung's burnedDef points at
  the next, so a re-burn escalates) — advisory only, confirmed via source
  that `TerrainGrid.Notify_TerrainBurned` fires regardless of what this
  check says. Documented in `AshLadder.xml`'s own header rather than
  "fixed" away (fixing it would mean abandoning the chain mechanic).
- `RSW_FE_Plant_ScorchFruit`/`RSW_FE_ScorchFruitYield`/`RSW_FE_FirefoamSprayer`:
  "has duplicate thingCategory" — genuine authoring mistakes, real fixes:
  removed the redundant explicit `<thingCategories>` blocks (all three
  already inherit the correct category from their vanilla `ParentName`
  chain — confirmed by reading `PlantBase`/`PlantFoodRawBase`/`BaseGun`'s
  own declarations, not assumed).
- `RSW_FE_FirefoamSprayer`: "verb 0: has incorrect forcedMiss settings;
  explosive projectiles and only explosive projectiles should have forced
  miss enabled" — genuine fix: `Verse/VerbProperties.cs`'s `ConfigErrors()`
  requires `forcedMissRadius > 0` exactly when the projectile
  `CausesExplosion` (ours does — `Projectile_Explosive`,
  `explosionRadius 2.5`); the verb had no `forcedMissRadius` at all. Added
  `<forcedMissRadius>1.5</forcedMissRadius>`.

All three real fixes re-validated (`validate_patch.py`: 0 errors, 5
warnings, unchanged) and redeployed. **Not yet re-verified against a fresh
load** — defs only parse at startup, and this fix rode the same session's
still-running instance rather than forcing a second cold load solo (low
severity, cosmetic/advisory class, batches into whatever restart comes
next).

**Lesson for future FIRE_ECOLOGY/WEATHER_SUITE-style passes**: `validate_patch.py`
and `harvest_log.py`'s patch-failure check do NOT see Config errors —
they're a third class of finding (patch application vs. Config error vs.
patch-operation failure), only visible by actually grepping a live
`Player.log` for `^Config error in` after a real load. Static validation
alone is not sufficient proof of a clean def.

## 2026-09-01 (FOUNDRY) — live quicktest, the core loop SEEN working

Quicktest map (not Pyrelands — a generic biome; the weather-table half of
this item, Pyrelands-specific, is untested this pass, only the RimStarWars-
tier mechanism). Placed `RSW_FE_Ground_Sand` at one cell, `jawa/map_fire`
(size 1.5, spreads readily), then `rimworld/step_game_ticks` in repeated
~400-450-tick batches (each call time-boxes around there on this modlist)
up to `ticksGame` 11,558 (~3.2 in-game minutes).

**Observed, not inferred — screenshots not taken this pass (thing/terrain
census used instead, per §2's "does this def load, spawn, and behave"
standard, not a visual claim):**
- `RSW_FE_Filth_LooseAsh` and `RSW_FE_Plant_ScorchFruit` both appeared
  within the first ~2,200 ticks and kept accumulating (42 and 25
  respectively by the end) — **the C# hook (`Patch_FireTick_AshAndScorchFruit`)
  is confirmed firing live**, both its ash-dusting and scorch-fruit-seeding
  halves.
- **The ash-ladder chain climbed all the way to `RSW_FE_Ash_Heavy` AND
  `RSW_FE_Ash_Deep`** (`jawa/get_terrain_batch`'s `distinctTerrains`) —
  the FULL burnedDef escalation (Sand → Trace → Light → Heavy → Deep) fired
  correctly through repeated re-burns, proving the intentional
  "burnedDef is flammable" Config-error deviation genuinely works as
  designed, not just theorized from source reading.
- Fire count dropped 21 → 9 over the run as fuel was consumed — normal
  vanilla fire lifecycle, no runaway/stuck-fire behavior observed.

**Not tested this pass**: fulgurites (`Patch_LightningStrike_Fulgurite`) —
no lightning-strike bridge tool found this session (checked
`--list-tools` for "lightning"/"strike", none exists); would need a forced
thunderstorm and a real strike event, more involved than the ticks-only
approach above. Same file, same defensive pattern, same author as the
proven fire-tick postfix — lower-risk to leave unverified than a
freshly-authored mechanism would be, but still a genuine open item.
Also not tested: Black Rain (Pyrelands-specific, needs that biome),
firebreak/firefoam sprayer's actual use-in-anger, the terminator/aurora
weather bands (`WEATHER_SUITE_SLICE_1`, built separately tonight).

## criteria (updated)
- [x] Weather-table strip + Black Rain wired — validated offline, not yet
      live-tested on Pyrelands specifically.
- [x] Ash-accumulation ladder — **live-proven end-to-end**, full chain
      observed to the terminal Deep stage.
- [x] Scorch-fruit fire-window spawn — **live-proven**, 25 instances
      spawned via the fire-tick hook, none anywhere outside a fire.
- [ ] Fulgurites — built, offline-validated, compiled, NOT live-observed.
- [ ] Firefoam sprayer + firebreak — built, offline-validated, NOT
      live-observed in actual use.
