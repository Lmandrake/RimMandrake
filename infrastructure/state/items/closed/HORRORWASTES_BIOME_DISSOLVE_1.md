# HORRORWASTES_BIOME_DISSOLVE_1 — remove the HorrorWastes biome from the frozen world

Owner ruling 2026-09-06 (`assailant_weapon_remnants.md` §Rulings 1): the biome leaves;
its tiles morph into their neighbors as usual.

## spec
- MEASURED: 1,711 `HorrorWastes` tiles — Deadstone 1,457, South Crags 93, Thornend 61,
  Rimewall 36, Gray Crags 21, Nightspill 20.
- 🔴 **Receiving defs RULED 2026-09-06 — the anti-bullseye LOBE MOSAIC** (`the_blue_desert.md`
  §0; the ring was MEASURED as all 12 bearing sectors ≥5%): by 30° bearing sector —
  **Blue Desert (`BiomeGRimond`) core in sectors 0, 7, 9, 10, 11**; 🔴 **RE-RULED
  2026-09-06 — `BMT_CrystalCaverns` is no longer a worldmap biome (`the_lantern_deeps.md`):
  the highland sectors 1, 2, 3 AND the former caverns' 578 tiles' HIGH ground (in
  3/4/5/8) go to the ICE SHEET — 🔴 ruled 2026-09-06: **our own def `RUT_NightsideIce`**
  (`NIGHTSIDE_ICE_DEF_1` authors it first; vanilla `IceSheet`'s 49 tiles repaint too; ⛔ no
  Bluefire second biome); the caverns' LOW tiles (7/9/10) join the Blue Desert core**;
  **PropaneLakes bulges up in 6**; arc excursions: Blue Desert lobes in 0 and 11 push down
  into 143–155, propane pushes up in 6. Produce the exact tile list from the sector
  census and **render it for the owner (`worldview.py`) before painting**. Spill regions
  take their local majority neighbor per the standing band-repair method.
- Re-biome via the world tools + `world_commit`, then re-freeze the savegame per the
  repair item's procedure; back up the Saves keepers first.
- Re-home the 29 legacy `design/Jawa/fauna/cast_assignment.csv` rows for this biome to
  the receiving def(s); mynock and neebray ride the icon carve-out.
- The Horrors *content* is NOT lost — it moves to `HORRORS_RAIDING_FACTION_1`.

## verify
`measure`/CSV re-count shows 0 `HorrorWastes` tiles; savegame re-frozen; cast rows moved;
no tile churn outside the 1,711.
