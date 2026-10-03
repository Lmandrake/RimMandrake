# ABYSS_FOLD_LAMP_BUILD_1 — heat-folding research and the fold-lamp

Biome: the Abyss (`RM_Abyss`, free tier, `mandrake.rm.biomes`; campaign twin `RUT_Abyss`). Review: `design/Jawa/worldbuilding/biomes/blackcrags_bedazzle_review_2026-09-30.md` §11.2 mark 2(a), ruled §12. Rides `ABYSS_DARK_BUILD_1`.

## spec

Decision taken by question card (turn 3, 2026-10-01). Research that warmth pushes the Dark back, then a heater-lamp that holds a clear lane open toward where it points. Useful as a cold-night lamp anywhere (it stays a good heater-lamp off the Abyss). First time a pawn watches heat open a clear pocket, a letter fires and unlocks the research. Heat is the one vanilla heat: no new hediff, not a sensor (ban 5).

## criteria

- ResearchProjectDef (heat-folding) unlocked by the first observed clear pocket.
- Fuelled lamp ThingDef with CompHeatPusher + CompGlower and a directional bias the Dark field reads.
- Works as a plain heater-lamp with the Dark absent; Mod Settings toggle, all-off degrades gracefully.

## verify

Offline build + selftests; live proof is a joint session.
