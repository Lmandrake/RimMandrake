# SALVATION_RITES_UNIFICATION_1 — every Salvation rite in one home; biomes teach rites

Supersedes `CONDITION_GATED_RITUALS_MOD_1` (its concept doc is retired; its still-true content is in the design doc). Design: `design/Jawa/salvation_rites_2026-10-01.md`. Origin: Abyss review `design/Jawa/worldbuilding/biomes/blackcrags_bedazzle_review_2026-09-30.md` §14.

## owner rulings (typed, card 2026-10-01 10:08 PDT)

R1: "Unlike all four of those! Amazing! Each of these should do different sorts of appeasrmentsnif the utinni gods. I am starting to love the idea that you don’t just discover tech in the biomes you discover new rites." ("Unlike" read as "I like".)

R2: "This is part of the Jawas religion already. So it’s part of the salvation mod suite. Decide where rites go in there and unify them."

Earlier rulings carried (card 09:22, decisions taken by question card; Q4 typed): darkness rites held anywhere the player makes it dark; new rites plus slot-free dark variants; dark breaking means the rite fails and Sh'kaar answers; campaign-only (RimUtinni); darkness the only condition.

## decided (BENCH)

- Home: `mandrake.rut.rites` (`src/RimUtinni/Rites/`), the existing liturgy tab ("revealed, not bought"). Gods' arithmetic stays in `mandrake.rm.ninefold`; the darkness gate is C# inside the Rites mod. `RM_Ishko_RitualOutcome_PlaceSacredMark` moves in from SacredGraffiti with the Dark Vigil.
- The four Abyss rites: Dark Vigil → Ishko (feeding by stillness); Blind Offering → Mob'Unloo (settlement); Snuffing → Sh'kaar (starving the evil god); Lightless Burial → Ozzik (consolation, pride-meter vented).
- Discovery: a CompStudiable inscription in the biome yields a techprint rubbing (commonality 0); its "found rites" project on the Rites tab completes through a ResearchMod that calls `Ideo.AddPrecept(..., fillWith)` on The Salvation. UNMEASURED: runtime AddPrecept fills a ritual correctly.
- There is no ritual-count cap (facts/salvation_ritual_precepts.json); the old "6 slots" claim was false.

## criteria

- Each found rite is locked until its inscription is studied, then learnable and performable anywhere its condition holds.
- A darkness rite is blocked with a stated reason when its spot is lit, and a mid-rite break fails it and hands it to Sh'kaar.
- The four rites move four different gods through Ninefold `ApplyDelta`.
- No Salvation rite def lives outside `mandrake.rut.rites`.

## next

Owner to rule the open questions in the design doc's report (names/inscriptions, the Rites mod display name, other faiths' rites). Then a FOUNDRY build item.
