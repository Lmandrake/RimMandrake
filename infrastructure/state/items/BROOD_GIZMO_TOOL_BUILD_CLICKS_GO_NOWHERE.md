## spec
Re-filed from UNPROVEN_LIVE_LEGS_TRIAGE_1 (triage of FEVERWOOD_BROOD_RANSOM_1 A3 tally and A4 gift, verdict NEEDS A TOOL).
Both legs start from the "Return to the deep" gizmo on an occupied `RM_SekkulaathTank` (`RM_CompCapturedSpecimen`).
A bridge UI click on a gizmo fails silently, and an OS-level `system_click.py` click on a gizmo bar is a pixel hunt
that no proof can read back. FeverWood's validation.py has no component for the tally or the gift (it has
`a_young_cask_reads_the_deeps_restlessness` and the brood toggle-off only). `jawa/static_call` reaches public
statics (`RM_WorldComponent_DeepYoung.RestlessnessLine()`, the gift grant `Grant(Map, IntVec3, int)` in RM_BroodRansom.cs)
but refuses instance methods, so neither the tally count nor the gizmo's action is reachable today.

Build (reuse first: JawaBench companion, rimbridge-companion skill):
1. A generic JawaBench `[Tool]` that lists a thing's gizmos (label, disabled reason) and invokes one by exact label
   (`Command_Action.action` / `Command_Toggle.toggleAction`) on the main thread, refusing an ambiguous or absent
   label with the candidates. Generic on purpose: every "click this gizmo" leg in the project needs it.
2. A read of the world tally (`RM_WorldComponent_DeepYoung` count, on maps, in caravans, + Sporefall while unfreed),
   either a tiny [Tool] or a public static the mod already should expose.
3. FeverWood validation.py components: `tally_counts_tanks_and_casks` (2 occupied tanks + 1 cask = 3) and
   `return_to_the_deep_lowers_tally_and_grants_one_gift` (gizmo -> young enters a Fever Wood pool -> tally 2, exactly
   one RM_DeepGiftLoot thing within 6 cells inside 2,500 ticks), each with its toggle-off arm.

## criteria
A1 L0: the gizmo tool and tally read build (winbuild) with a selftest refusing an absent/ambiguous label; the two components exist and the mock suite lists them.
A2 L2: live on a Fever Wood map, both components read PASS, proving FEVERWOOD_BROOD_RANSOM_1 A3 and A4.
