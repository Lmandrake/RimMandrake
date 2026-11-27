# BOUNDARY: ./publish's door checks queue for a per-machine slot, Design Version 0.1.0

Code: `src/RimMandrake/Utils/treecheck_slots.py` (`Gate`), used by `src/RimMandrake/Utils/publish.py` (`_publish`,
`tree_checks`, `pipeline_checks`). Item: `RIMMANDRAKE_THROTTLE_TREECHECKS_WHEN_DISK_SATURATES_HANG_GUARDS_FIRE`,
written 2026-11-24. On SteveDesktop, 2026-11-24 5:49 PM to 9:41 PM PST, nine detached runs each ended with `./publish`.
Up to six door checks ran at once on one disk: the disk read 100% busy, load reached 47, one publish was starved for
148 minutes, and hang guards fired on healthy git calls. Each promise has a test of its name in
`src/RimMandrake/Utils/selftest_treecheck_slots.py`.

## ACCEPTS (the only inputs this is built for)

- **publishers-on-one-machine.** Any number of `./publish` processes, from any clones, that share one `RM_ROOT`
  (`PUBLISH_RM_ROOT`, default `/home/mandrake/rm`). The gate lives in `RM_ROOT/.treecheck-slots/`. Two machines never
  share a gate.
- **a-filesystem-with-flock.** The gate directory is on a local filesystem where `flock` works (ext4 here).

## DOES NOT SURVIVE (not promised)

- **a-holder-that-hangs-inside-its-checks.** A holder keeps its slot while it lives. The bounds on its own work end
  it: `CHECKTREE_GIT_TIMEOUT_S` for the checkout git calls, `progress_guard` and `CHECK_CAP_S` for each check. The gate
  adds no wall limit of its own.
- **orphaned-check-children.** The slot is the publisher's flock. When a publisher is killed while its check children
  live on, the slot frees, and the next publisher starts beside the orphans.
- **a-gate-directory-that-cannot-be-opened.** Then the publish says so in one line and runs its checks without the
  gate, as before this page. Could not look is not a refusal.
- **other-disk-load.** The gate counts only door checks. The pool monitor's `find` scans, builds and live games are
  not in it.
- **a-check-that-starts-to-read-text.** The `"reads_text": false` mark is a measurement of 2026-11-26. A marked check
  that later starts to read text is not run on a text-only publish. A check with no mark always runs.
- **the-first-text-tree.** The first text-only publish on a machine makes the text tree: a full checkout (about 5 GB),
  outside the slots. Later ones reuse it and write only the files that differ. `rm_pool_room.py` on SteveDesktop counts
  it among the kept trees, but its `KEPT_TREES` still owes one per slot.

## PROMISES (each one is owed a test of the same name)

- **at-most-the-limit-run-at-once.** When more publishes than the limit reach their door checks on one machine, at most
  the limit run their full checkout and checks at the same time. The rest wait, and every one of them finishes.
- **waiters-go-first-come-first-served.** Publishes that wait take the free slots in the order in which they began to
  wait.
- **a-dead-holder-frees-its-slot.** A slot is a lock held by a live process, not a file. When a holder dies (killed,
  `SIGKILL` included), the next waiter takes the slot at once. A waiter that dies leaves the line, and the waiters
  behind it move up.
- **a-waiter-shows-progress.** A publish that must wait says so at once, and again every `SAY_S` seconds, on stderr:
  `waiting <s> s for a tree-check slot, <N> ahead, <K> running (<holders>)`. So a guard on progress never reads the
  wait as a hang.
- **one-publish-holds-one-slot-across-both-checks.** A publish that runs the whole-tree checks and then the pipeline
  checks holds one slot for both. It does not join the back of the line between them.
- **a-check-under-a-held-slot-never-waits-again.** A process started inside a held slot (a door check that itself runs
  a fixture publish) passes the gate at once. So no set of holders can wait on each other.
- **a-publish-with-no-door-checks-takes-no-slot.** A publish whose change runs no door checks (only `skip_when_only`
  paths, no pipeline test touched) neither waits nor takes a slot.
- **a-close-publish-passes-held-slots.** While both slots are held, a publish of only ledger lines, or of a
  `rimflow close` (its ledger line and the move of `items/<ID>.md` to `items/closed/<ID>.md`), lands at once and runs
  no check. A publish that adds live item prose (`items/<ID>.md`) is still checked: `selftest_retired_era_gone`
  judges item file names. Item prose is text, so its checks run on the text tree (next promise). Design (2026-11-26, `RIMMANDRAKE_UNJAM_PUBLISH_DOOR_LEDGER_WAITED_THIRTY_MINUTES`): the
  smallest one that keeps the disk guarded. Such a publish makes no checkout and runs no check, so it adds no disk
  load, and it never needed a slot. `skip_when_only` names `items/closed/*.md`, and `publish.py runs_no_tree_check`
  counts the deleted `items/<ID>.md` of the same move. Measured: on 2026-11-26 the tick's own close (the dispatch
  clone, a ledger line and one prose move) waited in the line behind two pipeline runs of 31 min each. With two
  planted holders, the close publish landed in 0.3 s; on the code before, it still waited after 60 s
  (`evidence/close_publish_parent.txt`).

- **a-text-publish-passes-held-slots.** While both slots are held, a publish of only rule or design text lands: every
  changed path is a `skip_when_only` path or a `.md` file outside `src/`, `.claude/` and `infrastructure/githooks/` that
  no `pipeline_files` glob names (`publish.py text_only`). Such a publish takes no slot. It runs on the machine's text
  tree (a kept full checkout of the landing commit, `TEXT_LANE`): every whole-tree check that is not marked
  `"reads_text": false`, and the pipeline tests whose `inputs` the change matches (`any_change`, such as
  `selftest_conductor_authority.py` for `CLAUDE.md`). A red check refuses it, as at the ordinary door. A publish that
  changes code, a def, a test, a hook, a brief or a pipeline page, alone or with text, still waits for a slot. Design
  (2026-11-26, `RIMMANDRAKE_BUILD_RULING_FAST_PATH_SENTENCE_TOOK_NINETY_MINUTES`): on 2026-11-26 the owner's
  one-sentence ruling, carried into `standing_rulings.md`, waited over 50 min in this line. At 5:35 PM PST that day the
  line held 7 waiters, the oldest 35 min. With two planted holders, a Markdown-only publish was still waiting after 30 s
  on the code before (`evidence/text_publish_parent.txt`), and landed in 0.9 s on the fix. Measured with the door-reads
  hook (2026-11-26, a clone at `4a9fd316d7`): 9 of the 28 whole-tree checks read no text, and they carry the mark; the
  other 19 read a `.md` file, list a folder that holds one, or run git over the whole tree.

## LIMITS

- **`SLOTS = 2`** (`RM_TREECHECK_SLOTS` sets another number for one machine). Danger: the 2026-11-24 SteveDesktop
  failure above. Evidence, measured on Archmagi 2026-11-24 9:47 to 10:01 PM PST at load 10 to 15
  (`evidence/measure_archmagi.jsonl`, made by `evidence/measure.py`): one door check run (full checkout and the 23
  checks) took 50 s alone. With 2, 4, 6 and 8 started at once, each took 44, 82, 133 and 179 s. So the machine's
  throughput is the same from 2 up (about 22 s of wall per run), and each run past 2 only adds wait and load (load 34 at
  4, 68 at 8). SteveDesktop was not measured: its disk was saturated by live runs, and a measurement there would have
  slowed them.
- **Measured again on Archmagi, 2026-11-26** (`RIMMANDRAKE_UNJAM_PUBLISH_DOOR_LEDGER_WAITED_THIRTY_MINUTES`). A slot
  holder's run is no longer the 50 s above. The tree checks are now 28 and take 21 to 40 s. A publish that changes a
  pipeline file then runs the pipeline tests in the same slot. Eleven green door runs are in the `waitalive` logs of
  the day, at load 15 to 30. In nine of them, the pipeline checks ran 220 to 229 tests and took 396 to 608 s. In two,
  they ran 2 tests and took 163 and 176 s. So one slot is held about 7 to 11 min for a typical pipeline publish.
  - **With two at once.** Each run above was with two at once: from 1:52 PM to 4:23 PM PST, both slots were held
    without a break, and 5 to 12 publishes waited in the line. One publish waited 2785 s (46 min) for a slot.
  - **Alone: UNMEASURED.** Neither slot was free during this run. A third run beside the two holders would be the load
    that this limit guards against. The nearest reading: all 243 pipeline tests run outside the door, 6 at once, took
    728 s at load 29.
  - **A red test made a slot hold 22 min or more.** Each red was run again on HEAD's commit and on the base. With both
    kept trees held, each re-run tree was a fresh 5044 MB checkout (34.8 s and 28.0 s). On 2026-11-26 four pipeline
    tests were red on origin/main, so many publishes paid for those re-runs. Those four tests are repaired, and
    `RIMMANDRAKE_FIT_PUBLISH_PROOF_TREES_STEVEDESKTOP_POOL_DISK` now re-runs HEAD's commit in the checks' own tree. The
    base re-run still makes a fresh tree while both kept trees are held.
  - The time is mostly the number of pipeline tests that a change selects, and the slowest ones. The door now leaves
    out a test whose last green run read no changed path (`design/specs/2026-11-26-door-reads/boundary.md`: a
    `publish.py` change drops from 228 to 102 tests). `selftest_conductor_authority.py`, the slowest test, drops from
    196 s to 64 s.
  - SLOTS stays 2. This measurement shows a long line, not a disk that two runs at once saturate.
- **`SAY_S = 30`**. Not a limit: the interval of the waiting line. The wait goes on.
- **The wait itself has no limit.** It is a guard on progress: the line moves while the holders live, and each holder's
  work is bounded by the limits named above.

## PROOF

- 2026-11-24 10:28 PM PST, Archmagi: four `./publish` runs of trivial commits, from four scratch clones, started at
  once (`evidence/proof4.py`, timeline in `evidence/proof4.json`). All four printed `PUBLISHED`. At most 2 of them held a
  check tree at the same time, and at most 2 slots were locked (`/proc/locks`). The two that waited printed the waiting
  line at 0 s and 30 s, and took a slot after 51 s and 52 s.
- The selftest was red on the code before the gate (`evidence/selftest_red_old_publish.txt`: 4 probes at once) and
  caught 4 of 4 plants (`evidence/selftest_mutants.txt`).
