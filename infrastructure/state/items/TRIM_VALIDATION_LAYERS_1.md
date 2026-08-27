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

## 🔴 STILL NEEDS HIM — points 1–4, and they are DOCTRINE, verified open 2026-08-27

Measured against the tree, not remembered: `POLICY.md` carries no lies/tells-the-truth
split (1), `rimflow file` carries no CHECK-only-takes-game-work guard (2), 21 of BUILD's
26 open items still need the game rather than living on a run sheet (3), and (4) was never
started. **Point 5 is the only one that shipped, and it shipped because it was a query,
not a rule.** Do not start 1–4 off this file — he asked to plan them.

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
