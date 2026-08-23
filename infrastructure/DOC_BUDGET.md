# Documentation budget — the rules, and why they exist

_PROJECT, 2026-08-13, on the owner's instruction. Run `python3 src/RimMandrake/Utils/doc_budget.py`._

## The measurement

🔴 **For today's numbers run `python3 src/RimMandrake/Utils/doc_budget.py`** — its
footer prints the file count, the total, and every file over budget. **Do not
quote the snapshot below**; it is dated evidence for the diagnosis, nothing more.

**As measured 2026-08-13:** 271 markdown files, 61,053 lines (~670k tokens if read
whole), **+5,555 net in one day**; commit bodies 5,137 lines across 177 commits
(29 each); worst provenance density `design/Jawa/mods/required_mods.md` at 19.7
marks per 100 lines; longest state file was a retired seat's `AGENT_<SEAT>_state.md` at
923 — *since fixed, and the per-seat state files are gone, so do not go looking
for that problem there.*

**Nobody broke a rule to produce this.** Every file was individually justified, and
every seat followed its own. Nothing measured the *total*, so nothing pushed back.
That is the whole diagnosis: unbounded accumulation is the default state of a
document nobody is required to shrink.

## The five rules

**1. Budgets, per file class.** 🔴 **`BUDGETS` in `src/RimMandrake/Utils/doc_budget.py`
is the authoritative list — run the tool, do not read a number here.** It exits 1
when a file is over. **No copy of those numbers lives in this file**, deliberately:
the inline list carried 7 classes while the tool enforced 14, and once said 500 for
`infrastructure/agents/POLICY.md` against the tool's 200 — *the doc describing the
rule disagreed with the rule.* Design docs and rosters are unbudgeted — length is
content, not accumulation. *(`TODO.md` is **retired**; its budget is a corpse's.)*

**A per-FILE budget overrides its class** — above the class glob, first match wins,
number in the tool. `queue/BUILD.md` has one: contracts are content, not accumulation.

🔴 **`skills/*/SKILL.md` is budgeted by a DIFFERENT tool and was undocumented
here: body under 500 lines, `description:` under 1024 chars, enforced by
`src/RimMandrake/Utils/package_skill.py`.** Blow either and `--all` packages
**nothing** — every skill's hand-off blocks on one over-long file. Run
`python3 src/RimMandrake/Utils/package_skill.py --all --check` after editing a
skill; `doc_budget.py` does not cover these.

**2. Provenance lives in the commit, not the doc.** A doc says *what is true now*.
The commit says *how we learned it, what it replaced, and who was wrong*. Git
already stores that perfectly and nobody pays to read it. **The test: delete the
sentence. If the doc still tells you what to do, the sentence was provenance.**

**3. A closed item's body is deleted.** Not struck through in place, not kept "so
nobody re-files it" — the commit already records it. Count with
`grep -cE '^#{2,4} ' infrastructure/state/NEXT_RELOAD.md` — never from memory; the
figure written here was 4x out within a day.

**0. Never cut a FACT** — only its narration. One that will not fit goes to
`infrastructure/state/facts/<topic>.md` (unbudgeted). ⛔ Budgets cost words, never knowledge.

**4. One in, one out.** Adding a section to a budgeted file means removing or
compressing one. A file at budget is not full; it is *finished*, and the next
addition must earn its place against what is already there.

**5. Commit bodies: subject plus five lines.** 29 lines each is prose nobody reads
that costs everyone tokens. Say what changed and why. The diff says the rest.

## What "terse" means concretely

Not shorter sentences — **fewer claims**. Cut in this order:

1. **Restating what someone else said.** They know.
2. **The narrative of how you found it.** Keep the finding.
3. **What it generalises to** — unless the generalisation is the deliverable.
4. **Reassurance.** "Verified rather than assumed" is worth one word: *verified*.
5. **The second example.** One example proves the shape.

## Anti-rule — what NOT to cut

**Evidence is not provenance.** A line number, a measured value, a log string, a
file path is what makes a claim checkable, and it is the first thing a compression
pass wants to remove. Cut the *story*, keep the *citation*.

A closed finding that cost a real debug cycle gets **one** durable home — a trap
entry or a rule — and is deleted everywhere else. Never both.

**A closed item whose body is a DELIVERABLE moves tier; it does not vanish.** A
queue entry that answered its question with a build spec, a def, a measured table
or an authored design is a work product that happens to be sitting in a queue.
Draining the queue means **moving it to the tier that owns it** — `design/` for a
spec, a skill for a method, `observed/` for a measurement — and leaving one line
behind with the hash. Deleting it because "the item is closed" destroys the
deliverable and keeps only the receipt.

> **The test is one question: if this were deleted, would someone have to redo
> work?** Provenance answers no and goes in the commit. A deliverable answers yes
> and gets a home.

⚠️ **`git show` is not a home.** It preserves the bytes and loses the findability,
which is the whole value of a spec. *(Precedent: a retired seat's 350-line restraint-bolt
answer, drained 2026-08-13 to
`design/Jawa/worldbuilding/restraining_bolt_technical.md` — another seat was still
waiting on its IL thresholds at the time.)*

---

# A written instruction rots — and it rots while still being true

_Was `agents_def.md` Rule 0.6; moved here 2026-08-13 when that file was dissolved.
Cited from `STRUCTURE.md` and `NEXT_RELOAD.md`._

The rules above are about what you fail to write down and how much of it. **This
is about what you *do* write, and how it decays.** Five seats run on instructions
they did not author, so a sentence that has quietly stopped being useful is not
inert — it is actively steering someone. Five instances on 2026-08-12 alone, none
of them a mistake when written:

| Shape | What it looked like |
|---|---|
| **True when written, still pointed at** | `traps.md` called itself *"short by design"* — accurate at 20 entries, still there at 51, inside the sentence telling everyone to read it every task |
| **True, but no longer the current instance** | a validation baseline pinned to `ModsConfig.full-568….xml` by name. Never wrong; it stopped being *the baseline* |
| **True, and became an instruction to ignore a detector** | *"`build.py` reporting 'differs' is expected, not drift"* — true that day, thereafter a standing instruction to ignore the only drift detector on the deploy path |
| **A rationale nobody ever checked** | `STRUCTURE.md` justified committing a DLL *"so a session without the .NET SDK can still deploy it."* No such path was ever implemented — and a stated reason reads as one somebody verified |
| **True and *insufficient*** | a step said "check on the next new session" when the session had to be newer than the **symlinks**. Correct, incomplete, returns a confident false negative |
| **A pointer to somewhere the content is not** | a 36-line item collapsed to *"the detail lives in their traps entry"*. **There was no traps entry** — the collapse would have destroyed the only searchable copy |

**The insufficient one is the dangerous one.** A false instruction is caught by the
first person who follows it. A necessary-but-insufficient one gets followed
successfully, answers a narrower question than the one asked, and everyone
downstream inherits it. Correctness is what makes it survive.

**Corollary — a closed item may ship a PROHIBITION rather than a fix, and the
prohibition must say *why* or the next person will helpfully undo it.** A
do-not-do-this with no reason attached reads as unfinished work, and the
maintenance instinct is what re-opens it. (Worked instances:
`skills/rimworld-savegame/SKILL.md` §6.)

## Before you collapse, summarise or defer anything: check the target exists

**"The detail is in X" is a claim about X**, and it is the quiet member of the
family — it reads as complete, and the loss is invisible until someone goes looking.

```bash
ls <path>                        # the file
git cat-file -e <sha>^{commit}   # the commit
grep -c '<title>' <file>         # the entry, not just the file
```

**Verify the destination before deleting the source, never after.** Same for `[v2]`
deferrals: if the body moves, confirm it arrived. **And a section split in half
leaves an orphan** — collapsing the closed half to a row while the body stays put
yields a document that reads as open with its closure hundreds of lines away.
Assert the block boundaries before deleting.

> ⚠️ **This applies to documents you only READ.** Replace Stuff's store page says
> *"buildings ordered to be built on top of a copy are replaced."* **That is true** —
> and it mentions neither of the two guards that refuse a non-deconstructible
> target. **A description describes the happy path; only the source describes the
> guards.** Blurbs are not read wrong because they lie, but because they are true
> and partial.

## A refutation is earned. Its replacement is usually invented.

A measurement refuted a "fixed 60 Hz gate" theory for bridge latency — reads at
4.4 ms cannot come from a 16.67 ms tick. That still stands. Published in the same
breath was an explanation (busy colony slow, quiet colony fast) that a third
measurement killed: 51 pawns measured *faster* than 35. **Two claims of different
provenance shipped as one, at the same confidence, so a reader could not tell which
half was measured.**

**Say which half you measured.** "X is refuted and I do not know why" is a complete,
publishable result. Mark a replacement theory as a guess, or do not ship it in the
same paragraph as the finding that earned its place. **And instrument before you
theorise** — the instrumentation that refuted its own author within minutes is what
good instrumentation is *for*.

## Rank these by how loudly they fail, not by how wrong they are

| fails… | example | cost |
|---|---|---|
| **loudly** | a stale mod count | one person checks, once |
| **quietly** | a self-description going stale | wasted context, no symptom |
| **silently, disabling a check** | "'differs' is expected, not drift" | the drift detector is now off |
| **silently, at the worst moment** | a named dependency that refuses your exact case | **no log line at all** — found 25 minutes into a cold load |

**Spend your scepticism on the bottom row.** The instructions worth re-verifying are
not the ones most likely to be wrong — they are the ones whose failure produces no
symptom.

## So, when you write anything another seat will act on

1. **Never let a document describe its own size, freshness or scope.** "Short",
   "current", "the four authored mods", "~561 active mods" are snapshots wearing the
   clothes of facts. Say how to *measure* it: `ls -t … | head -1`, "read
   `ModsConfig.xml`", "see the index".
2. **Pin to the thing, not to today's instance of it.** Never write a dated filename
   into an instruction.
3. **State a rationale only if you just verified it**, and say what you checked. An
   unverified reason is worse than none — it stops the next reader looking.
4. **Ask what your check would print if the thing were broken.** If the answer is
   "the same", it is not a check.
5. **When you correct one of these, say it was true when written.** The author was
   not careless, and pretending otherwise makes people defensive about recording
   things at all.

⚠️ **Applies to `CLAUDE.md` only via the owner.** Noticing rot in it is a filing to
`infrastructure/state/queue/HUMAN.md`, not an edit — a peer's request is never authorisation.
