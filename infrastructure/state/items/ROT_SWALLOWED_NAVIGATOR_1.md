# ROT_SWALLOWED_NAVIGATOR_1 — The Swallowed Navigator: the old drive core inside the hwelgrue pings the gravship, feeds its console a dead ship's log of salvage sites, and, cut out, is a major range upgrade that ship weapons will ruin

Caused by `ROT_SCORING_SITTING_1` (turn 1, new-marks redo). Free tier mechanism (`mandrake.rm.therot`),
campaign site list in `UtinniPatches`. Design: `design/Jawa/worldbuilding/biomes/rot_new_marks_redo_2026-10-02.md`
S1, review `design/Jawa/worldbuilding/biomes/rot_bedazzle_review_2026-10-02.md` §3 (hook 1), §8. Mark 6 (gravship
touch).

Rulings: **ship = Swallowed Navigator** (decision taken by question card 2026-10-02 10:50 PDT). Owner, typed
2026-10-02, extending it: *"(1) but more. The thing inside would also be a significant upgrade to your ship if
extracted. But you can't use ship weapons on the giant without harming it, making the fight much harder. Would
upgrade your range, as it was part of a drive system of an older ship."* And on the giant: *"I love the old ship
that's pinging from within begging the players to figure out how to kill it."*

So the dilemma has two sides: **keep the hwelgrue alive** and the log keeps writing salvage sites; **kill it**
and the log stops, but the core is a major range upgrade, and the easy way to kill a giant (the ship's guns)
wrecks the prize.

## spec

**Measured in RimSage 2026-10-02 (decompiled 1.6, Odyssey):** range is the stat `GravshipRange`
(`Defs/Odyssey/Stats/Stats_Building_Special.xml`); `Building_GravEngine.MaxLaunchDistance` =
`(int)GetStatValue(StatDefOf.GravshipRange)` (the engine's base is 0); the thrusters are **facilities** that
offset it, `SmallThruster` +10 and `LargeThruster` +16 (`Buildings_Gravship.xml`, `CompProperties_Facility`
`statOffsets`, displayed by `CompProperties_Facility` as "GravshipRangeOffset"); `CompPilotConsole` divides the
engine's range by the destination layer's `rangeDistanceFactor`; fuel separately caps a trip
(`GravshipUtility.TryGetPathFuelCost`, 10 fuel per tile × the engine's fuel factor). The console is
`CompPilotConsole` on `PilotConsole`. Ship cells are `Building_GravEngine.ValidSubstructureAt(cell)`.

1. **The core inside.** `RM_CompSwallowedCore` on the hwelgrue (`ROT_HWELGRUE_GIANT_BUILD_1`): present from
   spawn on the map's one hwelgrue (every hwelgrue carries one in the free tier; the campaign may restrict it to
   authored Rot tiles by a patch). It holds core integrity 0–100 (starts 100).
2. **The ping.** On every gravship landing on a map where a living hwelgrue with a core exists (reuse the
   landing hook `src/RimMandrake/EnvironmentalHazards/Source/RM_Patch_GravshipArrivalLetter.cs`, add a listener,
   never a second patch on the same method), and then every **12 hours** while the ship is on that map: a
   positional `SoundDef RM_CorePing` (a slow electronic pulse, muffled through flesh) from the hwelgrue, an
   answering chirp from the `PilotConsole`, and a world-map-style pulse mote on the giant. First time: a
   letter from the ship's Narrator (*"The console is answering something. It is inside that animal."*).
3. **The dead ship's log.** A `GameComponent` (`RM_GameComponent_NavigatorLog`) counts pings received by a
   console while the hwelgrue lives. Every **4 pings** (setting) it writes the next entry of a fixed,
   hand-written list in `RM_NavigatorLogDef` (8 entries by default, text authored, each a line of an old flight
   log), read out by the Narrator as a letter. Entries 2, 4, 6 and 8 each **reveal a salvage site**: a world
   object placed through a `QuestScriptDef RM_NavigatorSalvageSite` the way vanilla item-stash quests place a
   site (`SitePartDef`s holding a wreck, cargo or buried cache, with guards or hazards per vanilla site
   parts: ban 8, no undefended prize). Free tier: the site tile is chosen by the vanilla tile finder within a
   travel range. Campaign: a patch fills `RM_NavigatorLogDef.fixedTiles` with authored Ash'karr tiles (the world
   is fixed; nothing generated), used in order.
4. **Killing it ends the log.** When the hwelgrue dies, the component stops; the Narrator says the log
   stopped mid-line. Entries already written stay; their sites stay.
5. **The core comes out.** On death the hwelgrue drops `ThingDef RM_SwallowedDriveCore` (a minifiable
   building: a drive-coil housing from an older ship's drive, slick with gut). Installed on gravship substructure
   it is a **facility** linked to `GravEngine` with `statOffsets GravshipRange` **+24** at full integrity
   (setting; 1.5× a large thruster: *"a significant upgrade"*), scaled linearly by the integrity it came out
   with. It counts as one facility like a thruster (the engine's facility limits apply; measure
   `linkableBuildings`/`maxSimultaneous`).
6. **Ship weapons harm it.** In `RM_CompSwallowedCore.PostPostApplyDamage`: if the damage instigator is a
   building turret (or any `Building`) standing on a cell where a grav engine on the map reports
   `ValidSubstructureAt` (the ship's own guns), core integrity falls by `damage × 0.5` (setting). Any other
   damage source does nothing to the core. Below **25** integrity the core is ruined: the drop becomes
   `RM_RuinedDriveCore` (scrap: steel, components, no range). The inspect line warns (*"The ping falters when
   the ship's guns hit it."*), and the ping's pitch drops with integrity so it is heard.
7. **Readable signs:** the ping, the console chirp, the letters, the inspect line with integrity, the world
   sites, the facility's range offset shown on the engine's stats.
8. **Mod Settings** (Ship section): on/off; ping interval; pings per entry; range bonus; ship-weapon damage
   factor; ruin threshold.

Depends on: `ROT_HWELGRUE_GIANT_BUILD_1`. Soft: `GRAVSHIP_LANDING_FIRST_SCRIPT_1` (landing harness). Art:
`RM_SwallowedDriveCore`, `RM_RuinedDriveCore` in `infrastructure/artpipe/art_lists/rot_turn1_2026-10-02.csv`.

## criteria

Deterministic, in `THE_ROT_FIRST_SCRIPT_1`'s `validation.py` (campaign case in
`src/RimUtinni/UtinniPatches` validation), through `jawa/get_defs` and debug `[Tool]`s:
- Defs resolve: `ThingDef/RM_SwallowedDriveCore`, `ThingDef/RM_RuinedDriveCore`, `SoundDef/RM_CorePing`,
  `RM_NavigatorLogDef` (one, ≥ 8 entries), `QuestScriptDef/RM_NavigatorSalvageSite`.
- A spawned hwelgrue has `RM_CompSwallowedCore` with integrity 100.
- Landing (debug-forced arrival) on a map with a living hwelgrue: the component's ping count goes 0 → 1; with no
  hwelgrue it stays 0.
- After 4 pings, entry count = 1; after 8, = 2 and exactly one new `RM_NavigatorSalvageSite` quest is active
  with a world object on a valid tile (campaign: the first `fixedTiles` tile).
- Killing the hwelgrue: further forced pings do not change the entry count; one `RM_SwallowedDriveCore` exists.
- Range: a grav engine's `GravshipRange` stat with the core installed and linked, minus without it, equals the
  setting × integrity/100 (read both).
- Ship weapons: damage from a turret on substructure lowers integrity; the same damage from a colonist's rifle
  does not (integrity read before/after each). Integrity driven below 25 then a kill drops
  `RM_RuinedDriveCore`, not the core.
- Each Mod Settings toggle off removes exactly its effect.
</content>
</invoke>
<invoke name="Bash">
<parameter name="command">head -1 /home/mandrake/rm/bench/infrastructure/state/items/ROT_SWALLOWED_NAVIGATOR_1.md