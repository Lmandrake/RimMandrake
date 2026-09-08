# JawaIkee — validation walk
subject: src/RimStarWars/JawaIkee  (packageId mandrake.rsw.jawaikee)
deps: sarg.alphaanimals (Alpha Animals, hard dep, provides AA_Eyeling); loadAfter mandrake.rsw.starwarsraces
list: full   # needs Alpha Animals for AA_Eyeling AND starwarsraces for the tolerant XenotypeDefs
status-hint: an ikee (Alpha Animals' AA_Eyeling) nearby gives Jawa/Hutt/etc a mood buff via RSW_Jawa_IkeeWatching; every other xenotype gets a creep-factor malus instead.

## must be true
- ThoughtDef RSW_Jawa_IkeeWatching exists, workerClass RimMandrake.StarWars.JawaIkee.ThoughtWorker_IkeeNearby, and carries an IkeeToleranceExtension with radius 12.
- A humanlike pawn whose xenotype is in the tolerantXenotypes list (RSW_MandrakeJawa, RSW_RimMandrakeHutt, RSW_RimMandrakeGamorrean, RSW_RimMandrakeNikto, RSW_RimMandrakeKlatoonian, RSW_RimMandrakeWeequay, RSW_RimMandrakeTrandoshan, RSW_RimMandrakeRodian, RSW_RimMandrakeAqualish, RSW_RimMandrakeGeonosianVariants) gets stage 0 ("ikee underfoot", baseMoodEffect +4) when an AA_Eyeling is spawned and alive within 12 cells.
- A humanlike pawn NOT in that list gets stage 1 ("the ikee is watching me", baseMoodEffect -5) under the same condition.
- A humanlike pawn with no genes tracker (baseliner-equivalent) is treated as intolerant (stage 1), never stage 0.
- With no AA_Eyeling alive within radius, or the pawn dead/unspawned/mapless, or the pawn non-humanlike, the thought is Inactive for everyone.
- Every MayRequire="mandrake.rsw.starwarsraces" entry in tolerantXenotypes must not throw a red load error when starwarsraces is present (all ten are guarded — no ungated entries exist in the def).

## the walk
1. [L] Player.log after load contains no "Config error in mandrake.rsw.jawaikee" and no XML error naming Thought_IkeeWatching.xml   # load-time
2. [D] jawa/get_def defType=ThoughtDef defName=RSW_Jawa_IkeeWatching → workerClass = "RimMandrake.StarWars.JawaIkee.ThoughtWorker_IkeeNearby"; comps/modExtensions include IkeeToleranceExtension
3. [B] jawa/spawn_pawn kindDef=<a Jawa PawnKindDef>, xenotype=RSW_MandrakeJawa, faction=player, at (x,z) → spawns a tolerant-xenotype pawn
4. [B] jawa/spawn_pawn kindDef=AA_Eyeling, faction=none, at (x±3,z) → an ikee within the 12-cell radius of the pawn from step 3
5. [B] jawa/pawn_get pawn=<step-3 pawn> after a few ticks → needs/mood section lists the RSW_Jawa_IkeeWatching thought at stage 0 ("ikee underfoot")
6. [B] jawa/spawn_pawn kindDef=<a non-tolerant PawnKindDef, e.g. a baseliner colonist> faction=player, at a cell within 12 of the same ikee → jawa/pawn_get on it lists RSW_Jawa_IkeeWatching at stage 1 ("the ikee is watching me")
7. [B] jawa/spawn_pawn kindDef=<any humanlike>, faction=player, at a cell far (>12) from the ikee → jawa/pawn_get shows the RSW_Jawa_IkeeWatching thought absent
