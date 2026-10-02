# GREENTIDE_CEDED_ROOM_RITE_1 — The Ceded Room, for Ozzik: build a room outside the ship and let the jungle take it

Caused by `GREENTIDE_SCORING_SITTING_1` (turn 1). Campaign tier, `mandrake.rut.rites` (found rite). Design:
`design/Jawa/worldbuilding/biomes/greentide_bedazzle_review_2026-10-02.md` §6 R1, §8. Register:
`design/Jawa/salvation_rites_2026-10-01.md` B11 (row added) and §(d) for the found-rite machinery.

Ruling, owner, typed 2026-10-02: *"Use first and third. First can be here. Build it outside the ship and
let it be taken.  Works better the better the room. The third works on another map that doesn’t have one
for this god yet. Likely one with open sight lines."* The first is this rite, found in the Greentide. The
third, the Open Boast, is `WARSCAR_OPEN_BOAST_RITE_1`. The Uprooting (R2, Ta'Baa) was not chosen.

Grounding: the Greentide is the one place where the world visibly eats buildings (growth through doors,
roots taking what dry heat does not defend). Ozzik is pride and grief; the proudest thing a colony owns is
usually a room. The rite vents pride by surrender. ⚠️ Ozzik's found-rite count with this rite and the Open
Boast is **five**, one over the four-rite cap (register B11 note); recorded for the owner, nothing cut.

## spec

**God: Ozzik** (pride and grief; never "evil"). Kind: venting. One `GameComponent_Ninefold.ApplyDelta(
God.Ozzik, <sized by outcome quality and the room's impressiveness>, "The Ceded Room")` per performance,
the call shape of `SUMP_SINKING_RITE_BUILD_1`, sign chosen so Ozzik's pressure eases (venting).

1. **Found / learned.** Inscription `RUT_CededRoomLintel`: a windowless mud dome in the habitable band, its
   blower cold, its door wedged open, the room inside fully grown through, a carved chair and a sculpture
   still visible inside the green, and on the lintel a scratched mark: *we were proud of this.* Placed on
   Greentide maps by a map GenStep with a chance (never worldgen; a building group placed on map
   generation, the `RUT_FelledNoonStump` shape). Rubbing (`CompStudiable`) → the Rites tab's "found rites"
   row → `RUT_ResearchMod_GrantRite` adds the precept, per §(d). Performable after on any map.
2. **Asks.**
   - **Target: a room built outside the ship.** The ritual target is a finished, enclosed, roofed room
     (vanilla `Room`, not outdoors, not a doorless cell) **none of whose cells lie on gravship substructure**
     (BENCH's reading of *"outside the ship"*: the ship is never ceded, and a ceded room never flies). A
     `RitualObligationTargetFilter` over rooms; the player picks the room (any room the colony built
     qualifies, including one built for the purpose). Minimum impressiveness (Mod Settings, default about
     the vanilla "decent" band) so a shack cannot be ceded.
   - **The ceding:** participants gather in the room; the speaker names what the room was for; nothing is
     carried out (items and furniture stay); at the end the doors are forced open (held-open, vanilla
     `holdOpen`), the room's temperature-control buildings (coolers, heaters, the free-tier
     `RM_DryAirBlower`) are switched off, and wild seed is scattered on its floor.
3. **Let it be taken.** After the rite the room is **ceded**, a saved map record (`RUT_MapComponent_CededRooms`
   holding the room's cells and the date):
   - its doors stay open (re-closing one is a reclaim);
   - wild plants are seeded into its floor cells over the following days: through the
     `EXPLOSIVE_PLANT_GROWTH_1` engine where it is loaded, vanilla wild-plant spawning on its cells
     otherwise (plants that the biome's `wildPlants` allow; on a map with none, the room only weathers);
   - its furniture deteriorates at the outdoor rate (it counts as unroofed for deterioration only);
   - **nothing may be reclaimed for a season** (Mod Settings, default 15 days): deconstructing, hauling out,
     cutting plants in, re-closing a door or re-powering a climate building inside the ceded cells is a
     **reclaim**, which ends the ceding, gives every participant a negative memory, and the Narrator says
     Ozzik saw. After the season the record expires and the room is the colony's again, whatever is left.
   - In the Greentide the ceded room is a breach the jungle pushes from into adjoining rooms (that is the
     biome's own growth, no new mechanic).
4. **Works better the better the room.** Outcome quality, the shared memories' strength and the size of
   the Ozzik delta all scale with the room's impressiveness at the start of the rite (vanilla
   `RoomStatDefOf.Impressiveness`), on a curve (Mod Settings scalar). A grand room ceded is a big vent; a
   modest one a small one.
5. **Outcomes: cohesion only.** Shared memories by quality. Ozzik's ease is told by the Narrator and shows
   only as odds (his high pressure, the trap that raises Sh'kaar and Zizzik, eases), never a buff, hediff or
   stat.
6. **Readable signs:** the open, overgrown room on the map; an inspect line on its cells ("ceded to the
   green, N days left"); a lintel mark the colony scratches over the door (a small filth/graffiti decal);
   the letter naming the room and its worth.
7. **Mod Settings:** on/off; minimum impressiveness; season length; impressiveness scalar; inscription
   chance.

Collision check (review §6): the Unburdening destroys wealth at once; the Salted Keeping buries one finest
thing in a crater; the Flawed Masterwork mars an object. None surrenders a lived room to time, kept in
sight.

Depends on: `SALVATION_RITES_UNIFICATION_1` (found-rite machinery, `RUT_ResearchMod_GrantRite`).
Soft: `GREENTIDE_BASE_PORT_BUILD_1` (`RM_DryAirBlower` as a climate building to switch off),
`EXPLOSIVE_PLANT_GROWTH_1` (visible growth; vanilla spread is the fallback). Art:
`infrastructure/artpipe/art_lists/greentide_turn1_2026-10-02.csv` (`RUT_CededRoomLintel`).

## criteria

Deterministic state reads through debug `[Tool]`s, recorded as cases in `src/RimUtinni/Rites/validation.py`:
- Studying `RUT_CededRoomLintel` to completion: the found-rites row lists the Ceded Room and the precept is
  granted.
- Target filter: on a test map with three rooms (one on gravship substructure, one below the minimum
  impressiveness, one above it off the ship), only the third is a valid target; each refusal carries a
  reason line.
- After the rite on the valid room: `RUT_MapComponent_CededRooms` lists exactly its cells with a
  ticks-left equal to the configured season; every door in it reads held open; every climate building in
  it reads switched off; every item that was in it is still there.
- After N simulated days on a map with wild plants allowed: the count of plants on the ceded cells is > 0.
- Reclaim: deconstructing one furniture piece in the ceded cells during the season ends the record and
  gives each participant the reclaim memory; doing it after the season gives none.
- Scaling: two runs on rooms of impressiveness A < B give Ozzik deltas (tagged "The Ceded Room" in
  Ninefold) with |delta(A)| < |delta(B)| and outcome quality(A) ≤ quality(B).
- No new hediff or stat on any participant.
- Each Mod Settings toggle off removes exactly its effect.
