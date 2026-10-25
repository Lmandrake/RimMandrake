# ENACT_STALE_SLOT_KEY_MIGRATE_PATH

Found while vetting c3a382b9e0 (ART_SHEET_HOTKEY_GUARD_VET_UNREVIEWED), FOUNDRY 2026-10-24.

A schema-2 decisions record keys `slots{}` by the lane's texPath (`g["key"]`) at the time he clicked. When a later
build changes a lane key (folder moved, def renamed), the old key stays in `slots{}`. `build_plan` then sets
`picks[old_key] = letter` and `rel_for(old_key, facing)` installs at the OLD path, or at the path of a different def.
`remap_decisions.py` remaps letters but not slot keys. This is the schema-2 sibling of SHEET_SCHEMA1_FIX_MOVED_LETTER.

Census over 315 decisions files: 12 slot picks are keyed by a lane the current snapshot does not have. None is keyed
by a known lane with a letter from another lane. Evidence: `D:\ClaudeWork\rimmandrake\vet_hotkey_guard\census2.out`
(script `census.py` beside it). Examples:
- RM_BrineElder: slot key `Things/Building/Natural/RM_SaltChimney`, but the lane is now `.../RM_BrineElder`. A pick of
  B would install at the SaltChimney texPath, so the wrong texture lands on another def.
- `swanimals/...` versus `RimStarWars/SWBestiary/...`, and `Things/Plant/RM_X` versus `Things/RM_X`.

ENACT_SLOT_PICK_VERIFY_MEMBERSHIP deliberately leaves an unknown key unchecked (selftest case 4).

Fix sketch:
- Option 1: `remap_decisions.py` remaps slot keys by `slot_id`, then by def plus lane index.
- Option 2: enact refuses, by name, a slot key that is not a lane of the snapshot.

Failing test sketch (on selftest_enact_slot_membership's fixture):
`plan({"decision":"B","slots":{"oldfolder/Kite/Kite": slot("B")}})` should install nothing at
`oldfolder/Kite/Kite_east.png` and should name the stale key in conflicts. Today it installs there.
