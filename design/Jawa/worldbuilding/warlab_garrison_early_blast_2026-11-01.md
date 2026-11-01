# The early lake blast: Empire heat and the Imperial garrison

Item `WARLAB_GARRISON_DESIGN_EARLY_BLAST`. Every number here is PROVISIONAL. Build item:
`WARLAB_GARRISON_BUILD_TWELVE_MEN_ON_GLASS`.

Owner, 2026-10-10, story sitting card 8, typed: *"Blowing up the lake early (harder than you
think, but possible) will reveal the War Lab even if it cannot be opened yet. Then the Empire's
heat will significantly increase,and a small Imperial force will garrison outside the War Lab
that must be defeated to enter and use the codes."*

## Ruling

Status and judge record: see `## Judgment` at the end of this note.

1. **"The lake blew" means `WarLabCraterMutation.Ignite()` returned true**, whichever route lit
   it. That one call is the single hook. The waste run's propane branch and
   `CompIgniteCraterOnDestroy` both already land there, so both are covered without being
   touched.
2. **The heat is the Colony Visibility dial plus a permanent ladder floor.** No new meter.
3. **Early means no codes in hand when the lake blows.** An early blast posts the garrison. A
   blast with the codes in hand raises the same heat and posts no garrison, because the card
   ruled the garrison for the case where the lab cannot be opened yet.
4. **The garrison is fixed at 12 pawns and never refills.** It holds the lab until it is beaten or
   Route 6 ends it.
5. **The codes work only on the lab's own site map, only once the ground has opened, and only when
   no garrison stands there.**
6. **Every blast is a named Route 6 leak.** The Empire now knows the place exists, so the fuse is
   lit and cannot be put out, whoever holds the codes. An early blast adds the garrison as that
   route's first, unhurried step. Either way the player has until the ordnance arrives. See §6.

## 1. What exists, and what this design has to change

| piece | where | state |
|---|---|---|
| the blast | `WarLabCraterMutation.Ignite()`, once per save by `GameComponent_WarLabCrater` | built; swaps the Chill's tiles to `RM_ChillCrater`; fires nothing else |
| the heat meter | `GameComponent_ColonyVisibility`, reached softly through `EmpireSearch.AdjustVisibility` | built |
| the permanent price | `EmpireSearch.RaiseFloor` on `GameComponent_EmpireSearch.rungFloor`, read by `MapComponent_EmpireSearch` | built, no caller yet from the lake |
| blast-to-heat precedent | `FuelBlastInvestigation`, which binds a soft event by reflection and calls `EmpireLadderMath.BlastVisibility` | built |
| the codes | `RUT_RakatanCommandCodes`, redeemed by `CompRedeemRakatanCommandCodes`, which sets `AshfallCommandCodesFlag.HasBeenSeized` | built, with two defects below |
| the lab site | `RUT_WarLabSite`, `RUT_GenStep_WarLabSite` | built, with two defects below |
| an Imperial post | `RM_GenStep_DetentionPost`: spawns guards under `LordJob_DefendBase` | built, the pattern to copy |

Four findings shape the rest. Each would have broken the card as ruled.

- **The codes can be redeemed anywhere.** The gizmo is unrestricted (its own XML header flags the
  question), so a player could key them in at home and skip the garrison.
- **`HasBeenSeized` has no reader.** The door check is not built. It is owed by
  `ANCIENT_WAR_LAB_1`, and it must read that flag.
- **After the blast nobody can reach the lab.** `RUT_WarLabSite` sets `gravShipsCanLandOn` false
  because the route was the submerged one. `RM_ChillCrater` is not a water biome, so a cratered
  tile has no dive and no sea landing, and it is `impassable`, so no caravan. It has to be a place
  the ship can land.
- **A vanilla site deletes itself.** `Site.ShouldRemoveMapNow` (decompiled 1.6) removes the map and
  sets `alsoRemoveWorldObject` when no player pawn is left and no condition causer stands. So
  walking away from a plain `Site` would erase the lab and the garrison. Persistence must be
  authored.

## 2. The heat rise

On every successful `Ignite()`, early or not:

- **`EmpireSearch.AdjustVisibility(+80)`**, computed as
  `EmpireLadderMath.BlastVisibility(RFPSettings.fuelBlastVisibility, 200)`: the existing formula at
  its cap, on the existing dial (40 by default). The owner ruled a chemfuel detonation a *"massive
  imperial heat increase"*, and this is the planet's largest blast, so it must not rate below the
  top of that scale. Since the band boundary is 80, every clan lands on **Exposed** whatever it was
  before: interval ×0.5, and the top of the raid-points curve.
- **`EmpireSearch.RaiseFloor(2, "the lake blew")`**. An early blast is a named leak (§6), and a
  blast with the codes in hand is the same event to everyone watching. This is the same number the
  ladder design set for a named leak (`empire_escalation_ladder_design_2026-10-02.md` §4). Probes never open a
  ladder again, on any tile, for the rest of the game. Route 6's maximal floor of 3 still sits
  above it, and `RaiseFloor` only moves upward.
- **The Empire goes hostile if it was not.** A garrison that does not fight cannot be beaten.

Launching drops the dial as usual (`launchResetMultiplier`), so the +80 is the part the player can
run from. The floor is the part they cannot: *"prevent, never undo"*. That matches *"until you
move"*.

**No investigating raid.** `FuelBlastInvestigation.Investigate` needs a home map, and the blast has
none. The garrison is the Empire's answer.

**Why not only on an early blast.** The card ties heat to the early case, and it did not rule on
the other order. A blast in which *"everyone on the planet will notice"* (2026-09-12) cannot leave
the Empire calm because the player happened to be carrying a data core, so the heat applies to
both. This is an agent's reading, not his words.

**The wiring.** `WarLabCraterMutation` gains `public static event Action<bool> Ignited`, whose
argument is `early`, raised after `Triggered` is set. `EmpirePursuit` binds it by reflection,
exactly as `FuelBlastInvestigation` binds FlowWorks, so neither mod gains a dependency. With
Visibility absent, only the floor moves.

## 3. Early

`early` is computed at the top of `Ignite()`, before the tiles change:

    early = !HasBeenSeized && no RUT_RakatanCommandCodes is in the player's hands

In the player's hands means on a colonist or in a caravan (recursively, through
`ThingOwnerUtility`), or lying on a player home map. Codes still on the Spire's floor do not count,
even if that map is loaded. That is what "held" means here: taken, not merely found.

Routes 2 to 5 do not end the lake and never call `Ignite()`, so they post no garrison. The Empire
never saw them. The difficulty the card names (*"harder than you think"*) stays with each route's
own trigger, as the Chill's ban on ignition without a hot source already requires.

## 4. The garrison

**Where.** On every successful `Ignite()` a **new site appears at the island crag, tile 5873**, the
lab's access (`the_propane_lakes.md` §8). This is card 9's *"map change"*. It is a fixed tile from
one authored constant, placed once by one in-game event: the same shape as the reinfection nodes,
and not worldgen. A pre-blast `RUT_WarLabSite` there, if the held bridge placement has run, is
replaced by the revealed one.

The site part is a new `SitePartDef`, `RUT_WarLabRevealedSite`, linked to the same layout as
`RUT_WarLabSite` but with `gravShipsCanLandOn` true and `disallowsAutomaticDetectionTimerStart`
true. It is carried by a `Site` subclass, `RUT_Site_WarLab`, whose `ShouldRemoveMapNow` always
answers `alsoRemoveWorldObject = false`. The world object is permanent, while the map may unload.
The camp is a small authored layout, `RUT_WarLabGarrisonCamp`, outside the lab's outer gate: vanilla
`Sandbags` and `Barricade`, and two `Turret_Autocannon` covering the approach. No new art. The
guards stand *outside* the shielding, as the card says. They never enter it.

**Who.** A fixed roster, not a points roll, so that "small" stays small:

| kind | count | power each |
|---|---|---|
| `RUT_Jawa_Empire_Grunt` | 8 | 101 |
| `RUT_Jawa_Empire_Heavy` | 3 | 129 |
| `RUT_Jawa_Empire_Specialist` (the officer) | 1 | 119 |

That is 12 pawns and 1,314 points, scaled only by a Mod Settings size dial. It is a real fight for
a clan that can already reach the night side, and well below a ladder strike at Exposed. No leader
kind: `RUT_Jawa_Empire_Leader` is Palpatine.

**The cold.** The tiles run near −80 °C and the guards would freeze in hours, so waiting would beat
them. Each guard gets one new hediff, `RUT_GarrisonColdSealed`, which offsets
`ComfyTemperatureMin` far enough to hold. It is not added to the Empire's kinds, it applies only to
these 12, and it is removed from nobody: it is their kit. `RM_ChillHeatedSuit` is not the tool,
because it is charge-gated and needs a `RM_HeatedSuitCharger`.

**Behaviour.** One lord, `LordJob_DefendBase` on the camp, as `RM_GenStep_DetentionPost` does. They
stay in the camp until the player comes.

**Persistence.** `GameComponent_WarLabGarrison` is scribed and holds `state` and the survivors by
kind:

| state | meaning | codes |
|---|---|---|
| `None` | no early blast | usable at the lab once the ground is open |
| `Posted` | a garrison stands | refused |
| `Beaten` | latched; never returns | usable at the lab |
| `Moot` | the lab is struck or its door broken, or the Empire is defeated (§6) | usable at the lab, if there is a door left |

- The garrison has no timer of its own and never leaves. It takes no reinforcements, and no ladder
  contact adds to it. Only the player or Route 6's ordnance (§6) removes it.
- A guard counts as out when dead, downed, held prisoner by the player, or off the map. When none
  stands, the state latches to `Beaten`, and a downed guard who rises later changes nothing.
- If the player leaves and the map unloads, the survivors are written back by kind and the next
  map generates those, not a full roster. Wounds heal; losses stay. A fight can be walked away from
  and resumed.
- A map already loaded at the blast (a crew on site when it blew) gets the camp spawned onto it
  directly instead of through the GenStep.

**What the player sees.** Card 9's beats belong to the cut-scene. After it, two letters:

- Posted, on the site: *"Imperial garrison at the crater. The Empire has found the hole in the
  world and put men on it. They cannot open what is down there and neither can you, but they will
  not let you try."*
- Beaten: *"The crater is clear. Nothing stands between the clan and the door but the door."*

## 5. The codes

One choke point, the gizmo in `CompRedeemRakatanCommandCodes`, with one pure question:

    CodesUsable(mapIsWarLab, groundOpen, state) = mapIsWarLab && groundOpen && state != Posted

`groundOpen` is the first key: a new scribed latch on `GameComponent_WarLabGarrison`, separate from
`GameComponent_WarLabCrater.Triggered`, which stays the once-per-save blast latch. A successful
`Ignite()` sets it. Routes 2 to 5 set it too when they are built, since each ends at the same door
without a blast, and they leave `Triggered` alone so a later blast still has its consequences.

On any other map the gizmo is disabled, with the reason *"This is a key. It wants its lock."* On
the lab's map with the ground shut: *"The ground has not opened."* With a garrison standing: *"Not
with the Empire's rifles on your back."* It consumes nothing while refused, so it can never
softlock, and the codes stay the one item they are today.

`mapIsWarLab` is true on a site carrying either `RUT_WarLabSite` or `RUT_WarLabRevealedSite`. This
settles the question the item XML left open, in every route and not only the early one: the lock
is at the lab.

Entry and the codes are one gate: the shielding is intact, so nothing enters until the door does.
The gate order `ASSAILANT_WARLAB_BUILD_MERGE` owes is therefore **reveal → garrison if early →
codes → core socket**.

## 6. Where it meets other rulings

- **Route 6.** Its trigger is *"The Empire learns the place exists."* That is the whole fuse, and
  a garrison outside the lab means the Empire has learned it. So every blast **is** a leak: the
  named event *The Hole in the World*, which can be prevented by not blowing the lake and can never
  be undone. Route 6's two named paths are the plot's fuses (*"plot points, not just player
  behavior"*), so a fuse the player lights is allowed. The card's garrison and Route 6's bombing
  are then one sequence, and *"procedural, unhurried"* is the room between them:

  1. Any blast starts the **Route 6 clock**: 180 days by default, one scribed tick on
     `GameComponent_WarLabGarrison`, with a letter 15 days out, *"Imperial ordnance is on its way to
     the crater."* An early blast also posts the garrison. A blast with the codes in hand does not.
  2. **The player keys the codes first**, having beaten the garrison if one stands. The lab is open
     and the clock is stopped: there is no sealed door left for the Empire to bomb. The floor
     stays. The card is honoured in full.
  3. **The clock runs out.** Route 6 fires as ruled: the door breaks, the Empire is overrun, the
     lab stands open with no codes needed, and the floor goes to 3. A garrison still standing dies
     there and the state goes `Moot`. This is the one bypass the two-key rule allows, and the
     ending *"the world supplies when the player declines"*.

  Beating the garrison does **not** stop the clock, because a leak is never undone. Only using the
  codes does, and a clan that holds them when the lake blows is on the same clock. Paths A and B can still fire earlier, with the same result. Route 6's own
  consequences are not built: this design only starts the clock and calls Route 6's entry, and the
  build item owes that entry as a stub until Route 6 has an item of its own.
- **Strike or dive.** A Cradle strike on the lab while a garrison stands kills it too (`Moot`).
- **Sekkulaath.** This rises in the same event, and its reach is its own region. Nothing here
  touches it.
- **Specimen Casket** (`dungeons_arc_spec.md` §2.10). Its heat goes through
  `EmpireSearch.AdjustVisibility`, which is this same meter.
- **The Empire defeated.** If `Faction.OfEmpire` is defeated at the blast, no garrison is posted
  and the state goes straight to `Moot`.
- **A biome of ours on 0 tiles** is the expected state, and `RM_ChillCrater` stays that until the
  blast. No paint is owed by this design.

## 7. Mod Settings

On `StructureInjectionsRUT`: **War lab garrison** on/off (default on), **Garrison size** ×0.5 to
×2 (default 1), scaling each kind and keeping at least one officer, and **Days until the Empire
bombs the lab** 60 to 720 (default 180). Off means no garrison and no clock, and the gate reads
`None` with `groundOpen` still honest, so all-off degrades to the two-key lab.

On `EmpirePursuit`: **Lake blast raises heat** on/off (default on) and **Lake blast rung floor**
0 to 3 (default 2). The Visibility rise reads the existing fuel-blast dial.

## 8. Build plan

Filed as `WARLAB_GARRISON_BUILD_TWELVE_MEN_ON_GLASS`. It ships with its slice of the mod's
`validation.py`, under the 2026-10-01 debugging process.

1. A pure kernel, `WarLabGarrisonKernel`: `Early`, `CodesUsable`, the state transitions,
   `groundOpen`, the Route 6 clock, the survivor write-back. Selftests cover each table row above.
2. The `Ignited` event, the `EmpirePursuit` binding, and the settings.
3. `RUT_WarLabRevealedSite`, `RUT_Site_WarLab`, the camp layout, `RUT_GarrisonColdSealed`, and
   `GameComponent_WarLabGarrison`.
4. The gizmo gate.
5. Live proof on a test map, by state reads: `Ignite()` once → Visibility, floor, site on tile,
   state `Posted`. Refused gizmo on and off site. Leave with a part-killed garrison and return:
   survivors, not 12. Last guard down → `Beaten` → gizmo works and stops the clock. A second run
   with the clock jumped past 180 days → `Moot`, floor 3. A second `Ignite()` does nothing.

**To check at build, not settled here:**

- Tile 5873's biome after the swap and what map it generates, since the crag may or may not sit in
  the swapped set. The site must land either way.
- Whether `LordJob_DefendBase`'s `delayBeforeAssault` needs raising above the post's 25,000 for a
  guard that holds.
- Whether the −80 °C offset on `ComfyTemperatureMin` holds on the tile's real temperature.
- Whether pursuit's `PostMapGenerate` timers, which run on any generated map, should be stopped on
  this site. The ladder should not reinforce it.

## Judgment

Status: DESIGN NOTE WRITTEN, §4 JUDGE PENDING.
