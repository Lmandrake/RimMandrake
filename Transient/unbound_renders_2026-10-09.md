# Unbound renders, 2026-10-09 (ART_SUBJECT_RESOLVER_1 follow-up)

Start: 788 renders lacked a subject (686 unresolved + 102 ambiguous), 609 job families. Job files carry no target_def
for these (it was only stamped on later jobs); evidence below is style_notes / rimflow_item_id / prompt / git history.

## Newly resolved by deterministic rules (458 renders) - render_subjects.refine(), data in infrastructure/state/art/def_history.json
| rule | renders | evidence |
|---|---|---|
| vanilla-reskin | 346 | RSW_Junk_<Vanilla>_NN family = STARWARS_JUNK_RESKIN_1 art for vanilla Ancient* defs (spec table); subject is the vanilla def |
| primary-body | 69 | token match found body + its Catch/Meat/Fruit/Raw products; the products are not the subject (39 single-subject bound; 30 are RM_/RUT_ tier twins, name-matched, no binding written) |
| sibling | 26 | another render of the same job family is bound by its job target_def, all agree |
| rename | 16 | git hunk renamed the def (e.g. RSW_Ashworm to RM_Vurra, Sporemass to Mullgoth, Spinerat to Chikka; NONCANON_BEAST_RENAME_1) and the new name is live |
| donor-name | 1 | facingrepair_megatardi_v1 = VAEWaste_Megatardi |

No existing bound / name-matched render changed (full before/after compare of 4,743 entries).

## Dead subjects (33 renders, class `dead`, not bound): def removed from the game, no live successor
- RM_Kudda
- RM_Thurra
- RSW_Barbthorn
- desertportb_imperialtoad
- facingrepair_wyyyschokk_v1
- feverwood_gorrameth
- feverwood_lommerel
- feverwood_nemmel
- feverwood_plant_skethral
- feverwood_thavrik
- rut_gene_furnaceblood_icon_v1
- scald2_rainbowpigment_a
- scald2_rainbowpigment_b
- scald2_rainbowpigment_c
- scaldsteam_overlay_a
- scaldsteam_overlay_b
- twilightsea_moldmatroof

(RM_Kudda/Thurra cut 2026-10-04; Lommerel/Nemmel/Gorrameth/Skethral/Thavrik/ImperialToad deleted d074b131a 2026-10-08; RSW_Barbthorn renamed Skorra then Skorra gone.)

## Left for an owner binding sheet (297 renders)
| category | renders | examples / why not deterministic |
|---|---|---|
| creature/plant/prop with NO def in current files or history | 178 | contagion_* (14 creatures), crags_* (5), desert_gap_* droids, RM_Hoarfrost_*, RM_Sohl, RM_Frissim, nightside_zhissa: art ahead of any def (DONOR_DEFS_PORT_TO_OURS_1 etc.) |
| kit art for unbuilt mod | 39 | MessyConduit strands/hoses/masts: no MessyConduit def exists |
| rite/site props, no def yet | 21 | RUT_BroodBone, RUT_TarEffigy, RUT_RefusedTollMeter ... |
| non-def art (mockup/UI/terrain/decal) | 31 | spec_scene_*, spec_ui_*_icon, RM_TrackPrint_*, RM_WallFace_* (install_to a texture), saltcrystal pile, graffiti_scratches_p1-3, probe |
| xenotype head textures | 12 | xeno_head_{lasat,mimbanese,nelvaanian,ortolan}: each maps to several spawn/kind defs |
| repair/redo of a non-def name | 8 | facingrepair_{grmolebear,rutcathedralroach,rutscarroach}, mantrap_improve_a_r7 (RSW_Creature_Mantrap by eye only), webwork_tooketrap_redo |
| genuinely ambiguous | 8 | RSW_Stoneback (renamed to Bokka then Korrum: handed to two creatures), rut_liveingredient_* (RM_/RUT_/Live twins), RUT_AncientAirlock_Large_Top |
