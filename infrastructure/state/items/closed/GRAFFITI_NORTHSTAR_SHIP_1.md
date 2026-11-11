# GRAFFITI_NORTHSTAR_SHIP_1

Parent: `GRAFFITI_NORTHSTAR_TRIAL_1`. Plan: `design/RimMandrake/northstar_trials/Graffiti_trial_plan.md`, §5.

## acceptance
- Both GREEN rungs closed.
- Art is complete: every `texPath` resolves, and no BadTex.
- Mod Settings are superb per the 2026-09-12 ruling: tooltips on all 6, graceful all-off, defaults =
  shipped behaviour.
- `viewerReactionEnabled`'s consumer has been re-measured. If it is still dead in Graffiti alone, the
  setting is labelled or removed.
- `code_review_status.py check` reads CLEAN on every `Source/*.cs`, `validation.py` and
  `northstar_site.py`.
- `dll_source_stamp.py check` passes.
- `deploy_custom_mods.py --mod Graffiti` reads "in sync".
- The hashed-prose correction (plan §5.7) has been re-validated on the owner's word.
