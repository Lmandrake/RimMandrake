# STILLSAND_DUNE_GALE_1 — the dune gale, its static, the dust devils and what the wind gives back

From `STILLSAND_BEDAZZLE_SITTING_1` (closed 2026-09-30). Design source:
`design/Jawa/worldbuilding/biomes/stillsand_turn3_development_2026-09-30.md` §2.2, §3.2 and §4 #7,
#8, #16, with the turn-4 rulings in `stillsand_bedazzle_cast_2026-09-30.md` §0. Owner, typed:
*"Stillsyork makes no sense as a name. Call it a dune gale."* **Depends on
`MOVING_DUNES_BUILD_1`** being seen live; the gale is the natural test of that engine.

## spec

1. **`RM_DuneGale`** WeatherDef plus a GameConditionDef for its duration: rare (a few a year), one
   to two days; herald (ochre windward horizon, dust sheets off every crest), gale (brown-gold dim
   sky, short sight, accuracy and move penalties), aftermath. The rumble layer is drowned.
2. **The dunes march.** Through `DuneFieldExtension`'s existing per-weather override: storm
   transport about 20× and a raised `influxPerDay`; the mass cap stays binding.
3. **Sun off:** the gale's sky feeds `RM_SunHeatExtension` as an exposure multiplier of about 0.2,
   the one natural relief from the heat in a biome without night.
4. **Abrasion:** exposed outdoor pawns take a slow scratch-damage tick; thin roofs and light walls
   under a mass threshold take structural damage.
5. **Carry, never vanish:** a pawn or animal under a body-size threshold, in the open on a crest,
   can be dragged 3–10 cells downwind and lands bruised with an `RM_Filth_DragMark` line. One
   carried off the map edge gets a letter naming them and the bearing, and **comes back** (the next
   gale or dune pass returns the body, or the living pawn as a wanderer, downwind).
6. **Swimmers blind:** strike rates collapse during the gale (`STILLSAND_SAND_SWIM_KIT_1`'s
   appraisal reads the condition).
7. **Gale static (slate IN):** brief EMP-style stun ticks on turrets and droids and sparks on metal,
   so the droid road (droids invisible to swimmers) has its closing weather.
8. **One emergence at gale end:** one reveal, placed with the dunes engine's `BuryThingsAt` in
   reverse near a fresh erosion face, and a letter saying what the wind uncovered. Table: the
   **mummified caravan** (lore IN: a whole caravan, beasts and riders, desiccated where the dune
   took it, packs intact, water skins its most valuable thing; a mass burial that points nowhere,
   distinct from the Long Shade's gap graves), a hull, a sealed Jawa cache, a giant skeleton
   (`STILLSAND_SKELETONS_TRACKS_1`), or a cave mouth in the nearest rock
   (`STILLSAND_PRECIOUS_CAVES_1`).
9. **Seeding:** wake dormant siidda nearby, lay a glasscrust sheet, and fire the shipped
   `RM_IncidentWorker_BloomBurst` hourbloom if water is present.
10. **Dust devils (slate IN):** a rare, brief, single spinning column (`RM_DustDevil`, a moving
    Thing with flecks and a scour radius) that wanders the flat, lifts light items, scours sand off
    a cache for a moment, scatters a stockpile and spooks animals. It announces itself on the hiss.
    It is a fair-weather event, distinct from the gale.
11. **Tracks are wiped:** every track record (`FOOTPRINT_TRACK_GRID_1`) and scar filth on a cell whose
    sand depth changes past a threshold is cleared (shared with `STILLSAND_SKELETONS_TRACKS_1`); the gale
    resets the map's memory.
12. **Mod Settings:** a toggle each for the gale, abrasion, carry, static, emergence and dust
    devils; frequency sliders.

## criteria

- A dev-fired gale on a Stillsand quicktest moves measurable sand (dune field mass delta logged),
  cuts sun exposure, and ends with exactly one emergence and its letter.
- A carried pawn always has a drag line or a letter; none disappears silently.
- A dust devil spawns, moves, and despawns on its own with no leftover Thing.
