# Buildup prevention — design pass, 2026-10-18

Owner, 2026-10-18: *"we need to create some more rules/designs to prevent this enormous buildup
from repeatedly happening if we can in a design pass."*

Status: DESIGN ONLY. Nothing here is built. Estimates are ESTIMATED agent-hours, not measured.
A parallel helper is cleaning today's mess; this doc is about it not coming back.

## What was measured today (BENCH clone, mid-cleanup, 2026-10-18)

| what | measurement |
|---|---|
| `/` disk | hit 100% earlier (FOUNDRY lesson `20261018T165334Z`); 27% after the cleanup started |
| `~/.seat-tmp/FOUNDRY` | `pushclone` 13 GB, `pubclone` 7.8 GB, `rebase_clone` 6.9 GB — hand-made clones, none from `scratch_clone.py` |
| `~/.seat-tmp/BENCH` | `saves_backup_20261016b` and `…c` 5.4 GB each; `claude-1000` was 50 GB before the helper reached it |
| `/home/mandrake/rm/scratch/BENCH` | 12 GB |
| BENCH `git status --porcelain` | 8,095 lines: 18 modified, 8,077 untracked; 7,605 of them `Transient/biome_ffar/img/` |
| `src/` dirty | 145 untracked paths: 100 under `art_source/`, 40 under `northstar/` |
| `conversations/` | 46 dirty, 15 tracked in total — the records are almost never committed |
| `Transient/` | 12 GB on disk, **25,538 tracked files**; `.git` is 8.6 GB |

## The common root cause

Every source below has the same shape: **a writer puts its output somewhere nobody is assigned to
empty**, and the only safeguard is a prose rule ("~14-day shelf life", "delete a finished clone").
Prose rules about cleanup are never enforced, because cleanup is nobody's next action. Three fixes
recur: move the WRITER's output path; make the residue invisible to git *or* owned by a timer;
and make a gauge alarm before the disk does.

A second shared cause: since redesign #4 **each seat has its own clone**, so a dirty file in
`/home/mandrake/rm/bench` was written by BENCH, a BENCH subagent, or a timer running in BENCH
(`rm-selftests-nightly`). "Not ours, left untouched" is almost never true there — it is a way to
say "nobody's".

## Source 1 — scratch clones and backups under `~/.seat-tmp/<SEAT>` and `rm/scratch`

**Root cause.** `claude-seat-tmp.conf` ages `~/.seat-tmp` entries after 3 days, but tmpfiles skips
any directory under a held flock, and **every live seat holds a flock on its own dir** — a seat
that stays up for days is never aged at all. Agents also make clones by hand (`pushclone`,
`pubclone`, `rebase_clone`) instead of through `scratch_clone.py`, and copy the whole Saves
folder (5.4 GB) per backup. `block_tmpfs_clone.py` only refuses `/tmp`, not ext4 scratch.

**Prevention.**
1. *Writer first:* extend `block_tmpfs_clone.py` to refuse `git clone` anywhere except through
   `scratch_clone.py` (its refusal names the command). `scratch_clone.py clone` stamps a
   `.scratch_meta.json` (seat, purpose, created, ttl default 24 h).
2. *Reaper (`rm-scratch-reap.timer`, hourly):* for each clone under `rm/scratch/*` and
   `~/.seat-tmp/*` older than its TTL: if `git log origin/main..HEAD` is empty AND
   `git status --porcelain` is empty → delete; otherwise **never delete** — move nothing, write
   one alarm line naming the clone and its unpushed/untracked count (the
   `CRACKEDLANDS_FULL_RENAME_1` loss today was a delete of an unpushed clone). Runs regardless of
   the seat flock; the flock only guards the seat's own tmp files, not clones.
3. *Saves backups:* `saves_backup_*` keep the newest 2 per seat; older ones are deleted by the
   reaper (owner question Q4). Owner-review savegames are a different thing and are never reaped.
4. *Gauge:* see Source 7.

**Cost** 3 h. **Risk** deleting a clone that holds work — mitigated by the two-condition test and
alarm-not-delete for anything dirty. **Do NOT automate** deleting a dirty or unpushed clone, ever.

## Source 2 — northstar/proof run results inside `src/`

**Root cause.** `FlowWorks/validation.py`, `northstar/sprinkler_live.py`, `northstar/manifest.py`
(and GimmeSomeSlack's twins) write `*_result_<ts>.json` / `proof_*_<ts>.json` next to the source,
one per run. Each run is a program-read artifact, which CLAUDE.md already says belongs outside
the repo; the writer was never pointed there.

**Prevention.**
1. *Writer first:* one helper `run_output_dir(mod)` returning `/home/mandrake/rm/runs/<SEAT>/<mod>/`
   (ext4, untracked, TTL 14 days via the reaper), used by every northstar/proof writer.
2. Where a result IS evidence (a `modcheck` record, a validated north-star bar), the recording
   tool copies that ONE file into the tracked location it already uses; nothing else is kept.
3. `.gitignore`: `src/**/northstar/*_result_2*.json`, `src/**/proof_*_2*.json` as a backstop.

**Cost** 2.5 h (a grep for every writer + selftest that no writer targets `src/`). **Risk** a tool
reads "the latest result" by globbing `src/` — the grep must find readers too (`manifest.py`).

## Source 3 — `art_source/*/raw|out` logs and PNGs

**Root cause.** Per-mod art scripts (`art_source/PitRamp/v2/…`, WreckedMachines `Source/`) write
model output, cut PNGs and `codex` logs beside the source. The PNGs are **generated art and are
never disposable** (standing memory); the `.log` files are.

**Prevention.**
1. `.gitignore`: `src/**/art_source/**/*.log` (logs only).
2. *Writer first:* new art goes through the artpipe/art ledger (`art install`), whose store is
   already outside the tracked tree; the per-mod scripts get a one-line refusal pointing there.
3. Existing untracked art PNGs: **commit them** (they are small and owed), one commit per mod,
   by the seat that finds them — not ignored, not deleted.

**Cost** 1.5 h. **Do NOT automate** deletion or ignoring of any PNG.

## Source 4 — `deployed/config/ModsConfig.before-tier-*.xml`

**Root cause.** `modset_builder.py` writes a backup of the live ModsConfig into the tracked
`deployed/config/` before each tier swap, and a tracked one is rewritten in place.

**Prevention.** Write backups to `infrastructure/state/modlists/` with the already-ignored
`ModsConfig.PRESWAP.<ts>.xml` naming, keep the newest 10 (the builder prunes on write),
`git rm` the tracked `before-tier-*` copies. **Cost** 1 h. **Risk** `selftest_modset_restore.py`
reads the old path — update it in the same change.

## Source 5 — `Transient/` past its shelf life

**Root cause.** "~14-day shelf life" has no executor. Everything is *tracked*, so 25,538 files
and their history ride every clone (7-14 GB each). Image caches (`biome_ffar/img/*.webp`,
`*_full.png`, 7.6k files) are regenerable output of the sheet server, not human-read pages.

**Prevention.**
1. `.gitignore`: `Transient/**/img/` (sheet caches, regenerable) — confirm the sheet builder
   regenerates them before ignoring.
2. *Reaper (nightly, `rm-hygiene.timer` 03:30, after selftests):* a tracked `Transient/<dir>/`
   whose newest commit is >14 days old is `git rm`'d and landed via `land.sh` **unless** it is
   pinned: contains a `.keep` file, or a `*.decisions.json` not yet enacted, or a live item /
   served sheet names it. One commit per night, subject `Transient reap: N dirs >14d`.
3. Q1 asks whether Transient should stay tracked at all.

**Cost** 4 h (pin detection is the work). **Risk** reaping a sheet the owner is mid-way through —
the served-sheet and decisions pins cover it. **Do NOT automate** removing any `decisions.json`.

## Source 6 — `conversations/` records

**Root cause.** `~/dev/Lodestar/bin/conversations.py` "never commits" and relies on the hourly
sweep — but the Lodestar registry runs RimMandrake at **send off** (the sweep once swept authored
work in this multi-agent repo), so in practice **nothing ever commits them**.

**Prevention.** A RimMandrake-only step that lands `conversations/*.md` by explicit path through
`land.sh` — either inside `handoff.py` (it already runs `conversations.py`) or on the nightly
hygiene timer (Q3). **Cost** 1 h. **Risk** low; records are append-mostly and per-session.

## Source 7 — decisions/lock/serve residue

`*.serve.log` is ignored; lock files beside decisions are not. Add
`Transient/**/*.decisions.json.lock` and `*.lock` under sheet dirs to `.gitignore`.
**Modified `decisions.json` files are owner picks**: never ignored, never reaped; the gauge lists
any modified for >24 h so the seat that serves the sheet commits it. **Cost** 0.5 h.

## Cross-cutting 1 — the disk/git health gauge

One script `hygiene_check.py` (report-only, ~1 s on ext4), called by `rimflow seat ready` and
by `rm-hygiene.timer`, modelled on `rm-selftests-nightly` (oneshot, Nice=15, log to
`Transient/hygiene_nightly.log`, alarm into the pulse/hub health feed the owner already sees):

| check | warn | refuse (seat ready / clone spawn) |
|---|---|---|
| `/` used | 75% | 90% |
| scratch total (`rm/scratch` + `~/.seat-tmp`) | 40 GB | 100 GB |
| dirty clone past TTL | any | — |
| untracked files in a seat clone (ignored excluded) | 300 | — |
| modified `decisions.json` older than 24 h | any | — |
| tracked `Transient/` dirs past 14 d not pinned | count | — |

"Refuse" refuses only spawning clone-heavy work and prints the reap command; the seat still runs.
**Cost** 3 h. **Risk** an alarm nobody reads — it must land where the owner already looks.

## Cross-cutting 2 — handoff stops waving "not ours" through

`handoff.py` already demands a WHOSE per dirty line. Change:
1. **Ownership by default:** a dirty path in a seat's clone is that seat's unless a timer's known
   output pattern claims it. The template says so and the placeholder becomes a VERB, not a name:
   `commit` · `ignore <pattern>` · `delete` · `item <ID>`.
2. **Repeat refusal:** `--check` diffs the dirty list against the seat's previous handoffs; a path
   carried unresolved (or "not ours") through **3 consecutive handoffs** is refused until it has
   one of the four verbs, and the refusal names it.
3. Collapse by directory: 7,605 `img/` lines become one line with a count, so the list is readable
   and actually triaged.

**Cost** 3 h incl. selftest. **Risk** handoff becomes a chore — the directory collapse and the
ignore rules above should leave a handful of lines.

## What NOT to automate

- Generated art (any PNG/webp a human might pick from) — never deleted, never ignored by a reaper.
- `*.decisions.json` — owner picks; only committed, never reaped or regenerated over.
- Any clone with unpushed commits or untracked files; item prose in a clone.
- Owner-review savegames and his Saves folder (only *our* backup copies get the keep-2 rule).
- `conversations/` records — committed, never pruned.
- Anything in the other seat's clone: the reaper reports, the owning seat acts.

## Ranked build list (≈ 22 agent-hours ESTIMATED total)

1. `hygiene_check.py` gauge + `rm-hygiene.timer` + `seat ready` hook — 3 h. *Makes every other
   failure visible before the disk fills.*
2. Scratch reaper + `scratch_clone.py` TTL stamp + clone-outside-scratch refusal — 3 h.
   *Today's 100% disk.*
3. Writer moves: northstar/proof → `rm/runs/<SEAT>`, ModsConfig backups → ignored `modlists/` — 3.5 h.
4. `.gitignore` batch (art logs, Transient img caches, sheet locks, result backstops) — 1 h.
5. Handoff: ownership by default, verbs, 3-strike refusal, directory collapse — 3 h.
6. Conversations commit step — 1 h.
7. Transient reaper with pins — 4 h.
8. Commit existing orphan art PNGs per mod — 1.5 h.
9. Selftests for 1, 2, 5, 7 — 3 h (included above where small; this is the remainder).

## Draft standing rules (one line each; for the owner to adopt into CLAUDE.md / CHARTER)

- R1: A tool that writes per-run output writes it outside the repo (`/home/mandrake/rm/runs/<SEAT>/`); writing into `src/` is a bug.
- R2: Every clone is made by `scratch_clone.py` and carries a TTL; the reaper deletes it only when clean and fully pushed.
- R3: A dirty file in your seat's clone is yours; a handoff resolves it with commit, ignore, delete or an item ID — never "not ours".
- R4: `Transient/` shelf life is enforced by the nightly reaper; pin a dir with `.keep` to keep it.
- R5: Before spawning clone-heavy work, `hygiene_check.py` must not say REFUSE.

## Owner questions

**Q1. Should `Transient/` stay in git?** It is 25,538 tracked files today, and every one stays in
history (and every clone) even after deletion.
- A — Keep it tracked; the nightly reaper removes folders older than 14 days. *Recommended:* nothing
  you rely on changes; history still grows, but slower.
- B — Stop tracking it; only folders you pin get committed. Clones shrink over time; anything not
  pinned is only on the machine that made it (not visible from the phone or the other seat).
- C — Leave it as it is.

**Q2. May the reaper delete a stale scratch clone on its own?**
- A — Yes, after 24 hours, but only if it has no unpushed commits and no unsaved files; anything
  else just raises an alarm. *Recommended.*
- B — Never delete; alarm only, and a seat deletes by hand. Safest, but this is how 175 GB built up.

**Q3. Who commits the conversation records?**
- A — A nightly job in this project commits just `conversations/`. *Recommended:* works even when a
  session ends without a handoff.
- B — Each handoff commits them. Misses every session that never hands off.
- C — Turn this project's Lodestar sweep sending back on. It once swept up work in progress here.

**Q4. How many copies of the Saves-folder backup do we keep?** (5.4 GB each; your review saves are
not affected.)
- A — The newest 2 per seat. *Recommended.*
- B — The newest 5.
- C — Keep all until you say delete.
