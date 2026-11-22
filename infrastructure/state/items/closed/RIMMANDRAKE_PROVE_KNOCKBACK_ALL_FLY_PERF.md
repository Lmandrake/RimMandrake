# RIMMANDRAKE_PROVE_KNOCKBACK_ALL_FLY_PERF

## spec

Step 6 of `design/concepts/ExplosiveKnockback/plan.md` (Explosive Knockback Designer pass, owner card answers 2026-11-11 in `design/concepts/ExplosiveKnockback/record.json`). The tree leaves, scenes and acceptance bars are in `tree.json` and `scenes.json` in the same folder.

## Watch out

Builds the frame_time_probe instrument first; a frame budget measured blind is a query bug until a sanity probe shows the instrument sees a slow frame. Run on the full list on Archmagi. Owns the walk scene sc_walk_raid (reload, repeat, second order). Never live-test a flyer's flight.

## Flagship scene (2026-11-12)

This item also stages showcase 1, `sc_storeroom_bomb_pit` in `design/concepts/ExplosiveKnockback/scenes.json` (his write-in, OWNER:1794470697182934051): a bomb into a stocked storeroom with colonists, beside a pit; some goods and some people end in the pit. Hold owner_review. Needs builds 1, 2 and 5 (goods fly, closed containers, heavy knock).
