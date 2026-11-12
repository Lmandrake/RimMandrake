# RIMMANDRAKE_LIMIT_KNOCKBACK_STORAGE_CLOSED

## spec

Step 2 of `design/concepts/ExplosiveKnockback/plan.md` (Explosive Knockback Designer pass, owner card answers 2026-11-11 in `design/concepts/ExplosiveKnockback/record.json`). The tree leaves, scenes and acceptance bars are in `tree.json` and `scenes.json` in the same folder.

## Watch out

'Closed' is the delegated rule dl_closed_means_hidden: storage that does not draw its contents (plus an opt-in tag). Deep-storage mods differ in how they hide contents: read each def, do not guess. The container shove never moves into a pit, a wall or onto a pawn. Walk row light_things.item_on_a_shelf_stays asserts the OLD rule and must be reversed in the same commit.
