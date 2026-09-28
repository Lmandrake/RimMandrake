# STILLSAND_RULED_CONTENT_1 — build the Stillsand content the 2026-09-27 sitting ruled

Authority: `design/Jawa/worldbuilding/biomes/stillsand_bedazzle_2026-09-27.md`
**§ Rulings** (beats §7's recommendations). Sitting: `STILLSAND_DESIGN_SITTING_1`.

## spec — ruled and buildable now

1. **Tier move, all nine rows** (§2b): kudda*, ikee, vozzik, pikkut*, vekka, drazzik,
   qorrax (ThingDef out of `Absorbed_Cephaloids_Defs.xml`), light-pipe nub, ollim
   (+`RM_OllimWood`) into `RM_Stillsand` proper, `RM_` defNames.
   *kudda and pikkut then CUT from this biome's wiring — their one home is the Long
   Shade (ruled); they move tiers there, not here.
2. **Names ruled**: mirror giant → **`RM_Oommok`** "oommok"; dust husk → **`RM_Siidda`**
   "siidda". **vekka KEPT** (owner's call — do not swap to shakkir). Fix the two def
   headers citing the never-filed `STILLSAND_SHIPPING_NAMES_1`: the names are now
   ruled here.
3. **Roster per rulings**: kreetle and gizka STAY (kreetle one home here; gizka
   Pyrelands+here per 2026-09-14). Depth-arm annotation onto the roster notes:
   subsurface passes at any size — nothing mid-band evicted.
4. **Sizes**: ikee bodySize back to grain (~0.15, was ported at 0.4 vs approved 0.13);
   spined-gow (AA_SpinedGow, aurrok) grown to bs ≥4 and wired at ~0.15 commonality.
5. **Dunes engine**: add `RM_Stillsand` + frozen `RUT_ExtremeDesert` (until Phase B) to
   `mandrake.rm.movingdunes` `Patches/BiomeBindings.xml` (today it binds only vanilla
   Desert/ExtremeDesert — inert on Ash'karr). Check the light-pipe nub has a biosilica
   harvest item; add if missing (UNMEASURED at filing).

## Watch out

🔴 Owner, typed 2026-09-27: **"Dune Sea is a region, not a biome. Be careful!"** — the
Dune Sea is a REGION/campaign label over `RM_Stillsand` tiles (same law as Umbra).
Never create a Dune Sea BiomeDef, roster, or def-level split. Deep-sand terrain work is
`DEEP_SAND_WALKABLE_TERRAIN_1` — "muchly" of it lands in this biome.

## ⛔ NOT here — gated on the owner's review sheet

The commissioned roster fill-out ("More!") and the qorrax art: designs + renders go to
the owner's sheet first; defs land after verdicts.

## verify

Standalone `RM_Stillsand` on a minimal list loads clean; validate_patch.py clean;
dunes engine active on it; ikee/gow sizes as ruled.

## criteria

The free-tier Stillsand meets the stands-alone bar and every 2026-09-27 ruling is in
the defs.
