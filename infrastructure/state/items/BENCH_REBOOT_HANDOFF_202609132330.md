# BENCH reboot handoff — 2026-09-13 23:30 local (2026-09-14 UTC), mid-Pyrelands-walk

Owner said "prepare for agent restart" DURING the walk restart cycle. State is
live; the successor picks up mid-sequence. Read this top to bottom before
touching anything.

## THE ONE THING IN FLIGHT RIGHT NOW

Game is RELOADING on the 98-mod walk list. A background script in the dying
session fires `rimworld/load_game {"saveName": "PYRE_WALK_20260914"}` once the
bridge answers — it may already have run. **Successor's first acts:**
1. `./game` to measure; wait for UP if needed.
2. Confirm the save loaded (jawa/list_pawns works, colonists Takeru/Buckley/
   Nicole exist). If load never fired, fire it yourself: saveName
   PYRE_WALK_20260914.
3. Then the CACHE-BUST REGEN: debug actions
   `Actions\Leave settlement now (test harness, tears down this map)` then
   `Actions\Re-enter settlement here (test harness, needs one already created)`
   (8s apart, fresh connections). Tile 104504 is committed RM_FE_Pyrelands in
   that save; after a RESTART the session tile-cache is fresh, so this regen
   should finally produce a TRUE Pyrelands map (the pre-restart attempt made a
   chimera: mapBiome Pyrelands, content TemperateForest — engine caches tile
   biome per session, `jawa/map_info`'s own doc warns exactly this).
4. VERIFY before announcing: `jawa/map_info` mapBiome == RM_FE_Pyrelands AND
   center cells' terrain in the RM_FE_* family AND
   `jawa/list_things {"defName":"RM_FE_Plant_EmberGrass"}` count > 0.
   LIES: if it's STILL temperate after a fresh-session regen, the cache theory
   is wrong — stop, investigate, do not loop restarts.
5. Then respawn the review roster (the owner walks it): the spawn list and
   grid pattern are in this session's PYRELANDS_CREATURE_RERENDER_1 flow —
   59 kinds, jawa/spawn_pawn faction "none", GR_Mantistanis fails (likely VGE
   submodule setting, unresolved). Daylight: step_game_ticks to morning.

## Today's MAJOR RULINGS (all recorded as data, all pushed)

- **ART_PAINTERLY_RESTORATION_1** — the big one. Painterly wave-4/5 style
  restored (Ronto exemplar prompt inside done/ronto_v1_east.json), cartoonish
  toy-figurine pipeline stood down, legibility gate DEMOTED TO ADVISORY (the
  daemon was relaunched with ARTPIPE_LEGIBILITY_THRESHOLDS= empty, PID was
  2105912), 256 ceiling dead (resexp is UNMEASURED under the stack's enhanced
  zoom), every cartoonish-era render owed re-examination and re-ruling.
  Propagation debt listed in the item — README/fill_queue/artpiped edits NOT
  yet done.
- **ARTPIPE_FACING_COHERENCE_1** — N faces away, S faces toward, facings
  derived from one master; hook mandatory; "can't call it done until that's
  true"; broken everywhere today. Survives the style reversal.
- Review tier: small-modlist in-game load is a standing art-review tier
  (LESSONS_INBOX + review-tiers memory).

## Walk verdicts already ruled (recorded in PYRELANDS_CREATURE_RERENDER_1)

Bolotaur DONE · Gualaar DONE · AA_GreenGoo praised (study the wiggle —
LESSONS_INBOX) · Crystalline wall mystery solved: Biomes! Caverns crystal
stuff on a vanilla wall.

## State of the push (all committed AND pushed, main = artpipe-sync commit)

- 98-mod walk ModsConfig LIVE (scratchpad stage file also exists);
  FULL.LATEST = 631 incl. all 61 override mods — restoring full list keeps
  the art. MW2 stays cut.
- All backlog art installed: 47 flora overrides in UtinniPatches, 61 override
  mods on disk, SWBestiary natives, Pyrelands flora identity (5 defs OWN
  texPaths now, deploy hold LIFTED, all deployed). Iriaz/Nuna override mods
  exist but are NOT in the live ModsConfig (created after the list was
  written) — add them at the next list touch.
- Deploy: my 46 mods verified in sync; NOT deployed (other seats' work, left
  alone): Bacta, StructureInjectionsSW, EnvironmentalHazards, LanternDeeps,
  ManyWaters, ShipShields.
- Bridge: HELD by BENCH for the walk. FOUNDRY is offline-only (owner ruling
  today). If you are the successor BENCH, carry on; the 45-min staleness rule
  frees it if you are slow.
- Artpipe queue EMPTY; daemon must be RUNNING with the gate env EMPTY —
  verify with pgrep -af artpiped and re-launch per ART_PAINTERLY_RESTORATION_1
  if the reboot killed it (it is a WSL process, it survives agent restarts,
  not machine reboots).

## Traps re-paid today so you don't

- zsh does not word-split unquoted vars — a for-loop over a $var of lines runs
  ONCE (cost a silent 0-mod deploy pass AND a Nuna misname).
- drvfs serves stale reads — an ls after rm showed deleted files still there.
- The owner's screenshots land in Steam userdata (F10), newest by mtime.
- start_debug_game_ready on this list ≈ instant; bridge up ~75s post-launch.
- The engine tile cache poisons re-generation within a session (the chimera).

## Open questions for the owner mid-walk

- The 7 Pyrelands invented creatures + canon 5 are CARTOONISH-era renders now
  on re-rule row; he may order painterly re-renders of the whole set.
- The magenta WORLD map on the walk list (world layer material, all-
  TemperateForest scratch world) — cosmetic here, unexplained, unfiled.
- Non-roster wildlife will appear on the Pyrelands map via donor wildBiomes
  self-injection (34 SWBestiary defs alone); eviction patch does not cover
  RM_FE_Pyrelands. Roster purity is a design question for the biome sheet
  loop, not a bug fix to freelance.

HANDOFF READY
