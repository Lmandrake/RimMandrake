# Git migration — publish wrapper, build route, mirror, codex staging (2026-10-02)

Implements `design/RimMandrake/git_workflow_plan_2026-10-01.md` §2.6, §2.3 (build route + mirror
tooling) and the codex staging of §2.3/§5. Owner authorized full implementation 2026-10-02.

## 1. `./publish` (thin wrapper) — DONE

`src/RimMandrake/Utils/publish.py` (596 → ~200 lines): `git add --all -- <paths>` + `git commit -- <paths>`
+ `git pull --rebase --autostash origin main` + push, ≤8 retries on non-ff, never forced.
- Seat clone → `HEAD:main`. Pool slot (`/home/mandrake/rm/pool/<seat>/slotN`, branch `agent/<name>`) →
  `refs/heads/submit/<seat>/<name>`; a non-ff on a submit ref refuses (the seat has not landed the prior one).
- Any failed push is first checked for ambiguity: fetch, `merge-base --is-ancestor HEAD <target>`; ancestor ⇒ landed.
- Rebase conflict → `rebase --abort`, conflicted paths named, commit left on HEAD.
- Refuses when the repo's realpath is under `/mnt/`, naming `/home/mandrake/rm/<seat>`.
- Deleted: temp-index plumbing, `--catchup`, `--sync`, `--commit`, `--worktrees`, `--no-catchup`.
  `shared_sync.py` prints its retirement and exits 1. `selftest_publish.py` rewritten: 11/11.
- CLAUDE.md Git section rewritten to match (the documented-commands selftest checks it).

## 2. Build route — `winbuild.py`
(in progress)

## 3. Mirror — `./mirror sync`
(in progress)

## 4. Codex staging
(in progress)

## 5. Left open
(in progress)
