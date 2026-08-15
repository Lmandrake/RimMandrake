# Speed — the measured numbers

Read this before you optimise anything, before you quote a timing, and when a
loop runs slower than you expected.

---

## Cost tracks call count

**Cost tracks CALL COUNT, not cell count.** That one sentence is the whole
performance model, and everything below follows from it.

| operation | measured |
|---|---|
| `rimbridge/ping` | 0.3 ms — does not touch the main thread |
| any main-thread call | **4–17 ms**, varying run to run — see the warning below |
| `save_game` (13.9 MB) | 0.5 s |

A call in a tight sequence costs ~50 ms, three frames — not the 16.7 ms an
isolated call costs. So the number that matters is how many calls you make:

| a 421-cell dithered crater | calls | time |
|---|---|---|
| one cell at a time | 421 | ~7.0 s |
| one call per rect | 124 | 1,611 ms |
| **`jawa/set_terrain_batch`** | **1** | **14.0 ms** |
| capture, one `get_cell_info` per cell | 421 | 6,086 ms |
| **`jawa/get_terrain_batch`** | **1** | **17.5 ms** |

Measured 2026-08-12 on a live 250×250 map. A whole `formations.crater()` — 977
ground cells plus 100 scattered objects — is **0.52 s**, of which the terrain is
a single hop.

**Consequence:** each time you batch one layer, the cost moves to the next.
Terrain stopped dominating and object spawning took over — a crater became one
terrain call and ~100 `spawn_thing` calls. `jawa/spawn_batch` closes that too.
Measured against a stub, per formation:

| formation | per-call companion | batched |
|---|---|---|
| crater | 199 calls | **2** |
| cavern | 49 calls | **1** |
| geyser field | 67 calls | **2** |

Batch anything you do per-cell, or design around ~20 unbatched calls per second.
`src/RimMandrake/Utils/rimbench/selftest.py` asserts these call counts, so a refactor that
reintroduces a per-cell loop fails a test rather than just running 100× slower.

⚠️ The old "0.002 s per call" figure in this file was measured on **3 mods,
paused**, and did not survive the full stack. Treat any timing note as carrying
the tier it was measured on.

⚠️ **There is no 60 Hz frame gate, and a single latency number is not quotable.**
Every main-thread class once measured 16.7 ms at 568 mods and was written down as
a hard one-frame floor; two later runs on **one map** read `get_game_info` 5.673
then 4.358 and `jawa/set_terrain` 21.017 then 13.648. 4.4 ms reads cannot come
from a 16.67 ms tick, so the gate is refuted; the cause of the spread is unknown
and every mechanism offered has been withdrawn (pawn count went **up** while
latency went **down**). Mod tier is not the axis — three runs at 573 on one map
disagree by 35%. **Record the workload and `ticksGame` beside every benchmark,
and quote a range with its conditions or quote nothing.**

**Consequence:** prefer live bridge work over save-editing. Bridge changes are
also **reversible** — the player reloads if they dislike the result — where a
save-edit permanently changes state.

Full reasoning, tradeoffs and the test order:
`design/RimMandrake/map_authoring_decision.md`.
