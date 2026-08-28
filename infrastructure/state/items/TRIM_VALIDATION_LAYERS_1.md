# TRIM_VALIDATION_LAYERS_1 Restructure the seats to validate and test less

## spec

Owner, 2026-08-23 14:4x, verbatim:

> *"Restructure the agents to have less validation and testing. Not everything requires
> multiple validation and testing after the initial agent generates it... less traffic
> for CHECK, less thrashing. Let's talk and plan about it."*

🔴 **This is a DOCTRINE change, and it is filed for talk first — do not start rewriting
seat files off this paragraph.** He asked to plan it with REP; the plan is the first
deliverable, not the edits.

## What the plan has to settle

1. **Which classes of work get NO second pass at all.** The candidate line is
   *reversible and self-evidencing* (a def edit whose own tool reported success, a doc,
   a rename, a queue view) versus *irreversible or silent* (`--apply` deploys, anything
   the game must load, anything whose failure mode is silence).
2. **What CHECK is FOR once it stops re-reading BUILD's output.** If CHECK only runs
   what needs a live game or a load, its queue shrinks to the reload blocks and the
   findings — that may be the right answer, but it has to be said out loud.
3. **Where the verify obligation moves** — onto the generating seat's own return value,
   which POLICY already asserts (*"the return value is the verification"*) and the
   practice does not follow.
4. **What we keep, deliberately.** The three named exceptions in POLICY
   (`deploy --apply`, force-push, `ModsConfig.xml` writes) and the `measure` rule for
   numbers are the two things that have actually caught errors; they should survive any
   trim.
5. **How much traffic this is.** Count CHECK items closed with no finding versus with
   one, out of the ledger — that number decides how big the win is and should be
   MEASURED before the doctrine moves.

## Watch out

- ⚠️ **The counter-evidence is on file.** Handoffs this week record two items
  (`JAWA_ROBES_NEVER_WORN_1`, `EMPIRE_GRUNT_SPAWNS_BARE_1`) filed as defects against
  yesterday's defs, and `CLAUDE.md` carries several rulings that exist because a seat
  reported something settled that was wrong. Trimming validation is right where the
  check was ritual; it is wrong where the failure is silent. The plan must name which
  is which rather than lowering everything.
- Touches `infrastructure/agents/POLICY.md`, `CHECK.md`, `BUILD.md` and `CLAUDE.md` —
  files every seat reads, so it supersedes and must write INTO what it overrules.

## What shipped 2026-08-23 — BENCH, the first half

Planned with the owner in REP's window. **The measured case, so nobody re-litigates it:**
47 written obligations, **13 firing on every item regardless of size**; 13–19k tokens of
mandatory reading per seat wake of which **83–96% is doctrine**; **34% of commits since
Aug 21 touch nothing but the ledger, queues and item files**; median file→close **1.2 h
for BUILD, 15.7 h for CHECK**; **44 of 65 open items** parked waiting for a game load;
and CHECK's own split — **27 real defects out of 53 closed, 21 of them silent failures**,
but only **11 of 27** when verifying BUILD's fresh work against **16 of 26** when hunting
on his own.

🔑 **The finding that shaped it: the system is built for a human who is not in the room,
and he is in the room.** `POLICY.md` told a seat to write its question into a file and
move on **while he sat there**. That is the defect BENCH exists to kill.

**Landed:**
- `infrastructure/agents/POLICY.md` — the BENCH page, at the top, replacing the process
  below it while he is present; and `## Modes` rewritten to **BENCH · BELT · AFK**
  (his vocabulary, 2026-08-23). BENCH is per-window and lives nowhere on disk; BELT and
  AFK are global and live in `infrastructure/state/MODE`, now `belt`.
- `.claude/hooks/bench_mode.py` on `UserPromptSubmit` — ⭐ **the delivery route.** Doctrine
  reaches a seat only when it wakes, seats run for hours, and no agent may message
  another; so the hook reads the BENCH page out of POLICY and lands it in the window he
  just spoke into. Silent on an ordinary prompt.
- `doc_budget.py` — POLICY 320 → 420, with the reason and the debt named in a comment.

## What shipped 2026-08-27 — planned with the owner, points 1 and 4

**① VERIFY WHAT LIES; TRUST WHAT TELLS THE TRUTH.** A table in `POLICY.md > How you work`, split by
one question — *can this report success and be wrong?* **LIES:** a patch matching nothing, a bridge
setter answering `success: true`, a count off a large artifact, a texPath, a spawn that substitutes,
anything the game must LOAD. **TELLS THE TRUTH:** a file written, a def edited, a rename, a doc, a
queue view, a commit — ⛔ **no second pass, by anyone.** 🔑 The left column's check belongs to the
seat that GENERATED it, in the same turn; it is not a handoff. ⚠️ Verify-FIRST is a different axis
(irreversibility) and is still only the three: `--apply`, force-push, `ModsConfig.xml`.

- Propagated into `CHECK.md` — *"YOU HUNT. YOU DO NOT RE-READ"*, carrying the measurement that
  decided it: a real defect in **11 of 27** items verifying BUILD's fresh output against **16 of 26**
  hunting alone — and into `BUILD.md`, where 🔑 **the check being yours does not make it obligatory.**
- ⭐ **Found while propagating:** `BUILD.md`'s "Done means" step 3 still ordered the item *appended to
  `queue/CHECK.md`* — a generated view since 2026-08-20, with a hook that refuses the edit. The step
  was uncompletable and nobody had noticed. Now `rimflow file --for CHECK`, and only for live work.

**④ A NEW OBLIGATION NAMES THE ONE IT REPLACES.** New section in `POLICY.md`. ✅ *"It replaces
nothing"* is permitted — say it, and say why the page is worth being longer. ⚠️ **A budget may cost
WORDS and never KNOWLEDGE:** a rule that still earns its keep moves to `facts/`, which is unbudgeted.
🔑 **Applied to itself in the same commit** — POLICY 394→413/420, and CHECK.md and BUILD.md were both
brought back INTO budget (159→150, 145→150) by deleting what the new rules replaced. The `game.json`
rule was stated twice in `CHECK.md`; the no-reopen rule three times.

## 🔴 TIGHTENED THE SAME DAY, BY THE OWNER — human play is the default

> *"Modify such that BUILD does NOT automatically produce anything for CHECK. Only if it is not
> possible to validate function without the game… Regular human play is the default validation."*

⭐ **This goes further than ① and supersedes the rule ① had left standing.** *"A live check must be
PROVEN NEEDED"* set the default to SOURCE and still let a check be argued for; the default is now
**the owner playing the game**, and BUILD routes nothing on completion at all.

✅ **The single test: a mechanism NEW or significantly changed that has never once been observed
running.** ⚠️ **The MECHANISM, not the instance** — a 49th pawnkind built like the other 48 has been
observed; a comp nobody has ever seen fire has not. ⛔ **Offline, and closed by whoever holds it:** a
faction roster · a cherrypicked item · a def edit · a stat · a texPath · what a patch matched.

**Landed in all four places a seat would read it:** `POLICY.md` (the section replaced outright),
`BUILD.md` ("Done means" step 3 and the live-check rule), `CHECK.md` (his intake now says his queue
is the never-observed mechanism plus his own hunting), and a prompt on `rimflow file --for CHECK`
naming the test. ⚠️ **A PROMPT, NOT A GATE** — deliberately, because ② below dropped the proposal to
enforce routing in `file`, and because only the filer can tell whether the exception applies.
🔑 All three seat pages were brought back to exactly 150/150 to pay for it.

## ② DROPPED 2026-08-27, overtaken by events — not deferred

**"CHECK takes only work that needs the game running, enforced in `rimflow file`."** The case for it
was **42 of 100** items sitting with CHECK that never needed the game. Re-measured: **CHECK holds 7
open, 5 of which need the game.** A guard for two items is ceremony. ⇒ ①'s *"CHECK hunts, does not
re-read"* is the same fix without a gate, and gates are what this item exists to reduce.

## ③ HELD 2026-08-27 — the run sheet must survive one load first

**"Load-dependent work leaves the queue and becomes one run sheet per load window."** It is the
biggest number left — **21 of BUILD's 26 open items need the game** — and it is the one that could go
backwards. 🔴 **Measured the same morning: 7 blocks rode the 2026-08-26 load unscored, and
`NEXT_RELOAD.md` has rotted twice before.** Moving 21 tracked ledger items into a file that
demonstrably drops work trades a visible queue for an invisible one. `RUN_SHEET_STALE_BLOCK_CHECK_1`
now warns on exactly that rot ⇒ **revisit once it has caught one real load cycle**, not before.

## 🔴 STILL NEEDS HIM — what is left, verified open 2026-08-27

Only **③** remains, and it is held on a condition, not on him. What he still owes this item is the
call on ③ once the stale-block check has caught a load — nothing else here is waiting on a person.

## Still open — the rest of the plan, in the order agreed

1. **Verify what lies; trust what tells the truth.** Delete the self-verify step outright.
   Lies: patches (a patch matching nothing reports success), bridge setters returning
   `success: true`, counts off large artifacts, anything the game must load. Does not lie:
   a file written, a def edited, a rename, a doc.
2. **CHECK takes only work that needs the game running** — enforced in `rimflow file`.
   42 of the 100 items that have sat with CHECK never needed the game at all.
3. **Load-dependent work leaves the queue** and becomes one run sheet per load window.
4. **One page per seat**, and 🔑 **a new obligation must name the one it replaces** — the
   rule that stops a fourth occurrence.
5. ✅ **`rimflow next --bench` — BUILT 2026-08-27.** Triage as a query: per-seat counts,
   RIPE, IN TROUBLE and NEEDS HIM, in one call. ⛔ Refused to BUILD/CHECK, and the refusal
   says why — it scores actions seats CHOOSE, so it is the only rimflow output that can be
   gamed, and penalising upstream reassignment teaches a seat to absorb mis-scoped work
   rather than hand it back. ⚠️ **Its spec above was SUPERSEDED by measurement six hours
   after it was written:** "thrashing = 2+ reassignments" is refuted — reassignment COUNT
   is misleading (its top hit had **11 reassignments and closed in 1.0 h**), and DIRECTION
   is the whole signal (upstream 10.5 h / 26.9% closed against 1.5 h / 72.9%). It
   implements `facts/distress_signals.md`'s coarse index instead, with the per-kind p90
   computed at run time because that file forbids hard-coding it.

⚠️ **Rejected, with the reason on file: a fifth "Manager" seat.** It cannot tell any seat
what it took (messaging is off and hook-blocked), it only helps while he is in its window
— which is the situation BENCH already covers — and it is a fifth doctrine set to keep in
sync. The valuable half is the triage query above.
