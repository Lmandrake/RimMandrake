# The Scald round — result, 2026-09-26

_Driver: load-round agent, bridge held by BENCH. Skeleton written before the round
began; filled section by section as it ran._

## Status

- [x] 1. Deploy TerminalBiomes `--apply --prune`
- [x] 2. Add `mandrake.rm.luminouspigment` to the mod list
- [x] 3. Decision strings written (BEFORE launch)
- [x] 4. Minimal list + targets
- [x] 5. Launch via Steam, `Bridge token:` seen
- [x] 6. Quicktest `RM_TheScald`
- [x] 7. Harvest the whole log
- [x] 8. Restore the 629-mod list + release the bridge

## 1. Deploy TerminalBiomes (prune)

MEASURED: **161 files deployed, `-> VERIFIED in sync`.** The plan showed exactly
**7** `-` lines and every one is in the run sheet's table — no unaccounted deletion,
so the prune went ahead as the run sheet authorised.

Pruned: `RM_RainbowPigment.xml`, `RM_WelcomeBlanket.xml` (both deliberately renamed
away at `8052842e7`), `RUT_ScaldVent.png`, and the three stale flat catch textures
sitting inside `Graphic_StackCount` folders (`RM_Saal`, `RM_ShullaCatch`,
`RM_BladderboilCatch`) plus `RM_RainbowPigment.png`.

## 2. Mod list additions

MEASURED (parsed, never grepped):

| | activeMods |
|---|---|
| live, as handed over | 629 |
| stored `FULL.LATEST` before this round | 628 — **stale**, missing `mandrake.rm.explosivegrowth` (FOUNDRY's session) |
| live after inserting `mandrake.rm.luminouspigment` | **630** |
| `FULL.LATEST` after `--capture-full --apply` | **630**, md5 matches live |

`mandrake.rm.luminouspigment` inserted at index 556, immediately before
`mandrake.rm.terminalbiomes`, because TerminalBiomes' `About.xml` declares it a
**hard `modDependency`** and a `loadAfter`.

🔴 The stored FULL was 628 while the live list was 629. Restoring from the stored
snapshot at the end would have silently dropped `mandrake.rm.explosivegrowth` from
the owner's list. Captured live-as-FULL first, so the restore target is the true
630. Byte backup of the handed-over 629 also kept at
`deployed/config/ModsConfig.live-629.pre-scald-round-20260926.xml`.

## 3. Decision strings

Written before launch to `infrastructure/state/EXPECTED_FAILURES_next_load.md`
(the ExplosiveGrowth round's strings were spent and were replaced, not annotated).

🔴 **THREE assemblies ride this load, not the one the brief named.** MEASURED:
`RimMandrake.EnvironmentalHazards.dll` (rebuilt 13:37), `RimMandrake.TerminalBiomes.dll`
(rebuilt 13:37, `~` in the deploy plan) and `RimMandrakeLuminousPigment.dll` (brand
new, never loaded). One distinguishable expected-failure signature written per
assembly, per §3.

🔴 **`RimMandrake.TerminalBiomes.dll` emits NO log lines at all** — MEASURED, zero
`Log.Message/Warning/Error` calls in its `Source/`. Its success is entirely silent,
so it carries a def-read bar rather than a log bar.

## 4. Minimal list

🔴 **The stock `proof_terminalbiomes` tier builds a list that cannot load
TerminalBiomes' DLL.** MEASURED before launch:

- `TerminalBiomes/Source/RM_TerminalBiomesMod.cs` line 2 is
  `using RimMandrake.EnvironmentalHazards;`
- its `.csproj` carries `<Reference Include="RimMandrake.EnvironmentalHazards">`
  with a `HintPath` into that mod's `Assemblies/`
- 16 of its defs carry `MayRequire="mandrake.rm.environmentalhazards"`
- but `About.xml` declares EnvironmentalHazards only in `<loadAfter>`, **not** in
  `<modDependencies>`

`modset_builder` closes over `modDependencies` only, so the generated tier is 10
mods with EnvironmentalHazards absent — which is the exact shape of the
`TypeLoadException` → `Recovered from incompatible or corrupted mods` failure in
load-round §10.

Built the list by importing `modset_builder` and adding
`mandrake.rm.environmentalhazards` to the tier's `want`, then its own
`close_over`/`order`/`write_config`, with the same game-running guard and the same
`ModsConfig.before-tier-proof_terminalbiomes.xml` backup the tool writes.

**12 active**, all five expansions present (owner ruling 2026-09-19 — no DLC
ablated; Odyssey is load-bearing for `fishTypes`):

`brrainz.harmony` · `ludeon.rimworld` + Royalty/Ideology/Biotech/Anomaly/Odyssey ·
`brrainz.rimbridgeserver` · `mandrake.rm.creaturebehaviors` (EH's own hard dep) ·
`mandrake.rm.environmentalhazards` · `mandrake.rm.luminouspigment` ·
`mandrake.rm.terminalbiomes`

## 5. Launch

Launched via `steam.exe -applaunch 294100` (never the bare exe, load-round §10).

| pass | purpose | outcome |
|---|---|---|
| 1 | the round as briefed | `Bridge token:` seen, 272 log lines, **zero** abort strings, **zero** `Reached max messages limit` |
| 2 | verify the pass-1 fix | ready at **t+12s**, 175 log lines, zero abort strings |

Both logs kept: `Transient/Player.log.scald-round-pass1-20260926` and
`Transient/Player.log.scald-round-pass2-20260926`. The previous (FOUNDRY) log is
at `Transient/Player.log.pre-scald-round-20260926`.

`Initializing new game with mods:` names exactly the 12 intended mods — read off
that line, not off what I believed was active.

## 6. Quicktest RM_TheScald

### All three assemblies loaded — the expected-PRESENT check, not the absence of an error
`jawa/startup_types` (whole-process reflection over `[StaticConstructorOnStartup]`
+ `Verse.Mod` subclasses, joined to the owning mod) MEASURED live types per mod:

| mod | live types |
|---|---|
| RimMandrake: Environmental Hazards Kit | 10 |
| RimMandrake: Luminous Pigment | 2 |
| RimMandrake: Terminal Biomes | 1 |
| RimMandrake: Creature Behaviors | 1 |

⇒ TerminalBiomes' assembly resolved `RimMandrake.EnvironmentalHazards` cleanly.
The `TypeLoadException` its signature predicted did **not** fire, because EH was
put in the list. That is a positive result for the fix, not evidence the tier is fine.

### Def set — `jawa/get_defs`, one def per call
🔴 `jawa/get_defs` takes ONE `"DefType/DefName"` string. A comma-separated list
returns `success:true, foundCount:0` — MEASURED this round. Read `foundCount`/
`notFound`, never the payload text.

**21 of 23 PRESENT.** The 2 ABSENT are the two that MUST be absent:
`ThingDef/RM_WelcomeBlanket` and `ThingDef/RM_RainbowPigment` — ⇒ the prune took
and the rename is not duplicated in the live game.

PRESENT: `RUT_ScaldSteam` (the boil's breath) · `RUT_SteamCatch` · `RUT_ScaldVent` ·
`RUT_ScaldWreckHull/Tank/Frame` · `RM_Crowncarpet` · `RM_Deepfire` · `RM_GreySea` ·
`RUT_ScaldMargin` · `RM_RareScaldCatches` · all **10** Scald floor species.

### Resolved rosters — `jawa/biome_probe`, read off the RUNTIME caches
Not off XML: these backing fields are private and the resolved lists are properties,
so no reflective def read can see them.

| biome | animalDensity | animals | plantDensity | plants |
|---|---|---|---|---|
| `RM_TheScald` | **0.15** | **10** | **0.0** | 1 (`RM_Crowncarpet` 0.4) |
| `RM_GreySea` | **0.1** | **15** | 0.14 | **7** |

Scald: `RM_Eesh 1.2, RM_Doss 1.0, RM_Shulla 0.9, RM_Muddal 0.7, RM_Bladderboil 0.6,
RM_Thuum 0.5, RM_Karrash 0.45, RM_Noohm 0.4, RM_Ekkel 0.3, RM_ElderSando 0.005`.

Grey Sea plants: `RM_GlassVeilKelp 2.0, RM_SaltChimneyVine 2.0, RM_CubicSculpture 0.6,
RM_CruciblePod 0.5, RM_MosaicFanPalm 0.4, RM_SpherePlant 0.35, RM_BrineCrown 0.15`.

### What this quicktest could NOT prove
The quicktest colony lands on a **vanilla** biome, not the Scald — and the Scald is
`impassable`, reached only by `RM_SeaDiveHatch` from inside a gravship (owner ruling
2026-09-26). So `SCALD_MECHANICS_1`'s own bar — *condenser producing on a vent and
refusing off one; a pawn swimming the margin ring and never pathing through boil
cells; wrecks salvageable at burn cost; sails anchored to vents* — was **NOT** tested.
A def-resolution pass is not that bar. UNMEASURED, and the item stays open.

## 7. Log harvest

`harvest_log.py` **REFUSED** first, correctly: the def dump on disk was captured by
a 629-mod run and `ModsConfig` had 12. Re-run with `--stale-ok`, and **saying so out
loud** as the tool demands: *the baselines below are calibrated for the owner's
629-mod stack and this was a 12-mod tier, so every "BETTER" is an artefact of the
smaller list and means nothing.* Only the RED rows are readable.

### Pass 1 — two RED classes, both NEW, both ours

| class | pass 1 | baseline | pass 2 (after fix) |
|---|---|---|---|
| DEFS DISCARDED | **12** | 0 | **0** |
| cross-reference (def loader) | **13** | 0 | **0** |
| def ConfigErrors | 2 | — | 2 |
| dead mods (static ctor / type load) | 0 | 0 | 0 |
| Harmony patch failures | 0 | 1 | 0 |
| patch operations failed | 0 | 5 | 0 |
| stale Scribe refs | 0 | 0 | 0 |
| `Reached max messages limit` | **0** | — | **0** |

### 🔴 The round's main finding: 12 HediffDefs discarded whole — the `<li>` custom-loader trap

```
Exception loading def from file RM_DeepfireGlowHediffs.xml: System.ArgumentNullException:
  Value cannot be null. Parameter name: s
  at System.Single.Parse (System.String s, ...)
  at Verse.ParseHelper.ParseFloat (System.String str)
  at RimWorld.StatModifier.LoadDataFromXmlCustom (System.Xml.XmlNode xmlRoot)
```

`StatModifier` has a **custom loader**: it reads the node NAME as the stat and the
node TEXT as the value. Fed `<li><stat>Beauty</stat><value>1</value></li>` it takes
the stat name to be `li` and the value to be `null`, throws inside def parsing, and
**RimWorld discards the entire HediffDef** — not the one field.

MEASURED across the whole repo, **42** such entries in exactly **2** files, all inside
`statOffsets`/`statFactors` (both `List<StatModifier>`), so the rewrite is mechanical
with no judgement in it:

- `LuminousPigment/Defs/HediffDefs/RM_DeepfireGlowHediffs.xml` — **40** (27 offsets, 13 factors)
- `Greentide/Defs/HediffDefs/RM_Greentide_Hediffs.xml` — **2**

🔴 **The Greentide two were shipping silently in the owner's live 630-mod game** and
nothing had caught them; they are not part of this wave at all. This round found them
only because the same grep was run repo-wide rather than on the mod under test.

The 11 `No RimWorld.StatDef named li found to give to RimWorld.StatModifier (null stat)`
cross-references and the 1 `No Verse.HediffDef named RM_Glow_Products found to give to
RimWorld.ThoughtDef RM_ProductsGlowMood` are all **downstream of the same cause** —
`RM_Glow_Products` was missing because its def had been discarded.

**Fixed** (`<stat>X</stat><value>V</value>` → `<X>V</X>`), redeployed, and **re-proven
on a second 12-second load**: discarded 12→0, cross-references 13→0,
`HediffDef/RM_Glow_Products` and `ThoughtDef/RM_ProductsGlowMood` both read PRESENT live.

### Other findings, filed not fixed

1. **`RM_ElderUnknownWeapon`: `has a recipeMaker but no costList or costStuffCount`**
   (2 lines, `TerminalBiomes/Defs/ThingDefs_Items/RM_ElderTreasures.xml`). Survives
   both passes. Also carries a **borrowed placeholder texPath**
   (`Things/Item/RM_GreySea/RM_SaltCrystalItem`).

2. **`Graphic_StackCount`/`Graphic_Random` on single flat PNGs** —
   `Collection cannot init: No textures found at path ...`. ⚠️ The art is NOT missing:
   `RM_Deepfire.png`, `RM_CrowncarpetFresh.png`, `RM_CrowncarpetDead.png` and
   `RM_SaltCrystalItem.png` all exist in repo **and** in the game folder. A collection
   graphic class wants `_a`/`_b`/`_c` siblings and ignores the bare file. Either ship
   variants or drop to `Graphic_Single`. (Same family as the prune hazard the run sheet
   caught — one flat file inside a `Graphic_StackCount` folder.)

3. **Genuinely missing art**: `Things/Plant/RM_Leachmoss` and `Things/Plant/RM_Venomvine`
   (`RM_Leachmoss`, `RM_Venomvine`, EnvironmentalHazards, both `Graphic_Random`) —
   MEASURED absent from every `Textures/` root in the repo AND the game folder.

4. **`Got ThingsListAt out of bounds: (-1000, -1000, -1000)`** at map-gen, immediately
   after `Scatterer Verse.GenStep_ScatterThings from def RM_GreySeaScatterShoreDomes
   could not find cell to generate at` and `Could not find cluster center to scatter
   RM_SaltDomeShore`. Something is passing `IntVec3.Invalid` onward after a failed
   cluster-centre search. Grey Sea wave content.

5. 🔴 **`RM_TheScald` leaves `plantDensity` UNSET, so it is `0f`** — its one
   `wildPlants` row (`RM_Crowncarpet` 0.4) can never spawn through `WildPlantSpawner`.
   Same shape as `PROPANELAKE_ANIMALDENSITY_ZERO_1` on the plant axis. ⚠️ Not certainly
   a defect: `LuminousPigment/Defs/GenStepDefs/RM_GenStep_ShoreMats.xml` places
   crowncarpet by a GenStep scatter on ocean-shore cells instead, which is the mod's
   stated franchise-free route. So the biome row is at minimum dead, and regrowth after
   harvest is gated on the same zero. Needs a ruling, not a unilateral edit.
   (MEASURED alongside: `RM_PropaneLake` leaves BOTH densities unset, confirming
   `PROPANELAKE_ANIMALDENSITY_ZERO_1` live; `RM_TwilightSea` leaves `plantDensity` unset
   but carries 0 wildPlants, so it is moot there.)

### Not findings, recorded so nobody re-derives them
- The many `Could not load Texture2D at 'Things/Plant/Echeveria/...'`,
  `'swplants/Bloddle/...'`, `'Things/Item/ToxicMeat/...'` lines are **donor paths absent
  from a 12-mod tier**, not our defects.
- `RED  RimAI Core booted / Inhabited ready  MISSING` in the harvest is those mods not
  being in the list.
- `Scatterer RM_GenStep_ScaldWreckScatter ... could not find cell` on a vanilla
  quicktest map is a correctly-gated scatterer finding no Scald cells.

## 8. Restore + release

**RESTORED — 630 active, parsed with `ET.parse(...).find("activeMods")`, never grepped.**

Proved against the byte backup of the list as it was handed over
(`deployed/config/ModsConfig.live-629.pre-scald-round-20260926.xml`, 629):
**nothing lost**, exactly one addition — `mandrake.rm.luminouspigment`.
`explosivegrowth`, `terminalbiomes`, `environmentalhazards`, `greentide` all spot-checked
PRESENT. `modlist_swap --status` reports `live currently matches: FULL`, md5 identical.

The game is CLOSED, so the owner's next launch takes the restored list.

## Verdicts per item

| item | verdict | evidence |
|---|---|---|
| `SCALD_MECHANICS_1` | **NOT CLOSED** | Its remaining bar is a quicktest map *in the biome* showing the condenser, the margin swim, the wrecks and the sails. The Scald is `impassable` and reached only by `RM_SeaDiveHatch` from a gravship, so `rimworld/start_debug_game` lands on a vanilla biome and cannot exercise any of it. Every Scald def resolves live (`RUT_ScaldSteam`, `RUT_SteamCatch`, `RUT_ScaldVent`, the three wrecks) — that is def-resolution, not the bar. **UNMEASURED.** |
| `SCALD_ART_UPGRADE_WAVE_1` | **partially confirmed** | The three wreck defs load with no config errors and the stale flat predecessors were pruned out of the game folder. `shadowData` could not be read live — `jawa/get_defs` answers `(no such field)` for `graphicData`/`shadowData` (nested objects), so the three distinct volumes are verified from the deployed XML only. |
| `SCALD_WATER_AGITATION_FLECKS_1` | **half confirmed** | The `EnvironmentalHazards` DLL carrying `RM_MapComponent_WaterAgitation` deployed and loaded (10 live types), no error from that assembly in either pass. The ripple behaviour itself is a **look-at-it** bar and the owner asked to be present; not attempted. |
| `SEA_FISHABLES_ALIVE_IN_DEPTHS_1` (Scald half) | **CONFIRMED** | `jawa/biome_probe` read **10** resolved floor species off the runtime caches at `animalDensity 0.15`, against the item's own measured baseline of *3 inline + 3 canon patch-added*. The Scald half of the gap is closed; the Grey/Twilight/Propane halves are not this round's. |
| `SCALD_STEAM_WEATHER_DESIGN_1` | **confirmed present** | `WeatherDef/RUT_ScaldSteam` PRESENT (*the boil's breath*); `Patches/RUT_ScaldSteamLock_BiomeWiring.xml` deployed and produced no patch-failure line. ⚠️ A patch that matches nothing logs nothing, so "0 patch failures" is not proof the wiring bit — the weather's *behaviour* is unproven. |
| Grey Sea wave (rode along) | **defs land, two defects** | `RM_GreySea` resolves with **15** animals and **7** plants off the runtime caches. But `RM_SaltDomeShore` fails its cluster-centre search and is followed by `Got ThingsListAt out of bounds: (-1000,-1000,-1000)`, and `RM_SaltCrystalItem` is a flat PNG under a collection graphic class. |
| LuminousPigment (new mod, first ever load) | **LOADS, after a fix** | Shipped with its entire glow-hediff family (12 HediffDefs) being discarded at load. Fixed and re-proven in-round. Its three item graphics still fail `Collection cannot init`. |

## For the owner

1. **Two shipped mods were silently discarding whole HediffDefs.** `LuminousPigment`
   had never been loaded, so its 12 glow hediffs had never existed in a running game —
   but `Greentide`'s two have been in your live list all along, discarded every load,
   with nothing reporting it. Both are fixed and re-proven. Worth asking whether any
   other custom-loader field in the tree is written in the `<li>` form.

2. **`proof_terminalbiomes` — and possibly other `proof_*` tiers — cannot load the mod
   they are meant to prove.** The tier does `modDependencies` closure only, and
   TerminalBiomes' hard assembly reference to EnvironmentalHazards is declared as
   `loadAfter`. Two fixes, both cheap: add EH to TerminalBiomes' `modDependencies`, and
   have the wave check every biome mod's `.csproj` references against its `About.xml`.

3. **`RM_TheScald` has `plantDensity` unset (0f).** Its `wildPlants` row cannot fire.
   Crowncarpet does have a GenStep route, so this may be intended — but it needs your
   word rather than my edit.

4. `mandrake.rm.luminouspigment` is now in your list (630). That was required: the
   Scald's `wildPlants` row points into it.
