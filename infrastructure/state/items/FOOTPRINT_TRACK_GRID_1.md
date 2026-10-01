# FOOTPRINT_TRACK_GRID_1 — one footprint grid for the planet (Warscar film + Stillsand sand)

From `WARSCAR_BEDAZZLE_SITTING_1` (turn 4, by card 2026-09-30 20:50 PDT: *Stillsand tracks move onto
ONE shared footprint grid with the Warscar*). Design source:
`design/Jawa/worldbuilding/biomes/warscar_turn3_development_2026-09-30.md` §2.1 ("The tracks" and
"Shared kit"). **Build this once, in CreatureBehaviors (RM).** `WARSCAR_SETTLING_WEATHER_1` and
`STILLSAND_SKELETONS_TRACKS_1` §7 both consume it as XML; neither builds its own track store.

## spec

1. **`TrackGrid`** (a `MapComponent`): one compact record per cell (direction 3 bits, size class 2,
   source class 2, tick laid) in a **fixed-capacity pool** (proposed 6,000 per map) with a cell→slot
   index. Eviction when full: **by priority, then age** — small animals first, then old records;
   **recent humanlikes and large animals (bs ≥ 1.5) kept** (ruled at the GPT card). Saved with
   `Scribe` as packed arrays. **No `Thing` is ever spawned** for a print.
2. **Writer:** a Harmony postfix on `Pawn_FilthTracker.Notify_EnteredNewCell` writes a record when the
   cell's surface carries **`RM_TrackSurfaceExtension`** (on a filth def, terrain or condition-laid
   film). Verify first that animals and mechs reach that hook (it is gated on race filth flags); add a
   second hook if they do not.
3. **Invisible pawns are recorded too** (turn-4 IN, *unseen things leave prints*): no filter on
   `HediffComp_Invisibility` / `IsPsychologicallyInvisible`. The grid is how the planet answers every
   invisible hunter (the murrek, the drum-lure swimmers, Anomaly's).
4. **Draw:** one custom `SectionLayer` printing a rotated print sprite per record, rebuilt only for
   dirty sections (precedent: MovingDunes' `SectionLayer_DuneSand`). Sprites per **print class** set on
   the extension: human, animal, large, drag, plus per-race overrides (the Stillsand's oommok print and
   crawler tread, already queued, become override sprites rather than filths).
5. **Erase API:** `ClearCell`, `ClearRect`, and a batched **downwind sweep** helper. Each biome brings
   its own eraser: the Warscar's wind (`WARSCAR_SETTLING_WEATHER_1`), the Stillsand's dunes engine
   (a cell whose sand depth changes past a threshold clears).
6. **Mod Settings:** tracks on/off (labelled the performance switch), pool cap, print opacity.

## criteria

- 6,000+ pawn-steps on a surface leave exactly the cap in records; humanlike and bs ≥ 1.5 records
  survive a flood of small-animal records.
- A dev-spawned invisible pawn crossing a track surface leaves prints (state read on the grid).
- Save/load round-trips the grid byte-identical; no `Thing` count change from printing.
- The Stillsand and the Warscar each drive the grid with XML only plus their eraser call.
