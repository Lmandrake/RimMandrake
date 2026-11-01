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
4. **The garrison is fixed at 12 pawns and never refills.** It holds the lab until it is beaten, or
   until the lab's fate ends it (§4).
5. **The codes work only on the lab's own site map, only once the ground has opened, only when no
   garrison stands there, and only while the door is still shut.**
6. **A blast does not light Route 6.** Route 6 keeps the two fuses he named. Whether a blast is a
   third is his question, `WARLAB_ROUTE6_ASK_DOES_LAKE_LIGHT_FUSE`. Until he answers, the garrison
   holds for as long as it takes, and nothing here depends on the answer.
7. **The lab has one fate.** Once the Cradle strikes it, it is lost: no later event reopens it. That
   is *"Strike OR dive, never both"* carried into the state. See §4 and §6.

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
- **`EmpireSearch.RaiseFloor(2, "the lake blew")`**. The ladder design sets this floor for events
  the Empire cannot un-see (`empire_escalation_ladder_design_2026-10-02.md` §4: a Route 6 leak, or the
  droid line being discovered). The blast is the same kind of event but is not a Route 6 leak (§6);
  only the number is shared. A blast with the codes in hand is the same event to everyone watching.
  Probes never open a ladder again, on any tile, for the rest of the game. Route 6's maximal floor of
  3 still sits above it, and `RaiseFloor` only moves upward.
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

    early = labFate == Sealed && no RUT_RakatanCommandCodes is in the player's hands

In the player's hands means on a colonist or in a caravan (recursively, through
`ThingOwnerUtility`), or lying on a player home map. Codes still on the Spire's floor do not count,
even if that map is loaded. That is what "held" means here: taken, not merely found.

Routes 2 to 5 do not end the lake and never call `Ignite()`, so they post no garrison. The Empire
never saw them. The difficulty the card names (*"harder than you think"*) stays with each route's
own trigger, as the Chill's ban on ignition without a hot source already requires.

## 4. The garrison

**Where.** On every successful `Ignite()`, unless the lab is already `Lost`, a **new site appears at the island crag, tile 5873**, the
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

**Persistence.** `GameComponent_WarLabGarrison` is scribed and holds the garrison `state`, the
survivors by kind, and the lab's fate. The two tables are separate facts: who stands outside the door,
and what became of the door.

| `state` | meaning | entered from | left by |
|---|---|---|---|
| `None` | no garrison was ever posted | the start | an early blast → `Posted` |
| `Posted` | a garrison stands | `None`, on an early blast with the setting on and the Empire undefeated | last guard out → `Beaten`; fate `Broken` or `Lost` → `Moot` |
| `Beaten` | the player beat it; never returns | `Posted` | nothing |
| `Moot` | other hands ended it | `Posted` | nothing |

| `labFate` | meaning | entered from | left by |
|---|---|---|---|
| `Sealed` | the door is shut | the start | any of the three below |
| `Open` | the codes were used; this is `HasBeenSeized`, not a second flag | `Sealed` | `Lost`, if a strike can still land |
| `Broken` | Route 6 broke the door (aftermath 6) | `Sealed` | `Lost`, if a strike can still land |
| `Lost` | the Cradle struck it | any other fate | nothing |

- The garrison has no timer of its own and never leaves. It takes no reinforcements, and no ladder
  contact adds to it. It ends only by the player's hand or when the lab's fate changes under it.
- A guard counts as out when dead, downed, held prisoner by the player, or off the map. When none
  stands, the state latches to `Beaten`, and a downed guard who rises later changes nothing.
- If the player leaves and the map unloads, the survivors are written back by kind and the next
  map generates those, not a full roster. Wounds heal; losses stay. A fight can be walked away from
  and resumed.
- A map already loaded at the blast (a crew on site when it blew) gets the camp spawned onto it
  directly instead of through the GenStep.
- If the Empire is defeated after the garrison is posted, the state stays `Posted`. Its men are
  still on the glass, and they still have to be beaten. They just have no one left to answer to.

**What the player sees.** Card 9's beats belong to the cut-scene. After it, two letters:

- Posted, on the site: *"Imperial garrison at the crater. The Empire has found the hole in the
  world and put men on it. They cannot open what is down there and neither can you, but they will
  not let you try."*
- Beaten: *"The crater is clear. Nothing stands between the clan and the door but the door."*

## 5. The codes

One choke point, the gizmo in `CompRedeemRakatanCommandCodes`, with one pure question:

    CodesUsable(mapIsWarLab, groundOpen, state, labFate) =
        mapIsWarLab && groundOpen && state != Posted && labFate == Sealed

`groundOpen` is the first key: a new scribed latch on `GameComponent_WarLabGarrison`, separate from
`GameComponent_WarLabCrater.Triggered`, which stays the once-per-save blast latch. A successful
`Ignite()` sets it. Routes 2 to 5 set it too when they are built, since each ends at the same door
without a blast, and they leave `Triggered` alone so a later blast still has its consequences.

On any other map the gizmo is disabled, with the reason *"This is a key. It wants its lock."* On
the lab's map with the ground shut: *"The ground has not opened."* With a garrison standing: *"Not
with the Empire's rifles on your back."* With the door `Broken`: *"These were for a door that no
longer exists."* With the lab `Lost`: *"Nothing is left that would answer."* It consumes nothing while refused, so it can never
softlock, and the codes stay the one item they are today.

`mapIsWarLab` is true on a site carrying either `RUT_WarLabSite` or `RUT_WarLabRevealedSite`. This
settles the question the item XML left open, in every route and not only the early one: the lock
is at the lab.

Entry and the codes are one gate: the shielding is intact, so nothing enters until the door does.
The whole gate order is written once, in `dungeons_arc_spec.md` §2.3 (`ASSAILANT_WARLAB_BUILD_MERGE`).

## 6. Where it meets other rulings

- **Route 6.** A blast does not light it, and no clock runs from a blast. Route 6 is *"the route
  nobody buys, nobody places and nobody arms"*, with two named paths, and it sits off the price
  ladder. Route 1 keeps its door, and card 8 gives the Empire's answer to a blast as heat and a
  garrison, not ordnance. A fuse the player lights would also let a player blow the lake, skip the
  Spire and wait for a free door. Against that, the trigger reads *"The Empire learns the place
  exists"*, and a garrison outside the lab looks like the Empire knowing. The written text does not
  settle it, so it is his: `WARLAB_ROUTE6_ASK_DOES_LAKE_LIGHT_FUSE`. Until then the garrison guards a
  crater and a sealed door it cannot open and does not report what is behind it.

  Paths A and B stay exactly as ruled and can fire at any time. Their entry asks one pure question:

      Route6Live(labFate, empireDefeated) = labFate == Sealed && !empireDefeated

  False cancels the route: no door breaks and no floor 3 comes from it. True fires Route 6 as ruled:
  fate `Broken`, a standing garrison dies there (`Moot`), and the lab stands open with no codes
  needed. This is the one bypass the two-key rule allows. Route 6's own consequences are not built,
  so the build item owes this guard and a stub entry until Route 6 has an item of its own.
- **Strike or dive.** Dive means `Open`; strike means `Lost`. A Cradle strike on a sealed lab sets
  `Lost`, kills a standing garrison (`Moot`) and cancels Route 6 through `Route6Live`, so no door ever
  breaks afterwards and the codes never work. A later blast raises heat and places nothing. Whether
  a strike can still be called on a lab already `Open` or `Broken` is `dungeons_arc_spec.md` §2.9's
  open part. If one lands, the fate is `Lost`.
- **A blast on a lab no longer sealed.** Routes 2 to 5 can open the lab first, or Route 6 can break
  it. `early` is then false, so no garrison is posted and only the heat applies.
- **Sekkulaath.** This rises in the same event, and its reach is its own region. Nothing here
  touches it.
- **Specimen Casket** (`dungeons_arc_spec.md` §2.10). Its heat goes through
  `EmpireSearch.AdjustVisibility`, which is this same meter.
- **The Empire defeated.** If `Faction.OfEmpire` is defeated at the blast, no garrison is posted and
  the state stays `None`. A defeated Empire bombs nothing: `Route6Live` is false.
- **A biome of ours on 0 tiles** is the expected state, and `RM_ChillCrater` stays that until the
  blast. No paint is owed by this design.

## 7. Mod Settings

On `StructureInjectionsRUT`: **War lab garrison** on/off (default on), **Garrison size** ×0.5 to
×2 (default 1), scaling each kind and keeping at least one officer. Off means no garrison, and the
state reads `None` with `groundOpen` and `labFate` still honest, so all-off degrades to the two-key
lab.

On `EmpirePursuit`: **Lake blast raises heat** on/off (default on) and **Lake blast rung floor**
0 to 3 (default 2). The Visibility rise reads the existing fuel-blast dial.

## 8. Build plan

Filed as `WARLAB_GARRISON_BUILD_TWELVE_MEN_ON_GLASS`. It ships with its slice of the mod's
`validation.py`, under the 2026-10-01 debugging process.

1. A pure kernel, `WarLabGarrisonKernel`: `Early`, `CodesUsable`, the state transitions,
   `groundOpen`, `Route6Live`, the survivor write-back. Selftests cover each row of both §4 tables, and
   one row each for strike-then-Route-6 (lab stays `Lost`, no door breaks) and defeat-then-Route-6.
2. The `Ignited` event, the `EmpirePursuit` binding, and the settings.
3. `RUT_WarLabRevealedSite`, `RUT_Site_WarLab`, the camp layout, `RUT_GarrisonColdSealed`, and
   `GameComponent_WarLabGarrison`.
4. The gizmo gate.
5. Live proof on a test map, by state reads: `Ignite()` once → Visibility, floor, site on tile,
   state `Posted`. Refused gizmo on and off site. Leave with a part-killed garrison and return:
   survivors, not 12. Last guard down → `Beaten` → gizmo works. A second run calls the Route 6 stub
   with the garrison standing → `Moot`, `Broken`, gizmo refused. A third strikes the lab → `Moot`,
   `Lost`, and the Route 6 stub refuses. A second `Ignite()` does nothing.

**To check at build, not settled here:**

- Tile 5873's biome after the swap and what map it generates, since the crag may or may not sit in
  the swapped set. The site must land either way.
- Whether `LordJob_DefendBase`'s `delayBeforeAssault` needs raising above the post's 25,000 for a
  guard that holds.
- Whether the −80 °C offset on `ComfyTemperatureMin` holds on the tile's real temperature.
- Whether pursuit's `PostMapGenerate` timers, which run on any generated map, should be stopped on
  this site. The ladder should not reinforce it.

## Judgment

Status: **not yet ruled.** Round 1, a fresh opus judge under `delegation_policy.md` §4 (rm-consult):
**REDO**, two defects. Strike and defeat left Route 6 live, and a blast-lit Route 6 changed a ruled
route. Both are fixed in this text. Heat, garrison, codes gate and the cited engine facts it found
sound stand unchanged. Round 2, one new judge with a written rebuttal under §4.5, has not returned.
Brief: `infrastructure/state/delegated/2026-11-01/warlab_garrison_early_blast_judge_brief.md`.
Record: `infrastructure/state/delegated/2026-11-01/warlab_garrison_early_blast.json`.
