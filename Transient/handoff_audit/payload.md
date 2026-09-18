# Handoff Template Audit — 12 most recent REBOOT_HANDOFF files

## Scope & method
Selected via `git log --format="%h %cI" --diff-filter=A --name-only -- "infrastructure/state/items/*REBOOT_HANDOFF*"`,
ordered by commit time (newest first), top 12:

1. BENCH_REBOOT_HANDOFF_202609180411.md (12a11996c)
2. FOUNDRY_REBOOT_HANDOFF_202609180351.md (c830d86bb)
3. FOUNDRY_REBOOT_HANDOFF_202609180218.md (cd237a4ac)
4. BENCH_REBOOT_HANDOFF_202609180208.md (23d41cb44)
5. BENCH_REBOOT_HANDOFF_202609172331.md (2de4bd27d)
6. BENCH_REBOOT_HANDOFF_202609172203.md (dc71e87aa)
7. BENCH_REBOOT_HANDOFF_202609171637.md (c046853da)
8. MACBENCH_REBOOT_HANDOFF_202609162042.md (f7a940c7e)
9. BENCH_REBOOT_HANDOFF_202609160549.md (6d8d450d8)
10. BENCH_REBOOT_HANDOFF_202609160516.md (1433a9dd6)
11. BENCH_REBOOT_HANDOFF_202609160504.md (2ed732a4d)
12. BENCH_REBOOT_HANDOFF_202609132330.md (05af75f44)

Template reference read from `src/RimMandrake/Utils/handoff.py` (`build()`, `JUDGEMENT_SECTIONS`).
Script-generated ("mechanical") sections: Closed since the last handoff / Filed and still open /
Commits / Game-bridge-tree state at wrap. Agent-filled ("judgment") sections: The one thing to
carry forward / What the owner should see / What is half-done, and where it stops / Traps learned.

**File #12 (BENCH_132330) does not use the template at all** — its headers are
"THE ONE THING IN FLIGHT RIGHT NOW", "Today's MAJOR RULINGS", "Walk verdicts already ruled",
"State of the push", "Traps re-paid today so you don't", "Open questions for the owner mid-walk".
Predates or bypasses `handoff.py` entirely (script's own git-log `-S` history shows `handoff.py`
existed by this date, so this is a hand-written deviation, not a pre-script artifact). Excluded
from the line-count/fraction analysis below; noted as its own template-conformance defect.

## 1. Line counts per section, mechanical vs judgment

| file | total | judge lines | mech lines | mech fraction (of judge+mech) |
|---|---|---|---|---|
| BENCH_180411 | 241 | 81 | 154 | 0.655 |
| FOUNDRY_180351 | 263 | 131 | 126 | 0.490 |
| FOUNDRY_180218 | 844 | 137 | 701 | 0.837 (outlier — see below) |
| BENCH_180208 | 275 | 99 | 170 | 0.632 |
| BENCH_172331 | 233 | 85 | 142 | 0.626 |
| BENCH_172203 | 298 | 162 | 130 | 0.445 |
| BENCH_171637 | 334 | 136 | 192 | 0.585 |
| MACBENCH_162042 | 194 | 130 | 60 | 0.316 |
| BENCH_160549 | 148 | 105 | 37 | 0.261 |
| BENCH_160516 | 165 | 110 | 46 | 0.295 |
| BENCH_160504 | 301 | 120 | 175 | 0.593 |
| BENCH_132330 (off-template) | 98 | n/a | n/a | n/a |

Mean per-file mechanical fraction across the 11 template-conforming files: **~0.52 (52%)**.
Pooled (sum-of-lines) fraction: 1933/3229 = 0.60, but that pool is dominated by
FOUNDRY_180218's 701 mechanical lines; excluding that one outlier the pooled fraction drops to
0.515. **FOUNDRY_180218's Commits section alone is 556 of its 844 total lines** — see finding #2
below (window-since-last-FOUNDRY-handoff spans days, sweeping in every seat's commits, not just
FOUNDRY's own).

## 2. Judgment-section quality flags

**(a) Boilerplate "nothing this wave"**: **0 of 44 judgment sections** (11 files × 4) in this
sample use the boilerplate escape hatch. Every judgment section across all 11 template-conforming
files carries substantive, specific content (verified: `grep -i "nothing this wave"` across the
corpus only ever matches the HTML-comment PROMPT text itself, never agent-written content, in
these 12 files). This flag does not fire in the sampled window — either discipline held, or the
wave cadence (mostly sub-24h between handoffs) means there is usually something to report.

**(b) Template instructions left unfulfilled, invisible to `--check`**: **CONFIRMED, 7 of 11
files.** The script writes, verbatim, above every non-empty `git status --short` dump:

    Uncommitted (say for each whether it is yours or another seat's):

In 7 of 11 files this header is left completely unedited and the raw `git status --short` dump
follows with **zero per-line or blanket attribution** — the agent never satisfied the instruction
at all, and `--check` cannot detect it because it only greps for the `<<< WRITE THIS >>>` token,
which never appears here (this text isn't a TODO marker, it's fixed boilerplate the script always
writes). Confirmed by inspecting the literal line range between the header and the closing
fence in each:
  - BENCH_180411.md:161-239 (raw dump, no attribution)
  - FOUNDRY_180351.md:199-261 (raw dump, no attribution)
  - FOUNDRY_180218.md:782-842 (raw dump, no attribution)
  - BENCH_172331.md:167-231 (raw dump, no attribution)
  - BENCH_172203.md:290-296 (raw dump, no attribution)
  - MACBENCH_162042.md:185-192 (raw dump, no attribution)
  - BENCH_160549.md:140-146 (raw dump, no attribution)

Contrast with the 2 files that DID fulfill it, proving it's achievable within the same template:
  - BENCH_160516.md:153 — rewrote the header itself to "Uncommitted — **all of it is the OTHER
    BENCH's, none of it mine**:", then per-line trailing notes ("M infrastructure/state/queue/
    BENCH.md       derived view, regenerates").
  - BENCH_180208.md:190 — rewrote the header to "Uncommitted (whose): everything below is
    ANOTHER SEAT'S mid-flight work".
  (2 files had a clean tree, so the instruction never fired: BENCH_171637, BENCH_160504.)

**(c) Changelog-in-disguise**: **0 confirmed instances.** Cross-checked every judgment-section
bullet against that same file's own `## Commits` list (commit subject lines, lowercased,
substring match ≥15 chars) across all 11 template-conforming files — zero verbatim hits. The
judgment sections consistently add analysis/causal explanation beyond the commit subject (e.g.
BENCH_172203's "Traps learned" #2: not just "fixed grep -c bug" but *why* it lied, *how* it was
caught, and the generalizable rule). The specific failure mode CLAUDE.md warns about
("changelog-in-disguise") is not present in this 12-file sample.

## 3. Duplication spot checks (3-4 per file max, sampled not exhaustive)

- **BENCH_172203.md's "Traps learned" duplicates CLAUDE.md content authored in the SAME COMMIT.**
  `git log -S"backgrounded \`Agent\` dies at 600"  -- CLAUDE.md` and `git log -S"grep -c '<li>'"
  -- CLAUDE.md` both bottom out at `dc71e87aa` — the exact commit that carries
  BENCH_REBOOT_HANDOFF_202609172203.md itself. So two of its "Traps learned" bullets (the 600s
  backgrounded-Agent kill, and the `grep -c '<li>'` ModsConfig miscount) were written twice in
  the same commit: once as CLAUDE.md's durable-channel entry, once again as handoff prose with
  no cross-reference between them. Not wrong, but redundant authorship the template does nothing
  to discourage (no "see CLAUDE.md" pointer convention).
  - A THIRD bullet in the same section (Pits `__pycache__` existence-vs-identity trap) was
    *correctly* handled: the CLAUDE.md entry for it predates this handoff
    (`git log -S"holds only \`__pycache__\`" -- CLAUDE.md` → `c046853da`, 09:40:43, six hours
    before dc71e87aa's 15:09:56), and the handoff bullet explicitly says "This is already in
    CLAUDE.md and it still bit twice this window" — i.e. self-aware duplication, pointing at the
    prior source rather than re-explaining it. This is the template working as intended; the
    first two bullets are the counter-example.
- **BENCH_180208's "What is half-done" vs `DESERT_TRIBES_FIRE_HARVEST_1` / `MAYREQUIRE_
  OPERATION_INERT_SWEEP_1` item files**: spot-checked, the handoff bullets are compressed
  pointers ("needs a design pass + owner cards", "~18 more files carry the inert form") rather
  than restatements of the item files' own content — no verbatim duplication found.
- **BENCH_180411 / BENCH_180208 "What the owner should see" both mention "Ten Pyrelands
  north-star bars"** — not duplication within one file, but the same fact restated across two
  consecutive handoffs (see §4 below; also relevant here since the second telling adds no new
  information beyond "still true").

## 4. Cross-handoff repetition (same seat, 2+ consecutive)

- **CONFIRMED — MayRequire-on-Operation-is-inert.** BENCH_180208 ("The one thing to carry
  forward"): "**MayRequire on a patch `<Operation>` is INERT**... Fixed at `01eca070e`;
  repo-wide sweep filed as `MAYREQUIRE_OPERATION_INERT_SWEEP_1`". The very next consecutive
  BENCH handoff, BENCH_180411, restates the same class of defect as its OWN headline "one thing
  to carry forward" ("a value the game reads is not the value you wrote, and nothing errors...
  every MayRequire-gated def... has silently not existed") and repeats the rule a third time in
  its own "Traps learned" ("MayRequire on def nodes deletes content with zero log lines... census
  the mod LIST, never the log"). Three consecutive re-explanations of the same mechanism instead
  of one pointer to `MAYREQUIRE_OPERATION_INERT_SWEEP_1` or a CLAUDE.md line. (CLAUDE.md today
  has a related but distinct line — "A patch that matches nothing logs nothing" — not this
  specific MayRequire-on-Operation form, so the durable channel was never actually given this
  lesson in citable form; each handoff re-derives it instead.)
- **Ten Pyrelands north-star bars await his yes** appears near-verbatim in BENCH_180208 and
  BENCH_180411 (both "What the owner should see") — same fact, same phrasing, two consecutive
  handoffs, no pointer to the owning item/doc (`design/validation_walks/RimMandrake/Pyrelands.md`)
  in the second telling beyond the fact itself.
- Traps NOT found repeating consecutively despite superficially looking like candidates:
  "backgrounded Agent 600s kill" (BENCH_160504 and BENCH_172203 both carry it, but 4 handoffs sit
  between them — not consecutive, and by 172203 it's framed as citing the already-filed
  LESSONS_INBOX entry, not re-deriving it).

## 5. Staleness mechanics

**Both filename schemes present in repo history, but not within these 12.** All 12 sampled files
use the `<SEAT>_REBOOT_HANDOFF_<YYYYMMDDHHMM>.md` numeric-stamp scheme. Scrolling the full
`git log` output one page further back shows the OLDER letter-suffix scheme still in the
repository as of early September: `FOUNDRY_REBOOT_HANDOFF_20260906D.md`,
`..._20260906C.md` (commits `ded2fd4af`, `9279da378`). `handoff.py`'s own `previous_handoff()`
docstring explicitly calls this out as a solved trap ("digits sort before letters, so the newest
file sorted THIRD... filenames are not a clock" — ordering is by git commit time, not filename).
Confirms the scheme migration happened but the two families still coexist on disk/in history;
the ordering bug this caused is documented as already fixed in the script, not re-verified live
here (out of scope — would require re-running `previous_handoff()` logic by hand across the old
files, which the stop condition's 12-file cap does not cover).

**"Game/bridge state wrong at successor wake"**: spot-checked one case cheaply via the ledger
(`infrastructure/state/ledger/events.jsonl`, `"event":"bridge"` lines). FOUNDRY_180218
(committed `cd237a4ac`, 2026-09-18T02:20:48Z) recorded "Bridge: FREE since
2026-09-18T02:07:41Z" and self-flagged its own `running` field as unreliable ("BRIDGE NOT
PROBED — no port found... LOADING here is a DEFAULT, not a reading"). The next bridge ledger
event after that commit is BENCH taking the bridge at 2026-09-18T03:25:32Z (~65 min later,
"vegetation screenshot for the owner") — consistent with the handoff's FREE claim, not
contradicted. **UNMEASURED for the other 10 files** — checking each would mean diffing every
handoff's recorded bridge/game state against the next chronological ledger event by hand, which
exceeds the "spot-check, don't be exhaustive" stop condition; one clean case does not generalize.

## Top 5 concrete template defects (handoff.py-enforceable)

1. **"say for each whether it is yours or another seat's" is unenforced and unenforceable by
   `--check` — 7/11 files leave the raw `git status --short` dump completely unattributed.**
   Fix: either (a) have `--check` refuse when the literal boilerplate header string is still
   present AND the dirty block has non-trivial line count (the header text itself is a de facto
   second TODO marker that today's `todo_scan()` doesn't scan for), or (b) have `build()` emit a
   per-line `<<< WHOSE? >>>` placeholder after each dirty path instead of one header sentence, so
   the existing TODO-count gate actually covers it. FOUNDRY_180351.md:199, FOUNDRY_180218.md:782,
   BENCH_172331.md:167, BENCH_172203.md:290, MACBENCH_162042.md:185, BENCH_160549.md:140,
   BENCH_180411.md:161 are all live instances of the unfixed header.

2. **The Commits section is not scoped to the seat's own work and can balloon to hundreds of
   lines when the seat reboots infrequently.** FOUNDRY_180218.md:216-773 — 556 commit lines,
   most of them BENCH's, because `build()`'s `rng = "%s..HEAD" % since_sha` spans the full
   multi-day gap since FOUNDRY's own last handoff and includes every seat's commits in that
   window. Fix: either filter `git log` to `--author` for commits this seat plausibly made, or
   cap/collapse the list (e.g. "247 more, see `git log <sha>..HEAD`") past some threshold — a
   700-line mechanical section defeats the whole point of a script writing the parts a human
   doesn't need to read closely.

3. **No template support for "off-template" handoffs — nothing stops or flags a hand-written
   file that skips the schema entirely.** BENCH_132330.md (97 lines) uses six custom headers
   that map to none of the eight canonical section titles; `--check`'s `todo_scan` would pass it
   trivially (it contains no `<<< WRITE THIS >>>` tokens because it was never generated by
   `build()` at all) even though it structurally cannot be diffed against the rest of the corpus
   or programmatically checked for section presence. Fix: `--check` should verify the eight
   canonical `## ` headings are all present verbatim, not just scan for the TODO token.

4. **Repeated judgment content across consecutive same-seat handoffs has no pointer convention.**
   BENCH_180208.md and BENCH_180411.md both carry a full re-explanation of the
   MayRequire-on-Operation-is-inert mechanism (BENCH_180208.md:9-20 and BENCH_180411.md:10-18,
   again at BENCH_180411.md's own Traps section) instead of the second file citing
   `MAYREQUIRE_OPERATION_INERT_SWEEP_1` or a CLAUDE.md line. Fix: `build()` could grep the
   previous handoff's judgment sections for id/keyword overlap and pre-seed a "still true from
   last time, no new info" scaffold that discourages full re-derivation — cheap heuristic, not
   perfect, but changes the default from "write it again" to "point at it".

5. **Same-commit duplication between a handoff's "Traps learned" and CLAUDE.md, with no
   cross-reference in either direction.** BENCH_172203.md (commit `dc71e87aa`) writes out the
   600s-backgrounded-Agent-kill and the `grep -c '<li>'` ModsConfig miscount in full prose, and
   the SAME commit adds near-identical prose to CLAUDE.md — two authored copies, zero pointers.
   Contrast with the Pits bullet in the same file, which correctly says "already in CLAUDE.md."
   Fix: the "Traps learned" prompt could explicitly instruct "if this is going into
   LESSONS_INBOX/CLAUDE.md in this same commit, link it here rather than repeating the prose" —
   currently the prompt only says "Also file these to LESSONS_INBOX.md," which invites the
   double-write rather than warning against it.

## UNKNOWN

- Whether the 7 unattributed-dirty-tree cases actually caused a downstream mistake (a successor
  seat committing another seat's file) — not checked; would need per-successor-session evidence
  outside these 12 files' scope.
- "Game/bridge state wrong at successor wake" for 10 of the 12 files — UNMEASURED, spot-check
  budget spent on the one FOUNDRY_180218 case, which came back clean (not contradicted).
- Whether BENCH_132330.md's off-template format is a one-off or recurs further back in history —
  only checked within the 12-file window; the stop condition caps this audit there.
