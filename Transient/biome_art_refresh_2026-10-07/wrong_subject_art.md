# Wrong-subject art sweep (2026-10-07, BENCH helper)

Method: sha256 of every `src/**/Textures` PNG >= 2 KB (8,716 files); groups whose bytes are identical but whose subject stem
(facing / variant letter / RM_RSW_RUT prefix stripped) differs: 176 groups. Same-subject renames, gender/body-type heads, Flying_1
frames, Eopie/Togruta variants, Catch==Creature pairs were judged intentional and left out of the lists below. Judgement, not proof:
"same label" ports (Grellik/FungalWeevil, Gristle/Diggerpede, Liliana/AaroxisDendoria, Qorrax/cephalope, Ikee x3, Wildpod override) are NOT listed.

## Fixed: Kudda
- RM_Kudda_east (LongShade) and RSW_Kudda_east (SWBestiary) were sha 9e0e6c1d33b1 = `_artsrc/RM_PillarArmB_east` (white pillar limb). Introduced 2154ef2ea
  (2026-10-02 move); before that (dab5a10c4 / bbe171ebc / 502b24794) the east files were EMPTY (0-byte), never a real picture. south/north are real
  (96911a4a68db / 00bad92c05c3).
- The artpipe job RM_Kudda_east (2026-09-30, validated pass) holds a real render (cactus barrel body with spines and root limbs, 83b719b83fb3) that was never installed.
  Installed it into both defs through `art.py install ... --reason script:` (ledger). It is 512x512 while sibling south/north are 256x256 (needs a scale-down to match; not done, ledger-only).
- NOT queued for repaint: both Kudda rows carry the owner's note on desert_sheet_2026-10-04 "Just cut this creature. It's dumb." (hold). Cut/keep is his call; the real east is only there so nothing wears the pillar meanwhile.

## Kudda cut (2026-10-08 pass)
Already enacted before this pass: `7663b4e5c` (2026-10-04, "Cut the kudda (RM_ and RSW_)") deleted RM_Kudda and RSW_Kudda from RM_LongShade.xml, RUT_Desert.xml, RUT_ExtremeDesert.xml and both race files; the Stillsand patch row was cut in the same sitting (WildAnimals_Stillsand.xml carries only the explanatory comment). Rosters desert.json:716 and dune_sea_deep_desert.json:571 record the cut with his words. The sheet's decisions.json still reads `hold` (a record, not a roster). No Kudda job is queued (pending/ has none; done/ holds RM_Kudda_{east,north,south} renders). Left as is: the orphan textures `RM_Kudda/` (LongShade) and `RSW_Kudda/` (SWBestiary), tonight's east install, no def points at them.

## Decisions for the 12 groups (owner of the image / borrower / action)
1. Ossik north == RUT_AncientShieldedTurret: the turret owns it (artpipe `RUT_AncientShieldedTurret`, sha a25f92f19950, `502b24794` 2026-09-23 wired it into both Ossik folders by mistake). Borrower RM_Ossik/RSW_Ossik: **no def exists** (cut, sheet ruling "no longer needed"), so the textures are orphans. No install, no job. (Own render RM_Ossik_north exists in artpipe, 9ecd37095c8f, if Ossik ever returns.)
2. RSW_ElderSando == RM_GrippingTerror: **not wrong-subject.** GrippingTerror is the owner-ruled rename of RM_ElderSando (Scald sheet 2026-10-05: "draws its own copy of the elder-sando picture he kept"); the picture shows the long webbed-hand arms its description names. ElderSando (canon, SWBestiary) owns the original. No action.
3. RM_Aurrok == RM_Vaalok: Aurrok owns it (artpipe RM_Aurrok_{south,east,north}, `ba5bfe05f`). Vaalok borrowed. Vaalok's own finished renders exist: north e018cc1c7fa8, east fbb4552bd156 (512x512 = sibling canvas, art-gate PASS); south FAILED in artpipe. Install of north/east **REFUSED by the ledger** (the Aurrok bytes under Vaalok count as owner-kept: "may not displace it; needs his ruling"). **NEEDS-OWNER**; ready once he rules: `art.py install src/RimMandrake/Stillsand Things/Pawn/Animal/RM_Vaalok/RM_Vaalok_{north,east}.png <sha> --owner-said "..."` (store copies via `Transient/biome_art_refresh_2026-10-07/wrong_subject_install.py`, which runs install_file). South QUEUED p0: `wsfix_RM_Vaalok_south_v2_south` (derive_from RM_Vaalok_east).
4. RM_Mullgoth == Wildpod == AA_Wildpod: **not wrong-subject.** The Rot v2 renders (`06966e55d`) were briefed as mullgoth/durrok bodies (the mullgoth prompt: "the same body twice the mass"); Mullgoth wears the sagging hairy-dome/black-slime picture its description names. Deliberate donor-name pair. No action.
5. RM_Durrok == Wildpawn: same, the pale haystack-with-lichen picture is the durrok description. No action.
6. RM_Pallbearer == RUT_MortuaryCrawler: **same subject** (the def comment: "PALLBEARER (was RUT_MortuaryCrawler)", renamed `ee8fbc21f`; art is artpipe rutmortuarycrawler_v1). RUT_MortuaryCrawler retired (0 in save); its folder in UtinniPatches is a leftover duplicate, not touched. No action.
7. RM_Ulkhoss == RUT_Vapaad: RUT_Vapaad owns it (artpipe vapaad_canon_v2 / Blue Desert G). RM_Ulkhoss was DROPPED by the owner (`d2f36f0b6` "Drop the ulkhoss") and has no def: orphan textures. No action.
8. Gloomcast_Dessicated == Horax_Dessicated: Horax (donor-layer skeleton drawing) owns it; Gloomcast borrowed. QUEUED p0 `wsfix_Gloomcast_Dessicated`. The four juvenile Dessicated (FrilledGorg/Igitz/LongtailGorg/Worrt `_j_`) share one tiny skeleton: generic juvenile corpse art, each is a donor-layer stand-in; left (no per-species brief, barely visible), noted.
9. RM_Bones == RM_SummBone: RM_Bones owns the generic bone pile (Miasma, `6dd7fb403`); SummBone (honeycombed light brood bone) borrowed. QUEUED p0 `wsfix_RM_SummBone`.
10. RM_MuurrokSkeleton == RM_SummGreatBone: the muurrok skeleton owns it (`2655f315f`); SummGreatBone (one room-long bone) borrowed in `6f4ca7660`. QUEUED p0 `wsfix_RM_SummGreatBone` (1024x512 like the file).
11. RM_FlameStatuary == RM_FlameStatue_Placeholder: both are the same 2004-byte flat shape (the detector does not flag it; not in placeholder_allowlist.json). FlameStatuary (`53687b094`, 2026-09-24) is the original; the FlameStatues copy is a placeholder by name whose own renders failed in artpipe. QUEUED p0 `wsfix_RM_FlameStatuary` (the Placeholder file belongs to the FlameStatues mod's own failed jobs, not touched).
12. Plants: Ghemmel_a (Hydenock donor tree), Veluthar_a (AB_JungleTree donor), GiantLeaf_a (BMT donor port) are donor art that the owner KEPT as A on the Greentide/FeverWood sheets 2026-10-08 ("Add much more realistic variants"); the B/C variant renders are already pending at p0 (regen_gt_ghemmel/veluthar, regen_fw_giantleaf). BloddleB == BloddleA: same subject (donor Bloddle drawing duplicated as a variant; C-G are artpipe renders). CrystalCrab Female_east == Male_west: same subject, donor facing quirk. No action.

Jobs: `build_wrong_subject_jobs.py` -> `wrong_subject_jobs.json` (5 jobs filed, 0 refused). Nothing installed this pass.

## Not wrong-subject (venomvine)
RM_{Hoard,Quench,Rearing,Shedding,Sworn,Walking}Venomvine_a == RM_VenomvineThicket_a (29ae79060e16): documented interim placeholder from the venomvine rescue, renders queued.
