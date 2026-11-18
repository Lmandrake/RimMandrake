./publish with an explicit path of a file deleted by 'git apply --index' is REFUSED: its 'git add --all -- <paths>' fails with "pathspec ... did not match any files" for the deleted path (2026-11-17, converge.json in Abyss/cleanse). Nothing is committed. Pass the containing folder as the pathspec instead (it covers the deletion), after checking that folder holds no other dirty file.
item: RIMMANDRAKE_FOLD_OWNER_MARKS_INTO_ABYSS_AND_ROT_PROPOSALS
home: clone-landing-commits
