A sys.addaudithook hook that guards re-entry with one flag per process drops the events of every other thread while any thread is inside the hook, because the hook's own system calls release the GIL (door read hook: 8 threads lost 361 of 400 reads, 1 thread lost 0). Key the guard by thread id. Also: one O_APPEND write per line from many processes interleaves on /mnt/d (drvfs), so keep an append-only record on a local disk.
item: RIMMANDRAKE_REVIEW_NEW_MACHINERY_BLIND_185_SCRIPTS_ONE_WEEK
home: skills/rimworld-modding/references/project-engine-facts.md
