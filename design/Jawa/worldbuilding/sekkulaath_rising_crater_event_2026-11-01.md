# The sekkulaath rises: the crater event's Fever Wood beat

Item `SEKKULAATH_RISING_DESIGN_CRATER_EVENT`. Every number here is PROVISIONAL. Build items:
`SEKKULAATH_RISING_BUILD_THE_LAMPS_GO_OUT` (this event) and
`CRATER_CUTSCENE_BUILD_NOBODY_HELD_THE_REEL` (the planet-wide cut-scene it plays inside).

Owner, 2026-10-10, story sitting card 19 re-asked, typed: *"(1) appears rageful and dangerous, harms
local Wildsteam sites, makes certain world sites no longer accessible. Shows "the whole world is now
upset and more dangerous" and this is merely the shadow of the Assailants re-arrival."*

Owner, 2026-10-12, by question card: *"How far does the sekkulaath rising reach? → Its region only,
permanently"*. The option text recorded with it: *"damage confined to its own region, permanently
(Wildsteam sites damaged, a handful of regional sites close for good); elsewhere only threat rises."*

## Ruling

Status and judge record: see `## Judgment` at the end of this note.

1. **The trigger is `WarLabCraterMutation.Ignite()` returning true**, whichever route lit it, and
   nothing else. It fires once per save because `Ignite()` can return true only once.
2. **It is one IncidentDef, `RUT_SekkulaathRising`,** with `baseChance` 0, category `Misc`, target tag
   `World`. Its site lists are XML. Nothing ambient can reach it.
3. **Two Wildsteam sites are harmed: Sporefall and Steamreach.** Neither is destroyed. Sporefall
   takes the worse of it.
4. **Five regional sites close for good:** Vhelloth, Fevrakesh, Octopus Silted Creek, Elephant
   Sealshoulder Standing Channel and Minonlanen Town. Their ground sinks. Only a tile something still
   stands on waits, and it closes when that thing leaves (§4).
5. **Elsewhere only threat rises:** threat points ×1.15 for good, on everything that reads them.
   Nothing else changes outside the region.
6. **Inside the region, the pools stay savage for good.**
7. **The cut-scene gives it the last frame before the cut to the crater.**
8. **It is not Assailant flesh and not a woken ancient.** Nothing in this event names the Assailants.
   The player reads the shadow; the text never explains it.

## 1. What exists, and what this design has to change

| piece | where | state |
|---|---|---|
| the blast | `WarLabCraterMutation.Ignite()`, once per save by `GameComponent_WarLabCrater` | built; fires nothing else today |
| the event hook | the `Ignited` event | owed by `WARLAB_GARRISON_BUILD_TWELVE_MEN_ON_GLASS` (garrison note §8, step 2); this event subscribes to it and does not add a second hook |
| the world-tile swap | `Ignite()` sets `PrimaryBiome`, then its private `Commit()` | built; `Commit()` must become internal so this event can share it |
| the young | `RM_WorldComponent_DeepYoung`, `Notify_DisplayTankFreed`, `DisplayTankFreed` | built |
| the tentacles | six `RM_Sekkulaath_*` limbs, `RM_MapComponent_TentacleWatch`, `RUT_MapComponent_TheTenant` | built, as stationary buildings |
| the ground-spawner seam | `RUT_TenantEmergenceSpawner`, an empty subclass | built, no ThingDef uses it |
| the emerged body | `RUT_TenantEmergedMass` | not built, art owed |
| a cut-scene player | none | **does not exist anywhere** |

Four findings shape the rest.

- **The kit's tentacle plan is stale.** F4 said tentacles must be pawns and owed a
  `RUT_TenantTentacle` PawnKindDef. `FEVERWOOD_TENTACLE_BESTIARY_1` built them as buildings, on
  purpose. The rising uses those six limbs, so that def is no longer owed and F4 is corrected.
- **No settlement stands inside the Fever Wood label.** The region is the world feature `Fever Wood`
  (81 tiles, centre 18382, `world/paint_inputs_2026-10-20/ASHKARR_WORLDMAP_features.csv`). Sporefall
  (tile 11927) and Steamreach (12624) each sit one tile step (1.5°) outside its edge. Sporefall is
  still "in the Fever Wood, on the road" by the owner's ruling of 2026-08-24, so it counts. The
  next Wildsteam seat, Greenshadow, is 11.4° away and is out.
- **`tile.feature` cannot be the region test alone**, because Sporefall is off the label. The event
  therefore names its sites and does not sweep the region.
- **The Wildsteam's map-level places are not world objects.** The herd-groves, wood-roads and mirrors
  (`the_fever_wood.md` §8) have no world tile and no persistent state, so there is nothing to
  damage. "Wildsteam sites" here means their two world settlements.

## 2. The event

```xml
<IncidentDef>
  <defName>RUT_SekkulaathRising</defName>
  <label>the deep rises</label>
  <workerClass>RimMandrake.Utinni.StructureInjectionsRUT.IncidentWorker_SekkulaathRising</workerClass>
  <category>Misc</category>
  <targetTags><li>World</li></targetTags>
  <baseChance>0</baseChance>
  <letterLabel>The deep has risen</letterLabel>
  <letterDef>ThreatBig</letterDef>
  <modExtensions>
    <li Class="RimMandrake.Utinni.StructureInjectionsRUT.SekkulaathRisingExtension">
      <harmedSettlements>
        <li>Sporefall</li>
        <li>Steamreach</li>
      </harmedSettlements>
      <closedLandmarks>
        <li>Vhelloth</li>
        <li>Fevrakesh</li>
        <li>Octopus Silted Creek</li>
        <li>Elephant Sealshoulder Standing Channel</li>
        <li>Minonlanen Town</li>
      </closedLandmarks>
      <sunkenBiome>RM_SunkenGround</sunkenBiome>
    </li>
  </modExtensions>
</IncidentDef>
```

The def lives in `StructureInjectionsRUT`, beside the crater. The kit's promise of "one IncidentDef
of XML" holds for the content. The worker is C#, because no vanilla worker edits tiles or settlements.
Its ambient gate is structural: `baseChance` 0, and the only caller is the `Ignited` subscriber, which
runs `TryExecute` with `Find.World` as the target. `World` is an `IIncidentTarget`, and
`IncidentTargetTagDefOf.World` is a vanilla tag.

**Names are resolved at fire time, never tiles.** The planet is painted once at the end, and tile ids
in this note are readings from the paint inputs. Settlements match on `Settlement.Name`, the same way
`RM_GenStep_DisplayTank` finds Sporefall. Landmarks match on `Landmark.name`. A name that finds
nothing logs one warning and is skipped; the event still fires. This is one authored mutation of a
fixed list at runtime. It generates nothing and has no variants, so it is not worldgen.

**The worker's order** in one tick: harm the settlements, close the sites, set the permanent flag, run
one shared commit, call the live emergence if a player map qualifies, then send the letter built
from what actually happened.

## 3. The Wildsteam sites

| site | tile | what happens | permanent effect |
|---|---|---|---|
| **Sporefall** | 11927 | boughs down, lamps out, and the deep comes for what is in the tank | thin stock for good, no Mirror list for sale, tank gone |
| **Steamreach** | 12624 | floods, takes in Sporefall's survivors | thin stock for good |

**Both stay on the map.** A town the owner calls *"beloved"* is damaged, and "harmed" is not "razed".
Both stay visitable, and neither changes faction, goodwill or relations. The Wildsteam do not blame
the player, whoever lit the lake.

**Stock.** A `TraderKind` postfix on `Settlement_TraderTracker` returns `RUT_Trader_WildsteamRuined`
for a settlement in the harmed list once the flag is set, and the worker calls `TryDestroyStock` so
the change is immediate. `RUT_Trader_WildsteamRuined` is a thinner stock list and carries no Mirror
list. The postfix reads a persisted set of settlement IDs in `GameComponent_SekkulaathRising`.

**The tank.** Sporefall's young is the one thing the rage has a reason for.

- If the young is still held, the deep takes it. The worker calls `Notify_DisplayTankFreed`, so the
  tally drops by one and the tank is not regenerated. That call records state only. The goodwill
  break and the gift both live in the player's freeing action, so neither happens here, and the
  letter's young line reads *"The tank is gone. So is what was in it."* If Sporefall's map is loaded
  at that moment, the worker also destroys `RUT_SporefallDisplayTank` on it, so the tank is gone from
  the map a player is standing on and not only from the next one generated. That destruction goes
  through neither the freeing action nor its letter: it uses `DestroyMode.Vanish`, because a kill
  would run the freeing route and cost the goodwill.
- If the player freed it earlier, `DisplayTankFreed` is already true and the letter reads *"The tank
  was already empty. It came anyway."* Freeing the young early buys no mercy.

**The map.** A later visit to Sporefall gets a wreck pass on map generation: a scatter
of fallen bough and dead steam-lamps. It is cosmetic, and its build step can be dropped if it costs
more than a small GenStep.

## 4. The closed sites

Five is the handful. The rule is that the water table came up where the ground is lowest. The four
wet sites on the western basin floor all stand at 19 m or below, and Minonlanen Town is the one built
place on that basin's edge.

| site | landmark def | tile | elevation |
|---|---|---|---|
| Vhelloth | `Oasis` | 12631 | 19 m |
| Fevrakesh | `Oasis` | 18373 | 1 m |
| Octopus Silted Creek | `VEE_StagnantRivulet` | 12630 | 14 m |
| Elephant Sealshoulder Standing Channel | `VEE_StagnantRivulet` | 3468 | 1 m |
| Minonlanen Town | `RUT_ComplexStructures` | 11922 | 114 m |

The eastern half stays open: Sarrukesh, Thaoum Gorge, Artur's Destruction Ruins, Camcrouxosra Ravine
and Dojados Stagnant Rivulet. So does the road to Sporefall. Closing these five cuts no road to any
other tile (measured by `sekkulaath_rising_note_check.py` on the road links), and no other document or
source names them.

**How a site closes.** The tile's `PrimaryBiome` becomes `RM_SunkenGround`, a new biome modelled on
`RM_ChillCrater` with `impassable` true and `canBuildBase` false. Each flag closes one door, and both
were read in the decompiled engine:

- `impassable` makes `WorldPathGrid` refuse the tile, so no caravan path enters it.
- `canBuildBase` false makes `TileFinder.IsValidTileForNewSettlement` refuse it, with or without
  `forGravship`, so neither a settlement nor the ship can land.

The landmark stays on the tile, so the place keeps its name and reads as a lost place, not a blank.
`RM_SunkenGround` on 0 tiles until this fires is the expected state, the same as `RM_ChillCrater`.

**Nothing vanishes.** A tile holding any world object is not swapped when the event fires. The
component rechecks once a day and closes it the day the object has left, so a site's closing is
deferred, never cancelled. A caravan walks off before its ground goes. A player colony on one of these
tiles is the only long wait: the colony is never destroyed or cut off, and the site closes the day the
colony is abandoned. The letter then adds *"The ground under {COLONY} is holding. It is the only ground
out there that is."*, so the exception reads in play whether or not the map gets the live rising (§6).

## 5. Elsewhere only threat rises

The card's option text says elsewhere only threat rises, and F4 asked whether that means a storyteller
bump, raids or both. **It is one permanent factor: threat points ×1.15, set once, on every system
that reads them.**

A postfix on `StorytellerUtility.DefaultThreatPointsNow` multiplies the result by the factor once
the flag is set. About 50 call sites read that method, and the breadth is the point. Raids grow, and
`EmpireLadder` and `RuthlessPursuingMechanoids` inherit it because they call the same method. So do
infestations, mech-hive growth, ancient-complex sentries, thrumbo herds and quest difficulty. His
words are *"the whole world is now upset and more dangerous"*, and those systems are the world.
Raid frequency does not change: that would be a new schedule, and the ruling asks for "more
dangerous", not more often. No new incident is added, no faction relation moves and no tile outside
the region changes.

**This is a deliberate exception to `colony_visibility_stat.md` §4.3,** which says not to patch this
method. §4.3 governs Visibility, a replacement for the wealth term that non-raid systems were never
designed to read. The rising is one flat multiplier, fired once and meant for all of them, so §4.3's
"double-billing by accident" does not apply, and §4.3 now records the exception. It adds one duty:
F12's `RaidThreatPointsNow` will bypass this method at the four raid call sites, so it must apply the
factor itself. The factor is one public read on `GameComponent_SekkulaathRising`.

**Inside the region, the pools stay savage.** `BoldnessMultiplier` returns the cap for good once the
deep has risen, whatever the tally, and `RestlessnessLine` reads *the pools are savage*. This is the
rising's one lasting effect on the living biome, and it is confined to Fever Wood maps. Emptying the
world of young afterwards buys no peace.

**The scanner line changes.** The acoustic `quietText` *"Nothing under the pools is awake."* is false
after the rising. After the flag, it reads *"Mud and root and still water. Whatever was under the
pools has not gone back to sleep."*

## 6. The rising, seen live

Most players meet this as a frame in the cut-scene. A player map on a Fever Wood tile gets it in
person. The test is `tile.feature` named `Fever Wood`, or a biome of `RM_FeverWood` or
`RUT_FeverWood`. Each qualifying map gets:

- one `RUT_TenantEmergenceSpawner` at the map's largest `RUT_FeverWoodMirrorPool` body, which comes up
  as `RUT_TenantEmergedMass`, a building that cannot be damaged;
- the five limb roles `RM_Sekkulaath_Feeler`, `RM_Sekkulaath_Snare`, `RM_Sekkulaath_Lash`,
  `RM_Sekkulaath_Porter` and `RM_Sekkulaath_Sentinel` around that pool, through the same placement
  `RM_MapComponent_TentacleWatch` already uses;
- the mass sinks, once, at the first of two things: every limb on the map has retreated or been
  severed under the existing ladder, or two in-game days have passed.

The mass cannot be killed. *"you never can kill, but you can drive it off"* is the owner's rule, and
driving off the limbs is how it is driven off. **The rising brings no `RM_Sekkulaath_Bloom`.** The
Bloom carries `RM_CompTentacleEye`, whose severe branch calls `KillPermanentlyOnThisMap`; the whole
body offers no small eye to hit, so the rising's own limbs hold no way to end it for good. An ordinary
Bloom already up, or one that ambient emergence brings during the two days, stays under the ruled
ladder (`fever_wood_deep_and_mud_2026-09-23.md` §2b). Beating it clears the map's limbs, so the mass
sinks with the second letter below. Colonists are grabbed under the
Snare's existing rescue window, which outlives the mass, so nobody vanishes without a sign. When the
mass sinks, the map's player gets a second letter: *"It has gone down again. It has not gone back to
sleep."*

**A map that has already won keeps it.** The emergence uses the three gates of `ForceEmergenceNear`:
the bestiary setting off, `PermanentlyKilled`, or fouled water still in effect means no mass and no
limbs on that map, and the letter takes the plain `{DEPARTURE_LINE}`. The world changes still happen.

A map with no mirror pool gets no emergence. If `RUT_TenantEmergedMass` is not yet built, the emergence
is skipped with one warning and everything else in this note still happens.

## 7. The cut-scene and the words

No cut-scene player exists yet, and none of the crater's ruled presentation is built (*"We will
effectively have a 'cut scene.'"*, and card 4's *"every region notices"*). That build is filed as
`CRATER_CUTSCENE_BUILD_NOBODY_HELD_THE_REEL`. This note owes only its own beat.

**The beat is the last frame before the cut to the crater.** Every region notices. The Fever Wood is
the one region where something answers, so it goes last, and the cut to the crater lands on it. The
camera jumps to the world feature's centre (`CameraJumper.TryJump`, resolved from the feature by name)
and holds one full-screen image: black water going up through the crown, with the body too big for
the frame, in the owner's *"so big it can't even enter the screen."* It is art commissioned with F4.
No frame shows the whole outline. What stays a mystery is its size and what is at the bottom.

Until the cut-scene exists, the letter stands in with a look target on that same tile.

**The letter**, a `ThreatBig` letter, story text only:

> The Chill went up, and the Fever Wood heard it.
>
> Every pool in the wood went flat at the same moment. Then the sekkulaath came up through the mud,
> all of it, for the first time anyone alive can swear to. It did not hunt. It tore at the wood as if
> the wood had hurt it.
>
> Sporefall's lamps are out and its boughs are down. {YOUNG_LINE} Steamreach has its survivors, and
> its own water at the door. West of the road the ground has sunk under Vhelloth, Fevrakesh, the
> old creeks and Minonlanen Town, and it will not give them back.
>
> {DEPARTURE_LINE}
>
> Far from the wood, nothing has changed that anyone can point to, and everything is worse. Whatever
> comes for you now will come harder, and it could not tell you why. Something has frightened the
> world. The thing in the mud only felt it first.

`{DEPARTURE_LINE}` is *"It has gone down again. It has not gone back to sleep."*, unless a player map
has the live rising, when it is *"It is still up."* and the second letter (§6) says the rest. The
letter asserts stronger threats and nothing more, because §5 changes nothing else.

The last line is the shadow. The Narrator gets one line in the cut-scene, *"The deep was only the
first to feel it."*, and neither names what it felt. Story text says **sekkulaath**, never "the
Tenant", per the item's own rule.

## 8. Where it meets other rulings

- **The early blast.** An early blast and a blast with the codes both fire it, because both are
  `Ignited`. Early or late changes nothing here, and the garrison note says the same from its side.
- **The Reclamation.** Independent, either order (card 12). Nothing here counts toward it.
- **The strike or the dive.** Both come after the blast, so neither fires this event again.
- **The Brood Ransom.** Unchanged before the blast. After it, the tally still works and only the
  boldness is pinned to the cap.
- **A conquered, renamed or destroyed Sporefall or Steamreach** matches nothing, so it is skipped with
  the warning and the letter drops its sentences. The worker builds the letter from what was actually
  hit, including the list of closed sites.
- **No worldgen** (§2). **A biome of ours on 0 tiles** is expected (§4). **Every DLC is assumed**:
  nothing here tests for one.
- **Flyers.** No flight is involved. The limbs and mass are stationary.

## 9. Mod Settings

On `StructureInjectionsRUT`: **The sekkulaath rises** on/off (default on), and **World threat after
the rising** ×1.00 to ×1.50 (default ×1.15). With the first off, no event fires, sites stay open and
threat is unchanged. `warLabCraterEnabled` off already means no `Ignited`, so
this event cannot fire. On `RM_FeverWoodSettings`: **Pools stay savage after the rising** on/off
(default on).

## 10. Build plan

Filed as `SEKKULAATH_RISING_BUILD_THE_LAMPS_GO_OUT`. It ships with its slice of the mod's
`validation.py`, under the 2026-10-01 debugging process. It needs `WARLAB_GARRISON_BUILD_TWELVE_MEN_ON_GLASS`'s
`Ignited` event first.

1. A pure kernel: which sites are hit, which are deferred, which young line and which letter
   sentences apply. Selftests cover each case in §3, §4 and §8.
2. `RM_SunkenGround`, `RUT_SekkulaathRising`, `IncidentWorker_SekkulaathRising`,
   `GameComponent_SekkulaathRising`, `RUT_Trader_WildsteamRuined`, the `Commit()` change and settings.
3. The two postfixes and `BoldnessMultiplier`.
4. Live emergence: `RUT_TenantEmergedMass`, its spawner ThingDef and art. It may land last.
5. Live proof on a test map, by state reads: `Ignite()` once → the five tiles read `RM_SunkenGround`,
   a path to each is refused, settling is refused, both settlements report `RUT_Trader_WildsteamRuined`,
   threat points read ×1.15 before and after on one fixed colony. No Bloom stands among the rising's
   limbs, and a map with `PermanentlyKilled` set gets no emergence. A caravan parked on Vhelloth holds
   the swap until it leaves. With Sporefall's map loaded, the tank is gone and goodwill is unchanged. A second `Ignite()` does nothing.

**To check at build, not settled here:**

- Which state of `RM_CompProperties_TentacleLimb`'s ladder reads as retreated or severed, for the
  mass's sink test.
- Whether a river tile (Octopus Silted Creek carries a river) draws correctly on the swapped biome.
- Whether the soft reference from `StructureInjectionsRUT` to `RM_WorldComponent_DeepYoung` needs the
  reflection binding the garrison uses for `EmpirePursuit`.
- If the compile-excluded `Spike_ThreatPointReplace.cs` is ever built, its postfix on the same
  method and this one need an agreed order.
- Whether a saved `Settlement_TraderTracker` holding stock from before the swap needs more than
  `TryDestroyStock`.

## Judgment

Status: **not yet ruled.** A `delegation_policy.md` §4 opus judge returned REDO, confined to §5 and §6,
and passed the site list and hard reads 2-8. Both defects are fixed in this text, which a new judge
must rule. Brief:
`infrastructure/state/delegated/2026-11-01/sekkulaath_rising_judge_brief.md`.

Round 1 defects: the six-limb set included the Bloom, whose severe branch ended the rising for good,
and a map already won was unhandled (§6). The threat patch contradicted `colony_visibility_stat.md`
§4.3 unacknowledged, and §10 cited a postfix that does not exist (§5).

Pre-review only, by GPT (not a valid §4 judge for this class): one round, REDO, six defects, all fixed
in this text. They were a tank left standing on a loaded map, a closure with a permanent exemption, a
mass with no drive-off, a letter that announced the departure too early, a letter that promised raids
sooner than §5 delivers, and a line that claimed a time it could not know. Record:
`infrastructure/state/delegated/2026-11-01/sekkulaath_rising.json`.
