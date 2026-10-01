# CONDITION_GATED_RITUALS_MOD_1 — rituals that can only be done in certain conditions (first case: absolute darkness)

Origin: Abyss volley turn 3, mark 9 (relationship to the gods), `design/Jawa/worldbuilding/biomes/blackcrags_bedazzle_review_2026-09-30.md` §12. Concept doc: `design/RimMandrake/condition_gated_rituals_concept_2026-10-01.md`.

## owner ruling (typed, 2026-10-01 08:33 PDT)

"These are very good ideas about having a special ritual. They should not be about this particular biome, but rather something that you can do in absolute darkness, and this entire biome is resident with that so this should have implications into the Uini gods very richly and enable certain rituals that can be done in darkness. This may be an entire new mod for the idea, religion concept of rituals that can be done in certain situations or in certain conditions."

("Uini" read as Utinni.) Meaning: rituals are NOT biome-specific. New mod concept: rituals performable only in certain conditions (darkness first). The Abyss resonates because darkness is everywhere there; ties richly into the Utinni gods.

## what already exists (git grep, 2026-10-01)

- `src/RimMandrake` ships NO PreceptDef, RitualPatternDef or RitualBehaviorDef (MEASURED).
- Utinni gods / ideoligion design only: `design/Jawa/divine_satiation_engine.md` (gods as appetites; section 5 "Rituals are an INVITATION"), `design/Jawa/god_intercession_spec.md` (disposable shrine, managing gods against each other), `design/Jawa/devotional_sacrifice_catalog.md`, `design/Jawa/ideoligion_precept_removals.md`; skill `rimworld-ideoligion`.
- Ritual-shaped content elsewhere: the Stillsand's Return (pour water into sand). The Warscar pilgrim rung rides `GameComponent_LoreStage` + `RM_LoreStageTableDef`.
- Design assumes Ideology is present (all DLCs are a hard prerequisite).

## owner rulings, card 2026-10-01 09:22 PDT

Clicked (decision taken by question card): (1) a darkness rite can be held anywhere the player makes it dark, any sealed unlit room; (2) both new darkness rites and darkness variants of existing rites (wedding, funeral) that use no ritual slot; (3) if the dark breaks mid-rite the rite fails and Sh'kaar answers.

Typed: "There are no eclipses on this planet. This mod is going to be specific to the utinni scenario. Just make a discoverable rite here in the deep dark that they can perform later. That’s the discoverable tech, or one of them anyway."

## spec (as ruled)

- Tier RimUtinni: packageId `mandrake.rut.<name>` (candidate name Rites of Circumstance, owner to confirm), `RUT_` prefixes, namespace `RimMandrake.Utinni.<Mod>`. No free tier.
- One condition, absolute darkness. No eclipse and no other condition.
- A discoverable rite is found in the Abyss's deep dark (mark 2 of the nine marks, beside the fold-lamp) and performed later elsewhere. Candidate: the Dark Vigil, owner to confirm.

## criteria

- A darkness rite can start in any sealed unlit room and is blocked, with a stated reason, when the spot is lit.
- Darkness variants of the wedding and funeral exist and consume no ritual slot; new darkness rites exist beside them.
- A mid-rite break of the dark fails the rite and hands the event to Sh'kaar.
- The discoverable rite is learnable from the Abyss's deep dark and then performable outside it.

## next

Owner to confirm the mod name and the discoverable rite. Then a build item. Not a build item yet.
