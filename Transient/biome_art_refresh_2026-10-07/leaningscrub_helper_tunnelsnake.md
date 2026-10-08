# Leaning Scrub helper

## Task A TunnelSnake  (DONE)
- Not canon: Wookieepedia search "tunnel snake" returns tunnel worms/dragonsnakes only, page "Tunnel snake" is MISSING; canon_references has no entry (NO_SOURCE.json lists TunnelSnake as sourceless).
- Created `src/RimMandrake/LeaningScrub/Defs/ThingDefs_Races/RM_TunnelSnake.xml` (Snake body, Mouth/HeadAttackTool groups, ToxicBite, vanilla stages, Megascarab voice, Megaspider meat, no leather; size-ladder numbers kept).
- Art via ledger (ruling 9ca52399d9a90ca7b651) -> `src/RimMandrake/LeaningScrub/Textures/Things/Pawn/Animal/RM_TunnelSnake/RM_TunnelSnake_{east,north,south}.png`. No dessicated art made (Klorslug's is SW tier; fuzzviper omits it too).
- Cast inline in RM_LeaningScrub_Biome.xml at 0.5; row removed from WildAnimals_LeaningScrub.xml (header note added).
- RSW_TunnelSnake KEPT: frozen RUT_AridShrubland.xml line 164 casts it. RSW_ScrapNestBird/Excretor/VentStalker only mention it in comments (nothing to repoint).
- Docs updated: leaningscrub_bedazzle_cast_2026-09-29.md, leaningscrub_bedazzle_review_2026-09-29.md; sheet_row_overrides.json gains RM_LeaningScrub label override. arid_shrubland.md (frozen RUT design) left alone.

## Task B creature variants
- Bantha F,G,H: SKIPPED, already live. Their shas are byte-identical to BanthaV_G/H/I (installed by commit 5ab6473ee) and RSW_Bantha already lists those as alternateGraphics.
- Iriaz H,I: NOT DONE. Every sha of both is owner-purged in the ledger (the same decision file purges them) and absent from the store; install refuses. Same ticked-and-purged case as FrilledGorg A (purge won). QUESTION: did he mean to keep H/I? If so the purge must be released and the art re-rendered.
- Scurrier E: NOT DONE, QUESTION. Art is installable (not purged), but Scurrier has separate male/female graphics and E is a variant of the FEMALE graphic (Scurrier_f). An alternateGraphics texPath replaces both sexes, so wiring it would put female art on males. Options: wire it for both sexes anyway; or leave it unwired.
