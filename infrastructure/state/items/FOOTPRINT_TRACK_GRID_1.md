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
   film). **Verified (RimSage, 1.6 decompile):** the only caller is `Pawn_PathFollower.TryEnterNextPathCell`,
   right after `pawn.Position = nextCell` and `lastMoveDirection = (next - last).AngleFlat` (compass:
   0 = N, 90 = E, which is also `Printer_Plane.PrintPlane`'s rotation sense); every spawned pawn has a
   `Pawn_FilthTracker`; the race filth gates and the `Flying` return are INSIDE the body, so a postfix
   sees humanlikes, animals, mechs and entities. No second hook. A teleport (`Position` set directly,
   not a path step) lays no print: by design. Several consumers may tag one def (each with its own
   optional `biomes` filter); the first extension whose filter matches the map wins.
3. **Invisible pawns are recorded too** (turn-4 IN, *unseen things leave prints*): no filter on
   `HediffComp_Invisibility` / `IsPsychologicallyInvisible`. The grid is how the planet answers every
   invisible hunter (the murrek, the drum-lure swimmers, Anomaly's). The record is **flagged**
   (`RM_TrackRecord.Invisible`, the style's top bit, so the save format did not change); the flag never
   changes eviction. A surface may set `invisibleTexPath` to draw an invisible walker differently (the
   Stillsand: a submerged swimmer leaves a wake trough, not feet); null keeps its ordinary print.
4. **Draw:** one custom `SectionLayer` printing a rotated print sprite per record, rebuilt only for
   dirty sections (precedent: MovingDunes' `SectionLayer_DuneSand`). Sprites per **print class** set on
   the extension: human, animal, large, drag, plus per-race overrides (the Stillsand's oommok print and
   crawler tread, already queued, become override sprites rather than filths).
5. **Erase API:** `ClearCell`, `ClearRect`, `ClearAll`, and a batched **downwind sweep**
   (`BeginDownwindSweep(deg)` + `SweepStep(n, onCell)`, resumable across a save). Mesh dirtying skips a
   section not created yet (MessyConduit's measured NRE during `RegenerateEverythingNow`), so an eraser
   may run during map load. `RecordPrint(cell, pawn, surface)` is public for a comp that lays a print
   off the entry path (a wake). Each biome brings
   its own eraser: the Warscar's wind (`WARSCAR_SETTLING_WEATHER_1`), the Stillsand's dunes engine
   (a cell whose sand depth changes past a threshold clears).
6. **Mod Settings:** tracks on/off (labelled the performance switch), pool cap, print opacity.
7. **Consumers (XML only):**
   - **Stillsand** (wired): `src/RimMandrake/Stillsand/Patches/RM_TrackSurface_Stillsand.xml` puts the
     extension on `Sand` and `RM_DeepSand`, `biomes` = `RM_Stillsand` (both are shared terrains),
     `invisibleTexPath` = the drag placeholder until wake art exists. Its eraser (drift depth past a
     threshold clears a cell, from `MapComponent_DuneField`) is NOT wired: Stillsand prints persist
     until the cap evicts them.
   - **Warscar** (not wired: `RM_Filth_SettledFilm` does not exist yet, it is
     `WARSCAR_SETTLING_WEATHER_1`'s): the film filth carries
     `<li Class="RimMandrake.CreatureBehaviors.RM_TrackSurfaceExtension" />` in its `modExtensions`, and
     the Settling's end calls `BeginDownwindSweep` + `SweepStep` from its own tick.
8. **State window for tests:** `RM_TrackGridDiag` (public static session counters, never saved), read
   through `jawa/mod_settings_field action=list`; no new bridge tool.

### assumed (no ruling; record and revisit)
- Cap default 6,000 per map, slider 1,000-20,000; size classes: small < 0.65, medium < 1.5, large < 3,
  huge >= 3 (bs). The small-animal tier is `Animal` source AND small; a small mech is tier 1.
- Flying pawns lay nothing. A pawn's print overwrites the cell's older print (one record per cell).
- Persisted, not transient: tracks are evidence the player reads after a load (the item says "saved").
  A save carries `RM_MapComponent_TrackGrid`, so removing CreatureBehaviors from a save logs the usual
  missing-class error (it is a hard dependency of every biome that uses it).
- Placeholder sprites (`Textures/Things/Tracks/*`, 4 PNG); real art is queued in artpipe.

## criteria

- 6,000+ pawn-steps on a surface leave exactly the cap in records; humanlike and bs ≥ 1.5 records
  survive a flood of small-animal records.
- A dev-spawned invisible pawn crossing a track surface leaves prints (state read on the grid).
- Save/load round-trips the grid byte-identical; no `Thing` count change from printing.
- The Stillsand and the Warscar each drive the grid with XML only plus their eraser call.
- An invisible walker's records carry the invisible flag; a gravel control walk lays none; tracks off
  lays none.

## verify

- Offline: `python3 src/RimMandrake/Utils/selftest_track_grid.py` (C# on the real `RM_TrackPool.cs`:
  cap, eviction order, overwrite, clears, resize, sweep order, invisible flag count under
  eviction/resize/clear, byte-identical save/load, 200k-step perf) -> must print `OK n/n`.
- Build: `python3 src/RimMandrake/Utils/winbuild.py CreatureBehaviors` -> 0 warnings, 0 errors.
- Patch: `validate_patch.py src/RimMandrake/Stillsand/Patches/RM_TrackSurface_Stillsand.xml` against
  the installed game -> 0 errors (the add-if-missing warning is intended).
- Live (owed, needs a deployed run): `src/RimMandrake/CreatureBehaviors/validation.py` chain
  `track_grid` on an RM_Stillsand map (the Stillsand suite's `site` chain builds one): components
  `writer_patched`, `walker_lays_prints` (gravel control), `invisible_walker_recorded_flagged`
  (Royalty `PsychicInvisibility`), `toggle_off_no_prints`. On any other map the walking arms read
  UNMEASURED by design. Not covered live: sprite appearance, the erasers (none wired).
