# The Relentless Agent: design (2026-11-01)

Item: RELENTLESS_AGENT_DESIGN_NEVER_FORGETS_TWICE. Status: DESIGN, under skeptical review
(`relentless_agent_gpt_review_2026-11-01.md`), findings not yet applied.
Binding contract: `MandrakeWorkflows/relentless/agent/RELENTLESS_AGENT.md`. Extends `relentless_owner_design_2026-10-31.md`
(live) and `operating_requirements_2026-11-01.md` RW1-5, TE2, TE4, RO3. Evidence for the claims here:
`relentless_agent_research_2026-11-01.md`.

Owner, 2026-11-01: *"a fire-and-forget agent you can point at a modest goal and trust it will get all the way there."*

## 1. The promise and its limit

The promise: **a goal accepted at intake reaches a Judge-accepted, checkable done, or stops with a true statement of why.**
Everything else serves that sentence.

The enemy is the Pit (`north_star_validation_spec.md` §Why): state assertions all true, recorded GREEN, the screen wrong, and
the walk had dismissed the visual pass in writing. Relentless today can repeat it. MEASURED on the live store: 48 done, all
48 contracts written by the worker that built the work; 42 of 48 proofs name a selftest (grep, a floor). Its 16 blind fails
tell us nothing about its false passes, which nobody has measured.

So the design rests on one rule: **who builds does not set the exam, does not hold all of it, and does not mark it.** For a
mod the exam arrives as a tree from the concept debate; Relentless receives it and never authors it. Fire
and forget stays a claim, unearned, until the numbers in §9 say otherwise.

## 2. What exists, what this adds

**Kept, unchanged:** item on disk, disposable workers, the tick (no AI), fencing by `gen`, receipts, top-of-queue returns,
filler staffing, pool rules, `pilot`/`redesign` approaches, the live line. Nothing here rewrites the state machine.

**One state is added before `queued`:** `intake`. **Three holes in the live code are closed:**

| Hole, as read in `relentless.py` | Closed by |
|---|---|
| `contract()`: the first worker writes its own exam; a `redesign` may rewrite it with `--why`. That is a loosening door | §3, §4 |
| Judge blindness is prompt prose. `checker_prompt` passes free text `evidence`; the unit receives `RELENTLESS_ROOT`; `store/items` is world-readable; the clean clone carries `.git`, 225 tracked `conversations/` files and the ledger notes | §8 |
| `learned[-8000:]`: unbounded narrative, tail-cut, uncited | §5 |

## 3. Intake and the acceptance contract

**No tree, no item.** Owner, 2026-11-01: *"The mod isn't handed to a Relentless worker until this tree is well defined."* The
acceptance tree comes from the concept agent (item MOD_CONCEPT_AGENT_DESIGN_ARGUES_BEFORE_BUILDING, designed separately) after
its debate with him: human experience criteria plus mechanical constraints (resource consumption, latency, more). It holds
only *"the core concepts that must be true for the mod to pass"*. Relentless treats the tree as the research's **non-builder
contract**: input, read-only, never authored here. An item with no tree is refused at `intake`, before any worker starts.

**One agent, two modes, and Judge mode binds the exam to instruments.** A fresh Judge-mode instance, the **Setter**, reads only
the tree and the repo, before any Build lease. It will never build this item. It may not add, drop or reword a criterion. It
binds each leaf to an instrument (`oracle`, `tier`, the `guard` of `false_pass`) and writes the hold-outs (§3.3). A later Judge-mode
instance, the **Marker**, sits with a wall between it and everything Build wrote. No third mode exists.

**Goals that are not mods.** A tooling goal has no concept debate, so its filer supplies a tree, often one leaf. The rule holds:
the tree exists and was written by a non-builder before the lease. Who writes it for a small tooling goal (the filer, or a
Setter run as a service before admission) is a Conductor call, marked open here. Items already in the store get a one-leaf
tree from their item text at enrol, while intake is report-only (§13 step 5).

A goal is accepted only if every leaf has all eight fields once the Setter has bound it. The `intake` program checks them
mechanically; a missing or empty field refuses the goal back to its filer via `needs`, naming the field. A leaf the Setter
cannot bind goes back the same way, never rewritten.

| Field | Content | Mechanical check at the door |
|---|---|---|
| `experience` | One line: what the player (for a tool, its user) sees. A mechanical constraint states its limit instead | Present; names an observer, not a function; a constraint carries a number, unit and test machine |
| `scenario` | The setup and action that produces it | Runnable reference, or an owed instrument leaf |
| `oracle` | Instrument and what it must read, including visual expectation (must-show lines, frames) | Tier declared; an experience on screen needs a visual or read bar, or an explicit `cannot show` argument the Marker can refuse |
| `false_pass` | How this could read green while the experience is wrong | A named wrong world, plus the seeded change that creates it (`guard`) |
| `red` | Proof it can fail | Filled by the supervisor, §3.1 |
| `tier` | Cheapest tier that can settle it; live only with a stated reason | Adapter tier list; adapter forbids (a flyer's flight: refused) |
| `budget` | Expected spend and wall time | A number. Overrun is a trap signal (§6), never a hold: spend limits are off by his word |
| `owner_part` | `no`, or `yes: what he looks at` | Present. First GREEN of a mod is always `yes` (spec §5.5) |

**Mechanical constraints** are leaves like any other, with one difference: their oracle is a measurement, and their guard is
a change that breaks the limit (a planted slow path must read over the latency bar). **A waiver is data.** When he says *"this
doesn't matter to me"*, the tree records the line as `waived` with his words. The Setter gives it no leaf, the Marker may not
fail on it, the hunting list skips it, and a defect found there is not an escape. Only he reinstates it.

`false_pass` is the field that would have caught the Pit: *"pawn despawns but the player watches someone stand in a box
labelled Pit."*

### 3.1 Seen red, twice

"A check never seen red proves nothing" (`debug_process.md` rung 3). Absence at base is a cheap red, so the supervisor
records two, each a receipt of command, sha, exit and a matched signature:

1. **Base red:** the oracle at the lease sha fails with the contract's signature, the reported reason and not a crash.
2. **Guard red:** on the candidate, the `guard` change is applied and the oracle must go red. This runs at the evidence gate
   (§8), in a throwaway tree. It proves the instrument reads the quantity the experience is about.

A leaf whose guard cannot be built offline says so, and takes its guard red live at its tier, or goes up as a coverage gap.

### 3.2 Instruments that do not exist

Doctrine says code and scripts grow together. So the contract fixes what the oracle must read; Build may write the check.
An instrument that does not exist is **its own leaf**, ordered first, with its own guard. Any check file Build changes after
lock is listed by the supervisor in the packet (`oracle_diff`, computed, not reported), and the Marker reads that diff.

### 3.3 Hold-outs

The tree leaves room for hold-outs and does not contain them: the concept debate is visible, so anything in the tree is public.
The Setter writes 1-3 hold-out checks per leaf into judge-only storage, enforced by the mount wall (§8). They probe the same
experience from an angle the contract does not state, and may not reach past the tree or into a `waived` line. A failed hold-out must teach, or the next worker cannot fix it, so it
is **burned**: disclosed to Build, moved into the public contract (a tightening), and the Setter writes a replacement. Burn
count is a reading: many burns mean the contract was too thin.

## 4. The goal tree and the finish line

**A mod is a tree, received whole.** Root: the experience statement, owned by owner and Arbiter (the walk's `## north star`,
VALIDATED by his word). The concept agent delivers the tree. Relentless owns delivering its leaves, never its shape. **Well
defined** is a program's check at intake: tree hash locked; every leaf typed (experience or constraint) or `waived`; each
constraint numeric; no orphan, no uncovered root line (`modcheck floor`); the Arbiter's coverage signature present. A DRAFT root binds nothing: a model judging an
agent-written bar is two agents agreeing (spec §4), so a leaf under a DRAFT root can only close as `not experience-proven`.

Leaf size is an input: a leaf must fit one context. One that does not goes back to the tree's author to split, not looped.

**Leaves do not add up on their own.** A leaf receipt binds to its dependency hash; when a dep changes, the leaf goes stale and
re-enters the queue. Every root owns one **walk leaf**: the whole scenario on one sha, marked by a Marker, at the top of the
§6a ladder. No root reaches GREEN from leaf passes on different builds.

**The finish line is versioned.** `contract.v<N>.json`, hash-locked, each clause with an id.

- **Tighten:** add a clause under an existing leaf, or a hold-out. Open to the Marker, an escape (§9), or a finding. Applied at
  once; old PASSes on that leaf are void. A new concept, as opposed to a new clause, goes back to the tree's author.
- **Loosen:** any edit or removal of a clause. An edit counts as loosening by default, as the program cannot prove otherwise.
  Requires `--owner-said`, nothing else; a waiver is a loosening. `redesign` keeps the right to change approach and loses the right to change the
  contract. A clause Build finds impossible (live precedent: `bar_above_rater_ceiling`) goes up as a loosening request.

## 5. Build mode and memory

Each generation: fresh context, same clone, smoke check first (the inherited tree builds, the oracle runs, the leaf still reads
as last reported). A worker may not edit until that passes or it records why not.

Three stores, per the contract, sized by the research (context files often hurt; small, cited, verified at read).

**1. Result cache (no agent).** Extends `selftest_cache.py`; keys on tests, code, tools, env, data, with reads measured by
`suite_trace`, so XML and assets count. Default miss. External or unobserved input: never cached. `--no-cache` needs
`--because`. A sampled rerun and seeded changes audit it, since it is a grader. **Build's inner loop only: never the
evidence gate, never the Marker.**

**2. Tried-and-failed table (`tried.jsonl`).** Two authors, kept apart in the row:

```
{sig, gen, tree_hash, fingerprint, gate}                     # supervisor, always written, even if the worker died
{approach, evidence:[{cmd|path, sha, out_hash}], reading, retry_when}   # worker, at handoff
```

`reading` is an interpretation and labelled so. A row without a supervisor-checked citation is dropped.

**3. Current state (`state.md`).** Rewritten at handoff, 40 lines, replaced, never appended. Fields: what is true now, the leading
idea, next step. A handoff over the cap is refused. A worker that died leaves the old file, with the supervisor's row beside it.

**What a generation receives:** `state.md`, the 8 most relevant `tried` rows, pointers to the rest. Never an overview.

**Verified at read.** At lease the supervisor re-hashes every citation. Unchanged: shown. Changed: marked STALE, `reading` removed.
A worker that disproves a row deletes it with the evidence. Rows give no prohibitions; `retry_when` is advice.

**Cold after a change of approach.** A `redesign`, and Help, get evidence columns only, no `reading` and no `state.md`. This is
the firebreak for "bad memory compounds": at the moment circling is proven, the story that drove it is withheld.

`learned.md` stays as a raw log nobody is fed. Nothing here reaches the Marker or the Setter.

## 6. Trap awareness

Computed by the tick from tool records, the clone and the receipts. Never from worker words, because self-diagnosis is
unreliable (research §4) and slugs rotate.

| Signal | Source | Fires when (thresholds in `relentless_rules.json` `circling`, unmeasured) |
|---|---|---|
| Test churn (RW2a) | transcript, `tree_hash` | `test_share_limit` of the last `test_share_min` on one unchanged tree; a cache-known rerun counts double |
| Time ledger (RW1) | `agents_timeline` | Run's split by selftest, live, build, reading, editing, waiting; feeds the others and Operations |
| Repeating approach (RW2c) | fingerprint of normalised failing ids and error lines, diff hash, gate name | Same fingerprint across `same_failure_limit` returns, or A-B-A diff hashes `oscillation_limit` times |
| No new finding kind (RW5) | new distinct fingerprints per run, leaf clauses gone green | Runs rising, kinds flat, clauses flat: `going_round`. Finding the right file is not progress |
| No change (RW2b) | diff hash, findings | `no_change_min`; a read-only investigation that yields citations is movement |
| Spend outlier | run tokens against `budget` | Over budget ×2. A review trigger only |

A flake is not a repeat: a fingerprint counts only once confirmed by rerun on the same tree, or it would eat the limit.

**Movement** is the one definition everything uses: a new fingerprint, or a contract clause newly green.

**Interruptions, in order:**

1. **Fact in the run.** A hook delivers a one-line reading at the worker's next tool call: *"38 of 45 min on selftest_x, tree
   unchanged, result known."* A reading, no instruction.
2. **Stop.** Existing path, class `circling`, work kept, `gen` bumped, reading carried on. Counts as a forced change of approach.
3. **Help,** on the second stop (§7).
4. **Conductor,** when two Help rounds bring no movement. Hold kind `stuck`. Precedent: `debug_process.md` rung 8. The item keeps
   its place; a Conductor answer returns it to the top. This is the third hold beside spend and §2 calls: without it, with spend
   limits off, an unprovable item burns forever.

All of 1-3 start **report-only** and may stop runs only after a replay of hand-labelled real runs shows wrongful stops under
`false_stop_limit` (RW2's rule). Long builds with a moving diff and long read-only investigations are test cases.

## 7. Calling for help

`relentless help --item X`: worker may call it any time; forced after two `circling`; one per `help_cool_h`; refused with no
failed approach on record.

- **Who:** a fresh, read-only agent. Round one same model, round two second vendor via the `gpt_consult` port.
- **Sees:** experience line, contract, current failing evidence, `tried` evidence columns. No `reading`, no hold-outs.
- **Gives:** up to 3 options, each with the single observation that would confirm or kill it. For hypotheses, never a verdict
  (`debug_process.md` §0.5).
- **After:** options enter the next brief; that worker must pick one or refute each with evidence, recorded in `tried`.
- **Scored:** by movement in the next two runs. Help that moves nothing counts toward `stuck`.

## 8. The Judge gate, the packet, the wall

**When Judge is called:** on evidence. `finish` opens a no-AI gate; a failure returns to Build without spending a Marker.

1. Sha on origin/main, contract at current version.
2. Every clause has a receipt from a **supervisor-run, uncached** oracle at that sha, at its tier.
3. Base red and guard red on file with matching signatures.
4. Packet passes lint. `code_review_status` CLEAN on touched files.
5. No tighten pending, no leaf dep stale.

The supervisor runs these itself, so a green is never just Build's word. Cost: real, bounded by offline tiers first. Live
receipts go through the adapter's queue.

**The packet** is the contract's four parts, as JSON with no free field. The supervisor copies goal and proof from the
contract, computes the range and `oracle_diff`, and refuses any mismatch. Build authors only `exists`, `how_to_check` (from a
command and expected-output pair) and `unverified` (flat clauses, 200 characters each, no "because"). Lint: schema, then a
forbidden-word list, then the Marker's own contract check as the semantic layer. A contaminated packet spends a fresh Marker.

Dropping the `evidence` prose is the point. MEASURED: 6 of 48 done `evidence` fields hold history or advocacy words (grep, a floor).

**The wall** is a mount namespace, declared per mode as data, so it is a checked field and not prose:

| Mode | Cannot see | Can see |
|---|---|---|
| Build | hold-outs, seed keys, verdict history | clone, its memory, public contract |
| Setter | everything of Build's, other items' runs | repo at base, item, DEFECTS |
| Marker | store, memory, attempts, git history, `conversations/`, ledger notes, seed keys, commit messages | packet, exported tree at sha (no `.git`), supervisor's diff file, hold-outs, hunting list |
| Help | hold-outs, seed keys, `reading`, `state.md` | clone read-only, evidence columns |

MEASURED: `systemd-run --user -p InaccessiblePaths=` denies the store on this host, and `bwrap` is installed. Not yet proved on
the real worker launch path; §13 step 1 proves it there. `RELENTLESS_ROOT` leaves the Marker's env: a verdict is written through
a narrow bound path holding only its nonce.

**The Marker:** packet check first; reruns everything itself in its tree; runs hold-outs; judges the contract against the item
(a too-easy contract is a FAIL); hunts `DEFECTS` classes; must state per clause what it ran and saw. Verdict: PASS, FAIL,
REJECT-PACKET, or UNJUDGEABLE, which never collapses to a pass. It never proposes a fix's design. It uses a purpose-written
agent: today `checker_agent` is `rm-judge`, the art judge.

Leniency is the known failure. Logged Marker/human disagreements feed the Arbiter's tuning, with seeded misses as the regression set.

**A second model** marks when the contract is `owner_part: yes`, when the diff touches an instrument or a gate, and on the
walk leaf. A disagreement is a FAIL-to-review, not an average.

## 9. Escapes, seeds, TRUST

**Escape:** anything found wrong after a PASS, by him, live, Auditor, a later Marker, or a regression. `relentless escape` writes
one record and requires its layer:

`contract_gap | oracle_blind | marker_missed | memory_poison | evidence_faked`

Effects, all mechanical: a `DEFECTS.md` row (RA-nnn); the finish line tightens (old PASS void, item back at the top); a test
that fails on the old build (TE4); a class line on the **hunting list**.

The hunting list is what the Marker reads: classes and probes, 12 lines maximum, no item history. A class seen twice stops being a
line and becomes a gate in code (RO5); it leaves the list. Fix the domain, not the instance, and signs do not accrete.

**Seeds** run through the real Marker, by the real path:

- After a real PASS, at rate `seed_rate`, a separate Setter-mode instance writes a fault into a copy of the candidate, drawn from a
  DEFECTS class. The supervisor builds a packet identical in form. A Marker sees exported tree and packet, with no `.git`, so
  nothing marks it as planted. The sha never reaches main; the key is in seed storage.
- **Controls:** known-good candidates go through too, so a Marker that fails everything scores badly.
- Equivalent mutants: a miss on a seed is second-read by a human or other model before it counts.
- **Other planted streams,** on the same table: contaminated packets (lint and Marker), false memory rows (must expire or be
  dropped), planted circling workers, and cache changes that must miss. Each fault table row is a conformance test.

**`relentless trust`** computes `TRUST.md` from the store, no prose:

| Measure | Computed from |
|---|---|
| Finish rate | accepted ÷ intake-accepted, unaided, by window |
| Escaped defects | escapes ÷ PASSes, ageing by window |
| Marker catch rate | per class, with counts and control false-fail rate |
| Contaminated packets | rejects ÷ packets, seeded and real |
| Repeat work | hours on cache-known results, time ledger |
| True stops | `stuck` or held items a Conductor agreed needed a human |
| Help value | movement after Help ÷ Help calls |

Bars stay his, unset. Counts stay honest: 0 misses in 30 seeds still allows about 10% (rule of three). Until a bar is set and
met, reports say "accepted by Judge", never "trusted".

## 10. How the v3 roles use it

| Role | Part |
|---|---|
| Owner | Experience statements; VALIDATES roots; loosens; first look; sets TRUST bars |
| Conductor | Receives `stuck`, §2 holds and loosening requests; reads TRUST. Never marks work |
| Concept agent | Upstream supplier, not a chair here: delivers the tree. Designed under its own item |
| Producer | Sets order; files goals; admits a mod once its tree exists. Proposes `budget`. WIP cap (RO2) reads the leaf count |
| Arbiter | Co-owns roots; signs coverage; tunes the Marker from disagreements. A Marker PASS is the non-maker verdict RO3 needs; an Arbiter FAIL blocks the close (ruling D1(b)) |
| Auditor | Samples closes, classifies escapes by layer; repeated classes become rules (RO5) |
| Operations | Reads signals, time ledger, `trust`; owns alarm routing (RO4) |
| Innovator | Reads finding curves; proposes ablations: each rule names the assumption it encodes and the test that would retire it |
| Foundry | Staffed by the filler; keeps FlowWorks and GSS; its head hands leaves to the queue |
| BENCH | Owner's live looks when `owner_part: yes` |
| Test Pilot | The `pilot` approach, and live-tier receipts |

The pool's `foreign_exclude` stands. `pool_needs: ["offline"]` stands until a live tier has a receipt path; §13 step 9 opens it.

## 11. Core, ports, adapter

Extraction only (owner: *"only extracting out RimMandrake-specific items, not changing its design for re-use in any way."*).
Ports are named from the `Effects` methods that exist, so nothing new is invented:

| Port | Live code |
|---|---|
| Tracker | `ledger_*`, `item_text`, `closed`, `pool_order`, `seat_*` |
| Workspace | `prepare`, `clean_checkout`, `bundle_clone`, `restore_bundle`, `remove_clone`, `pool_*` |
| Runner | `launch`, `alive`, `stop`, `tokens`, `activity`, with per-mode wall profiles |
| Proof | oracle tiers, `live_check`, `published`, red and guard runs |
| Host | `mem_gb`, `oom_kills`, `budget`, `burn` |
| Notifier | `conductor_alarm`, `told`, `alarm_signal` |
| Consult | Help's and second-mark's other model |

Core: state machine, fencing, store, memory, signals, gate, packet schema, seeds, trust, rules. Adapter (`rimmandrake`):
modcheck and north-star oracles, tier list and forbids, prompt lines, foreign-seat logic, DEFECT classes. A word lint fails the
core on game terms. A toy fixture repo is the second adapter, and the fault table is the conformance suite for both. Records carry
`schema_version`. Definition stays in `MandrakeWorkflows/relentless`; code moves there last, once a step proves it can.

## 12. What stays unsolved

- **Correlated blindness.** A Setter and Marker share Build's model, and second vendors correlate too. Seeds bound the misses of
  seeded classes only; an unseeded class has no number.
- **Taste.** Oracles reach "the screen shows X", never "this is delightful". That stays his eye, once per mod's first GREEN. Later
  drift below his attention is detected only as far as bars state it.
- **A wrong tree** passes all stages. A tree with a missing concept, or a Setter binding that reads the wrong quantity, is
  checked by nothing downstream except his eye and hold-outs. Coverage signing proves lines map to leaves, not that the lines
  were the right ones. A tooling leaf has not even that.
- **Meaning-level circling.** Fingerprints catch exact repetition; the same idea in new words is unmeasured, and repetition is a
  minority of failure anyway.
- **Thresholds** are guesses until the replay. Self-reported `reading` stays judgment; bad memory is bounded, not removed.
- **Threat model stays honest-but-stale.** The wall stops accident, not a hostile worker on the same host.
- **A commit reaches main before its check** (`finish` names a published sha). Failed candidates sit on main until fixed. Unchanged here.
- **Long properties and rare live behaviour** cost more than any budget here; a tier can only state what it did not run.

## 13. Build order

Each step lands, is proved by its planted fault on the real path, and stops. New rules run report-only first. Order: **measure,
then wall, then change**, so the baseline exists before any improvement claims it.

| # | Step | Proved by |
|---|---|---|
| 1 | Wall profiles on the real launch path; Marker gets exported tree, no store, no env root | Unit run tries to read store, `.git`, `conversations/`: denied. Real check still reaches a verdict |
| 2 | Packet schema and lint, report-only | Planted contaminated packets rejected; 48 real ones scored by hand for false rejects |
| 3 | Seeds, controls, `relentless trust` | First catch-rate baseline on today's Marker, over a set of real DEFECTS classes, recorded before any change below |
| 4 | Purpose-written Marker agent, hunting list | Same seed set rerun, compared with step 3 |
| 5 | Tree intake and Setter binding, report-only on new items, then refusing | An item with no tree, and a tree missing each field, is refused; a Setter edit to a criterion is refused; a `waived` line gets no leaf; hand-graded sample of bindings against worker contracts |
| 6 | Base and guard red; evidence gate | A check that cannot go red is refused; a guard that leaves it green blocks. Pit case replayed: `false_pass` goes red |
| 7 | Versioned finish line; `redesign` loses the contract | Redesign edit refused; tighten voids PASS; loosen without `--owner-said` refused |
| 8 | Hold-outs, burn | Build's unit cannot read them; a burn moves the clause and spawns a replacement |
| 9 | Live tier receipts; pool opens to one live-tier leaf | A real live leaf closes through a testq or pilot receipt on the deployed hash |
| 10 | Memory: `tried`, `state.md`, citation check, cold redesign | Seeded stale row marked; dead worker leaves supervisor row; replay compares returns-to-done with `learned` tail |
| 11 | RW1 time ledger, fingerprints, signals report-only | Fixture within 5%; replay labelled runs for misses and wrongful stops |
| 12 | Interrupts: fact hook, then stop | Planted workers stopped within limit; long build and long read left alone |
| 13 | Help, `stuck` hold | Two hits give one consult; options reach the brief; no movement after two rounds holds |
| 14 | Cache coverage, audit | TE2 tests; seeded XML change misses; gate and Marker refuse a cached result |
| 15 | Escapes, tighten, hunting list flow | Fixture escape files every effect; a test passing on the old build is refused |
| 16 | Goal tree, stale leaves, walk leaf, on one small mod with a VALIDATED north star | Pre-registered: **the Pit test.** Given the 2026-09-15 Pit, the system must not say GREEN |
| 17 | Extraction, toy adapter, conformance | Same selftests pass before and after; word lint clean; fault table passes on both adapters |
| 18 | Trust trial: a fixed set of modest goals, unattended | `relentless trust` numbers given to him to set bars |

Owed after review: the tree's file format, agreed with MOD_CONCEPT_AGENT_DESIGN_ARGUES_BEFORE_BUILDING; the Conductor's ruling on the findings, a matching update of `RELENTLESS_AGENT.md`, and one rimflow item per step.
