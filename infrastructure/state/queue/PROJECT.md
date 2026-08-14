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
Taken by PROJECT as repo tooling. A bare
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
   It has never had a named owner. Ambiguous between **OPS** (same
   fail-toward-success family as O1–O3) and **CREATE** (it is a patch-authoring
   tool). → owner picks.
2. **O5, the expected-failure signatures** — possibly consumed by the 01:05 load
   already. → owner confirms, then OPS works it or drops it.
3. ✅ **CLOSED — the question died with its subject.** This asked where
   `TODO.md`'s doctrine should go. **`TODO.md` was retired and is gone**, so
   there is nothing left to route. Do not re-raise.
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

1. **The prisoner `interactionMode` finding in `TODO_v2.md`.** ⚠️ **Dead twice
   over:** the save it rested on is gone (`acc3261`), and the file was compacted
   from 1,144+ lines to 350, so its old line citation points at nothing. **Find
   it by text, not by number.** Mark measured-and-unreproducible; do not delete —
   it was true when taken. 📌 A line number is the first thing to rot.
2. **`save_authoring_pipeline.md:141` and `rimworld_file_lore.md`** anchor the
   whole `.rws` teardown to `~/GDrive/Personal/Rimworld/observed/2026-08-13_pre-restructure/savegame/03_Gravtasm__starting_save.rws`.
   ⚠️ **`~/GDrive` does not exist in this WSL at all** — checked, the directory is
   absent, not the file. This is unrelated to today's deletion and predates it.
   Establish whether that path is a Windows-side location, another machine, or
   simply dead, then either correct it or mark the teardown as a record whose
   source artifact is unavailable. **Do not delete the lore** — the findings are
   the value and they were verified when taken.


---

## Closed — P8, P9, P10. One line each in `CLOSED.md`; do not re-open.

**P10 was fixed by OPS before I raised it, and my first diagnosis of it was
wrong** — I blamed the interpreter; the cause was a `hasattr` on a name
`game_paths` never exposed, so the platform branch was dead for every seat.
Checking the source before raising it is what caught this. Keep doing that.

---

## Three Stage-2 gap-audit defects resolved or re-aimed — 2026-08-14, VISION

Found while encoding the faction religions against the live def dump. Evidence in
`D:\Luke\dev\Rimworld\design\Jawa\worldbuilding\faction_religions_spec.md`.

- **D2 — Homestead ideology structure. DECIDED.** It is `Structure_TheistAbstract`,
  deity *the Withdrawn*, gender `None`. The either/or at roster `:726` can close.
  Reason: the covenant is *addressed* to something, and the ideological structure
  has `deityCount 0` — there would be nothing to address.

- **D3 — Geonosian species. MIS-SPECIFIED, not unresolved.** The roster's
  *"Preferred xenotypes: Geonosian"* names a route that does not exist:
  `PreferredXenotypes` has exactly one precept (`PreferredXenotype`, Biotech) and
  its xenotype is chosen at **ideo-generation time, not in XML**. There is no
  FactionDef path to it. ⇒ **Retarget the defect at `PawnKindDef` xenotype
  chances — which is where faction 8's composition already is — or close it.**
  Group E is not blocked on a roster decision; it is blocked on a wrong one.

- **D1 — Homestead raid frequency. Better fix available than picking a number.**
  `VME_Raiding_Abhorrent` (Vanilla Ideology Expanded, active) states the refusal
  as *doctrine*. Put it on the Homestead and the Deepwater Compact and the
  "never (Rw 0)" vs "very low" argument stops being a stat dispute — set the curve
  low and let the precept carry the reason.

⚠️ One more for the audit's own hygiene: it is **older than the roster it audits**
and its line citations have drifted ~14-20 lines. D4, D5, D6 and open question 1
are all already fixed in the roster and still shown open in the audit.

---

## Filed by VISION, 2026-08-14 — two mod-inventory defects, neither mine to fix

Found while specifying `design\Jawa\worldbuilding\precept_the_unearned.md`. Both
`[?]` — I cannot tell whose they are, and neither blocks anything today.

1. 🔴 **An active mod has a malformed closing tag and silently loses two precepts.**
   `C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\2896845138\Defs\Precepts.xml`
   line 210 reads `<defName>GarryFlowers_Slave_Relation_Vanilla<defName>` — no
   slash. The live dump shows `GarryFlowers_Slave_Relations` carrying **2**
   positions where the XML defines **4**; `_Equality` and `_Vanilla` are lost with
   no error. **Checked clean:** nothing in the religions spec or the Unearned spec
   depends on them, and the campaign's slave-romance love-gate uses
   `GarryFlowers_Slave_attendance`, which is unaffected.
2. ⚠️ **"More Slavery Stuff (Continued)" WS `3530586159` is NOT installed.** A grep
   of all 1246 workshop `About.xml` files matches only the original `2896845138`.
   **Several design docs cite `3530586159` as adopted.** Nothing is broken — every
   `GarryFlowers_` def this campaign uses comes from the original, which is active —
   but the ID in the docs is wrong and will send someone hunting.
