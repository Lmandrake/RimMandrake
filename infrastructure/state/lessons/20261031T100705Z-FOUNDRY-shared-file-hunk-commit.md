When another helper co-edits the same file uncommitted, a pathspec commit takes the whole working-tree file. Commit your hunks only: build HEAD+yours in a temp copy, test it, git hash-object -w + update-index --cacheinfo, then write-tree/commit-tree/update-ref guarded on the old HEAD. mark-clean then cannot certify the shared file (on-disk bytes include the peer's code).
home: NONE
