When a live run already landed the fix of a guarded item (one whose fix died before), show the guard red with 'rimflow guard <ID> --test <selftest>' on the unfixed instance: put the parent's version of the fixed code file back in your tree for that one run, then restore it. Close with --sha of the commit whose copy of the test equals the one shown red: a later commit that changed the test (2026-11-27: 207e406f8e after ed970cf55b) makes a close at the first fix sha refuse 'is not the test shown failing'.
item: OPS_WORKER_CLONE_POOL_RESTORE_HMOQ_PBAL
home: skills/using-rimflow
