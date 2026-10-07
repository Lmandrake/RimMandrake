# BILEWORM_CORPSE_ROT_1

## spec
`RM_Bileworm` (Warscar, port of AA_Helixien) says in its description that anything it passes near "rots in
minutes into a black, reeking fluid, which the bileworm then happily drinks". The donor did this with two VEF
comps that were dropped at the port (WARSCAR_SHEET_DONOR_PORT_1), so the description was false.
`RM_CompBilewormGas` (`src/RimMandrake/Scarlands/Source/RM_BilewormGas.cs`) makes it true:
- corpses within 6 cells rot 40x their own clock, frozen or not;
- a rotting corpse within 1.9 cells dissolves into `Filth_CorpseBile`, and the worm's food need rises by body size x 0.5;
- a colonist's corpse dissolving raises a message;
- colonists within 10 cells get `RM_BilewormStench` (-3, renewed, never stacked).
Setting `bilewormGasEnabled` (off = an ordinary slug). Numbers PROVISIONAL.

## criteria
- A1 L0: Scarlands `validation.py` `bileworm_gas_problems()` passes (comp wired, radii nest, human corpse turns within a day, real filth, thought defined, setting gate, csproj).
- A2 L2: on a quicktest map a fresh corpse beside a spawned bileworm dissolves into corpse bile within a day; a colonist nearby shows the stench thought; with the setting off neither happens.
