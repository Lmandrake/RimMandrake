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

## Other likely wrong-subject textures (listed, NOT fixed) — 12 groups
Distinct creatures/things sharing identical bytes:
1. RM_Ossik_north (LongShade) + RSW_Ossik_north == `RUT_AncientShieldedTurret.png` (a building) — Ossik north-facing is a turret picture. (a25f92f19950)
2. RSW_ElderSando == RM_GrippingTerror, all four facings, plus SWBestiary and TerminalBiomes copies (c42637fdca56, 4007dc4c1cf2, 9eb74f8836df, 7317a2b3cfbb). Two different sea beasts, one picture.
3. RM_Aurrok == RM_Vaalok (Stillsand), S/E/N (d165910a7108, 3511b5ed892e, 5f1ddc63c80b). Two defs, one picture.
4. RM_Mullgoth (SWBestiary) == TheRot Wildpod == AA_Wildpod override (bc89bf873cf8, 014b59c7f23a, c0dedfeb2852). Mullgoth wears Wildpod art.
5. RM_Durrok (SWBestiary) == TheRot `RotSpecies/Wildpawn` S/E/N (00da96559e31, 30701f14ee3c, cf024497dad1).
6. RM_Pallbearer (Scarlands) == RUT_MortuaryCrawler (UtinniPatches) S/E/N (4b41b1e8500c, d46d41cb2754, 4f49c7f68e63); MortuaryCrawler has no def, so possibly a stale leftover/override.
7. RM_Ulkhoss (TerminalBiomes) == RUT_Vapaad (UtinniPatches) S/E/N (0caf52893b2f, 4328879aaf0f, df9220c00d1e); Vapaad is only a sound def stem, so probably a stale leftover.
8. Gloomcast_Dessicated (LongShade) == Horax_Dessicated (SWBestiary) (b18e3629bb96); and the four juvenile Dessicated of FrilledGorg/Igitz/LongtailGorg/Worrt (5318d852f3e1) — shared placeholder.
9. RM_Bones (Miasma item) == SummBone (Abyss item) (fc67f9e8f4ea).
10. RM_MuurrokSkeleton (Stillsand building) == SummGreatBone (Abyss building) (b6e9cc89d641).
11. RM_FlameStatuary (EnvironmentalHazards) == RM_FlameStatue_Placeholder (FlameStatues) (80371766af7d) — placeholder by name.
12. Plants: RM_Ghemmel_a == UtinniPatches HydenockTreeA (f14d780a43ee); RM_Veluthar_a == AB_JungleTreeA (5345c1f53544); RSW_Plant_BloddleB == BloddleA (0f35431ae70c); RM_GiantLeaf_a == GiantLeafA (816cf4e9de3d, probably a deliberate port).
Also odd: CrystalCrabFemale_east == CrystalCrabMale_west (cross-facing swap, 49ad11a8b443).

## Not wrong-subject (venomvine)
RM_{Hoard,Quench,Rearing,Shedding,Sworn,Walking}Venomvine_a == RM_VenomvineThicket_a (29ae79060e16): documented interim placeholder from the venomvine rescue, renders queued.
