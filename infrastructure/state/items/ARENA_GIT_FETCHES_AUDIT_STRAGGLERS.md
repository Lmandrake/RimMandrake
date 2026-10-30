## spec
Audit every `git` subprocess under src/RimMandrake/Utils/arena/ outside arena_safe_git.py. Classify each call site as
BUILDER-controlled (the clone/gitdir/worktree an arm or build helper wrote into: its .git/config, refs, objects) or
HARNESS-owned (source repo, harness-made scratch repo, a dest just `git init --template=`-ed). Migrate every
builder-controlled site to arena_safe_git (git_run/git_argv/safe_env; transport=True and --upload-pack for
fetch/ls-remote). Harness-owned sites stay and are listed in the note so the next audit does not redo them.

## criteria
1. Every builder-controlled call site is listed (file:function) with its class in the item note.
2. Each migrated site has a forced-failure test: trap planted in a throwaway clone (replace, fsmonitor, hooksPath,
   filter, sshCommand/uploadpack, include.path, url.insteadOf as relevant), plain git shown fooled (marker file or
   wrong answer), the migrated call not; test is red when the migration is reverted.
3. selftest_arena_ralph_a, _ralph_a_drill, _ralph_c, _gate, _eventlog, _v3_control, _trio, _switch, _lane and the
   selftests of touched files pass.
