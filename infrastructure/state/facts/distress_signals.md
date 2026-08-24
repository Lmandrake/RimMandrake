# What predicts that a queue item is in trouble — measured 2026-08-23

**Measured by REP with the owner, on `infrastructure/state/ledger/events.jsonl` as it stood
2026-08-23T20:4x PDT: 2,029 events, 436 items, 306 closed / 47 dropped / 83 open, spanning
2026-08-21T05:05Z → 2026-08-24T03:06Z (2.92 days).** Feeds the BENCH scan in
`infrastructure/agents/REP.md`. ⚠️ **Every weight below is a rounded LIFT from this population.**
Re-derive at three weeks; do not treat any number here as a constant.

## 🔴 Two methodological traps that will bite anyone who redoes this

1. **The backfill.** The ledger opens with **352 events stamped across 3 timestamps inside 2 seconds**
   (05:05:16–05:05:18Z), including **122 claims**. It is an import, not work. Exclude by a 60-second
   window from `t0`. A narrower filter left six items reading as "claimed 70 h ago" — the full age of
   the ledger — and every one was an artifact.
2. **`drop` is mostly not failure.** Of 47 drops, **38 are triage** (24 blanket-v2 rulings, 9 owner
   rulings, 5 premises measured false) and **only 9 are failures** — 5 outside the backfill.
   ⛔ **Do not fit a mortality model on this.** n=9 is noise. Track detention instead.

## The clock: expected duration is per-KIND and varies 7×

Absolute age is meaningless on a mixed board. p90 of items that CLOSED:

| kind | n | median | **p90 — the detention line** |
|---|---|---|---|
| decision | 68 | 0.65 h | **7.25 h** |
| task | 123 | 1.85 h | **15.01 h** |
| fix | 15 | 2.62 h | **15.18 h** |
| check | 45 | 12.78 h | **53.41 h** |

🔑 **A ruling sitting 20 h is in trouble; a check running 40 h is normal.** Compute these at run time
from closed items — hard-coding them guarantees they are wrong within a fortnight.

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

⭐ **Direction is the whole signal, not movement.** Upstream-reassigned items live **10.5 h against
1.5 h** median and close **26.9% against 72.9%**. Downstream is the conveyor working; upstream is a
seat saying *"this is not what I thought it was."*

## ⛔ REFUTED — do not re-derive these, they cost an hour

- **Prose thinness predicts NOTHING.** `has_file`, `has_spec`, `has_verify`, `has_criteria` and
  links-to-other-items all sit at **AUC 0.48–0.53, coin flips**, against death. Against detention they
  are **inverted**: no prose file **0.00×**, under 200 words **0.00×**, no `## spec` **0.00×**. Not one
  thin item was ever detained. 🔑 **Thin items are thin because they are small, and small things
  finish.** What kills work is contested scope, and contested things are verbose.
  ⇒ The mandatory `## spec` / `## verify` / `## criteria` prose buys **no** early warning. It may be
  worth writing for other reasons; it cannot be defended on this one.
- **The apparent thinness effect was the backfill.** 70% of dropped items are backfilled vs 28% of
  closed; backfilled items drop at 22.9% vs 4.8%. Control for it and word-count AUC falls 0.615 → **0.49**.
- **"Fast class stuck in a long line" is not a term — it is the DENOMINATOR.** Cohort-relative slowness
  scored **0.45–0.60× against drops**. It works only as the per-kind normalisation above.
- **Reassignment COUNT is misleading.** Its top hit had **11 reassignments and closed in 1.0 h** —
  DECIDE reassigning an item to itself to get past `COMMIT_GUARD_BLOCKS_SPECS_1`.
- Useless breadth: silence >48 h flags 21 of 83 open; unmet `needs` flags **51 of 83 — that is just the
  load queue**; `spawn`/`caused_by` has no hotspot.

## The coarse index

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

🔑 **When it fires, believe it. When it does not, that is not safety.** Good triage, bad alarm.

## ⚠️ Why this is not on the board, and must not be

Every other board tile measures a fact about the world — `ps`, a TCP probe, `git`. **This one measures
actions seats CHOOSE**, so it is the one metric that can be gamed. Most pressure it creates is
harmless; one is not. **Penalising upstream reassignment would teach seats to absorb mis-scoped work
rather than hand it back** — which is worse and invisible. So the score goes to the OWNER and to REP;
a seat gets the underlying fact (*"claimed 33 h, no commit"*) and never a number to optimise.

## What would sharpen it

1. 🔴 **`reassign` records no `from` — 0 of 73.** The best signal is reconstructed by inference. One
   line at the writing end, and it is the prerequisite for trusting it.
2. No event exists for a seat putting an item DOWN. Claims are visible; abandonment is not.
3. **195 of 436 items carry no `needs` on any event**, which blurs every population count here.
