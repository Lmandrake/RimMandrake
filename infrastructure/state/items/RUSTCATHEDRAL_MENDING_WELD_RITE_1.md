# RUSTCATHEDRAL_MENDING_WELD_RITE_1 — The Mending Weld, for Rekko: rebuild a broken stretch of old structure into a whole room

Caused by `RUSTCATHEDRAL_SCORING_SITTING_1` (turn 1). Campaign tier, `mandrake.rut.rites`
(`src/RimUtinni/Rites/`, found rite). Design:
`design/Jawa/worldbuilding/biomes/rustcathedral_bedazzle_review_2026-10-02.md` §6 R1 (the pitch) and §8 (the
ruling, which changes the act). Register: `design/Jawa/salvation_rites_2026-10-01.md` B12 (row added).

Ruling, owner, typed 2026-10-02: *"Mending Weld (Rekko): Repair a stretch of old structure here into a
properly formed room, restoring an old creation. Very sacred."*

**What changed from the pitch:** R1 welded the colony's best salvage into a damaged wall that is not
theirs. The ruling makes the act **restoration of form**: a broken run of old structure is rebuilt until it
is a properly formed room again. Kept from the pitch: Rekko, the found site (a gap mended in a foreign
hand), the risk at sacred walls. Grounding unchanged: Rekko is *"positive when we mend, sharply negative
when we scrap the mendable"* (`divine_satiation_engine.md` ⑤), and the Rust Cathedral is the planet's
purest salvage country, so restoring one of its old creations inverts its economy. Rekko's found rites: the
Unfinished Laid Down, the Inherited Wreck, the Mud Claim (B7, pitched), and this: **four**, one under the
five-rite cap.

## spec

**God: Rekko.** Kind: feeding, **very sacred**: the largest single Rekko delta of any found rite (Mod
Settings scalar; default twice the Mud Claim's). One `GameComponent_Ninefold.ApplyDelta(God.Rekko, <sized by
outcome quality and the room's size>, "The Mending Weld")` per performance.

1. **Found / learned.** Inscription `RUT_MendingWeldPlate`: a run of the Cathedral's maze broken once and
   mended in a foreign hand, a gap in a conduit wall filled with mismatched scrap welded rough and roofed over
   with a sheet of plate so the cell behind it is a room again; the living bolts dance calm figures around it;
   on the patch plate, scratched in the clan's trade marks: *what was broken is whole.* Placed on Rust
   Cathedral maps by a map GenStep with a chance (never worldgen). Rubbing (`CompStudiable`) → the Rites
   tab's found-rites row → `RUT_ResearchMod_GrantRite`, per §(d). Performable after on any map.
2. **Target: a stretch of old structure that was once a room.** A `RitualObligationTargetFilter` over
   *ruin regions*: a connected set of non-colony walls (ancient ruin walls, the Cathedral's wall tiers, a
   wreck's hull) that **almost** encloses an area, with gaps (missing wall cells) and/or missing roof, such
   that filling at most N missing wall cells (default 12) and roofing it yields one enclosed, roofed vanilla
   `Room` (`ProperRoom`). The filter computes the plan (the missing cells) and shows it as a ghost overlay
   when choosing. Colony-built walls never count as old structure. Minimum size (default 9 cells inside).
3. **The act.** The rite lays the plan as blueprints owned by the rite; participants build them by hand
   (Construction), in the **old structure's own material** where one is defined (on Cathedral ground:
   `RM_CathedralDeckPlate` plate for plain runs; `RM_DeadSmartsteel` for a sacred conduit run), otherwise
   the wall's stuff; then roof the interior. The rite completes when the region reads as one enclosed,
   roofed room. The rebuilt cells take the **original owner** (a Cathedral wall stays the Cathedral's; a ruin
   stays unowned): the colony restored it, it did not take it.
4. **Risk.** The material is really spent; the work stands in the open for hours. On Cathedral ground a
   **botched weld** (each built cell rolls the builder's Construction; a failure) reads as damage to a sacred
   thing when the run is a sacred tier: the hum's irritation jumps and the ruled goodwill drain runs. A
   sacred run restored well is the opposite: the hum settles a band for a while (a world-state sign, not a
   reward).
5. **After: the restored room is sacred to Rekko.** A saved record (`RUT_MapComponent_MendedRooms`). Later
   deconstructing or destroying any of its rebuilt cells by colony order is **scrapping the mendable**:
   Rekko sharply displeased and a negative memory on everyone who took part; damage by enemies is no fault.
   The colony may use the room (it is a room); it may not take it apart.
6. **Outcomes: cohesion only.** Shared memories by quality; the room's size and the share of the plan
   rebuilt in original material scale quality. Rekko's favour is told by the Narrator and shown as his
   Exalted odds (*"salvage yields feel providential"*), never a buff.
7. **Readable signs:** the ghost plan while choosing; the rebuilt cells visibly newer within the old run; an
   inspect line on the room (*"Mended by the clan. Rekko watches it."*); the letter.
8. **Mod Settings:** on/off; max missing cells; minimum size; Rekko scalar; inscription chance.

Collision check: the Scrap Shrine offers scrap to Rekko; the Seating puts a relic into our hull; the Mud
Claim and the Inherited Wreck take salvage; Nine Faults leaves a broken thing as an offering; the Ceded
Room gives a colony room away to the jungle. None rebuilds someone else's old structure into a whole room.

Depends on: `SALVATION_RITES_UNIFICATION_1` (found-rite machinery), `RUSTCATHEDRAL_FREE_NAMES_TIDY_1`
(the wall and attitude names). Art: `infrastructure/artpipe/art_lists/rustcathedral_turn1_2026-10-02.csv`
(`RUT_MendingWeldPlate`).

## criteria

Deterministic state reads through debug `[Tool]`s, recorded as cases in `src/RimUtinni/Rites/validation.py`:
- Studying `RUT_MendingWeldPlate` to completion: the found-rites row lists the Mending Weld and the precept
  is granted.
- Target filter on a test map with three regions (a colony-built broken room; an ancient ruin needing 6
  cells; an ancient ruin needing 20 cells): only the second is valid; each refusal carries a reason line;
  the valid one's plan lists exactly the missing cells.
- After completion: the region is one vanilla `Room` with `ProperRoom` true and fully roofed; every
  rebuilt cell's faction equals the run's original owner (null for a ruin; the Cathedral's faction on a
  Cathedral run); `RUT_MapComponent_MendedRooms` lists the room.
- Ninefold logs one Rekko delta tagged "The Mending Weld", larger in magnitude than the Mud Claim's default.
- Deconstructing one rebuilt cell by colony order afterward: Rekko displeased delta logged and each
  participant holds the negative memory; the same cell destroyed by a spawned hostile: neither.
- On a Rust Cathedral map with a sacred run: a forced construction failure raises irritation; a clean
  restoration lowers the band for the configured duration.
- No new hediff or stat on any participant.
- Each Mod Settings toggle off removes exactly its effect.
