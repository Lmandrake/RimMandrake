./publish with an explicit path of a file whose deletion is already staged (deleted by 'git apply --index', removed from the index by git rm, or 'git add'-ed by you after rimflow close moved it to items/closed/) is REFUSED: its 'git add --all -- <paths>' fails with "pathspec ... did not match any files" for the deleted path. Nothing is committed.

Sightings:
- 2026-11-17, converge.json in Abyss/cleanse, deleted by 'git apply --index'.
- 2026-11-19: after rimflow close moves an item's prose to items/closed/, do not 'git add' the old path yourself before ./publish: once its deletion is staged, ./publish's own 'git add --all -- <old path>' fails ('pathspec ... did not match any files', REFUSED rc 2).
- 2026-11-19 (measured): ./publish runs 'git add --all -- <paths>', which fails 'pathspec did not match' on a file already removed from the index by git rm.

Acts, either one:
- Leave the deletion unstaged: delete with plain rm (or git reset the git rm), or leave the old path of a rimflow close move unstaged, and pass each deleted FILE path; publish stages the deletion itself. A git mv/rename needs its old path listed too or the old file survives on origin (measured 2026-11-19).
- Pass the containing folder as the pathspec instead (it covers the deletion; e.g. ./publish ... infrastructure/state/items), after checking that folder holds no other dirty file (only your moves are dirty there).
item: RIMMANDRAKE_FOLD_OWNER_MARKS_INTO_ABYSS_AND_ROT_PROPOSALS
home: clone-landing-commits
