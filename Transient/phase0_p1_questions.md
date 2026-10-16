# Phase 0 P1 (SWAC) - open owner questions and residue, 2026-10-15

## Q1. The Sarlacc landmarks: port, trim, or let the repaint settle it? (owner's call)

**DECIDED 2026-10-15 by card: A, port both.** Done: `RSW_DonorPack_Sarlacc.xml` (SWBestiary); renames table `Transient/phase0_sarlacc_save_renames.md`.

What still names the donor: `RUT_GapingDoom` (`src/RimUtinni/UtinniPatches/Defs/LandmarkDefs/RUT_GapingDoom.xml`) requires the donor mutator `sw_DeadSarlaccCave`
(`MayRequire="Mlie.StarWarsAnimalCollection" Required="True"`); two StructureInjectionsSW patches (`SarlaccRing.xml`, `WhisperSarlaccSign.xml`) append gen steps to the donor
`sw_SarlaccLair`; the canonical save holds `sw_Sarlacc` x8 and `sw_DeadSarlacc` x7 landmark defs. What a port would copy: the donor's `DeadSarlacc` MapPortal building
(12x9, pocket map generator `SarlaccCavity`, exit `CaveExit`), `sw_DeadSarlaccCave` (TileMutatorDef) + `sw_DeadSarlaccPit` (GenStep), `sw_Sarlacc`/`sw_DeadSarlacc` LandmarkDefs, `sw_SarlaccLair` + `sw_SarlaccPit`, and 15x15 art
(`swbuildings/Sarlacc_Dead`, which the donor owns). Our `RimStarWars/Sarlacc` mod is a different thing (swimmer / anchored mouth / cistern creature), it has no landmark.

| option | what happens | trade-off |
|---|---|---|
| A. Port both landmarks (dead cave + live pit) as `RSW_` defs | Gaping Doom, the ring and the whispered sign keep working; save landmark defs get `RSW_` names | Biggest job: a pocket-map generator, a 12x9 portal building, 15x15 art to commission, and the save's 15 refs need renaming. Most faithful. |
| B. Port only the dead cave (`RSW_DeadSarlaccCave` + portal + `SarlaccCavity` map) | Gaping Doom works; Sarlacc ring/sign patches get retargeted to our own Sarlacc mod or dropped | Half the job; live pit landmark (`sw_Sarlacc`) is lost, so its 8 save refs vanish at the repaint |
| C. Drop the donor landmarks; Gaping Doom takes a non-donor mutator (a vanilla/Odyssey cave or junk mutator), ring and sign patches deleted | Cheapest; zero art | The Gaping Doom stops being "a dead sarlacc used as a waste pit" in mechanism (its text still says so); no enterable cavity |

Why I did not decide: it is content (a dungeon) and art, and it changes what the Gaping Doom IS. Nothing blocks on it except gate item 2 (one `MayRequire` remains, in a frozen-adjacent `RUT_` landmark) and gate item 4 (save refs).

## Q2. Is a second nest in the Webwork wanted? (low stakes; I acted, you can revert)

The Webwork mod already ships `RM_Webwork_NestWall` (the mother's guardian spawner, `RM_Ollathrix`, with its own gen step). `RUT_Webwork_Nest` (Shokkweave Economy) was a second, campaign-side nest whose guardian was the donor Wyyyschokk.
Because owner ruling 2026-10-03 says `RM_Ollathrix` IS the wyyyschokk, I repointed the guardian to `RM_Ollathrix` and rescaled its spawn budget 600/1200 -> 160/320 points (the Ollathrix kind's `combatPower` is 160, so the nest keeps "one guardian, room for one more"). Options if you do not want two nests: (a) delete `RUT_Webwork_Nest` + `RUT_WebworkNestScatter` + its patch + the settings text, (b) keep as is.

## Residue the SWAC gate still sees: CLEANED 2026-10-15 (Phase 0 cleanup)

Done: the generated tolerance/flammability patches key on our names (`design/Jawa/mods/donor_name_map.py` is the donor-to-ours map the
generators and `retarget_donor_patch.py` read), MegafaunaYield / TrophyCraft / PawnFlavor thoughts / BeastNorm_Law3 `tools` ops retargeted or deleted, all
ten donor-NAME `FindMod` gates removed (ten files; four emptied files deleted), `loadAfter` lines for both donors removed from 20 About.xml.
What is left and the options: `Transient/phase0_cleanup_questions.md`.

## Art owed before SWBestiary is deployed

Four renders are filed to the artpipe (`design/RimMandrake/swac_p1_art_2026-10-15.json`): hydenock tree, jogan tree, tooke-trap plant (canon entry `tooke_trap_plant`), raw jogan fruit. Until they install, the four new defs in `RSW_DonorPack_P1_Plants.xml` have no texture: do not deploy SWBestiary past this commit before they land. Immature and snow-overlay art reuse the mature render.
Also: `RSW_Plant_Nysyllin_Wild` still draws `swplants/Nysillin` (donor-owned pixels); its redraw is already filed (`nysillin_redraw_v2_2026-10-15.json`).
