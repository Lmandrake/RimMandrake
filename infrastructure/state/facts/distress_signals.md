# What predicts that a queue item is in trouble — measured 2026-08-23

**Measured by REP with the owner, on `infrastructure/state/ledger/events.jsonl` as it stood 2026-08-23T20:4x PDT.**

- The ledger held 2,029 events and 436 items: 306 closed, 47 dropped, 83 open.
- The ledger spanned 2026-08-21T05:05Z → 2026-08-24T03:06Z (2.92 days).
- REP is a retired seat (`infrastructure/agents/REP.md`).
- The query `rimflow next --bench` computes the index
  of this file (`cmd_bench` in `src/RimMandrake/rimflow/cli.py`).
- A lift of detention is the rate of detention among flagged items, divided by the base rate (8.2%). The next two
  sections define detention and the base rate.
- ⚠️ **Every weight below is a rounded LIFT from this population.** Re-derive each weight at three weeks. Do not treat
  any number here as a constant.

## 🔴 Two methodological traps that will bite anyone who redoes this

1. **The backfill.** The ledger opens with **352 events stamped across 3 timestamps inside 2 seconds**
   (05:05:16–05:05:18Z).
   - Those events include **122 claims**. The backfill is an import, not work.
   - Exclude the backfill with a 60-second window from `t0`, the first timestamp.
   - A narrower filter left six items that read as "claimed 70 h ago". That is the full age of the ledger. Every one of
     the six was an artifact.
2. **`drop` is mostly not failure.** There are 47 drops.
   - **38 are triage**: 24 blanket-v2 rulings, 9 owner rulings, 5 premises measured false.
   - **Only 9 are failures**, 5 of them outside the backfill.
   - ⛔ **Do not fit a mortality model on this.** A sample of n=9 is noise. Track detention instead.
   - Detention means that an item lives longer than the p90 of its own kind (next section).

## The clock: expected duration is per-KIND and varies 7×

Absolute age is meaningless on a mixed board. This table shows the p90 life of items that CLOSED:

| kind | n | median | **p90 — the detention line** |
|---|---|---|---|
| decision | 68 | 0.65 h | **7.25 h** |
| task | 123 | 1.85 h | **15.01 h** |
| fix | 15 | 2.62 h | **15.18 h** |
| check | 45 | 12.78 h | **53.41 h** |

- **A ruling that sits for 20 h is in trouble. A check that runs for 40 h is normal.**
- Compute these figures at run time, from closed items. Hard-coded figures are certain to be wrong within a fortnight.

## What predicts detention (life > its own kind's p90). Base rate 8.2%

**Readable on the item at filing time — two fields, and that is all:**

| signal | lift |
|---|---|
| `needs: owner` | **4.26×** |
| `needs: game-up / bridge / harvest / deploy` | 2.65× |

**Visible only by watching it:**

| signal | lift |
|---|---|
| blocked, unresolved | **5.62×** |
| ≥2 notes since the last commit — talk without work | **3.20×** |
| **upstream** reassign (CHECK→BUILD, CHECK→DECIDE, BUILD→DECIDE) | **2.28×** |
| owner had to intervene (`ownerSaid` / `override`) | 2.13× |
| **downstream** reassign (DECIDE→BUILD→CHECK) | **0.55×** |

**Direction is the whole signal, not movement.**

- Upstream-reassigned items live **10.5 h against 1.5 h** median. They close **26.9% against 72.9%**.
- Downstream is the conveyor working. Upstream is a seat that says *"this is not what I thought it was."*

## ⛔ REFUTED — do not re-derive these, they cost an hour

- **Prose thinness predicts NOTHING.** `has_file`, `has_spec`, `has_verify`, `has_criteria` and links to other items all
  sit at **AUC 0.48–0.53, coin flips**, against death (a dropped item).
  - Against detention, these fields are **inverted**: no prose file **0.00×**, under 200 words **0.00×**, no `## spec`
    **0.00×**. Not one thin item was ever detained.
  - **Thin items are thin because they are small, and small things finish.** What kills work is contested scope, and
    contested things are verbose.
  - So the mandatory `## spec` / `## verify` / `## criteria` prose gives **no** early warning. That prose may be worth
    writing for other reasons. It cannot be defended on this one.
- **The apparent thinness effect was the backfill.** 70% of dropped items are backfilled vs 28% of closed items.
  Backfilled items drop at 22.9% vs 4.8%. Control for the backfill, and the word-count AUC falls 0.615 → **0.49**.
- **"Fast class stuck in a long line" is not a term — it is the DENOMINATOR.** Cohort-relative slowness scored
  **0.45–0.60× against drops**. That slowness works only as the per-kind normalisation in the clock section.
- **Reassignment COUNT is misleading.** The top hit of the count had **11 reassignments and closed in 1.0 h**. DECIDE
  reassigned that item to itself to get past `COMMIT_GUARD_BLOCKS_SPECS_1` (the commit guard refused a filing seat its
  own spec prose).
- Useless breadth. These signals do not single out an item in trouble:
  - Silence >48 h flags 21 of 83 open items.
  - Unmet `needs` flags **51 of 83 — that is just the load queue**.
  - `spawn`/`caused_by` has no hotspot.

## The coarse index

The number is the score that each signal adds.

```
3  blocked, unresolved >24h  (1 if <24h)   2  per upstream reassignment
2  needs: owner                            2  age > its own kind's p90
2  ≥2 notes since the last commit          2  claimed >24h, no commit since
1  needs game/bridge/harvest/deploy        1  owner had to intervene
```

**Backtested with the age term removed, because it leaks the target:**

| threshold | flags | recall | precision | lift |
|---|---|---|---|---|
| ≥2 | 57/353 | 44.8% | 22.8% | 2.78× |
| **≥3** | **21/353** | **31.0%** | **42.9%** | **5.22×** |
| ≥5 | 4/353 | 10.3% | 75.0% | 9.13× |

**When the index fires, believe it. When the index does not fire, that is not safety.** The index is good triage and a
bad alarm.

## ⚠️ Why this is not on the board, and must not be

- Every other board tile measures a fact about the world: `ps`, a TCP probe, `git`.
- **This index measures actions that seats CHOOSE.** So the index is the one metric that can be gamed.
- Most pressure that the index creates is harmless. One pressure is not harmless. **A penalty on upstream reassignment
  would teach seats to absorb mis-scoped work rather than hand it back.** That is worse, and it is invisible.
- So the score goes to the OWNER and to BENCH (the Conductor). A seat gets the underlying fact (*"claimed 33 h, no commit"*). A seat never
  gets a number to optimise.

## What would sharpen it

1. 🔴 **`reassign` records no `from` — 0 of 73.** So the best signal is reconstructed by inference. One line at the
   writing end fixes this. That line is the prerequisite for trusting the signal.
2. No event exists for a seat that puts an item DOWN. Claims are visible. Abandonment is not.
3. **195 of 436 items carry no `needs` on any event.** This blurs every population count here.
