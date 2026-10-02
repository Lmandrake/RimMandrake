# Git migration drain — Phase 6 part A (2026-10-02)

Plan: `design/RimMandrake/git_workflow_plan_2026-10-01.md` §5 "Draining", §2.2, §2.3.
Tool: `src/RimMandrake/Utils/drain_worktrees.py` (run from ext4 against `/mnt/d/Luke/dev/RimMandrake`).

**Archived means reachable, not accepted.** Nothing here was reconciled into main.

## Status

IN PROGRESS — census done, archive tags pushed; dirty snapshots running.

## Census

Measured 2026-10-02 against origin/main `a38adf79a8e8`: **102 worktrees** (100 under
`.claude/worktrees/` on drvfs, 1 `/home/mandrake/wt_p3`, 1 under `/tmp`), **140 refs** (133 local branches,
2 detached worktree HEADs, plus the shared tree's `main`) and **4 stash entries**. None locked, none held
by a visible (WSL) process — Windows processes are invisible to the `/proc` scan.

Only **10 branches are not ancestors of origin/main** (cross-checked: `git branch --no-merged origin/main`
in D:\ also gives 10); the plan's "68 unmerged / 257 unique" was measured before most of them landed.
After patch-id (`git cherry`) and content checks (touched paths at the commit == origin/main), **19 commits
across 10 refs** remain unaccepted, plus the 4 stash commits.

**91 linked worktrees are dirty**, almost all with the same 5 paths the health heartbeat regenerates
(`Transient/codebase_health{.html,.json,_artifact.html}`, `infrastructure/dashboards/…`,
`infrastructure/state/…`); 2 carry hundreds of `Transient/northstar*`/`modcheck*` outputs. A dirty
worktree cannot be removed without `--force` (forbidden), so all 91 stay; their state is snapshotted.

Safe-ignored set for removal: `obj/ bin/ __pycache__ *.pyc .vs node_modules mod_sources/`, `*.lock`,
`Transient/codebase_health_hook.log`, `infrastructure/state/BRIDGE`, `infrastructure/state/derived/`.

| worktree | branch / HEAD | dirty | unaccepted | locked | proc | verdict |
|---|---|---|---|---|---|---|
| `/mnt/d/Luke/dev/RimMandrake` | main | None | 2 |  |  | keep: shared tree |
| `/home/mandrake/wt_p3` | detached 8a2549b7e | 5 | 0 |  |  | keep: dirty (snapshotted) |
| `/mnt/d/Luke/dev/RimMandrake-wt-handoff` | detached 66e940092 | 5 | 0 |  |  | keep: dirty (snapshotted) |
| `/mnt/d/Luke/dev/RimMandrake-wt-livedeploy` | detached c77993069 | 5 | 1 |  |  | keep: archived commits |
| `.claude/worktrees/agent-a02392976818cfb0b` | worktree-agent-a02392976818cfb0b | 5 | 0 |  |  | keep: dirty (snapshotted) |
| `.claude/worktrees/agent-a0ab2dedb67b52608` | worktree-agent-a0ab2dedb67b52608 | 5 | 1 |  |  | keep: archived commits |
| `.claude/worktrees/agent-a0abe60e090975391` | worktree-agent-a0abe60e090975391 | 5 | 0 |  |  | keep: dirty (snapshotted) |
| `.claude/worktrees/agent-a0bec43512946effd` | worktree-agent-a0bec43512946effd | 5 | 0 |  |  | keep: dirty (snapshotted) |
| `.claude/worktrees/agent-a0dad2ca871f1826f` | worktree-agent-a0dad2ca871f1826f | 5 | 0 |  |  | keep: dirty (snapshotted) |
| `.claude/worktrees/agent-a0ddddf2ceed86637` | worktree-agent-a0ddddf2ceed86637 | 1 | 0 |  |  | keep: dirty (snapshotted) |
| `.claude/worktrees/agent-a10296e3637da90dd` | worktree-agent-a10296e3637da90dd | 6 | 0 |  |  | keep: dirty (snapshotted) |
| `.claude/worktrees/agent-a12fd861a545ba263` | worktree-agent-a12fd861a545ba263 | 5 | 0 |  |  | keep: dirty (snapshotted) |
| `.claude/worktrees/agent-a133a1138dc65e4ae` | worktree-agent-a133a1138dc65e4ae | 5 | 0 |  |  | keep: dirty (snapshotted) |
| `.claude/worktrees/agent-a1477dfd9650e8496` | worktree-agent-a1477dfd9650e8496 | 5 | 0 |  |  | keep: dirty (snapshotted) |
| `.claude/worktrees/agent-a1bde88477154716d` | worktree-agent-a1bde88477154716d | 5 | 0 |  |  | keep: dirty (snapshotted) |
| `.claude/worktrees/agent-a1e4e06155363b8bc` | worktree-agent-a1e4e06155363b8bc | 5 | 0 |  |  | keep: dirty (snapshotted) |
| `.claude/worktrees/agent-a2115faa8782c94f6` | worktree-agent-a2115faa8782c94f6 | 5 | 0 |  |  | keep: dirty (snapshotted) |
| `.claude/worktrees/agent-a261ad6e7e7af4185` | worktree-agent-a261ad6e7e7af4185 | 5 | 0 |  |  | keep: dirty (snapshotted) |
| `.claude/worktrees/agent-a2645937576f77cd4` | worktree-agent-a2645937576f77cd4 | 5 | 0 |  |  | keep: dirty (snapshotted) |
| `.claude/worktrees/agent-a292aed282ceaee75` | worktree-agent-a292aed282ceaee75 | 5 | 0 |  |  | keep: dirty (snapshotted) |
| `.claude/worktrees/agent-a30a18be0409158b8` | worktree-agent-a30a18be0409158b8 | 5 | 0 |  |  | keep: dirty (snapshotted) |
| `.claude/worktrees/agent-a30cc4451e0acd60a` | worktree-agent-a30cc4451e0acd60a | 5 | 0 |  |  | keep: dirty (snapshotted) |
| `.claude/worktrees/agent-a3218de47d804daa9` | worktree-agent-a3218de47d804daa9 | 5 | 0 |  |  | keep: dirty (snapshotted) |
| `.claude/worktrees/agent-a3a9b77af1f415739` | worktree-agent-a3a9b77af1f415739 | 5 | 0 |  |  | keep: dirty (snapshotted) |
| `.claude/worktrees/agent-a3cbfe8b3828c5d47` | worktree-agent-a3cbfe8b3828c5d47 | 5 | 0 |  |  | keep: dirty (snapshotted) |
| `.claude/worktrees/agent-a3d3522a0dc2eef1c` | worktree-agent-a3d3522a0dc2eef1c | 5 | 0 |  |  | keep: dirty (snapshotted) |
| `.claude/worktrees/agent-a43ba7332156bafe7` | worktree-agent-a43ba7332156bafe7 | 3 | 0 |  |  | keep: dirty (snapshotted) |
| `.claude/worktrees/agent-a43ce2ebd15c04667` | worktree-agent-a43ce2ebd15c04667 | 5 | 1 |  |  | keep: archived commits |
| `.claude/worktrees/agent-a44eb0a32c3bb5b2c` | worktree-agent-a44eb0a32c3bb5b2c | 5 | 0 |  |  | keep: dirty (snapshotted) |
| `.claude/worktrees/agent-a45b030a60a7b2cc3` | worktree-agent-a45b030a60a7b2cc3 | 8 | 0 |  |  | keep: dirty (snapshotted) |
| `.claude/worktrees/agent-a47c03bf8fbf50ce4` | worktree-agent-a47c03bf8fbf50ce4 | 0 | 0 |  |  | remove |
| `.claude/worktrees/agent-a48112638b900d2cc` | worktree-agent-a48112638b900d2cc | 5 | 0 |  |  | keep: dirty (snapshotted) |
| `.claude/worktrees/agent-a4e097cdf67973884` | worktree-agent-a4e097cdf67973884 | 5 | 0 |  |  | keep: dirty (snapshotted) |
| `.claude/worktrees/agent-a4f89b4041c331e00` | worktree-agent-a4f89b4041c331e00 | 1 | 0 |  |  | keep: dirty (snapshotted) |
| `.claude/worktrees/agent-a54f6cd270cffc856` | worktree-agent-a54f6cd270cffc856 | 5 | 0 |  |  | keep: dirty (snapshotted) |
| `.claude/worktrees/agent-a5d8a7d3826c2ee7a` | worktree-agent-a5d8a7d3826c2ee7a | 5 | 0 |  |  | keep: dirty (snapshotted) |
| `.claude/worktrees/agent-a5dbd7ee890599533` | worktree-agent-a5dbd7ee890599533 | 5 | 0 |  |  | keep: dirty (snapshotted) |
| `.claude/worktrees/agent-a6078aa3a36a0ae9e` | worktree-agent-a6078aa3a36a0ae9e | 5 | 0 |  |  | keep: dirty (snapshotted) |
| `.claude/worktrees/agent-a60fea95dfe4ab06d` | worktree-agent-a60fea95dfe4ab06d | 5 | 0 |  |  | keep: dirty (snapshotted) |
| `.claude/worktrees/agent-a63708bdffef397bb` | worktree-agent-a63708bdffef397bb | 5 | 0 |  |  | keep: dirty (snapshotted) |
| `.claude/worktrees/agent-a6bf24a7234d71b06` | worktree-agent-a6bf24a7234d71b06 | 5 | 0 |  |  | keep: dirty (snapshotted) |
| `.claude/worktrees/agent-a6cb2bce30dd3f2a3` | worktree-agent-a6cb2bce30dd3f2a3 | 5 | 0 |  |  | keep: dirty (snapshotted) |
| `.claude/worktrees/agent-a6dd599f9ccf6975b` | detached 27f8db36b | 0 | 1 |  |  | keep: archived commits |
| `.claude/worktrees/agent-a6de400f8105fde14` | worktree-agent-a6de400f8105fde14 | 5 | 0 |  |  | keep: dirty (snapshotted) |
| `.claude/worktrees/agent-a6e26728e5edb374c` | worktree-agent-a6e26728e5edb374c | 6 | 0 |  |  | keep: dirty (snapshotted) |
| `.claude/worktrees/agent-a71f905d356cffc0e` | worktree-agent-a71f905d356cffc0e | 5 | 0 |  |  | keep: dirty (snapshotted) |
| `.claude/worktrees/agent-a7628f56d960c9ef2` | worktree-agent-a7628f56d960c9ef2 | 5 | 0 |  |  | keep: dirty (snapshotted) |
| `.claude/worktrees/agent-a7845f819b5b7db2f` | worktree-agent-a7845f819b5b7db2f | 5 | 0 |  |  | keep: dirty (snapshotted) |
| `.claude/worktrees/agent-a7aef640ddca2ea00` | worktree-agent-a7aef640ddca2ea00 | 5 | 0 |  |  | keep: dirty (snapshotted) |
| `.claude/worktrees/agent-a7cde2640ceecff76` | worktree-agent-a7cde2640ceecff76 | 5 | 0 |  |  | keep: dirty (snapshotted) |
| `.claude/worktrees/agent-a817d2d77d188563c` | worktree-agent-a817d2d77d188563c | 5 | 0 |  |  | keep: dirty (snapshotted) |
| `.claude/worktrees/agent-a82bba9e9819cefe2` | worktree-agent-a82bba9e9819cefe2 | 5 | 0 |  |  | keep: dirty (snapshotted) |
| `.claude/worktrees/agent-a851bfa146e35205d` | worktree-agent-a851bfa146e35205d | 5 | 0 |  |  | keep: dirty (snapshotted) |
| `.claude/worktrees/agent-a8529dcc68ba7b971` | worktree-agent-a8529dcc68ba7b971 | 5 | 0 |  |  | keep: dirty (snapshotted) |
| `.claude/worktrees/agent-a87a11193411f516e` | worktree-agent-a87a11193411f516e | 5 | 0 |  |  | keep: dirty (snapshotted) |
| `.claude/worktrees/agent-a883fa2541c99ecb1` | worktree-agent-a883fa2541c99ecb1 | 5 | 0 |  |  | keep: dirty (snapshotted) |
| `.claude/worktrees/agent-a88f788f06d554de7` | worktree-agent-a88f788f06d554de7 | 5 | 0 |  |  | keep: dirty (snapshotted) |
| `.claude/worktrees/agent-a8a31f7541396fab8` | worktree-agent-a8a31f7541396fab8 | 5 | 0 |  |  | keep: dirty (snapshotted) |
| `.claude/worktrees/agent-a938d8d0b3726fd59` | worktree-agent-a938d8d0b3726fd59 | 1 | 0 |  |  | keep: dirty (snapshotted) |
| `.claude/worktrees/agent-a97268cdc045210fd` | worktree-agent-a97268cdc045210fd | 0 | 0 |  |  | remove |
| `.claude/worktrees/agent-a9e650b272c547d2e` | worktree-agent-a9e650b272c547d2e | 5 | 0 |  |  | keep: dirty (snapshotted) |
| `.claude/worktrees/agent-aa327ddb76b35239c` | worktree-agent-aa327ddb76b35239c | 7 | 0 |  |  | keep: dirty (snapshotted) |
| `.claude/worktrees/agent-aa4b45ef1781a1816` | worktree-agent-aa4b45ef1781a1816 | 1 | 0 |  |  | keep: dirty (snapshotted) |
| `.claude/worktrees/agent-aa82658f28e7f9cd4` | worktree-agent-aa82658f28e7f9cd4 | 5 | 0 |  |  | keep: dirty (snapshotted) |
| `.claude/worktrees/agent-aa84d6d384b66617c` | worktree-agent-aa84d6d384b66617c | 5 | 0 |  |  | keep: dirty (snapshotted) |
| `.claude/worktrees/agent-aa96bb74b8447d095` | worktree-agent-aa96bb74b8447d095 | 5 | 0 |  |  | keep: dirty (snapshotted) |
| `.claude/worktrees/agent-aa9a8709520b33c21` | worktree-agent-aa9a8709520b33c21 | 5 | 0 |  |  | keep: dirty (snapshotted) |
| `.claude/worktrees/agent-aab5a4281f07d5ff4` | detached b7bb7edae | 279 | 0 |  |  | keep: dirty (snapshotted) |
| `.claude/worktrees/agent-ab03431d6bcc8d162` | worktree-agent-ab03431d6bcc8d162 | 5 | 0 |  |  | keep: dirty (snapshotted) |
| `.claude/worktrees/agent-ab0882ddff1707d0c` | worktree-agent-ab0882ddff1707d0c | 5 | 0 |  |  | keep: dirty (snapshotted) |
| `.claude/worktrees/agent-ab09851982f9d443d` | worktree-agent-ab09851982f9d443d | 5 | 0 |  |  | keep: dirty (snapshotted) |
| `.claude/worktrees/agent-ab1bc6041108190bd` | worktree-agent-ab1bc6041108190bd | 5 | 0 |  |  | keep: dirty (snapshotted) |
| `.claude/worktrees/agent-ab350e3d11f63af80` | worktree-agent-ab350e3d11f63af80 | 5 | 0 |  |  | keep: dirty (snapshotted) |
| `.claude/worktrees/agent-ab4c10bd36f9e4679` | worktree-agent-ab4c10bd36f9e4679 | 5 | 0 |  |  | keep: dirty (snapshotted) |
| `.claude/worktrees/agent-ab602f67ac708b75b` | worktree-agent-ab602f67ac708b75b | 10 | 0 |  |  | keep: dirty (snapshotted) |
| `.claude/worktrees/agent-abdbe7906a7e65382` | worktree-agent-abdbe7906a7e65382 | 5 | 2 |  |  | keep: archived commits |
| `.claude/worktrees/agent-ac0f84ac50e586268` | worktree-agent-ac0f84ac50e586268 | 5 | 0 |  |  | keep: dirty (snapshotted) |
| `.claude/worktrees/agent-ac1ab2efa990605e6` | worktree-agent-ac1ab2efa990605e6 | 7 | 1 |  |  | keep: archived commits |
| `.claude/worktrees/agent-ac4689bac515bb783` | worktree-agent-ac4689bac515bb783 | 5 | 0 |  |  | keep: dirty (snapshotted) |
| `.claude/worktrees/agent-ac7b89266c38507bf` | worktree-agent-ac7b89266c38507bf | 5 | 0 |  |  | keep: dirty (snapshotted) |
| `.claude/worktrees/agent-ac8053cc6bdf8bb59` | worktree-agent-ac8053cc6bdf8bb59 | 5 | 0 |  |  | keep: dirty (snapshotted) |
| `.claude/worktrees/agent-aca6ac98a2b7a0750` | worktree-agent-aca6ac98a2b7a0750 | 0 | 0 |  |  | remove |
| `.claude/worktrees/agent-acea828584fcaf1f1` | worktree-agent-acea828584fcaf1f1 | 5 | 0 |  |  | keep: dirty (snapshotted) |
| `.claude/worktrees/agent-ad132f92ea6f33420` | worktree-agent-ad132f92ea6f33420 | 5 | 0 |  |  | keep: dirty (snapshotted) |
| `.claude/worktrees/agent-ad31e65dd073ff9a1` | worktree-agent-ad31e65dd073ff9a1 | 5 | 0 |  |  | keep: dirty (snapshotted) |
| `.claude/worktrees/agent-adceffd488c26ef10` | worktree-agent-adceffd488c26ef10 | 1 | 0 |  |  | keep: dirty (snapshotted) |
| `.claude/worktrees/agent-add5f52b48a03ed78` | worktree-agent-add5f52b48a03ed78 | 5 | 0 |  |  | keep: dirty (snapshotted) |
| `.claude/worktrees/agent-ae2bb4d24c9c283e0` | worktree-agent-ae2bb4d24c9c283e0 | 13 | 0 |  |  | keep: dirty (snapshotted) |
| `.claude/worktrees/agent-ae8b97baae10b39e0` | worktree-agent-ae8b97baae10b39e0 | 7 | 0 |  |  | keep: dirty (snapshotted) |
| `.claude/worktrees/agent-ae920bacad2b614fc` | worktree-agent-ae920bacad2b614fc | 5 | 0 |  |  | keep: dirty (snapshotted) |
| `.claude/worktrees/agent-aeae257342dcfd8d3` | worktree-agent-aeae257342dcfd8d3 | 5 | 0 |  |  | keep: dirty (snapshotted) |
| `.claude/worktrees/agent-aebc8526d512b897c` | worktree-agent-aebc8526d512b897c | 5 | 0 |  |  | keep: dirty (snapshotted) |
| `.claude/worktrees/agent-aec3bd1cc9177b953` | worktree-agent-aec3bd1cc9177b953 | 5 | 0 |  |  | keep: dirty (snapshotted) |
| `.claude/worktrees/agent-aed40a98576cd94bc` | worktree-agent-aed40a98576cd94bc | 5 | 0 |  |  | keep: dirty (snapshotted) |
| `.claude/worktrees/agent-aee3c0cb0288b9afd` | worktree-agent-aee3c0cb0288b9afd | 6 | 0 |  |  | keep: dirty (snapshotted) |
| `.claude/worktrees/agent-aee8ca27b67f43c6f` | worktree-agent-aee8ca27b67f43c6f | 5 | 0 |  |  | keep: dirty (snapshotted) |
| `.claude/worktrees/agent-af670f7b3d9848060` | worktree-agent-af670f7b3d9848060 | 5 | 0 |  |  | keep: dirty (snapshotted) |
| `.claude/worktrees/agent-af904f79c7e1c5be2` | worktree-agent-af904f79c7e1c5be2 | 0 | 0 |  |  | remove |
| `.claude/worktrees/agent-afaf7be2eec0cf763` | worktree-agent-afaf7be2eec0cf763 | 5 | 0 |  |  | keep: dirty (snapshotted) |
| `.claude/worktrees/agent-afcfb5957ca43a47c` | worktree-agent-afcfb5957ca43a47c | 5 | 0 |  |  | keep: dirty (snapshotted) |
| `/mnt/d/Luke/dev/wt_live2` | detached 1ae95a9d8 | 210 | 0 |  |  | keep: dirty (snapshotted) |
| `/tmp/claude-1000/-mnt-d-Luke-dev-RimMandrake/1a943ca3-44c7-4d42-b421-051361e3fdca/scratchpad/pushwt` | detached f5043be7a | 2 | 0 |  |  | keep: dirty (snapshotted) |

| ref | ahead of origin/main | unaccepted | archive tag |
|---|---|---|---|
| `backup-foundry-pre-reconcile-20260925T174257Z` | 10 | 4 | `archive/backup-foundry-pre-reconcile-20260925T174257Z` |
| `detached/RimMandrake-wt-livedeploy` | 1 | 1 | `archive/detached/RimMandrake-wt-livedeploy` |
| `detached/agent-a6dd599f9ccf6975b` | 1 | 1 | `archive/detached/agent-a6dd599f9ccf6975b` |
| `detached/wt_live2` | 2 | 0 |  |
| `main` | 10 | 2 |  |
| `rescue/feverwood-92bd25209` | 5 | 2 | `archive/rescue/feverwood-92bd25209` |
| `stash/0-676b21035d` | 1 | 1 | `archive/stash/0-676b21035d` |
| `stash/1-0361d58bc9` | 1 | 1 | `archive/stash/1-0361d58bc9` |
| `stash/2-6592a55ead` | 1 | 1 | `archive/stash/2-6592a55ead` |
| `stash/3-8c2d955b86` | 1 | 1 | `archive/stash/3-8c2d955b86` |
| `worktree-agent-a0ab2dedb67b52608` | 1 | 1 | `archive/worktree-agent-a0ab2dedb67b52608` |
| `worktree-agent-a43ce2ebd15c04667` | 1 | 1 | `archive/worktree-agent-a43ce2ebd15c04667` |
| `worktree-agent-a6dd599f9ccf6975b` | 1 | 1 | `archive/worktree-agent-a6dd599f9ccf6975b` |
| `worktree-agent-a9e650b272c547d2e` | 3 | 0 |  |
| `worktree-agent-abdbe7906a7e65382` | 5 | 2 | `archive/worktree-agent-abdbe7906a7e65382` |
| `worktree-agent-ac1ab2efa990605e6` | 1 | 1 | `archive/worktree-agent-ac1ab2efa990605e6` |
| `worktree-agent-aebc8526d512b897c` | 2 | 0 |  |


## Archive tags pushed

(pending)

## Dirty snapshots

(pending)

## Shared tree

(pending)

## Removal

(pending)

## Verification

(pending)
