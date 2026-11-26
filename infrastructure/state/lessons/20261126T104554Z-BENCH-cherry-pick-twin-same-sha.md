A test fixture that makes a 'twin' by cherry-picking a commit onto the same parent can make the SAME sha (same tree, parent, author and committer second), so no twin exists and the test passes or fails by the clock. Move the other branch first (one commit), then cherry-pick, and assert the shas differ.
item: RIMMANDRAKE_TRACE_DESIGNER_TWIN_COMMIT_LAND_SAID_LEVEL
home: skills/clone-landing-commits
