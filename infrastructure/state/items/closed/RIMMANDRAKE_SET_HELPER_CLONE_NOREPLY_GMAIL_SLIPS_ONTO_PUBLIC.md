# RIMMANDRAKE_SET_HELPER_CLONE_NOREPLY_GMAIL_SLIPS_ONTO_PUBLIC

## spec

`gh repo view Lmandrake/RimMandrake --json visibility` reads `PUBLIC` (measured 2026-11-19). The user-level rule: a
public repo's commits carry `313496996+Lmandrake@users.noreply.github.com`, set repo-local. The seat clone
`/home/mandrake/rm/bench` has it repo-local; a helper clone made by `src/RimMandrake/Utils/scratch_clone.py` does not,
so it falls through to `~/.gitconfig` (`lukas.mandrake@gmail.com`). Measured in the clone
`/home/mandrake/rm/relentless/clones/RIMMANDRAKE_CRYSTALLIZE_KNOWLEDGE_EVIDENCE_MOVES_NEVER_VANISHES.det`:
`git config --show-origin --get-all user.email` → `file:/home/mandrake/.gitconfig lukas.mandrake@gmail.com`, and its
commit `3b90ed9505` landed on origin/main with that address. Two of the last five commits on origin/main carried it.

Fix: when `scratch_clone.py` creates or reuses a clone, copy the seat clone's repo-local `user.name`/`user.email` (or
run `~/dev/Machinist/tools/install-git-identity.sh`'s per-remote rule) into the clone's `.git/config`. No history
rewrite: past commits stay as they are.

## verify

For a clone `D` that `scratch_clone.py` hands out: `git -C D var GIT_AUTHOR_IDENT` names
`313496996+Lmandrake@users.noreply.github.com`.

## criteria

- A freshly created clone and a reused pool clone both read the noreply identity.
- The seat clone's identity is not changed.

## Acceptance test

```sh
D=$(python3 src/RimMandrake/Utils/scratch_clone.py <create-or-reuse verb> ...) ; git -C "$D" config --get user.email | grep -qx '313496996+Lmandrake@users.noreply.github.com'
```

Expected: exit 0 for a new clone and for a reused one (2 passes). Watched fail on the base: the clone above read
`lukas.mandrake@gmail.com` (repo-local value empty). The exact create/reuse verb is `scratch_clone.py --help`'s; not
looked up at filing.

## refs

file: src/RimMandrake/Utils/scratch_clone.py
none: no def or tier; this is git plumbing
