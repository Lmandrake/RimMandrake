# RIMMANDRAKE_PROVE_KNOCKBACK_ALL_FLY_PERF

## spec

Step 6 of `design/concepts/ExplosiveKnockback/plan.md` (Explosive Knockback Designer pass, owner card answers 2026-11-11 in `design/concepts/ExplosiveKnockback/record.json`). The tree leaves, scenes and acceptance bars are in `tree.json` and `scenes.json` in the same folder.

## Watch out

Builds the frame_time_probe instrument first; a frame budget measured blind is a query bug until a sanity probe shows the instrument sees a slow frame. Run on the full list on Archmagi. Owns the walk scene sc_walk_raid (reload, repeat, second order). Never live-test a flyer's flight.
