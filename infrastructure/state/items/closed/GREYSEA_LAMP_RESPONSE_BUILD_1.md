Split from `GREYSEA_RULED_CONTENT_1` (ruling 8, Q12: deterministic and forgiving). Design: `design/Jawa/worldbuilding/biomes/the_grey_deep_danger_floor_pass_2026-09-27.md` §2.1-§2.2.

## spec
- Generalise the suulk-named gate on `RM_JobGiver_SeekGlow` to a per-race/per-sea setting; add a drawn-to mode (approach, linger near the light, wander off) beside the feed mode.
- Layer 1: `RM_Nissik`, `RM_Sallik`, `RM_Immu` drawn in. Layer 2: `RM_Fessk` stands at the rim of the light, never enters, never attacks, leaves when approached.
- Layer 3: `RM_Reefback` answers only worklight-class light (high glow radius, never a torch) after HOURS of steady burn on the same glower; telegraphed by the fessk and fresh scrape-sign; dowsing (glower off) always resets the burn clock. It breaks the lamp, never the ship, never the pawns.
- Mod Settings for each layer.

## verify
- Offline: race extensions present on the five races; reefback never targets a glower below the threshold. Live: a worklight burning N hours on a Grey map brings the watcher, then scrape-sign, then the reefback to that lamp; switching it off before then resets.
