# SEND_HOME_NEVER_SEABED_1 — X-1: shared helper so send-home never picks a sea-floor map

## spec

Filed from `design/RimMandrake/gpt_reviews/DESIGN_PASS_2026-10-08.md` (remaining rows, helper pass 2026-10-09; owner 'Queue all' card 2026-10-08). Row X-1 there is the spec; its 'Checked' column says what was read to confirm it is unbuilt. Re-check src before building.

| X-1 | **"Send them home" never means the sea floor.** Five mods return a pawn to "any player home map", and that can be a sea-floor map. That breaks the rule that the ship is the only way down and back. One shared helper picks a surface home map. | one helper that skips `RM_SeabedLayer` maps, then five call-site swaps | S | low | Stillsand, FlowWorks, FeverWood, TheRot, WeepingStones, DivingInteraction | `Find.AnyPlayerHomeMap` in `RM_DuneGale.cs`, `RM_WorldComponent_SweptAway.cs`, `RM_BroodRansom.cs`, `RM_NavigatorLog.cs`, `RM_WalkingCondenser.cs` (re-grepped). GALE_CARRIED_RETURN_HARDENING_1 fixes only the gale |

Every invented number is PROVISIONAL. Every feature gets a Mod Settings toggle; names follow the three-tier scheme.
