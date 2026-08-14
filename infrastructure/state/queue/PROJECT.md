# infrastructure/state/queue/PROJECT.md

_PROJECT's queue. **You own this file.** You also assemble `NEXT_RELOAD.md` from
all five queues before a load, and drain unassigned items._

---
## ⭐ v1 — you own the burn-down itself, not a row

**No build row is PROJECT's.** Your v1 work is the two things that make the other
four seats' rows move:

1. **Keep the burn-down honest** (`V1_SCOPE.md`) — including when the answer is
   "no progress". Rows 2, 3 and 4 sat at 0 while being closable offline; that
   invisibility is the failure this seat exists to catch.
2. **Sweep `OWNER_DECISIONS.md`** — every seat with a question for the owner adds
   a row there. You drain answered rows into `CLOSED.md`. Unanswered questions
   are the other half of why nothing moved.

---

## Open

### P1. `agents_def.md` contradicts itself on its own status
Migrated from `TODO.md` §2. It carries a DRAFT marker while also declaring itself
settled. **Now larger than when filed:** the whole file needs rewriting for the
five-seat structure — seats moved to `infrastructure/agents/<SEAT>.md`, WORLD renamed to OPS,
VISION added, queues split per seat.

### P2. The git hook guards `add`, not `commit`
Migrated from `TODO.md` §11 (`[ANY]`, taken by PROJECT as repo tooling). A bare
`git commit` still sweeps another seat's staged files. **Partly mitigated in
practice** — the hook now blocks pathspec-less commits too, observed 2026-08-13 —
so the item is to confirm the guard matches the intent and close it loudly either
way.

### P3. Retire `TODO.md`
848 lines holding roughly **14 live items**; the rest is closed records and
doctrine. Section numbers are non-sequential and `13` appears twice (`:599`,
`:634`), which is what a file appended-to and partly drained looks like.
**Plan:** migrate done (this commit), move the surviving doctrine into
`agents_def.md`, then reduce `TODO.md` to a pointer at `infrastructure/state/queue/` plus the closed
ledger. Do not delete the ledger — it is what stops items being re-filed.

### P5. Execute the restructure to option B
Plan: `infrastructure/disposing/RESTRUCTURE_PLAN.md` — ten stages, **one commit each**, lowest-risk
first, nothing moved yet. Run `src/RimMandrake/Utils/check_refs.py` and `src/RimMandrake/Utils/doc_budget.py`
after every stage; §8 names the check that proves a stage landed whole.
**Stage 9 (`skills/`) is owner-gated and may never run**; §3's seven unplaced
items need a ruling before stage 4.

### P6. Deferred renames — convention on new work now, renames later
Owner deferred these; do not start one without a spare cycle. Scope measured in
`infrastructure/disposing/RESTRUCTURE_PLAN.md` §7: `JawaBench.BridgeTools` → `RimMandrake.Bridge`
(14 tracked files, 4 identities including the deploy folder); the `jawa/<tool>`
namespace (**35 tracked files at once**, canonically 17 `[Tool]` attributes in
`src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchTerrainTools.cs`, 3 of the 35 being
generated JSON); the five `Jawa*` mod folders.
⚠️ **Correction to the deferral's stated basis** — it was taken as "no packageIds
at risk". All five ARE active in `ModsConfig.xml` (lines 560–571 of 575), so that
rename is a load-order edit at a specific slot plus a RimSort rules edit, not a
`sed`. Raises the cost; does not change the deferral.

---

## Needs the owner — routing calls I will not guess

The migration surfaced four items I could not route confidently. **Guessing an
owner is how work falls out of every queue**, so they are parked here rather than
filed at a seat.

1. **`validate_patch.py` reads `Patches/` only, never `Defs/`, and does not say so.**
   No attribution anywhere in `TODO.md` §12. Ambiguous between **OPS** (same
   fail-toward-success family as O1–O3) and **CREATE** (it is a patch-authoring
   tool). → owner picks.
2. **O5, the expected-failure signatures** — possibly consumed by the 01:05 load
   already. → owner confirms, then OPS works it or drops it.
3. **`TODO.md` §12's doctrine and §7's closed record** — the lessons are worth
   keeping, the queue entries are not. → do they go to `agents_def.md`, a traps
   file, or nowhere?
4. **Space Tower split** (VISION V11 / CREATE C2) — filed as a split with VISION
   gating CREATE. → confirm that is the right dependency direction.

---

## Standing duties

- **Assemble `NEXT_RELOAD.md`** from the five queues before each load. That file
  stays shared: it is one document about one event, read top-to-bottom by whoever
  drives the load.
- **Drain unowned items.** `grep -rn '\[?\]' infrastructure/state/queue/ *.md`.
- **Close findings loudly.** A filed item that turns out fine is recorded as
  checked-and-fine, never deleted quietly.
- ⚠️ **Re-read the source before raising anything from a list of other seats' work.**
  On 2026-08-13 two settled items went to the owner from a stale list. One grep is
  cheaper than a decision cycle.

---

## P4. Two git traps from 2026-08-13 — file them when their homes are free

Both are `CLAUDE.md`'s "Commit explicit paths only" section, which was `M` under
another seat when these happened. Add as two short bullets; do not expand.

1. **`git commit <path>` cannot carry an index-only change.** It records the
   WORKING TREE state of that path, so `git rm --cached <f>` followed by
   `git commit <f>` silently RE-ADDS the file. Symptom: the commit lands, the
   removal does not, and nothing warns you. To untrack while keeping the file on
   disk: move it aside, commit the path while it is absent, move it back.
   *(Cost: a `CLOSED.md` entry claimed a log was untracked for four hours while it
   was not — caught only by the stale-file audit.)*
2. 🔴 **`git commit --amend` is unsafe in this tree, full stop.** A seat amended
   to fix its own subject line and rewrote a DIFFERENT seat's commit, because that
   seat committed between the `rev-parse` check and the amend.
   **`--force-with-lease` does not protect you** — the lease is against the
   remote-tracking ref, not against a local commit landing underneath. A cosmetic
   message fix is never worth this: leave the message wrong and correct it in the
   next commit.

---
## P7. Two save-citation sweeps left by the 2026-08-13 deletion

Filed after annotating the two I own. **Neither is urgent; both are the "true
statement an instruction still points at" shape this seat hunts.**

1. **`TODO_v2.md:1144`** cites `New arrivals2.rws` as the evidence for a prisoner
   `interactionMode` finding. The save is gone (`acc3261`), so the finding stands
   but is unverifiable. Mark it measured-and-unreproducible, do not delete it.
2. **`save_authoring_pipeline.md:141` and `rimworld_file_lore.md`** anchor the
   whole `.rws` teardown to `~/GDrive/Personal/Rimworld/observed/2026-08-13_pre-restructure/savegame/03_Gravtasm__starting_save.rws`.
   ⚠️ **`~/GDrive` does not exist in this WSL at all** — checked, the directory is
   absent, not the file. This is unrelated to today's deletion and predates it.
   Establish whether that path is a Windows-side location, another machine, or
   simply dead, then either correct it or mark the teardown as a record whose
   source artifact is unavailable. **Do not delete the lore** — the findings are
   the value and they were verified when taken.

---
## ✅ P8 — DONE `a43b610`. Do not re-open.

`rimworld-start-prep` reviewed and approved; the contradiction OPS found was real and
**OPS's measurement won** — the game does not rewrite `ModsConfig.xml` on exit.
Corrected in `rimworld-load-round` §4 and pointed at the new skill. Full reasoning is
in the commit and in `CLOSED.md`.

---
## ✅ P9 — CLOSED, and the constraint never existed. Do not re-raise.

OPS declined to write a real trap because *"the traps set is at 723 lines against a
700 budget"*. **Measured: the 700 is PER FILE**, glob `skills/*/references/traps*.md`
(`doc_budget.py:69`), and its own comment reads *"append-only by nature; the index is
what stays short."*

| file | lines |
|---|---|
| `skills/rimbridge/references/traps.md` | 348 |
| `traps.md` (index) | 177 |
| `traps-tooling.md` | 172 |
| the other four | 41–119 |

**Not one is within half of 700.** The 723 was the SET total compared against a
per-file number.

🔴 **The ruling: never suppress a trap for the budget.** The traps files are
designed to grow; only the **index** is held short, and that is what a split is for.
A trap not written costs a full debug cycle to re-find — the budget exists to stop
doc bloat, not to stop learning.

📌 **The lesson is mine, not OPS's.** A per-file budget printed as a flat column is
easy to read as a set budget, and the cost was a real finding nearly going unwritten.
