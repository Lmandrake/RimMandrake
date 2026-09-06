# HORRORWASTES_BIOME_DISSOLVE_1 — remove the HorrorWastes biome from the frozen world

Owner ruling 2026-09-06 (`assailant_weapon_remnants.md` §Rulings 1): the biome leaves;
its tiles morph into their neighbors as usual.

## spec
- MEASURED: 1,711 `HorrorWastes` tiles — Deadstone 1,457, South Crags 93, Thornend 61,
  Rimewall 36, Gray Crags 21, Nightspill 20.
- Receiving def for Deadstone is RULED AT THE PROPANELAKES SITTING (its other occupants:
  AB_PropaneLakes 299, BMT_CrystalCaverns 194, IceSheet 49). Do not pick it unilaterally.
  Spill regions take their local majority neighbor per the standing band-repair method
  (`WORLDMAP_DESERT_BAND_REPAIR_1`).
- Re-biome via the world tools + `world_commit`, then re-freeze the savegame per the
  repair item's procedure; back up the Saves keepers first.
- Re-home the 29 legacy `design/Jawa/fauna/cast_assignment.csv` rows for this biome to
  the receiving def(s); mynock and neebray ride the icon carve-out.
- The Horrors *content* is NOT lost — it moves to `HORRORS_RAIDING_FACTION_1`.

## verify
`measure`/CSV re-count shows 0 `HorrorWastes` tiles; savegame re-frozen; cast rows moved;
no tile churn outside the 1,711.
