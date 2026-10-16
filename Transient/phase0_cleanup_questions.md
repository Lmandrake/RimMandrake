# Phase 0 cleanup (owner order 2026-10-15): decisions I did not take

Measured on the non-frozen `src/**/Patches|Defs` XML, donor-name xpaths (a `defName="X"` where X is a name the donor defines):
6,288 before, 2,704 after. 1,594 of the 2,704 still have a twin of ours, 1,110 are donor-only. The files I was told to clean
are done; the biggest leftovers are below.

## Q1. The big generated donor-name patches I was not asked to touch

`BiomeCastEvictions_WildBiomes.xml` (1,852 donor xpaths), `AnimalBiomeDuplicates_Generated.xml` (382), and the rename patches
`RotSpecies_NamesAndSizes` (69), `Contagion_Rename` (62), `CreatureResize_Ashkarr` (47), `Slime_Rename` (45), `Waterline_Lane1` (42),
`Abyss_Rename` (38). All match nothing once the donors are gone.

- **A. Run the same migrator over them** (`design/Jawa/mods/retarget_donor_patch.py`, about an hour including checks). Trade-off: the evictions
  were stopped by your ruling ("Let's stop evictions right now"); retargeting them to our twins would re-enact edits to rosters.
- **B. Delete the eviction files outright** since donor rosters vanish with the donors. Trade-off: loses the record of what was evicted.
- **C. Leave them until the repaint.** Trade-off: gate 1 stays green by letter but not by spirit; they log nothing either way.

## Q2. Seven patch files still gate on "Alpha Animals" by NAME

`Ikee_Tuning`, `Ikee_Rename`, `Turrets_DamageDoctrine`, `RM_AlphaAnimals_DeathBursts`, `AA_Aerofleet_TwilightSea`,
`AA_ShockGoat_NightsideIce`, `RM_LanternDeepIncidentSuppression`. Your list named only the Star Wars collection, so I left them.
The migrator dry-run is clean on all seven (retargets to our twins or drops donor-only ops).

- **A. Migrate them now** (minutes). **B. Leave until P7 removes the donor from the list.**

## Q3. Three generated files no longer reproduce from their generators

`MegafaunaYield.xml` (the generator now emits 9,229 lines against the committed 11,390 and wants `Alpha Animals` back in the Doctrine
loadAfter), `Armour_Leather.xml` (a dry run emits 98 ops against a file of 3,095 lines), `PawnFlavorPhase2_ThoughtDef.xml`. I migrated them with
`retarget_donor_patch.py` and noted it in their headers. A re-run re-emits donor names.

- **A. Hand-maintain them from here** (stop calling them generated). **B. Call the migrator at the end of each generator** (small change, keeps
  the claim true). **C. Rebuild the generators against a fresh dump** (a day; not recommended before the paint).

## Q4. `plant_tolerances.py` cannot write by itself

Its name map is fixed (it now emits our `RSW_`/`RM_` names), but `verify()` refuses to write on the stale 2026-10-04 `defs.sqlite`:
`RUT_Dewshrooms` and 13 other Rot rows name plants that no longer exist under those names, so 15 landed rows "cannot grow". I did not
fake the verdict; the committed `PlantTolerances_Ashkarr.xml` was retargeted by the generator module's own `retarget` mode instead.

- **A. Fix the Rot roster names and rebuild the dump** (needs the game up for a capture). **B. Retire the generator** and let each biome mod
  own its plants' bands. **C. Keep as is** (retarget mode only).

## Q5. Five render families still read as the snail slime

`slime_hennul`, `slime_thummorak`, `slime_vohhm`, `slime_wuppik`, `slime_yollum` still name-match the token `slime` to
`RSW_Filth_Snail_Slime`. Their donors (`AA_Mime`, `AA_OvergrownColossus`, `AA_TeratogenicOriginator`, `GR_Chickenrabbit`, `GR_Manbear`) are not
ported, so there is no subject of ours to bind them to. **A. Leave** (they resolve when a twin exists). **B. Bind them to a dummy "unported"
subject** so no review ever offers them as filth art.
