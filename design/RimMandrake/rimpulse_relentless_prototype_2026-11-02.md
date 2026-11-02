# RimPulse with Relentless — markdown prototype v1 (2026-11-02)

Owner, 2026-11-02: *"With Relentless, I think Rimpulse's purpose is tremendously different. We should prototype
in markdowns first so I don't have you chasing design all over the place in the meantime."*

Nothing is built from this until he has reacted to it. Mark it up in place; v2 follows his notes.

## The shift

Old RimPulse watched **seats** (who is busy, which window holds the bridge, what each seat said).
With Relentless, the work is a **line of items** carried by replaceable workers, so the seat is no longer the
interesting thing. The questions become:

1. Is the factory running and safe? (one glance)
2. What is on the line right now, and is each item moving or circling?
3. What came off the line, and did an independent check pass it?
4. What needs me? (only true owner calls)
5. What is it costing, and what is wasted?

## Mockup (one screen, phone first)

```
RIMPULSE                                   05:12  ● factory running   disk ok   watchdog ok
──────────────────────────────────────────────────────────────────────────────────────────
NEEDS YOU (1)
  ▸ TEMPLE_NINE … asks: "our own gods first, or reuse the vanilla ones?"   held 2 h   [open]

ON THE LINE (4 of 4 workers)                                   bridge: free · game: down
  ▸ Pipe atlas kink          gen 3  attempt 2   offline   moving    12 min since last step
  ▸ Walk saves silence       check 1            offline   checking  blind checker running
  ▸ Suspension proof         gen 5  attempt 3   LIVE      waiting   queued for the bridge
  ▸ Ant hive geometry        gen 7  attempt 4   offline   CIRCLING  same blind fail twice → redesign next

OFF THE LINE TODAY (14)                              all passed a blind check · 1 reopened
  ▸ Flier frames fill        passed first try      3 files   [commit]
  ▸ Amend hook harden        passed after 1 fail   2 files   [commit]
  … 12 more                                                          [show all]

PARKED (9)          blocked on: predecessor 5 · owner 1 · judge 2 · game 1        [show]

COST TODAY          31M tokens · 2.2M per pass · 18% spent on items that never passed
WASTE               2 items circling · 0 restaffs on a known blocker · clones 4/10 (14 GB)
```

## What each band reads (all of it exists or is being built)

| Band | Source |
|---|---|
| Factory light | `rm-relentless.timer` alive, breaker state, integrity gate result, Windows heartbeat log, `df` |
| Needs you | Relentless items held with `owner_call` (delegation_policy §2 only), plus `pulse hand` looks |
| On the line | `relentless/store/items/*/state.json` (gen, attempts, approach, last beat), `runs/roles/*` |
| Moving / circling | `circling.py` marks; two same-kind rejections = circling |
| Off the line | `journal.jsonl` `done` + blind-check verdicts; reopen events from the ledger |
| Parked | the structured `blocked_on` field (PLAN_BUILD_BLOCKED_BY_IS_TEXT_ONLY) |
| Cost and waste | `spend-YYYYMMDD.json` (real usage after RELENTLESS_USAGE_MEASURE_NO_FLAT_GUESSES), clone pool report |

## What goes away

Per-seat busy lamps, per-seat chat excerpts, the seat timeline as the main view. FOUNDRY live work shows up
as items on the line like any other once Relentless runs live mode.

## Questions for him

1. Is "Needs you" really the top band, or does the factory light come first?
2. One screen like this, or a phone glance (top three bands) plus a detail page?
3. Should finished items show what changed in plain words, or just the item name and a commit link?
4. Does Fleet Watch (the Conductor's own helpers) fold into this, or stay separate?
