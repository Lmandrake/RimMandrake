## spec
Spawn each biome and photograph what actually grows, normalize before adjusting,
and identify the rainbow prolific unclickable bushes the owner keeps seeing.

## finding: the def-level fix already landed, and it worked
`BiomeFlora_Ashkarr.xml` (a later, unrelated authoring pass — `biome_flora.py`,
commits `32f9d25d`/`9574513a`/`e0983a4f`, 2026-09-08/09) already replaces
`wildPlants` wholesale for Desert, ExtremeDesert, AridShrubland and
AB_RockyCrags. Live `jawa/biome_probe` on a freshly-restarted process matches
the patch file byte-for-byte: Desert 5 plants, ExtremeDesert 2, AridShrubland
10, AB_RockyCrags 8 (no frost/tundra flora) — **zero** VCE succulents or GRim*
recolors in any of the four. The 2026-09-06 note claiming DESERT_PLANTS_SCRAGGLY_1
"was specced but never executed" was itself reading a stale process (the note
says so); a fresh process shows the fix is in and matches disk.

## finding: the def fix cannot touch an already-generated map — and that's what he's seeing
The live campaign map (`AridShrubland`, tile 16869, the actual colony) was
generated before this patch existed. A `wildPlants` commonality patch only
steers FUTURE map generation and growth reseeding — it does not retroactively
remove or reweight plants already placed as Things. Full plant census of the
current colony map (`jawa/list_things`, group=Plant, 4,244 things):
**hundreds of off-roster plants absent from the current 10-item AridShrubland
roster** — the `GRim*` bush/berry/shrub-low recolor family (700+ combined:
GRim1/2ShrubLow, GRimShrubLow, GRimBush family, GRimBerryBush family,
GRimBushPoplar family, GRimClivia, GRimBrambles), plus `VEE_Gorse` (264),
`VEE_Heather` (196), `VEE_Plant_JuniperBush` (153), and a long tail of
`VEE_*`/`RG_Plant_*`/`ZBiome_Plant_*` decorative flowers. This — not a live
def bug — is what the owner is seeing: **the map is old, the def is new.**
Confirmed by the owner's own live screenshot (07:21 PDT 2026-09-10): a sharply
rectangular, densely-packed rainbow patch, consistent with pre-fix wild growth
rather than a colonist-sown zone.

## finding: "unclickable" is normal ground-clutter behaviour, not a bug
`GRim1ShrubLow` and `GRimClivia` (both heavily represented on the live map)
read `selectable: false` off `jawa/get_defs` — but so does **vanilla**
`Plant_ShrubLow` and `RG_Plant_AridGrass`. Low ground-cover plants are
deliberately unselectable in RimWorld; the GRim recolors inherit the same
convention. Nothing to fix here — the "unclickable" complaint is the density
and rainbow variety of clutter, not broken click targets.

## finding: Rose of Rebirth is a THIRD, unrelated mechanism — filed separately
476 `RotR_RoseOfRebirth` on the live map, flagged independently by the owner
mid-session. Its ThingDef (`Romance On The Rim`, `telardo.romanceontherim`)
has `plant.wildClusterWeight = 0` (cannot wild-spread) and empty `sowTags`
(cannot be sown via an ordinary grow zone) — the only two XML spawn routes are
the ThingDef itself and a `GenStep_ScatterThings` on a special "Riot Roses"
quest site (`countPer10kCellsRange 2~3`, nowhere near 476). The real spawn
route is compiled C# (`RomanceOnTheRim.RoseOfRebirth` / `CompProperties_
PlantableByWidowed`, tied to widowed-pawn/grave events) and needs a decompile
to pin down — see `ROSE_OF_REBIRTH_CONTAINMENT_1`, filed as its own item.

## verify
LIVE, on the fresh 2026-09-10 process: `jawa/biome_probe` (plants=true) on
Desert/ExtremeDesert/AridShrubland/AB_RockyCrags matches
`BiomeFlora_Ashkarr.xml` exactly. `jawa/list_things` (group=Plant) on the
current map's `perDef` census backs the "old map, new def" read. Both captured
2026-09-10 ~07:18-07:22 PDT.

## NOT chased (threshold discipline)
Did not spawn/photograph every OTHER biome on the planet (Grasslands,
TropicalRainforest, AB_MycoticJungle, etc.) — the owner's complaint and the
DESERT_PLANTS_SCRAGGLY_1 spec were both scoped to the desert/badlands family,
which is now fully verified both at the def level and against the live map.
Did not attempt to clean the existing campaign map's legacy flora — the owner
said explicitly: "We'll repair savegames later."
