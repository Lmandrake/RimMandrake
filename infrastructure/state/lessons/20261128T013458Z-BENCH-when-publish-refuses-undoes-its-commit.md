When ./publish refuses and undoes its commit, the new files of that commit become untracked again; a later git commit -- <paths> then fails with 'pathspec did not match' on each new file. git add the new files by path first, then commit by path.
item: RIMMANDRAKE_RESTORE_TREE_WHEN_RED_SEEN_IS_KILLED_PLANT_STAYED_APPLIED
home: skills/clone-landing-commits/SKILL.md
