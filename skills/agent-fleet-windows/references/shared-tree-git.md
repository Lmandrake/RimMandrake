# Many seats, one working tree — the evidence and the procedures

Five Claude Code seats, one checkout, one `.git`, one index.

🔴 **The RULES live in `D:\Luke\dev\Rimworld\CLAUDE.md`, which every seat loads
every session, and `SKILL.md` §9 states them in short.** This file deliberately
does **not** restate them — it carries only what those cannot: the commit hashes
that prove each failure happened, the hook's exact accept/reject surface, and
the `index.lock` decision procedure. (`infrastructure/DOC_BUDGET.md` rule 1: a
rule gets one durable home.)

---

## 1. Why `git commit <path>` is not the protection people think

A pathspec bypasses the index and records **whatever is at that path right
now**, including a peer's uncommitted edits to that same file.

> **The protection a pathspec gives you is against *other files*, never against
> *other edits to your file*.** Staging carefully first buys you nothing.

```bash
git status --porcelain <paths>     # BEFORE any commit
```

**Corollary, same root cause:** `git rm --cached <f>` then `git commit <f>`
silently **re-adds** the file, because the pathspec re-reads the working tree
where the file still sits. To untrack while keeping it on disk: move it aside,
commit the path while it is absent, move it back.

⚠️ **A brand-new file is a two-step, and the second step still carries the
pathspec:**

```bash
git add   path/new.md          # makes the path known to git
git commit path/new.md -F -    # still bypasses the index
```

MEASURED 2026-08-12 in a throwaway repo: with a peer's `theirs.txt` also staged,
`git commit mine.txt` committed only `mine.txt` and left `theirs.txt` staged and
untouched. The belief in circulation had been that the pathspec form "cannot
commit a new file" and that the workaround was a bare commit — which reopens the
index race below. It is true only of an *untracked* path.

---

## 2. The blanket-stage hook — its exact surface

`D:\Luke\dev\Rimworld\.claude\hooks\block_blanket_git_stage.py` — a `PreToolUse`
hook on `Bash`, wired in `.claude/settings.json`, returning a `deny` decision.
Self-test: `.claude/hooks/selftest_block_blanket_git_stage.py`.

| **blocked** | why |
|---|---|
| `git add -A` / `--all` / `.` / `-u` / `--update` | sweeps every dirty path in the tree, including peers' |
| `git commit -a` / `-am` / `--all` | same, in commit form |
| **`git commit` with no pathspec** | commits the whole **shared index** |
| the same via `git -C <dir> …`, or inside a compound command | the hook parses through both |

**Not blocked:** `git add <explicit paths>` · `git commit <paths> -m "…"` ·
`git commit --amend` · `git commit --pathspec-from-file=<f>` ·
`git diff --cached --stat` · `git restore --staged <p>` · anything non-git.

`-u`/`--update` is included deliberately: it is `commit -a` in `add` form.

### Why the naked `git commit` had to go — the index race

Naming paths on `git add` is **not sufficient**. The index is shared, so a bare
`git commit` commits files another seat staged in the window between your add
and your commit. MEASURED failures, all real commits in this repo:

- **`76d7f64`** (2026-08-11) — a blanket add swept three staged `git mv` renames
  out of another thread's in-flight docs audit and committed them under a
  message about load order. The same commit documented a script while leaving
  the script behind, because `commit -a` stages tracked modifications and
  ignores new untracked files.
- **`7c15278`** and **`5f67910`** (2026-08-12) — the index race fired twice, and
  **the prescribed `git diff --cached --stat` guard printed the foreign file and
  was still missed**.

> 🔴 **Discipline does not fix a race. Only removing the index from the path
> does.** That is why the hook blocks a form that is, in a single-seat repo,
> completely correct.

---

## 3. `index.lock` — a dead git, or a live peer?

When a git process dies mid-commit it leaves `.git/index.lock` behind and every
other seat sees:

```
fatal: Unable to create '.../.git/index.lock': File exists.
```

That message **cannot** distinguish "a peer is committing right now" from "a
corpse is holding the door" — and the safe reading (wait) is the one that blocks
forever. **MEASURED: five seats sat unable to commit for 19 minutes on exactly
that ambiguity, and nothing reported it.**

**MEASURED again 2026-08-14, mid-session: a live peer.** 🔴 **The correct
handling is wait and retry. Never delete the lock** — deleting it on the
assumption it is stale corrupts a peer's in-flight commit, and "stale" is
precisely the thing you cannot tell by looking.

```bash
python3 src/RimMandrake/Utils/check_git_locks.py
```

It prints four pieces of **evidence** rather than a verdict to trust: lock
**age**; **holders** via `fuser` (git holds the lock open for the whole
operation, so a lock nobody has open is a lock nobody is using); any live `git`
in `ps -ef` as the fallback when `fuser` is missing; and **size** — a 0-byte
`index.lock` is the signature of a crashed start.

| verdict | action |
|---|---|
| **STALE** | run the exact `rm` it prints, then proceed |
| **LIVE**, young | a peer is mid-commit. **Wait 60 s and re-check** — a commit takes seconds |
| **LIVE**, not clearing at 2 min with nothing holding it open | it **is** stale, and is clearable |
| cannot clear, machine going down now | get work **on disk**, skip the commit — DEGRADED WRAP, `skills/agent-messaging/SKILL.md` §9b |

---

## 4. Two consequences people meet late

- **A push publishes the TREE, not your change.** MEASURED: one push carried 225
  commits, six of them another seat's. Verification commands: `SKILL.md` §9.
- **Deploys read the tree, not your intent.** `deploy_custom_mods.py --apply`
  overwrites the game install with whatever is in the repo *right now*,
  including a peer's half-finished file. **Read the plan before `--apply`** —
  same root cause as §1: tree-reading operations do not respect authorship.
