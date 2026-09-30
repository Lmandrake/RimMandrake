# CONTAGION_RULED_CONTENT_1 — resume notes (2026-09-30)

## Roster measurement (python ET parse, repo AND deployed Mods/RimMandrake.Biomes copy — identical)
- wildAnimals: 22 rows, 0 `<li>`, 0 donor (AA_/AB_/AG_/GR_/RUT_Sytheclaw), all 21 ruled names present at ruled
  commonality (Ikee as RM_ContagionIkee 0.6). Extra: RM_Ogleknot 0.3 (separately ruled, OGLEKNOT_CREATURE_BUILD_1).
- wildPlants: 13 rows, 0 `<li>`, 0 donor, all 12 ruled flora present at ruled commonality. Extra: RM_RustPuff 0.3 (kept by ruling).
- animalDensity 3.0, plantDensity 0.35 explicitly set.
- All 22 fauna have ThingDef + PawnKindDef; flyers Blisterfloat/Sparkleech/Skinflap/Gorekite carry MaxFlightTime>0; Gawpsack none (grounded, ruled).
- No flora yields food (harvest: WoodLog / RM_RedSap / RM_SeedFistFertilizer / RM_WombpodSac / none).

## Gap found
Genome-loop host still `AA_RedGoo` (AmoebaHostUtility.HostDefName) and RM_WombpodSac hatches AA_RedGoo under
MayRequire sarg.alphaanimals — the donor def the port replaced. With donor rows out of the roster, the loop's host no
longer spawns in the Contagion. Fix: retarget host + hatcher to RM_BloodyMess ("the body" port).

Done: HostDefName -> RM_BloodyMess; RM_WombpodSac CompHatcher -> RM_BloodyMess, MayRequire sarg.alphaanimals dropped;
settings text, About.xml and comments updated; DLL rebuilt (0 warn/0 err) with .srchash. NOT deployed: the composed
biomes deploy also carries unrelated Miasma/WeepingStones drift, so it waits for the next deploy pass.

## Criteria
| criterion | state |
|---|---|
| Donor defNames absent from RM_Contagion roster | MET, measured (repo + deployed) |
| Every ruled name present at ruled commonality | MET, measured 21/21 fauna, 12/12 flora |
| Shorthand form, densities explicit | MET, measured |
| 4 flyers carry flight stats, Gawpsack grounded | MET in defs (measured); live flight = state read, needs live pass |
| Wombpod harvest -> usable gestation host | wired offline (sac hatches RM_BloodyMess = HostDefName); needs deploy + live quicktest |
| Quicktest map spawns the new cast | needs live quicktest |
