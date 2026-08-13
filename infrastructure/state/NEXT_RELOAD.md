# NEXT_RELOAD.md — the queue for the NEXT game load

_A cold load costs **~23–30 minutes**. It is the scarcest resource in this project.
This file exists so that a load is never spent on one question._

**PROJECT assembles this file from `infrastructure/state/queue/<SEAT>.md` before a load.** It holds only
what the *next* load must carry. **Harvest it and clear it afterwards** — a closed
item becomes ONE line in `CLOSED.md` and its body is deleted (`DOC_BUDGET.md` §3).

**How to spend the load** — batching, decision strings, the shutdown window, the
harvest — is `skills/rimworld-load-round/SKILL.md`. This file is only the queue.

**The v1 gate is `V1_SCOPE.md`: every v1 item must be SEEN working in-game once.**
Rows marked ⭐ below are gate items. Everything else rides along.

---

## 🔻 BEFORE THE GAME GOES DOWN — the shutdown window

**Announce it to BRIDGE before the game closes** (skill §6). Companion-DLL work and
mod-list work both need the game **down** and are unrecoverable once it relaunches.

**Companion:** nothing owed. BRIDGE's B0 deployed 2026-08-13 10:05, byte-verified,
17 tools (`infrastructure/state/queue/BRIDGE.md`).

**Mod list — OPS's alone (rule 7), all three ride one window:**

| # | change | why |
|---|---|---|
| 1 | **Enable `matathias.ruthlessmechanoids`** — downloaded, 1.6, deps present, **not in `ModsConfig`** | the whole pursuit design is inert until it is enabled |
| 2 | **Turn mechanoids OFF**, against which they are currently on | owner's ruling; needs #1 first |
| 3 | **Disable `com.yayo.yayoAni.continued`** `[v2]` | the lightsaber flies up and behind **on draft**; Yayo's is the suspect (the Force lightsaber mod ships a `Mods/MeleeAnim` compat folder and nothing for Yayo's). The pawn-render items it was held back for are all closed, so it no longer creates ambiguity |

Then `python.exe src/RimMandrake/Utils/refresh.py` — **Windows** interpreter; WSL's `python3` fails
on the Windows paths with a bare `cannot read ModsConfig`.

---

## 🔴 FIRST CALLS OF THE LIVE SESSION — two seats are blocked on these

```
1. jawa/get_def GravFieldExtender        <- BRIDGE owes this; nothing builds until it lands
2. jawa/get_def VFEFactory_AutomatedCannery
3. read mapSize {x,z} off any companion reply
```

**1 — the gravship radius.** `30` = the owner's Bigger Gravships settings reached
the live defs and CREATE's plan is verified. `25.9` = they did not, and the
extender at **(56,8) — 84.72 out against an 85 cap, 0.28 of a cell of margin** — is
the first thing that breaks. Bigger Gravships bakes radii into defs at **startup**
via a Harmony prefix on `DefGenerator.GenerateImpliedDefs`, so only a live def
answers it. `get_def GravEngine` exposes no radius — only `SubstructureSupport
632.7954`, which matches neither π·34² nor π·25.9². **Until this call, "the radii
applied" is inference.** A ship built on the wrong answer does not lift and
**nothing logs why**.

**2 — a conditional def.** `VFEFactory_AutomatedCannery` is not in VFE-Factory's
own `Defs/`; it lives under `1.6/Mods/VanillaCookingExpanded`, gated by
`loadFolders.xml` `IfModActive="VanillaExpanded.VCookE"`. The offline dump cannot
see a conditional folder's outcome. If absent, one `spawn_batch` op fails and the
wing is short a machine — survivable, and much cheaper to know before the build.
(`VFEFactory_AutomatedFishfarm` is gated on Odyssey, which is in the stack.)

**3 — the map size**, because the plan on disk may be aimed at the wrong map. See
the gravship section.

---

## ⭐ v1 ROW 8 — THE GRAVSHIP BUILD (DEEP)

`file:///D:/Luke/dev/Rimworld/design/Jawa/worldbuilding/ship_build/ship_bridge.json`,
regenerated 2026-08-13 09:44. Verified against the file itself, not from a note:

| | |
|---|---|
| origin | **+81,+57** — "centred on a 250×250 map" |
| hull | 86×133, occupying x 82–167, z 58–190 |
| foundation | **1 call**, `layer=foundation`, Substructure, **4,057 cells in 132 rects** |
| terrain | 4 calls — MetalTile 3,328 · SterileTile 507 · WoodPlankFloor 197 · CarpetMarine 25 |
| spawn | 26 calls, ~1,053 things |
| `buildOrder` | `foundation → terrain → spawn` — stamped into the JSON, load-bearing |

Rehearsed end to end on a disposable quicktest map: **1,045 of 1,045 things, 4,057
of 4,057 foundation cells, 5.6 s wall clock.**

### 🔴 THE MAP SIZE IS STILL UNRESOLVED — and the file contradicts itself

The plan was generated for **250×250**. One note says WORLD measured the real
colony map at 250×250; another says **250×250 is the DEBUG map, not the colony**,
and that BRIDGE read that size off a scratch map. **Both cannot be right, and
building on the wrong one puts the ship on the wrong map entirely.**

⇒ **Settle it from a live `mapSize {x,z}` before firing anything.** If it is not
250×250, regenerate: `python3 src/RimMandrake/Utils/rimbench/shipbuild.py --center W,H`.

⚠️ **Do not discover the placement by watching 4,057 tiles land.** Paint one small
rect first and read back where it went.

### 🔴 The build sequence is FIVE steps, not the JSON's three

```
destroy_batch {"categories": "All"}    <- PLURAL. the singular key was silently dropped
  -> strip floors back to a natural terrain (Sand)
  -> foundation      (the JSON's buildOrder starts here)
  -> floors
  -> spawn
```

- **`destroy_batch` removes THINGS, never terrain.** Clearing the site is not
  enough — pre-existing floor terrain refused **103** foundation cells on the
  rehearsal map; with the terrain reset it was **0**. ⚠️ Do not read the 103 as a
  layout signal; it describes that random map's ruins, not ours.
- 🔴 **Foundation before floors is MANDATORY.** RimWorld refuses `SetFoundation`
  where a floor exists and refuses **silently at the write** — measured 25/25 on
  bare ground, **0/25** with `MetalTile` laid first. **A floor is a one-way door:**
  substructure cannot be retrofitted, so a wrong order means demolish and rebuild.
  Full entry: `skills/rimbridge/references/traps.md`.
- The entire hull's substructure goes down in **ONE** call, so there is no ordering
  hazard *inside* the foundation phase.

⚠️ **The old plan would have run clean and produced a thing that is not a
gravship.** `GravshipHull` spawns fine on bare ground — `GenSpawn` does not check
`terrainAffordanceNeeded` — so a silent success, not a failure, is the shape to
watch for here.

### Placement facts that are easy to get wrong

- ✅ **A multi-cell thing's coordinate is its CENTRE** — `GravEngine:172,172`
  occupies 171–173 × 171–173, confirmed live.
- **FOUR machines emit at `rot=0` flagged `needsManualRotation` and must be turned
  by hand:** `Autofarmer`, `Autoloom`, `ConveyorOven`, `Cannery`. A footprint
  cannot tell east from west.
- Interior detail (beds, doors, lamps) is deliberately not placed.
- **Mangled metal salvage stands in for the wrecked machines** — the owner's v1
  call. Map authoring, no custom defs, no new research. WreckedMachines is v2 and
  stays undeployed.
- Build order and zone map:
  `file:///D:/Luke/dev/Rimworld/design/Jawa/worldbuilding/ship_build/ship_build.md` §"Build order".

### ⚠️ The design is settings-dependent, with 0.28 of a cell of margin

The hull needs a reach of **74.46**; Bigger Gravships' defaults give **51.80** and
**no layout can rescue it** (966 tiles beyond any possible extender). It flies only
on the owner's four values in
`file:///C:/Users/Mandrake/AppData/LocalLow/Ludeon%20Studios/RimWorld%20by%20Ludeon%20Studios/Config/Mod_3522759531_GravshipSizeSettings.xml`
(`gravEngineMaxDistance` 34 · `gravExtenderMaxDistance` 30 · `gravExtenderMax` 12 ·
`gravExtenderMaxDistanceFromEngine` 85). **If that file is lost or "Restore Mod
Defaults" is clicked, the hull silently stops being liftable.** Nothing logs it.

⚠️ **Read the FILE, never the settings panel** — the panel renders 25.9 as "26",
and only non-default values are written, so an absent key means *default*, not zero.

`D_MAX = 85` is now a real constraint in `src/RimMandrake/mapsynth/ship_designs.py`.

### ⭐ Do this BEFORE the 4,057-tile build — 5 minutes, one contradiction

`V1_SCOPE.md` calls it the only residual live question on the flagship: Gravship
Exporter's README says floors cannot be saved (*"you can only place one TerrainDef
and that has to be the Substructure"*), while the author's own shipped example
holds **204 non-null `terrainDef` cells** (128 MetalTile, 38 SterileTile, 22
WoodPlankFloor, 16 CarpetMarine). Both cannot be true.

**Test:** build a tiny ship — engine, a few hull tiles, **one extender**, a patch
of each of two floors. Export, re-import, look.

**It decides two things at once:** whether floors survive, and whether `*Extender*`
survives. The extender half is currently inference — the string `Extender` appears
nowhere in the assembly in either encoding.

⚠️ If floors do NOT survive, **the big build is still worth doing** — it just
cannot be delivered as an exported ship, and terrain must be repainted on import.
Say which, because it changes the delivery artifact, not the build.

---

## ✅ v1 ROW 2 — Faction Control's settings panel — **DONE, DO NOT SPEND A LOAD ON IT**

**Closed by OPS 2026-08-13 offline. The click already happened in the 09:31–10:04
session; both confirm conditions below are MET.** Measured after the game came
down, on
`C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Config\Mod_2882785581_Controller.xml`:

- **mtime 09:31 today**, not 2025-12-09 — the file was re-enumerated.
- `grep -c "<faction>"` → **41**; `grep -c "<li>"` → **41**; the file has no other
  `<li>` field, so 41 is the entry count, not an artefact of the tag.
- `grep -c "<faction>OuterRim"` → **4** (`GalacticEmpire`, `BinaryStarRaiders`,
  `MoistureFarmers`, `RebelAlliance`). The non-zero condition is satisfied.

⚠️ **But the click bought less than this section promised, on two counts.**
1. **41 is not "well above 32" in the way that mattered** — the 11 settlement-less
   modded factions (`JDSCIS_CIS_Faction`, `guy762_KotORFaction_RogueDroids`,
   `AA_BlackHive`, `HoraxCult`, …) are STILL absent. Faction Control enumerates
   what it can place, not what exists.
2. 🔴 **The file cannot suppress a faction at all.** `FactionDensity` serialises
   exactly `faction` / `density` / `enabled`, and `density` is a **clumping
   radius** (`__result = dist < fd.Density;` in the
   `TileFinder_IsValidTileForNewSettlement` postfix), not a count. The English
   key "setting to 0 disables the faction" is a pre-1.3 leftover string. Faction
   removal is a **worldgen-time** choice on vanilla's Configure Factions page.
   Full derivation in `infrastructure/state/queue/OPS.md` §5b.

**So: the click is done, and row 2 is NOT closed by it.** Row 2 now lands as a
worldgen-screen checklist, not a settings write.

**Historical instruction, kept for the record — do not execute:** Options → Mod
settings → **Faction Control** → let it draw its faction list → close with
**Accept/OK**.

`Config/Mod_2882785581_Controller.xml` holds the per-faction settlement densities
and is the file v1 row 2 must write into — Faction Control ships **zero defs** and
keeps its whole capability in settings, so nothing in our pipeline can generate it.

~~**The block is an INCOMPLETE LIST, not a stale timestamp, and that is why the fix
works.** The file holds **32** factions, dated 2025-12-09~~ — **both numbers are
now stale: it is 41, dated 09:31 today.** OPS measured **55** in
the world. Every Star Wars faction is missing, because mods enabled in August
cannot appear in a file written in December. Opening the settings UI is what makes
the mod re-enumerate against the current mod set.

⚠️ **A clean exit does NOT write it** — measured: the 2026-08-12 session loaded,
ran and exited cleanly and the mtime never moved. `ModSettings.Write()` is called
by each mod's own code; 7 of 42 `Config/Mod_*.xml` wrote at startup with no UI
visit, 9 are still frozen pre-2026. Faction Control is not one that writes on init.

**Confirm after:** entry count well above 32, and
`grep -c '<faction>OuterRim' ".../Config/Mod_2882785581_Controller.xml"` non-zero.

⚡ **Only after the click succeeds**, BRIDGE may test `rimworld/update_mod_settings`
/ `rimworld/reload_mod_settings` against a mod where a wrong result costs nothing —
this file goes stale again every time the faction set changes.

---

## 👁️ Live checks riding along — cheap, and each one is a look, not a grep

| # | check | passes when | owner |
|---|---|---|---|
| 1 | 🔴 **Ion vs a KotOR droid** — see below | severity climbs, `downed: true`, pawn still exists | OPS |
| 2 | **Megafauna butchering yields** | `DA_Taraal`, `DA_SnowTaraal`, `DA_DwarvenMuffton`, `DA_Goldilox` butcher their intended yields **on screen** | OPS |
| 3 | **Galactic Empire trooper ladder spawns** | the ladder appears; mod is enabled and its faction is live | OPS |
| 4 | **LK Mineable Resources** | the four ores scatter, and durasteel sits at **0.5** — reference: `file:///D:/Luke/dev/Rimworld/design/Jawa/worldbuilding/desert_world_design.md` §3B(6) | OPS |
| 5 | **Wookiee head swap** | `BTD_Wookiee` visibly crisper, most obviously in the **east profile**. Then decide the FA question per race: FA deletes the vanilla head draw call, so `forcedHeadTypes` can never render on a pawn FA draws — exclude the race, or author blank heads | CREATE |
| 6 | **Colonists can no longer TEND droid injuries** | tending refused. Tending still working means the `isOrganic` flip did not take behaviourally | OPS |

### 🔴 #1 in full — the droid ruling's load-bearing family, never tested

Filed after the owner's droid ruling
(`file:///D:/Luke/dev/Rimworld/design/Jawa/droid_ruling.md`): KotOR droids are
**THE capture-and-upgrade line**, and the owner's words were *"they should NOT blow
up when ion blasted."*

⚠️ **W8 proved the guard on two families and neither was KotOR** —
`OuterRim_BattleDroid` (`Asimov_Automaton`) and `JDSCIS_B1_Battle_Droid`
(`Mechanoid`). `ABF_FleshType_Synstruct_Base` is a **third** flesh def, never
tested, and it ships `CorpsesMechanoid` as its corpse category. **If a downed KotOR
chassis resolves as a corpse rather than a capturable pawn, the whole loop is dead
while every static check still looks green.** [INFERRED — which is why it needs
measuring.]

```
jawa/spawn_pawn  kindDef=KotORDroidBad_KM1MD  faction=hostile   (45 kinds available)
jawa/damage      ion, repeatedly
jawa/list_pawns  includeHealth=true
```

| read | PASS | FAIL |
|---|---|---|
| ion hediff **severity** | climbs toward 1.0 | stays 0.0 → the guard wrongly blocks it |
| `downed` | **true** | false while severity is 1.0 |
| the pawn still exists | present in `list_pawns` | gone / became a corpse → 🔴 **loop is dead** |
| Consciousness | ~0.10, like the Outer Rim control | — |

⚠️ **Read `severity`, not presence** — the hediff exists as a 0.0-severity shell on
a blocked pawn, which is how W8 nearly produced a false alarm.
⚠️ **`amount` is a request, not a delivery** — W8 needed **14** applications to
reach severity 1.0, so a single call reads as a weak negative.

**If it fails it is a top-priority defect, not a balance question** — ion is
explicitly the way *around* detonation.

---

## 🎨 CREATE'S ROWS — assembled 2026-08-13, all of it verified today

_Everything below is CREATE's. Three parts: a shutdown-window mod-list change, the
two ⭐ v1 gate rows that are the point of the load, and two facts that are otherwise
discovered the expensive way._

### 🔻 (a) SHUTDOWN WINDOW — seven fix mods exist in the repo and load NOTHING

They are built, deployed-ready and **absent from `ModsConfig.xml`**, so today they
are inert files. **This is a shutdown-window change** — RimWorld rewrites
`ModsConfig.xml` on exit, so an edit made while the game is running is silently
undone. It rides the same window as the three OPS rows above, and the same
`python.exe src/RimMandrake/Utils/refresh.py` afterwards.

**packageIds read from each mod's own `About/About.xml`, not from a note:**

| packageId | source folder under `src/RimMandrake/` | ordering constraint |
|---|---|---|
| `mandrake.gravshipastronautfix` | `GravshipAstronautFix` | **after `vanillaexpanded.gravship`** (line 380) — donor ships art **loose**, so order is load-bearing |
| `mandrake.sauridfrillfix` | `SauridFrillFix` | **after `vanillaracesexpanded.saurid`** (line 394) — loose donor, load-bearing |
| `mandrake.toolbeltfix` | `ToolBeltFix` | **after `vanillaexpanded.vaeaccessories`** (line 362) — loose donor, load-bearing |
| `mandrake.researchkiteastfix` | `ResearchKitEastFix` | **after BOTH `petetimessix.researchreinvented` (275) and `aw.researchreinvented.retextured` (458)** — two mods, one def owner and one texture shipper; RRR loads later and is what actually renders |
| `mandrake.blastdoorframeasyncfix` | `BlastDoorFrameAsyncFix` | **after `lumi.doorsexpanded`** (line 433) — loose donor, load-bearing. ⚠️ NOT base Doors Expanded |
| `mandrake.cereanmanefix` | `CereanManeFix` | **none** — donor serves art from an AssetBundle on 1.6 and a loose PNG beats a bundled asset regardless of order. Declares no `loadAfter` on purpose |
| `mandrake.msedroidfix` | `MSEDroidFix` | **none**, same reason, and academic twice over: the bundle has no `MSE_north` to beat |

🔑 **One placement clears all seven: put them together next to
`mandrake.missingartfixes` (line 560).** Every donor above sits at line 551 or
earlier, so that slot satisfies every `loadAfter` at once. Verified by grepping
`ModsConfig.xml` today; do not re-derive it per mod.

⚠️ **None of these seven can ever produce a log line, before or after.** `Failed to
find any textures at` fires only when **every** direction of a `Graphic_Multi` is
missing, so a single absent or zero-alpha facing is a silent south-fallback.
**They are settled by eyeballing a pawn, never by `harvest_log.py`.**

### ⭐ (b) v1 ROW 3 — quest `Jawa_TheClaim` ("The Claim")

**Gate: seen working in-game once** (`V1_SCOPE.md`). Built and committed
(`47733f8`); never seen.

🔴 **Do NOT wait for the storyteller.** The quest is root-selected, so waiting is
the most expensive possible way to clear this. The rumour item exists precisely to
fire it on demand:

```
Dev mode ON  ->  Debug actions (the ▤ / "..." toolbar button)
  ->  category "Spawning"  ->  Spawn thing
  ->  type  Jawa_ClaimRumour  in the search box, click it
  ->  left-click a map cell to drop it
  ->  select a COLONIST, then right-click the item on the ground
  ->  float menu reads "Read the rumour"  <- this is the click
```

The colonist walks over, the item is consumed, and **the quest is offered**.

| passes when | |
|---|---|
| the quest appears in the **Quests tab**, named **The Claim** | offer text is VISION's, verbatim |
| the **Accept** button is live (not greyed with *"cannot accept in space"*) | `everAcceptableInSpace` is set true; this is what it buys |
| it reaches an end state — **completed OR expired, either counts** | it does not have to be balanced and the site does not have to be interesting |

⚠️ **Expiry is 10–18 days**, so an end state will not be seen inside one session
unless the site is visited. **Offered + acceptable is the honest read of "seen
working"; say which one was actually observed.**

### ⭐ (c) v1 ROW 4 — three terrain/resource overrides

Built and committed (`73ca76c`); never seen. Salt pans (`Jawa_SaltCrust` into
Desert / ExtremeDesert / AridShrubland), wider dune seas (SoftSand thresholds
lowered), scrapfields (`ChunkSlagSteel` scatter on the player map).

🔴 **ALL THREE ARE MAP-GENERATION-TIME AND NEED A NEWLY GENERATED MAP.** A
`terrainPatchMaker` runs during map gen and a `GenStepDef` runs during map gen —
**nothing whatsoever appears on an existing map, however long you look.** Checking
row 4 on the current colony map is a guaranteed false negative.

⇒ **Generate a fresh map** (the world-gen session, a new colony, or a dev quicktest
map on a Desert / ExtremeDesert / AridShrubland tile) and look for: broad pale
cracked pans in the low ground, obviously wider soft-sand dune fields, and steel
slag chunks strewn in the open with machine-bit filth around them.

🎁 **FREE SHORTCUT — the art half of the salt crust costs no load at all.**
`Jawa_SaltCrust` is an ordinary `TerrainDef`, so the live bridge can paint it onto
the map that is already up:

```
jawa/set_terrain   def=Jawa_SaltCrust   a rect of ~10x10   layer=top
jawa/get_terrain_batch  the same rect FIRST, so it replays back as a restore
```

That answers "does the texture resolve, and does the colour read as evaporite
white rather than as sand" — which is the half most likely to be wrong — **without
spending a map generation.** It does **not** answer whether the patch makers
attach; only a generated map does that. ⚠️ It also requires the deploy below.

### 🔴 (d) TWO THINGS THAT ARE OTHERWISE DISCOVERED THE EXPENSIVE WAY

**1 — A DEPLOY IS OWED BEFORE ROW 3 OR ROW 4 CAN BE SEEN AT ALL.** The deployed
copy at `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\Jawa_Patches`
is well behind the dev tree. Measured today, on the game copy itself:

- `Defs/` was last written **Aug 11 08:57** and holds only `GeneDefs`,
  `PawnKindDefs`, `WeatherDefs`, `XenotypeDefs`. **There is no `TerrainDefs/`, no
  `QuestScriptDefs/`, no `ThingDefs_Items/` and no `MapGeneration/` at all.**
- `Patches/` is newer (its most recent file is **Aug 13 01:10**) but holds neither
  `JawaTerrain_SaltPans.xml`, `JawaTerrain_DuneSeas.xml` nor
  `JawaResource_Scrapfields.xml`.

⇒ **Six new files must reach the game copy or rows 3 and 4 are not in the load.**
The quest def, the rumour item and its texture, the terrain def, both terrain
patches, the gen step and its registration. Plan-first deploy, procedure in
`skills/rimworld-deploy/SKILL.md`. ⚠️ **`--apply` overwrites the game copy with
whatever is in the repo right now, including another seat's half-finished work** —
read the plan before applying.

**2 — RETIRING `mandrake.missingartfixes` HAS AN ORDER, AND ONE DEPENDENCY.** Its
seven textures now live in the five per-donor fix mods (`61fe954`, `48e5e16`), so
it is redundant — but it is **LIVE and deployed**, so deleting it carelessly leaves
a missing-mod entry in `ModsConfig.xml`. **The dependency is that the blast-door
brief still lives inside its `Source/` and must be moved out before its folder is
deleted.**

⇒ **Do not re-derive the sequence. It is written up in
`D:\Luke\dev\Rimworld\infrastructure\state\queue\CREATE.md` under C11** — follow
it there.

---

## 📋 After the load — harvest the WHOLE log

```bash
python.exe src/RimMandrake/Utils/harvest_log.py                  # every standing check, with baselines
python.exe src/RimMandrake/Utils/harvest_log.py --show crossref  # read the actual lines
```

Exit code 1 means something is above baseline. The script carries the standing
checks, the per-item queued greps and an EXPECTED-PRESENT section for lines whose
*absence* is the finding. Procedure: `skills/rimworld-load-round/SKILL.md` §8.

⚠️ **Exit 0 means the LOG is clean. It does not mean the load passed.** Every item
in this file that says *look* is settled only on screen:

- **A patch that silently no-ops logs NOTHING.** `PatchOperationConditional` and
  `PatchOperationFindMod` both return `true` when they match nothing.
- **The art items have no log strings at all.** A present-but-empty PNG is a
  successful load by every measure the engine has, and `Failed to find any textures
  at` fires only when **every** direction is missing.

Afterwards: triage anything new into `vendor/wisdom/benign_log_errors.md`, append anything
that surprised you to the matching `skills/rimworld-modding/references/traps-*.md`,
and file the rest into the per-seat queues.
