# Work bundle WB-mod-ExplosiveKnockback-20261126-000018 (mod:ExplosiveKnockback)

Updated 2026-11-25 17:17 PST. Both members closed. One group: both members share the scar defs and LayScar.

## Done
| ticket | class | outcome | commits |
|---|---|---|---|
| RIMMANDRAKE_RENAME_KNOCKBACK_SCAR_DEFS_DIGIT_ENDING_CONFIG_ERROR | REAL | fixed: defs `RM_KnockbackBlast<Kind>_<n>Wide`; old names load (RM_Patch_ScarOldNames). Offline B_NO_DIGIT_THINGDEF red on parent, green; live: 0 digit lines in Player.log, walk save D 20 of 20 old scars load as *Wide, settings sweep 17/17 | d62ff67597, 834a545dbc |
| RIMMANDRAKE_FIND_KNOCKBACK_IED_SCAR_MISSING_ONE_RUN_IN_THREE | REAL (SITE + cross-mod) | cause measured: The Rot's ThinOutdoorFilth removes 1-thickness scars (8 of 24); a roofed station collapse in probe 1. Scene library unroofs stations; both blast-show scenes hold acceleratedRotEnabled off. sc_blast_show 5 of 5 real 28/28 + polished build 28/28; show_off plant red | 595acb512e, 1e03d4da73, 2d9e31fc35 |

Evidence: design/concepts/ExplosiveKnockback/version/evidence/ied_scar_2026-11-25/README.md

## Finished
- Fresh reader (Opus): nothing significant; its four nits done (art jobs renamed 422444cbf4; polish fb515d1dc3, 1cd9e0e961, 4168159c89); red_seen T_BLAST_SHOW_OFFLINE 11c7411358.
- Closed: RIMMANDRAKE_RENAME_KNOCKBACK_SCAR_DEFS_DIGIT_ENDING_CONFIG_ERROR at d62ff67597; RIMMANDRAKE_FIND_KNOCKBACK_IED_SCAR_MISSING_ONE_RUN_IN_THREE at 1e03d4da73.
- ArchSmall holds the final committed build (11c7411358's DLL), bridge released.

## Context after the group
357,782 of 1,000,000 (work_bundle.py context: GO ON).
