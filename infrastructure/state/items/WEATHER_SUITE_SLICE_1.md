# WEATHER_SUITE_SLICE_1 — tidally-locked weather, v1 slice

Green-lit slice of `design/Jawa/proposals/weather_suite_deep_design.md` (owner,
2026-09-01). Glass storms, static seasons, spore blooms, pressure tides,
mirages all WAIT for PROPOSAL_SUITE_REVIEW_1 — build ONLY the v1 ladder.

## spec

Per the doc's §1, §5, §8:
1. **Terminator storms**: the permanent weather WALL where dayside heat meets
   nightside cold — a fixed-geometry band (arc-distance from the substellar
   point decides membership; the world is frozen so the band is authorable
   as data, no simulation). Maps inside the band get the storm-wall weather
   set; crossing the band with the gravship is a felt event (warning letter +
   condition on the traverse). Nearly free once the arc-distance test exists.
2. **Dark-side auroras**: nightside-band WeatherDef, visual + mood event,
   almost no C#. The one beauty of the dark.
3. **Tier 0–1 forecasting**: folk signs (inspect-string tells on existing
   weather) + the instrument building that reads upcoming weather — every
   later weather system needs this reader; build it first.

## verify

(a) A map inside the terminator band draws from the storm-wall weather set and
one outside it never does — MEASURED by forcing weather rolls on both via dev
tools/bridge; (b) auroras occur only on nightside-band maps; (c) the forecast
building's prediction matches the actual next weather in a logged multi-roll
test; (d) validate_patch + clean Player.log.

## criteria

Band membership driven by authored data (tile list or arc test) with the SAME
fingerprint discipline as other derived artifacts; auroras and forecasts
observed live in a quicktest; no per-tick C# in any weather path.

## Watch out

- Biome weather commonalities interact with FIRE_ECOLOGY_LOOP_1's table edits —
  the two items patch NEIGHBORING data; coordinate xpaths so neither clobbers
  the other (both anchor on distinct `<li>` keys, never whole-node replace).
- The world map is FROZEN: the band is authored once against the real planet;
  never compute it from worldgen parameters (there is no worldgen).
- WeatherDefs with `isBad` affect caravan/incident logic globally — check what
  vanilla reads before flagging.
