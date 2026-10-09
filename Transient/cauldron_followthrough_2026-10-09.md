# Cauldron sheet follow-through — 2026-10-09

One line per TODO/conflict from `art.py enact` (8eaa2b252): what was done, evidence.

## TODOs
- AA_OcularJelly pick B (3 facings): new override mod `src/RimUtinni/OcularJellyArtOverride` (loadAfter sarg.alphaanimals), installed via `art.py install … --ruling cee4797f0e0dfd1d5f16`.
- AA_Plasmorph pick B (3): `src/RimUtinni/PlasmorphArtOverride`, ruling 080eb8b460c4178b8dd0.
- AM_Dryad_Corruptor pick B (3): `src/RimUtinni/DryadCorruptorArtOverride` (loadAfter sarg.alphamemes), ruling f4cf19902d45f267e962.
- AM_Dryad_Tumorous pick B (3): `src/RimUtinni/DryadTumorousArtOverride`, ruling b10fc06c28d5a6b1c1d0.
- GR_Beetlefleet pick B (east, south): `src/RimUtinni/BeetlefleetArtOverride` (loadAfter vanillaexpanded.vgeneticse), ruling 0bc5d894264bbaa0b3c6. North NOT installed — he ✕'d it (1353dead) and asked for a north regen; until it lands the donor north shows.
- Visceral pick B adult (3) + his C/D picks for VisceralBaby/VisceralTeen (6, donor pictures — standing rule: no donor art kept as donor, so our own copies): `src/RimUtinni/VisceralArtOverride` (loadAfter mlie.horrors), rulings c9fbfc688f6c0d771396 / 50a214bd2225e02cfa39 / f161a94418bfd74c9ec4.
- RM_TreeMartyr pick B: OUR def, Graphic_Random folder `Things/Plant/RM_TreeMartyr`; B installed over `MartyrTree_a.png` (ruling ffc7a3559d915aa7d294), `MartyrTree_b.png` (same rejected style) retired through the ledger.
- RM_TwistingThornwood pick B: same — over `TwistingThornwood_a.png` (ruling df968e719e90b2e540e3), `_b` retired.
- AA_OcularJelly note "move to the Contagion": roster line removed from `src/RimMandrake/Cauldron/Defs/BiomeDefs/RM_Cauldron.xml`, added inline (shorthand element, MayRequire sarg.alphaanimals, 0.5) to `src/RimMandrake/Contagion/Defs/BiomeDefs/RM_Contagion.xml`. NOTE: Contagion Wave A (CONTAGION_RULED_CONTENT_1) had ruled the donor AA_ cast out; this re-admits it on his word, said in a comment.
- AA_InfectedAerofleet (not a TODO, but part of his note "This creature should be moved to the Contagion" that enact marked followed by the redraw job alone): moved the same way. "Redo description" waits for the redraw (enact_d3c59886_infectedaerofleet_v1) — the description should describe the new art.
- AM_Dryad_Corruptor note: renamed **rhossak** (root-stag carrying splitting red seed-husks; LOOKED at pick B 33d2ed6f) — `src/RimUtinni/UtinniPatches/Patches/Cauldron_Rename.xml` (ThingDef label+description, PawnKindDef label).
- AM_Dryad_Tumorous note: renamed **galled rhossak** (root-flesh covered in fleshy galls and moss; LOOKED at pick B d292b376), tied to the rhossak; galls stay edible (donor mechanic). Same file.
- GR_Beetlefleet note: renamed **garsulix**, description from his note (keeps the donor's explode-on-death truth). Same file. North regen queued: job `enact_c8bcd172_garsulix_north_v1_north` (derive_from the accepted east render gapall_GR_Beetlefleet_v1_east, his note verbatim as owner_note), jobs file `Transient/enact_cauldron_sheet_2026-10-04_garsulix_north_jobs.json`.
- RM_TreeMartyr note "Redo name and description": our def — renamed **sarrowan** with a new description matching pick B (twisted rope-trunk rosette tree with a pale flower stalk), `src/RimMandrake/Cauldron/Defs/ThingDefs_Plants/RM_CauldronFlora.xml`. The frozen campaign twin RUT_TreeMartyr keeps "martyr tree".

## Conflicts
- RSW_VentStalker ×3 (pick C vs Kinrath override): CONFIRMED it shared `swanimals/Kinrath/Kinrath` with RSW_Kinrath. Gave it its own slot: def texPath -> `swanimals/VentStalker/VentStalker` (`src/RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_VentStalker.xml`), pick C installed at `src/RimStarWars/SWBestiary/Textures/swanimals/VentStalker/` (ruling 63e6a1304088fc48d4e6). Kinrath's override art untouched.
- RSW_VentStalker ✕ ×3 (478166/9a89a9/0acf8d, "owner-kept greentide"): he ✕'d the same three on the Greentide RSW_Kinrath row too; the only keeps were Greentide's same-row DEFAULT variant keeps (variants [A,B,C], variantsDefault) — the same bug class. Purged with release_keep (via cauldron decisions).
- Second ledger bug found on the way: a purge's `release` freed the WHOLE keep ruling, so purging one facing unprotected its sibling facings (20 unpurged pictures, 7 live, had lost their keep: Nuudal, Oobo, Pallu, Tikkarr, Cravvet, Skennet, Orray, PekoPeko). `Index.protected` now releases per picture; selftest in selftest_enact_selfpurge.py.

## Enact bug
- ROOT CAUSE: on --apply, step 1 ingest wrote owner KEEP rulings for the row's own pick column (GR_Beetlefleet: pick B incl. B-north 1353dead) and for a DEFAULT variant column on a redo row (AA_InfectedAerofleet: variants [B], variantsDefault, all three B pictures ✕'d) — ruling ids 0bc5d894264bbaa0b3c6, f23447ec2a9ccf1a612b. Step 4 then read those fresh keeps as protection. The dry run never writes ingest, so it planned the purges: dry ≠ apply.
- FIX: ingest.py drops ✕'d shas of the same row from pick/picks/variant keeps (a wholly ✕'d column gets no keep); enact.py never installs or protects a same-row ✕'d picture, and a keep minted by the same row of the same decisions file no longer blocks that row's ✕ (purge releases it). Selftest `src/RimMandrake/Utils/art/selftest_enact_selfpurge.py` (fails 8/10 on the pre-fix code, passes 10/10 after).

## Legacy unqueued
