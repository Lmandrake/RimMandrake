# RimStarWars: Shokk — validation walk
subject: src/RimStarWars/Shokk  (packageId `mandrake.rsw.shokk`)
deps: `mandrake.rm.biomes` (RM_Ollathrix lives in the composed biome mod), `mlie.starwarsanimalcollection` (the donor Wyyyschokk PawnKindDef the faction fields)
list: no named modset_builder tier yet; the smallest tier is BRIDGE + the donor mod + `mandrake.rm.biomes` + `mandrake.rsw.shokk` + the five DLCs
status-hint: SHOKK_FIRST_SCRIPT_1 — data-only mod after SHOKK_SKIN_SHRINK_1: one skin patch and one hidden faction; no C#, no Mod Settings class; first script drafted, never run live

Sources: `src/RimStarWars/Shokk/About/About.xml` description, `Patches/RSW_Shokk_OllathrixSkin.xml`, `Defs/FactionDefs/RSW_Shokk_FeraliskBrood.xml`, `src/RimMandrake/Webwork/Defs/ThingDefs_Races/RM_Ollathrix.xml`, `src/RimMandrake/FeverWood/Source/RM_MapComponent_TwoFrontLure.cs`.

## must be true
Agent-owned, not hashed. Chains and components are in `src/RimStarWars/Shokk/validation.py`.
- The hidden feralisk-brood FactionDef loads, and the donor Wyyyschokk kind and `RM_Ollathrix` race it and the skin patch depend on are present; a def that fails to load is dropped whole and silently. [About.xml; `Defs/`] → defs_resolve.every_shipped_def_resolves, defs_resolve.donor_wyyyschokk_kind_resolves
- The def-probe instrument can say "not found". [method] → defs_resolve.control_probe_can_say_absent
- With this mod loaded, `RM_Ollathrix` (race and kind) reads as the canon wyyyschokk: label, plural and description, one def and never a second race. [`RSW_Shokk_OllathrixSkin.xml`; OLLATHRIX_OWNER_SPECIES_1] → skin_patch.race_label_and_plural_are_wyyyschokk, skin_patch.kind_label_and_plural_are_wyyyschokk, skin_patch.description_names_the_canon_species
- The label reader can read a different label (an unpatched vanilla def does not read "wyyyschokk"). [method] → skin_patch.probe_can_read_a_different_label_control
- All three life stages carry the swanimals Wyyyschokk texture instead of the RM_Ollathrix art. [`RSW_Shokk_OllathrixSkin.xml`] → skin_patch.life_stage_art_swapped (reports UNMEASURED while `get_defs` returns `lifeStages` as bare type names)
- The skin patch never touches mechanics. [`RSW_Shokk_OllathrixSkin.xml` header] → UNCOVERED: a negative over every field of the race; the patch's xpaths are the whole proof and the static check reads all of them against the Webwork source
- The feralisk brood is a hidden, permanent-enemy, animal-tech, non-humanlike faction in the Fever Wood's two-front category, fielding the Wyyyschokk in its Combat group. [`RSW_Shokk_FeraliskBrood.xml`; FEVERWOOD_TWO_FRONT_LURE_1] → feralisk_brood.faction_is_hidden_permanent_enemy_animal, feralisk_brood.combat_group_fields_the_wyyyschokk (reports UNMEASURED while `get_defs` returns `pawnGroupMakers` as bare type names)
- The Fever Wood raid's second front fires this faction. [`RM_MapComponent_TwoFrontLure`] → two_front_lure.fever_wood_second_front_fires_this_faction (reports UNMEASURED: needs a generated Fever Wood map and a raid; the mechanism belongs to `mandrake.rm.feverwood`)
- The mod ships no Mod Settings screen, and that is by design: it has no mechanics to toggle. [About.xml; folder has no Source/] → settings.no_settings_class_by_design

## the walk
1. [D] defs_resolve: one batched `get_defs` of the shipped faction, a donor-kind and race presence read, a control name
2. [D] skin_patch: read label/labelPlural/description off `RM_Ollathrix` ThingDef and PawnKindDef; control read on `Wolf_Timber`
3. [D] feralisk_brood: read the faction's scalar fields; the group list is read when the tool returns it
4. [S] two_front_lure stays UNMEASURED with its reason

## north star
state: DRAFT
validated-hash:

No owner north-star bars are drafted for this mod yet.

## anti-guessing notes
RULED OUT: "the skin patch's plural operation lands on the race" — `RM_Ollathrix`'s ThingDef ships no `labelPlural` node (only its PawnKindDef does), so the match-only operation was a silent no-op and the race kept the auto plural; fixed 2026-10-03 with a `nomatch` Add, and the static check goes red for any operation that matches nothing and has no `nomatch`.
RULED OUT: "the Shokk mod still ships mechanics" — SHOKK_SKIN_SHRINK_1 moved the loom-bound hediff, loom spit, sun-scald and emergent spawn into `mandrake.rm.webwork`; this mod holds one patch and one faction, and the static check goes red if a `Source/` folder reappears without a settings chain.
RULED OUT: "the faction needs the donor mod to resolve" as a defect — the FactionDef is MayRequire `mlie.starwarsanimalcollection` by design; absent the donor the lure's lookup returns null and the Fever Wood raid is "ants only". The def check names the donor in its failure text.
