An 'implemented'/verify brief can cite a lesson-only commit sha instead of the code commit (arena 2026-10-30: 8743729944 and f3040c976c were lesson-only; code was c2fda90ae5/aca3a1e1fb/695fc364f9 and 5ba096ddc5/a3d1a34240/fe4436d196). A verifier must git show --stat the cited sha and find the real code commits by file log before testing.
home: using-rimflow
