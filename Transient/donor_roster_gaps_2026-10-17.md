# Roster gaps RM_Bileworm (Cauldron, Miasma) and RM_Zrrik (Greentide): proposal only, NO roster edited (evictions are stopped)

Both gaps are one wrong GUARD, not missing content. The defs exist and spawn elsewhere.

## RM_Bileworm in RM_Cauldron and RM_Miasma
- Def: `src/RimMandrake/Scarlands/Defs/ThingDefs_Races/RM_Bileworm.xml` (the Warscar member, now inside `mandrake.rm.biomes`; its standalone id was `mandrake.rm.warscar`).
- The rows exist: `src/RimMandrake/Cauldron/Defs/BiomeDefs/RM_Cauldron.xml:150` and `src/RimMandrake/Miasma/Defs/BiomeDefs/RM_Miasma.xml:264`,
  both `<RM_Bileworm MayRequire="mandrake.rm.scarlands">`. **No mod ever had packageId `mandrake.rm.scarlands`**, so the row is dropped on load, donors or not.
  Same typo in `src/RimMandrake/Utils/aa_port.py:445` (the port map that wrote them).
- Needs (at his sitting): delete the `MayRequire` attribute on those two rows (Cauldron, Miasma and Warscar are the same composed mod, so no guard is needed),
  weights stay 0.1 / 0.1; fix `aa_port.py` to `mandrake.rm.biomes`. Then rerun `ROSTER_RM_Cauldron` / `ROSTER_RM_Miasma`.
- Related, not part of this gap: campaign layer still casts the DONOR `AA_Helixien` (guarded by `sarg.alphaanimals`, harmless once the donor is gone) in
  `UtinniPatches/Defs/BiomeDefs/RUT_Cauldron.xml:147`, `RUT_Miasma.xml:240`, `RUT_Slime.xml:89`, `RUT_Contagion.xml:130`; `Warscar_Rename.xml` still renames it.
  Those four become RM_Bileworm rows (same weights 0.1/0.1/0.075/0.1) or are deleted when the donor retires; that is a roster edit, his call.

## RM_Zrrik in RM_Greentide
- Def: `src/RimMandrake/Greentide/Defs/ThingDefs_Races/RM_Zrrik.xml` (port of AA_BloodShrimp), in the Greentide member.
- The cast row lives ONLY in `src/RimUtinni/UtinniPatches/Patches/WildAnimals_Greentide.xml` (~line 57-75), inside `PatchOperationFindMod` **`sarg.alphaanimals`**
  (the donor). With the donor off, the whole block is skipped, so `RM_Greentide` never gets Zrrik (weight 0.2). `RM_Greentide.xml` `<wildAnimals>` (line 172) has no Zrrik row.
- Needs: move `<RM_Zrrik>0.2</RM_Zrrik>` into the BiomeDef's own `<wildAnimals>` (no guard; the def is in the same mod), then delete the donor-gated block.
  Check first whether the donor-gated block carries other rows for the same FindMod (it does not in the lines read; confirm at the sitting).
- Risk: a shrimp-like channel predator at 0.2 enters a roster whose animal is "one biome" per owner rule; confirm Greentide is Zrrik's single home.

Verify after: `jawa/biome_probe find=RM_Bileworm`/`RM_Zrrik` on the donor-off tier (needs the game; not run here).
