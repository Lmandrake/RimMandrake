# Functionless tech — repurposing candidates

Owner's ask, 2026-09-04 (going AFK): *"flag effectively functionless tech in the
game that might be repurposed for our plot or other functions."*

Method: every SURVIVING manifest row (untouched/keep/reflavor) checked against
the live 2026-09-04 capture's `cachedUnlockedDefs`, cuts read via
`cherrypicker.py` (typed where the type is known). A row is a candidate when it
unlocks NOTHING that still exists. 15 hits: 7 are the prep-§1 allowlist
(mechanism-only unlocks — biosculpter cycles, surgery ops, job unlocks — alive,
no action) and 8 are genuinely functionless today, triaged below.

⚠️ An empty `cachedUnlockedDefs` misses mechanism-only unlocks by design —
each row below was judged on its description and mod, not the cache alone.

## The 8, triaged

| tech | tree · tier | mod | verdict + repurpose hook |
|---|---|---|---|
| Ancient Era Ship Designs | THE SHIP · T3 | Jawa Armoury Rebalance | **ALREADY RULED reflavor** (`shape_src`, memory-core-gated trio). The strongest plot carriers on this list: currently unlock nothing, which is exactly the room the ship-memory reveals need — each design era becomes a chapter the Utinni *remembers*. |
| Clone Wars Era Ship Designs | THE SHIP · T3 | Jawa Armoury Rebalance | same trio, same hook |
| Empire Era Ship Designs | THE SHIP · T3 | Jawa Armoury Rebalance | same trio, same hook |
| Xenobiology | The Reach · T1 | Space Worms | Pure flavor today ("identifies non-native lifeforms"). **Prime repurpose**: the study node for Ash'karr's strange fauna — sea-beasts, the sarlacc — and a natural anchor for the non-research containment route `ANOMALY_EXCEPTION_ACCESS_1` needs. |
| Subspace gravitic penetration | The Waking Mind · T2 | RimAI Core | Structural: it gates the RimAI ladder by prereq even though it unlocks no thing. **Repurpose**: fold into the Rites' God-Speaker Array flavor — the moment the ship's voice first *echoes back*. |
| mobile mineral sonar: enhanced | The Refinery · T1 | MiningCo. MMS | A settings-tweak upgrade for one scanner tool. Weak as content. Either reflavor as Jawa sand-prospecting craft or a **cut candidate** next trim. |
| food preparation | Scavenger · T0 | Research Reinvented | RR scaffold node (splice target). **Leave alone** — RR is the ruled substrate; its pseudo-nodes are load-bearing prereqs, not content. |
| lateral thinking | Scavenger · T0 | Research Reinvented | RR's orphan-prereq catch-all. **Leave alone**, same reason. |

## The 7 allowlisted (alive, listed for completeness)

mining · complex clothing · efficient drilling · bioregeneration ·
archogenetics · warcasket removal · Energy Systems (droid modules) — all carry
mechanism-only unlocks the cache cannot see (prep §1's confirmed-alive list).

## Where the next functionless tech will come from

The mech cut (owner's frozen deck) and future Cherry Picker trims create new
all-unlocks-cut rows silently. Re-run this sweep (the logic lives in this
file's git history and in `research_manifest_validate.py` check 1) after any
cut wave — a clean 0 today is not a standing fact.
