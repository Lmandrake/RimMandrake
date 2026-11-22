# RIMMANDRAKE_SKIP_HASHIGNORED_FILES_IN_WHOLE_MOD_RERUN_DOCS_SENT_WALK_BACK

rerun_relation: a whole-mod check ignores the mod's .hashignore, so review docs send the full-list walk back.
Caused by RIMMANDRAKE_DRIVE_GIMMESOMESLACK_IN_GAME_VISIT_THREE_RUN_TWO (GSS in-game visit 3).

## spec
`rerun_relation.py` treats a whole-mod or full-list check (GSS `sc_walk`) as touched by any change under the mod,
including files the mod's `.hashignore` lists (they never ship; `modcheck/status.py mod_hash` leaves them out).
Measured 2026-11-21 7:55 PM PST: GSS's change d0b6483f04..c8ef19b610 under the mod was only `review/KEYSHEET.md`,
`review/README.md`, `review/keysheet.html` (all under `.hashignore` `review`); the deployed mod_hash stayed
sha256:e9c2b80d6890; yet sc_walk (PASS on his full list in visit 2, same hash) read RERUN and in-game visit 3 was told to
run it again on his full list. `save_review_map.py` rewrites review/ on every keeper save, so ordinary operation reaches it.

## refs
file: src/RimMandrake/rimflow/rerun_relation.py
file: src/RimMandrake/rimflow/selftest_rerun_relation.py
file: design/specs/2026-11-21-rerun-only-related/boundary.md

## verify
Acceptance test: `python3 src/RimMandrake/rimflow/selftest_rerun_relation.py` -> `0 of 19 checks failed`.
Seen red on base c8ef19b610: `1 of 19 checks failed` (whole-mod-check-skips-hashignored: ['sc_whole', 'sc_full']).

## criteria
A change only under `.hashignore` paths reruns no whole-mod or full-list check; the same change beside a shipped file
still reruns both. `rerun_relation.py --mod GimmeSomeSlack` at c8ef19b610 reads sc_walk untouched.
