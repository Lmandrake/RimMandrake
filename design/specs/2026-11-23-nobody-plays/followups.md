# Two follow-ups of the nobody-plays census

## RIMMANDRAKE_REMOVE_GRANT_EXPIRY_CHECKS_ONCE_FOUR_COMPANIONS_REDEPLOYED

The companion of f3c90ff50c ignores `expiresUtc` on a save that is not canonical. Until all four games run it, an older
companion refuses test tools on an old grant, so `src/RimMandrake/rimflow/companion_grant.py`, the ops alarm
`companion.grant_hours_left` and the lapse half of `ensure_test_profile` (`src/RimMandrake/Utils/modcheck/runner.py`)
still warn. When each game's `jawa/companion_handshake` shows a `companionSha` at or after f3c90ff50c, remove the expiry
half of the three. Keep the "effective profile is test" check: it is a true reading of the loaded game.
Acceptance test: none, it depends on what four live games have loaded.
First live read owed (UNRUN): with an old `expiresUtc` and a save that is not listed, the handshake reads `test`.

## RIMMANDRAKE_LIST_CANONICAL_SAVES_IN_COMPANION_PROFILE_CURRENT_START_MISSING

`companion_profile.json` on Archmagi lists `CANONICAL_ASHKARR_START_2026-09-12, Ashkarr, Ashkarr autosave`. The current
canonical start (`canon.yml` `planet.start_savegame`, R3) is not on the list, so the CAMPAIGN profile does not guard it.
The two other names are no save on disk. Decide: list R3 and the `CANONICAL_*` saves (the test tools are then refused in a
game that loaded one; load a copy under another name), or leave the list.
Acceptance test: none, a decision of the Conductor's and a file outside the repo.
