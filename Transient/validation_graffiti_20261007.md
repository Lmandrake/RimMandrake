# Graffiti validation, 2026-10-07 - LINT ONLY (under the ~800-line non-engine bar), nothing committed

Sizing: 1487 lines in 18 files. Non-engine logic is about 200 lines: GraffitiPool (weighted pick + meme / skill / hostility gates, ~60), ThoughtWorker ResolveReactionThought (~30), AutoCleanProtection decision (~10), the candidate-cell bag in GraffitiJobUtility (~40), going-over rule in Filth_Mark.MakeMark (~10), the validator (~40). Everything else is Harmony patches (BreachBias, RaidExitTagger, AutoClean), Filth printing, JobDriver toils, Designator/WorkGiver, settings UI. No kernel extracted: below the bar and the pure parts read engine objects (Pawn.Ideo, Faction.HostileTo, DefDatabase) at every step.
North star untouched (Graffiti carries hash-bound bars).

## Lint
`python3 src/RimMandrake/Utils/lint_graffiti_defs.py [--quiet]`: 8 defs + 1 patch file, 18 classes, 49 refs, 43 field checks, 1 driver, 6 settings: 0 ERROR, 0 WARN.
Shared-tool fix found here: `lint_mod_defs.py` demanded every `giverClass` derive from WorkGiver, so a JoyGiverDef (`RM_JoyGiver_PaintGraffiti`) was a false ERROR; it now expects JoyGiver under a JoyGiverDef. Wasteland / LeaningScrub lint output unchanged.
