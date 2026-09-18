# BENCH_REBOOT_HANDOFF_202609180533 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202609180411`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
**The 81 walk findings are NOT rot, and `doctor`'s ORPHAN_WALK is asserting a model a
third of the corpus does not follow.** MEASURED 2026-09-18 with a subject parser that reads
each walk's own `subject:` line: of the 33 failing walks, **25** have a fully live subject and
the defect is a stale identifier inside a STEP, 6 ship with no packageId on the subject line,
1 declares NOT BUILT deliberately, 1 is absorbed with an absorber proven on disk, and **0 are
genuinely orphaned**. `doctor` derives a walk's mod from the walk's BASENAME
(`mod_name_from_walk`), never from its subject line, so its 24 ORPHAN_WALKs and 10
SUBJECT_COLLISIONs are ONE phenomenon: **34 of 78 walks are deliberate per-feature walks
sharing a live mod's subject.**

⛔ **Do not "fix" a walk on an ORPHAN_WALK finding alone, and do not rebuild the decision
sheet.** A 43-row sheet was built for these findings and deleted the same day — the owner's
instinct (*"this doesnt feel like a sheet I should be asked"*) was right twice: wrong as a
format, because where an absorbed mod went is provable from disk and was never his to
adjudicate; and wrong as DATA, because its backtick-only packageId regex read `None` for 50 of
78 walks. Full account in `DETERMINISM_ASSESSMENT.md` §11a.

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
**1. 🔴 The one decision he still owes: the walk model.** Adopt the per-feature
convention with a `feature:` key so `modcheck run` can reach all 34, or collapse 34 walks into
10. He was asked, replied "advise", and my advice REVERSED once measured — I first said merge
(believing the walks were rot), then retracted: a third of the corpus already follows the
convention, so modelling it is not premature abstraction. Still unruled.

**2. His absorbed-walk ruling is recorded and is nearly a no-op.** Verbatim choice: *"Delete
the stale walk, rewrite against the absorber."* ⚠️ It applies to **ONE** walk, not the ~30 I
implied when I asked. Do not go rewriting 30 walks on the strength of that ruling.

**3. 🔴 The FULL modlist still restores the stale pre-merge mods.** Re-MEASURED 2026-09-18 by
PARSING `ModsConfig.FULL.PRECAPTURE.20260917_085900.xml` (631 active): `mandrake.rm.fluidcanals`
PRESENT, `mandrake.rm.pits` PRESENT, `mandrake.rm.flowworks` **ABSENT**, and
`mandrake.rm.environmentalhazards` ABSENT (matching `ENVHAZARDS_NEVER_ACTIVATED_1`). Restoring
that list loads the pre-merge FluidCanals and Pits and never loads FlowWorks — a ~15-minute
cold load proving nothing. ⛔ The live file is a Windows path unreachable from the Mac and
editing it is a Charter expensive-list action: **his hands, on the Desktop.**

**4. Coverage is still zero — independently re-confirmed.** `shows=` appears in **0** of
**54** mod `validation.py` files (my own measurement 2026-09-18, matching CLAUDE.md's 0-of-54,
which the Desktop had already corrected at `7fc491ebc`; the Desktop's VALIDATION_SCRIPT_BACKFILL_1
tripled the script count without adding one line of coverage). ⚠️ I told him CLAUDE.md's figure
was "stale at 17" — that was MY stale reading, corrected here. Every `modcheck run` still
returns REFUSED before the game is consulted, and `NORTH_STAR_PIT_PILOT_1` has never run.

**5. Shipped deliberately, flagged:** three scripts gained the exec bit in git
(`game`, `bridge`, `show.sh`, now 100755). Inert on Windows, and it is why `./game` can run on
the Mac at all. Say so if a Windows-side diff looks odd.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
- `DETERMINISTIC_CHECKER_WAVE_1` — C1/C2/C5/C7/C8/C9 shipped, C3 declined by him.
  **NEXT:** build C4 `modcheck floor --all` (~90 LOC, the triage join nobody has used); then C6
  `rimflow lint --citations`. ⛔ Neither as a blocking PreToolUse hook (§10.9).
- `DETERMINISTIC_CHECKER_WAVE_1` — C1's suite gate is deliberately NOT armed (41 live findings;
  a permanently red checker is a disbelieved one). **NEXT:** arm it only after the walk-model
  ruling lands and the findings are cleared.
- `DETERMINISTIC_CHECKER_WAVE_1` — `bridgetools/selftest_tool_metadata.py` is a third
  Windows-toolchain absence that does not carry the UNMEASURED phrase, so it still counts as a
  real FAIL. **NEXT:** give it the phrase `UNMEASURED, not a pass or a fail` rather than
  widening the matcher in `run_selftests.py`, which would be inventing a signal.
- `PIT_SUPERDEEP_COLLAPSE_1` — fully ruled, nothing built; the ITEM not the 1127-line spec is
  the authority. **NEXT:** revise the spec against the item's ten owed revisions BEFORE any
  code, and put his first implementation question to him: two pits joined by a channel become
  one liquid body — do their fluids merge or refuse to?
- `FLOWWORKS_DOOR_FAMILY_1` — filed, no spec. **NEXT:** spec it and build the TWO-def stuffable
  version (`Sluice`, `SecurityGrateDoor`); ⛔ never the three he talked himself out of.
- Code-review census scope — `find_untracked` scans only `src/`, so new `.claude/hooks/*.py`
  and `skills/**/*.py` land invisible (today just 2 unentered hook files, 0 in skills).
  **NEXT:** widen `UNTRACKED_SCAN_DIR` to those two trees; I told him I would rather than spend
  his attention on it.
Nothing is mid-edit. The 5 generated codebase-health artifacts are committed rather than left
dirty, deliberately — the rebase trap below is why leaving them dirty blocks a rebase.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it to LESSONS_INBOX.md the moment it is learned, then cite `(filed: LESSONS_INBOX)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- 🔴 **A subagent that runs `git reset --hard HEAD` to clear a conflict destroys the
  parent seat's staged work** — same tree, same index. It took 3 of my staged files; recovered
  byte-exact from dangling blobs via `git fsck --unreachable` + `git cat-file -p`, because
  `git add` writes blobs before any commit. Brief subagents that `reset --hard`/`checkout --`/
  `stash` on shared paths is FORBIDDEN — "leave those files alone" reads as licence to clear
  them another way. (filed: LESSONS_INBOX)
- 🔴 **`git rebase --continue` refuses with "You must edit all merge conflicts" while
  `git status` says all conflicts are fixed** — the real cause is an unclean worktree, and here
  it was self-inflicted: `code_review_status.py`'s own `_trigger_health_rebuild` spawns the
  health publisher, so every `prune`/`list` call re-dirties 5 tracked artifacts. Commit them
  (MIN_INTERVAL is 900 s, so it holds) or the rebase can never finish. (filed: LESSONS_INBOX)
- 🔴 **A walk's subject `packageId` is backticked in 28 walks, BARE in 34 and absent in 16** —
  a backtick-only regex reads `None` for 50 of 78 and callers then treat the subject as
  MISSING. `modcheck/doctor.py`'s `_SUBJECT_PKGID_RE` already handles all three; parse the
  subject PATH as primary evidence since it is always present. (filed: LESSONS_INBOX)
- **`modcheck` must be run as a module from its package root** — `python3 -m modcheck.cli lint`
  with `cwd=src/RimMandrake/Utils`. ⚠️ A `cd` in a Bash call PERSISTS across later calls, and
  querying git or globbing from that subdirectory makes `infrastructure/` look deleted — it
  cost a real scare this window. (see: this handoff)
- **The assessment's own premises were wrong twice and are now corrected in place**: C7's
  "make the health publisher separate DIRTY from ORPHANED" was unnecessary (`review_verdicts`
  only iterates live files, so an orphan never entered its census), and C9's "the exec-bit
  finding is spurious here" was false. (see: DETERMINISM_ASSESSMENT.md §11a)
- **A subagent's own report can contradict itself** — C8's claimed 7 boilerplate wordings while
  its selftest printed "four" and covered six fixtures. Re-measuring gave 7, and the fixture
  totals are now DERIVED from the wording list so a new wording adds coverage instead of
  breaking a test. Verify a subagent's numbers by running its tool. (see: DETERMINISM_ASSESSMENT.md §11a)

## Closed since the last handoff (1)

- `HANDOFF_RITUAL_OPTIMIZATION_1` — 217075133

## Filed and still open (0) — the next seat's queue

Nothing filed in this window.

## Commits

```
8b00caf67 Ledger: his absorbed-walk ruling, and the sheet retracted with the re-measurement
3a11c60cc Delete the walk decision sheet — he was right, and its data was wrong too
77041ca73 rimflow: file+close DIRTY_CODE_REVIEW_LOOP_RESTART_15 (this wave's continuity note)
7aea51f56 VAULT_DUNGEON_BUILD_1: record 2026-09-18 pass in the item file
b224e70a8 chore: publish codebase-health artifacts (generated; they block a rebase when left dirty)
260383a30 handoff.py: a blank line ends a bullet in _bullets
c93a3a75d VAULT_DUNGEON_BUILD_1: fresh quicktest screenshots, all 3 templates
2398d6a13 Code review: lift a stale DEPLOY_HOLD entry, mark 6 files clean
10013ce07 MLIE_FAUNA_ABSORPTION_1 Pass 15: port Kreetle, Krykna, Kwi (45 -> 42 remaining)
c2e8ad4ca MINIMAL modlist: fix stale mandrake.rut.vaultdungeons packageId
896456979 Ledger: C8 shipped and verified, walk decision sheet delivered
342362f69 The boilerplate has SEVEN wordings, not four — and record what shipped
0dc1a8cfc Lesson: a subagent's `git reset --hard` eats the parent seat's staged work
4bcd53961 The walk decision sheet he asked for — 43 rows, pre-filled, nothing applied
4a022088e Add canon_census.py: ruled/unruled/non-conforming census + lint (C8)
559e52278 rimflow: ledger sync (HANDOFF_RITUAL_OPTIMIZATION_1 close)
217075133 HANDOFF_RITUAL_OPTIMIZATION_1: audit-driven handoff ritual v2
e7a523ae6 rimflow: file+close DIRTY_CODE_REVIEW_LOOP_RESTART_14 (this wave's continuity note)
f42da4dd6 Code review: mark clean RUT_Greentide/RUT_TarMoat, code_review_status.py, artpipe cluster
ceb78be3e C9: 13 reds were 6 — fix the exec bit, and stop printing UNMEASURED as FAILED
... 12 more: git log --oneline 12a11996c..HEAD
```

## Game / bridge / tree state at wrap

- running   : UNMEASURED   (could not run tasklist.exe — no reading taken)
- recorded  : UP
- Bridge: FREE    since 2026-09-18T03:58:39Z

Working tree clean apart from untracked `Transient/`.

