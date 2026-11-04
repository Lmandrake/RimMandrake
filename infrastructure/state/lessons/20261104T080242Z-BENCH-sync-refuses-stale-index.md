seat_sync REFUSED 'dirty files really overlap upstream' even though each file's working-tree bytes equalled origin/main: the index still held my older staged copy (status MM), a third version sync will not drop. Fix: git restore --staged -- <those paths> (index only, never the worktree), then ./sync. Check with: git show origin/main:<p> | cmp - <p>.
home: clone-landing-commits
