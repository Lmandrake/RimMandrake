## spec (design proposal, Fable subagent, 2026-09-09 — awaiting owner ruling)

**Reading the brief.** ManyWaters' own About.xml says it "gathers all water
effects/*types*", so the coherent reading is: **ManyWaters becomes the
RimMandrake-tier roster of coloured liquid TerrainDefs (water and slime),
FluidCanals consumes them** (`FluidDef.floodTerrain` is already just "which
TerrainDef"), and Utinni patches decide which biome/canal gets which colour.
Slime is not a conflation: FluidCanals' About names slime as a fluid it will
carry, and the only slime water in the stack today is Alpha Biomes'
`AB_LiquidSlime` (third-party, `WaterShallowBase` + its own `AB_SlimeRamp`
texture + `Map/WaterDepth`) — i.e. slime already IS "water with a different
texture". Colour lives entirely in the terrain; neither engine has a colour
field anywhere today.

**1. Many colours of water — mechanism.** Recommend **(a): N pre-authored
TerrainDef variants sharing one texture, differing only in `<color>`.** That
is vanilla's own colour convention (`Terrain_Floors_StoneTile.xml`: one
texture, six `<color>` defs) and this repo's own (`AshLadder.xml` four rungs
on one texture, `ScorchableGround.xml`, `JawaSaltCrust.xml`). `TerrainDef
.DrawColor` is passed straight into `GraphicDatabase.Get<Graphic_Terrain>
(texturePath, Shader, …, DrawColor)` for every edgeType including
`TerrainWater` (`Verse/TerrainDef.cs:433`). No runtime tint exists —
`TerrainGrid` stores a def per cell, nothing per-cell for colour — so a
runtime-tintable-material approach (b) means a Harmony draw patch plus a
per-colour material and buys nothing the owner can see that (a) doesn't.
Cost per colour: one ~10-line def (ParentName `WaterShallowBase`, clone
`WaterShallow`, add `<color>`), zero art.

⚠️ One gate before authoring twelve: **no vanilla water def uses `<color>`**,
and water draws twice — the base `TerrainWater` material (tinted) plus the
`Map/WaterDepth` overlay material, which is created with no colour at all
(`TerrainDef.cs:448`). Whether the tint reads through the depth overlay is
UNVERIFIED. Test ONE coloured def on a quicktest first. Fallback if it
washes out: a recoloured copy of `WaterShallowRamp.png` per colour (still
XML-only, no shader work) — exactly Alpha Biomes' own route.

**2. Many colours of slime — whose feature.** Split, along the line already
drawn today:
- **FluidCanals owns identity**: one `FluidDef` per (fluid, colour) → one
  **temporary** slime TerrainDef (`FluidDef.ConfigErrors` refuses
  non-temporary; `ShallowFloodwater` is the model). `ticksPerTile` makes it
  viscous; nothing else changes.
- **ManyWaters owns the terrain roster and the ambient effect.** Two
  findings make the effect cheaper than expected: (i) the Steam fleck uses
  the `Mote` shader and `FleckCreationData.instanceColor` tints it at spawn
  (`FleckStatic.cs:86,145`), so the existing hook gains a `fleckColor` field
  on the extension with no new art; (ii) vanilla 1.6 already has
  **`TerrainDef.throwFleckChance` + `fleckData`** consumed by
  `SteadyEnvironmentEffects.cs:171` — per-terrain ambient flecks in pure
  XML. So coloured slime bubbles need a tinted `Steam` FleckDef clone
  (`graphicData.color`) and a `fleckData` block on the slime def: **zero
  C#**. ManyWaters' C# extension would move from biome-scope to
  terrain-scope only if the owner wants river-style timing control per
  fluid; not needed for v1.
- Slime standing pools vs canal slime are **two defs per colour**
  (non-temporary + temporary), because the flood layer demands
  `temporary=true` and a permanent pool must not.

**3. v1 slice — one sitting, one look.** A quicktest map, saved per the
"options he must LOOK at ship as a savegame" rule with a grid key:
- Row A: `WaterShallow` untinted control + 5 tinted `RM_Water_<Colour>` defs
  (colour on `WaterShallowRamp`).
- Row B: `AB_LiquidSlime` control + 5 tinted `RM_Slime_<Colour>` defs
  (colour on `AB_SlimeRamp`, texture referenced by path; AB must be active),
  each with `fleckData` pointing at a matching `RM_Fleck_Steam_<Colour>`.
- Palette entry per colour: name, RGB, base ramp, intended fluid, one-line
  lore hook — a `Palettes/*.md` OPTIONS list per this repo's material-palette
  convention, not a ruling.

Author count: **12 TerrainDefs + 5 FleckDefs**, all XML, all in ManyWaters.
No FluidDefs yet — the temporary siblings and canal wiring follow once the
owner picks colours. Painted via `jawa/set_terrain`, 4×4 patches, ~6-cell
pitch, night lighting available for `glowColor` if wanted.

## verify
Owner looks at the saved v1 quicktest (grid key names which cell is which
colour/fluid) and picks: which water colours stay, which slime colours
stay, whether the fleck-tint effect reads right, and whether the
runtime-tint gate (water colour surviving the WaterDepth overlay) needs the
texture-recolour fallback instead.

## criteria
Not yet ruled — this item stays a design proposal until the owner reviews
the v1 slice and rules on colour count/palette. Do not author the full
roster past the single quicktest-gate check without that ruling.

## Open questions the design could not resolve
- Whether `<color>` survives the `WaterDepth` overlay material (gates
  whether (a) needs the texture-recolour fallback) — UNVERIFIED, needs a
  live quicktest check, one tinted def is enough to answer it.
- Whether `jawa/set_terrain` can lay a `temporary` def for a look-test (it
  calls `SetTerrain`, not `SetTempTerrain`, per FluidCanals' own notes) — v1
  sidesteps by testing standing (non-temporary) variants only.
- `AB_LiquidSlime` ships from Alpha Biomes' `1.5/` folder only; not
  confirmed it loads under 1.6.
- Whether Dubs Bad Hygiene treats a tinted clone as drinkable depends on
  tags copied, not colour — copy the parent's tags verbatim and it is
  unchanged.
- `SteadyEnvironmentEffects.throwFleckChance` was only read as firing on
  outdoor unroofed cells (line 171) — worth confirming for roofed canal
  cells if that matters to the design.

## Owner RULED — question card, 2026-09-09

**Skip the one-def gate test — author the full v1 slice now** (12
TerrainDefs + 5 FleckDefs, still saved as a look-and-pick savegame per the
"options he must LOOK at ship as a savegame" rule; if the WaterDepth-overlay
tint gate turns out to fail, fix forward with the texture-recolour fallback
rather than blocking on a separate pre-test).

**Added scope, owner verbatim (paraphrased from voice): "if the thirst kid is
present, we should have different bottles of the colored waters too.
Conditional mod check. Look for other water-related mod interactions like
this — like maybe the whole diving mod, and rain."**

- Identify what mod actually provides a drinkable water-bottle/canteen item
  with a thirst mechanic on the live modlist (candidates to check: Dubs Bad
  Hygiene's water bottles, RimWorld of Magic, any "Thirst"-named mod, a
  child/"kid" mechanic mod referencing thirst) — do not guess the packageId,
  read `ModsConfig.xml` and the candidate's own defs.
- If found: add colour-matched bottled-water item variants, gated behind a
  `MayRequire`/`PatchOperationFindMod` on that mod's packageId — never
  ungated.
- Separately check for any other live mod with a genuine water-COLOUR
  interaction worth coordinating with: a diving/underwater mod, and any
  rain-collection or weather mod that reads terrain water colour. Report
  what's found even if nothing is actionable.

## FOUNDRY offline pass, 2026-09-09 — done, live step OWED

**Offline authoring complete.** `src/RimMandrake/ManyWaters/Defs/`:
- `TerrainDefs/RM_ColoredWater.xml` — 10 new TerrainDefs, 5 colours (Rust,
  Verdigris, Amber, Violet, Chalk): `RM_Water_<Colour>` (ParentName
  WaterShallowBase, tints vanilla WaterShallowRamp, ungated) and
  `RM_Slime_<Colour>` (same base, tints Alpha Biomes' AB_SlimeRamp,
  `MayRequire="sarg.alphabiomes"` on the def tag — confirmed live packageId
  and confirmed AB ships a 1.6/ folder, resolving the design's open question).
- `FleckDefs/RM_ColoredSteam.xml` — 5 tinted `RM_Fleck_Steam_<Colour>` clones
  of vanilla `Steam`, wired via `throwFleckChance`/`fleckData` on each
  `RM_Slime_<Colour>` (the exact mechanism Odyssey's own `HotSpring` uses,
  confirmed by reading `Data/Odyssey/Defs/TerrainDefs/Terrain_Water.xml:128`).
- `ThingDefs/RM_ColoredWaterBottles.xml` — 5 `RM_WaterBottle_<Colour>`,
  `ParentName="DBH_WaterBottle"`, `MayRequire="Dubwise.DubsBadHygiene.Lite"`.
- `Palettes/manywaters_color.md` — the colour set, marked freshly-authored
  (not sourced), plus `Palettes/README.md` updated.
- `About/About.xml` — description + `loadAfter` for the two soft deps.

Read against the live def dump (`.../DefDump/captures/2026-09-09T01-54-07Z`):
`DBH_WaterBottle`, `AB_LiquidSlime`, `WaterShallowBase`, and vanilla `Steam`
all exist in the current mod set; none of the 20 new defNames collide with
anything in that dump.

**Thirst-mod finding**: `Dubwise.DubsBadHygiene.Lite` (workshop 2570319432)
defines `DBH_WaterBottle` itself (`1.6/Defs/ThingDefs_Items/
Items_Resource_Stuff.xml:108`); `Dubwise.DubsBadHygiene.Thirst` (workshop
2582878800, "Adds a thirst need to Dubs Bad Hygiene Lite") supplies only the
`Need_Thirst` need/class Lite's own NeedDef references — it ships no Defs of
its own. Both are active. The correct MayRequire gate is therefore Lite's
packageId (it's what actually defines the parent), which is what was used.
DBH's full (non-Lite) mod is NOT active and was not depended on.

**Diving/underwater mod**: none found on the live modlist — no defName,
packageId or mod name containing dive/scuba/submarine/ocean/kelp/reef/
snorkel/amphib. Nothing to coordinate with.

**Rain/weather-reads-water-colour mod**: `dorbo.watersfx` ("LiquidSFX",
workshop 3758773902) is the only water-adjacent ambient mod on the list; its
own About.xml says it "Adds sound to rivers, coasts, still bodies of water,
lava and marshes" — audio only, confirmed by reading its About.xml. No
colour interaction, nothing to gate against.
Two more names turned up in a keyword sweep of ModsConfig.xml —
`milkwater.destinymod` and `grimterra.terrainretexturemod` — but neither
was locatable on disk (workshop or local Mods) to inspect their defs before
the time budget on this sub-check ran out. Neither name suggests a
water-colour reader; flagged UNCONFIRMED rather than asserted clean.

**Live step OWED — two separate blockers found, in sequence.**

1. `rimflow bridge who` first showed it held by another FOUNDRY window (idle
   ~2 min, well under the 45-min staleness bar) for
   `WORLD_BOUNDARY_LAND_AT_SEA_ELEVATION_1` — per this item's own
   instructions, did not wait or force-take it.
2. It freed up shortly after and was taken (`bridge take --for
   "MANYWATERS_COLOR_SUPPORT_1 v1 quicktest"`). Running
   `deploy_custom_mods.py --mod ManyWaters` (plan only) then surfaced a
   bigger blocker: **`mandrake.rm.manywaters` is not in the currently active
   `ModsConfig.xml` at all** — confirmed by grepping the live file for every
   `mandrake.rm.*` entry; ManyWaters (and its `RM_DeepSand` content from
   SAND_SWIMMERS_MOD_1, already merged) has apparently never been switched
   on in the campaign's mod list. Testing this item therefore needs a
   **mod-list change plus a full cold-load restart** (~15-25 min on the
   ~580-mod full list) — a quicktest map cannot fake a mod-list change
   (`rimworld-debug-testing` skill, §6). The game is currently UP and running
   the full list.
   ⚠️ **Did not restart.** The bridge-who probe a minute earlier showed
   ANOTHER FOUNDRY window actively mid-investigation on
   `WORLD_BOUNDARY_LAND_AT_SEA_ELEVATION_1`, which — unlike a bridge *drive*
   lock — the "bridge free" state does not capture: that window may still be
   relying on the currently-running game/world for its own live checks.
   Restarting the whole game process out from under a concurrent
   investigation is a materially bigger disruption than taking the drive
   lock, and the owner was not present to arbitrate a collision between two
   live needs. Released the bridge again rather than take that risk
   unilaterally.

Still owed, exactly as scoped in the original ask, PLUS the newly-found
mod-activation step:
0. Snapshot the current `ModsConfig.xml` to `infrastructure/state/modlists/`,
   add `mandrake.rm.manywaters` to `<activeMods>` (its only real dependency
   is `Ludeon.RimWorld`; `sarg.alphabiomes` and
   `Dubwise.DubsBadHygiene.Lite`/`.Thirst` are already active, well before
   the existing `mandrake.rm.*` cluster near the end of the list, so plain
   insertion into that cluster satisfies `loadAfter`), then restart the game
   — check `rimflow bridge who` AND that no other window's item plausibly
   needs the currently-running game before pulling it down.
1. `rimflow bridge take --for "MANYWATERS_COLOR_SUPPORT_1 v1 quicktest"`
   once free (retake after the restart).
2. Deploy ManyWaters (`deploy_custom_mods.py --mod ManyWaters --apply`) —
   these defs have never been deployed or loaded in a running game.
3. Quicktest map, paint Row A (WaterShallow control + 5 RM_Water_Colour)
   and Row B (AB_LiquidSlime control + 5 RM_Slime_Colour), 4x4 patches,
   ~6-cell pitch, per the design's §3 recipe.
4. **First thing painted**: one RM_Water_Colour cell — confirm whether
   the tint survives the `Map/WaterDepth` overlay (the design's one
   UNVERIFIED mechanism). If it washes out, recolour a copy of
   `WaterShallowRamp.png` per colour as the fallback (still XML-only) rather
   than stopping.
5. Save as a look-and-pick savegame per the ship-as-savegame rule, with a
   grid key (cell -> colour/fluid) as its own file, not inside `Transient/`.
6. `rimflow bridge release` the instant done.
7. Only then close the item.

This item stays in `doing` — do not close on this commit.

## 🔴 BLOCKER FOUND 2026-09-09 (FOUNDRY, `MODLIST_RESTORE_AND_BATCH_DEPLOY_1`) — this mod HARD-CRASHES every game construction

Step 0 above was executed as part of the batch restore: ManyWaters was deployed
and added to the live `ModsConfig.xml`. **The mod list loaded fine and the main
menu was healthy, but no game could be constructed at all** — loading the
campaign save, starting a colony and quicktest all died identically:

```
Verse.GameDataSaveLoader.<LoadGame>g__PreLoadAct
 → Verse.Game..ctor()
   → RimWorld.ReadingPolicyDatabase..ctor()
     → ReadingPolicyDatabase.GenerateStartingPolicies()
       → Verse.GenTypes.SameOrSubclassOf(baseType, parentType)   ← NullReferenceException
```

**Cause.** `Defs/ThingDefs/RM_ColoredWaterBottles.xml` defines five ThingDefs —
`RM_WaterBottle_Amber`, `_Chalk`, `_Rust`, `_Verdigris`, `_Violet` — with
`ParentName="DBH_WaterBottle"`, and that inheritance is **not supplying a
`thingClass`**. The live load says so directly, five times:

```
Config error in RM_WaterBottle_Amber: has null thingClass.        (and the other four)
```

`ReadingPolicyDatabase.GenerateStartingPolicies()` (`Source/RimWorld/ReadingPolicyDatabase.cs:69`)
walks **every** ThingDef in the database and dereferences the field with no null
guard:

```csharp
foreach (ThingDef item in DefDatabase<ThingDef>.AllDefsListForReading)
    if (item.thingClass.SameOrSubclassOf<Book>())
```

Because that constructor runs inside `Game..ctor()`, a single null `thingClass`
anywhere in the database makes the game **unable to start or load anything**.
🔑 This is why the symptom looked like "the save won't load": it is not about
the save, the mod list, or load order. Every entry point into `Game..ctor()`
hits it — which is also why an attempted quicktest produced RimWorld's
"Error while generating a map" dialog from the same root cause.

**Action taken**: `mandrake.rm.manywaters` was REMOVED from the live
`ModsConfig.xml` (582 → 581) and the campaign relaunched without it. The mod
folder is still deployed under `RimWorld/Mods/ManyWaters` — inert while
inactive. Snapshots: `infrastructure/state/modlists/ModsConfig_582_before_manywaters_drop_2026-09-09.xml`
(with it) and `ModsConfig_RESTORE_581_no_manywaters_2026-09-09.xml` (without).
Evidence log kept at
`D:\Luke\dev\Rimworld\Transient\Player_log_manywaters_thingclass_NRE_2026-09-09.log`.

### The repair this item now owes, BEFORE step 0 is retried

1. Establish why `ParentName="DBH_WaterBottle"` yields a null `thingClass` —
   read Dubs Bad Hygiene Lite's own `1.6/Defs/ThingDefs_Items/Items_Resource_Stuff.xml`
   and confirm the parent's real defName, whether it is abstract, and whether
   `thingClass` is declared anywhere on its inheritance chain. 🔴 Do not guess
   the parent's name or assume the chain — a dangling `ParentName` and a parent
   that simply never sets `thingClass` produce the same null and need different
   fixes.
2. Whichever it is, give the five defs an explicit `<thingClass>` rather than
   relying on inheritance for it. The correct value comes from the parent's
   chain (vanilla `ThingWithComps` for an ingestible resource, but **read it,
   do not assume**).
3. ⛔ **A def-level null `thingClass` is not a cosmetic config error.** Treat
   `Config error in <X>: has null thingClass` in any future load as a
   game-breaking finding, not a warning to note and move past.
4. Re-verify offline before ever re-enabling the mod: after the fix, a load
   must show **zero** `has null thingClass` lines, and the proof that the mod
   is safe is a game that actually constructs — a clean main menu proves
   nothing here.

This item stays in `doing`.
