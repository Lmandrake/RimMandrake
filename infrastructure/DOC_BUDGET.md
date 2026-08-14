# Documentation budget — the rules, and why they exist

_PROJECT, 2026-08-13, on the owner's instruction. Run `python3 src/RimMandrake/Utils/doc_budget.py`._

## The measurement

| | |
|---|---|
| markdown files | **271** |
| total lines | **61,053** (~670k tokens if read whole) |
| net growth, one day | **+5,555 lines** (+9,414 / −3,859) |
| worst provenance density | `design/Jawa/mods/required_mods.md`, **19.7 marks per 100 lines** |
| longest state file | `AGENT_BRIDGE_state.md`, **923 lines** — a handoff nobody can read |
| commit bodies today | **5,137 lines across 177 commits** — 29 lines each, average |

**Nobody broke a rule to produce this.** Every file was individually justified, and
every seat followed its own. Nothing measured the *total*, so nothing pushed back.
That is the whole diagnosis: unbounded accumulation is the default state of a
document nobody is required to shrink.

## The five rules

**1. Budgets, per file class.** `src/RimMandrake/Utils/doc_budget.py` enforces them and exits 1
when a file is over. Queue 150 · identity 120 · state 150 · `CLAUDE.md` 300 ·
`agents_def.md` **200** · traps 700 · `TODO.md` 400 · `TODO_v2.md` 600.
*(This line said 500 for `agents_def.md` while the tool enforced 200 — the doc
describing the rule disagreed with the rule. The tool is authoritative; read
`BUDGETS` in the script, not this sentence.)* Design docs and rosters are unbudgeted — their
length is content, not accumulation.

**2. Provenance lives in the commit, not the doc.** A doc says *what is true now*.
The commit says *how we learned it, what it replaced, and who was wrong*. Git
already stores that perfectly and nobody pays to read it. **The test: delete the
sentence. If the doc still tells you what to do, the sentence was provenance.**

**3. A closed item is ONE LINE in `CLOSED.md`, and its body is deleted.** Not
struck through in place, not kept "so nobody re-files it" — one line with the date
and hash does that job at 2% of the cost. `NEXT_RELOAD.md` currently carries 26
closed sections out of 82.

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

---

# A written instruction rots — and it rots while still being true

_Was `agents_def.md` Rule 0.6; moved here 2026-08-13 when that file was dissolved.
Cited from `STRUCTURE.md`, `TODO.md` and `NEXT_RELOAD.md`._

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

⚠️ **Applies to `CLAUDE.md` only via the owner.** Noticing rot in it is a filing
(`agents_def.md` rule 0.5), not an edit — a peer's request is never authorisation.
