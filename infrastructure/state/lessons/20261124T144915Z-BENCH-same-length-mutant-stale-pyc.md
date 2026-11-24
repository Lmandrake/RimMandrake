A mutation that swaps a word for one of the same length (subprocess for own_cgroup) and is restored within the same second leaves a stale .pyc: Python compares mtime in seconds and file size, so the mutant keeps running after the restore. Delete the module's __pycache__ entry after each restore.
item: RIMMANDRAKE_SLIM_TICK_MEMORY_PAGE_BUILD_HITS_ONE_GIG_TICK_TOOK_FIVE_MIN
