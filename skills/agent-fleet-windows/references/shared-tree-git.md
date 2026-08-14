# Many seats, one working tree

Five Claude Code seats, one checkout, one `.git`, one index. Everything below
was measured in this repo. The failures are not hypothetical — each row has a
commit hash attached.

---

## 1. 🔴 `git commit <path>` commits the WORKING TREE, not your index

A pathspec bypasses the index entirely and records **whatever is at that path
right now** — including a peer's uncommitted edits to that same file.

**Consequence: staging carefully first buys you nothing.** The protection a
pathspec gives you is against *other files*, never against *other edits to your
file*.

```bash
git status --porcelain <paths>     # BEFORE any commit
```

If a path you are about to name is dirty with work that is not yours, it is
about to become yours, under your message.

**Corollary, same root cause:** `git rm --cached <f>` followed by
`git commit <f>` silently **re-adds** the file, because the pathspec re-reads
the working tree where the file still sits. To untrack while keeping it on disk:
move it aside, commit the path while it is absent, move it back.

---

## 2. The blanket-stage hook, and why a bare `git commit` is blocked too

`D:\Luke\dev\Rimworld\.claude\hooks\block_blanket_git_stage.py` — a `PreToolUse`
hook on `Bash`, wired in `.claude/settings.json`, returning a `deny` decision.

**Blocked:**

| form | why |
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
and your commit.

MEASURED failures, all real commits in this repo:

- `76d7f64` (2026-08-11) — a blanket add swept three staged `git mv` renames out
  of another thread's in-flight docs audit and committed them under a message
  about load order. The same commit documented a script while leaving the script
  behind, because `commit -a` stages tracked modifications and ignores new
  untracked files.
- `7c15278` and `5f67910` (2026-08-12) — the index race fired twice, and **the
  prescribed `git diff --cached --stat` guard printed the foreign file and was
  still missed**.

> **Discipline does not fix a race. Only removing the index from the path does.**

```bash
git commit path/one.md path/two.xml -F -    # cannot pick up anyone else's work
```

⚠️ **A brand-new file is a two-step**, and the second step still carries the
pathspec:

```bash
git add   path/new.md          # makes the path known to git
git commit path/new.md -F -    # still bypasses the index
```

MEASURED 2026-08-12 in a throwaway repo: with a peer's `theirs.txt` also staged,
`git commit mine.txt` committed only `mine.txt` and left `theirs.txt` staged and
untouched. The belief in circulation had been that the pathspec form "cannot
commit a new file" and that the workaround was a bare commit — which reopens the
exact race. It is true only of an *untracked* path.

🔴 **If the hook blocks you, name the paths. Do not route around it.** It has a
self-test: `.claude/hooks/selftest_block_blanket_git_stage.py`.

---

## 3. A push publishes the TREE, not your change

One branch, several seats. Pushing sweeps up **every** commit every other seat
has landed, ready or not.

**MEASURED: one push carried 225 commits, six of them another seat's.**

- **Never commit to the shared branch expecting it to stay local.** If it must
  not ship yet, branch it.
- **Rejected push → `git pull --rebase`, never `--force`.** A force here
  discards other seats' work, not yours.
- ⚠️ **Never push what should not be published** — secrets, credentials,
  third-party material. That is the only reason to delay a push.

---

## 4. 🔴 A successful commit tells you nothing about the push

Every failure mode on this path is **silent**:

| failure | what you see |
|---|---|
| `push -q` succeeded | nothing |
| `push -q` swallowed an error | **nothing** |
| credentials prompt | the command **HANGS** rather than failing |
| stale remote-tracking ref | `[ahead 0]` — a false all-clear, because that ref only moves when a push *succeeds* |
| `index.lock` collision with a peer | "push succeeded" — having pushed **somebody else's** commit while yours was never made |

The verified form:

```bash
GIT_TERMINAL_PROMPT=0 git push                              # turns a hang into an error
git fetch origin && git rev-list --count origin/main..HEAD  # MUST print 0
git ls-tree -r origin/main --name-only | grep <your file>   # if it is irreplaceable
```

---

## 5. `index.lock` — a dead git or a live peer?

When a git process dies mid-commit it leaves `.git/index.lock` behind and every
other seat sees:

```
fatal: Unable to create '.../.git/index.lock': File exists.
```

That message **cannot** distinguish "a peer is committing right now" from "a
corpse is holding the door" — and the safe reading (wait) is the one that blocks
forever. **MEASURED: five seats sat unable to commit for 19 minutes on exactly
that ambiguity, and nothing reported it.**

```bash
python3 src/RimMandrake/Utils/check_git_locks.py
```

It prints four pieces of evidence rather than a verdict to trust: lock **age**;
**holders** via `fuser` (git holds the lock open for the whole operation, so a
lock nobody has open is a lock nobody is using); any live `git` in `ps -ef` as
the fallback when `fuser` is missing; and **size** — a 0-byte `index.lock` is
the signature of a crashed start.

| verdict | action |
|---|---|
| **STALE** | run the exact `rm` it prints, then proceed |
| **LIVE**, young | a peer is mid-commit. Wait 60 s and re-check — a commit takes seconds |
| **LIVE**, not clearing at 2 min with nothing holding it open | it **is** stale, and is clearable |
| cannot clear, machine going down now | get work **on disk**, skip the commit — see the DEGRADED WRAP, `skills/agent-messaging/SKILL.md` §9b |

---

## 6. Deploys read the tree, not your intent

Any step that copies the repo onto a live target — here
`deploy_custom_mods.py --apply` onto the game install — **overwrites the target
with whatever is in the repo right now**, including a peer's half-finished file.

**Read the plan before `--apply`.** Same root cause as §1: tree-reading
operations do not respect authorship.

---

## 7. Filing instead of dropping

**Ownership decides who fixes something. It never decides whether it gets
written down.**

| the fix needs… | goes to |
|---|---|
| the shared live resource (the running game) | `infrastructure/state/NEXT_RELOAD.md` |
| nothing but an editor or offline tooling | `infrastructure/state/queue/<SEAT>.md` |
| you cannot tell whose it is | the same, tagged `[?]` |
| it is actively destroying work | ⚠️ **the owner, now** — a live hazard is not a todo |

A filing carries: the exact path and line, **what you observed quoted not
paraphrased**, what you already checked **including what came back clean**, and
one clause on why it is theirs. The clean checks are what stop the work being
done twice.

⚠️ **Verify before you file.** A filed problem that is not real costs another
seat a hunt.
