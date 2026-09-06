# FUNGALFOREST_RAID_MERGE_1 — dissolve BMT_FungalForest into its neighbors; ingest its content into the Rot

Owner ruling 2026-09-06: no basement biome — "raid this biome for its cool contents… then
merge this biome with its neighbors sensibly and in a nonbullseye manner."

## spec — the merge (MEASURED per cluster: region × 30° sector, the dominant OTHER biome in
the same region within ±6° of arc)
| cluster | tiles | arc | receiver |
|---|---|---|---|
| Sporefields, sector 2 | 85 | 94 | **the Rot** (`AB_MycoticJungle`, 130 neighbors) |
| Nightspill, sector 7 | 69 | 118 | the Rot (236) |
| South Crags, sector 8 | 62 | 119 | the Rot (38) over Wasteland (37) — split by local majority per tile |
| Sweatwood, sector 7 | 44 | 81 | the Rot (45) |
| Nightspill, sector 6 | 38 | 118 | the Rot (235) |
| Stillwood, sector 3 | 33 | 128 | the Rot (88) |
| Frostcaps, sector 3 | 30 | 122 | the Rot (129) |
| South Crags, sector 9 | 16 | 124 | **the Wasteland** (67; the dissolved ring 58 goes to its own receivers) |
| Stillwood, sector 2 | 16 | 130 | the Rot (93) |
| Blindwood 5 · Stepwood 7 · Hanging Wood 9 | 26 | — | the Rot |
- Every cluster takes its own neighbors — the merge follows the terrain map, adds no
  ring (the Rot already sits in 7 sectors as lobes; it grows by ~400 tiles). Re-count
  the Rot's sector coverage after painting and record it.
- Re-biome via world tools + `world_commit`; re-freeze; back up Saves keepers; render for
  the owner before painting (patch-a-curated-artifact rule).

## spec — the raid (`the_rot.md` §7b)
- Ingest the spore kit (DamageDefs, SporeCloud incident/condition, SporesBuildup,
  SporeFlesh, thrumbungus, mantis scythe), materials/terrains (mushroom leather, bridges,
  mycelial soil/matting), buildings (fungiponics, fungal torches), research row, drugs
  (ambrosyx), flora (marsh fungi, Skultop, morel, inkcap…) — as OUR defs under the tier
  grammar (`RSW_`/`RUT_`), art referenced by texPath per the absorption precedent;
  Cherry Picker the originals if the mod stays installed.
- 🔴 Ruled 2026-09-06: blastpod→chemfuel ingested WILD-ONLY (no sow tags for Jawa; may be
  cut later if hokey); the fungal power generator (`BMT_FungalPowerGenerator`) is CUT —
  do not ingest, Cherry Picker it if the mod stays installed.
- Fauna admission at `BIOME_FAUNA_ASSIGNMENT_SITTING_1` (hybrid-or-out list in §7b).
- Verify the Skultop's actual defName (UNMEASURED in 1.6 defs) before citing it.

## verify
CSV re-count: 0 `BMT_FungalForest` tiles; receivers as tabled; the Rot's sector coverage
recorded; ingested defs resolve in the dump; the owner has ruled the two flagged chains.
