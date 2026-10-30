Real foundry tree tracks absolute symlinks .claude/skills/* -> /mnt/d/Luke/dev/MandrakeWorkflows/skills; find_leaks now exempts only base-tracked unchanged links (judge-pointing always flagged). A full-tree checkout of the real repo takes ~40 s on ext4 and outlasts 60 s on drvfs: put arm clones on ext4 (/home/mandrake/rm/arena), not /mnt/d.
home: src/RimMandrake/Utils/arena/arena_tasks.py
