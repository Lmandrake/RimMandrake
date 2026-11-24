# History: evidence and old lines that left `SKILL.md`

The lessons are in `../SKILL.md`. This file holds only the old lines that are no longer true. Git holds the rest. Each
line below is a record, not a rule. Every correction below is of 2026-11-23.

## The helper and the shot

- The skill once called the paused barrier for a settled shot PLANNED (item `SHOTSETTLE_BUILD_PAUSED_BARRIER`). The tool
  is `jawa/settle_tweens`, built 2026-11-05 at 044b33fa8c. A live run passed on 2026-11-06.
- §2 once pointed at §4 for plants, weather and ash drifts. §5 holds them.
- Before 2026-11-23, `--daylight` stepped seven chunks of 2000 ticks and read no hour, and `--two-pass` set no weather
  before its `_clear` shot. An older `_clear` picture can show any hour and any weather.
- §1 once said that `--kill-hostiles` clears every hostile. The code stops after six rounds and reports what is left.
- Before 2026-11-23, `--clear chunks` destroyed every loose item in the rect (its category was Item).
- §5 and §8a both told the two traps of 2026-09-18 (`rimworld/take_screenshot` ignores `x`/`z`/`zoom`; the debug log
  window). §5 now holds them.
- §8 once said that `resolve_endpoint` scrapes the endpoint from Player.log. Player.log is now one of several sources.
- §8 once called the xenotype grid one pawn per XenotypeDef; `--per` now puts 3 side by side. §8 also told the reader to
  swap the mod list back after a load. There is no such step now (root `CLAUDE.md` §Facts you cannot guess).

## Generated maps (§3)

- §3 once said that every map of `jawa/world_tile_map_generate` is a non-home **Settlement** map. Since 33854f6f5c
  (2026-11-05), the call makes a settlement of the player on a tile with no map parent.
- §3 once said that spawned colonists make the map a player home map (owner, 2026-09-17). They only block its removal
  (`MapPawns.AnyPawnBlockingMapRemoval`). The heading of §3 stays, because the rewrite keeps each heading. §3 also
  said that a downed colonist un-homes the map (2026-09-18). The 1.6 source counts each colonist that is not dead. The
  memory file `generated-map-culled-unless-home` that it named is gone.
- §3 once said that the map renders stale until you call `jawa/map_commit`, because `RegionAndRoomUpdater` is off and
  meshes never invalidate (2026-09-18). The call now runs that sequence itself (2b235a8960, 2026-09-19).
- §3 once said that there is no bridge route that enters a tile-generated map the way a player does, and that any such
  review is blocked. The companion has `jawa/settlement_attack`, untested for this; only a map that renders black
  blocks a review.

## The clock (§8b)

- §8b once gave `jawa/time_set_ticks` with no refusal. The companion now refuses it while
  any loaded map holds a spawned free colonist. §2 gained the pointer to the long-advance rule on the same day.
