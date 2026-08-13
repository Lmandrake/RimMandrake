# Map authoring: RimBridge vs save-editing — the decision

_Owner + assistant, 2026-08-12. Written at the point where both paths are
proven and the choice is real._

## The goal

> A boring new tile map is loaded, an app runs, and the map is now amazing,
> improved, interesting and fascinating to explore.

Abandoned semi-working oil refineries with angry aliens descending out of the
pipeworks. Procedural caverns. Towns far better than Large Faction Bases. Ship
graveyards with ruined gravships. Galatross caves where they actually live, and
they are HUGE now. Geyser maps where explosive fumes are a reusable weapon.

Three uses: **(1)** debugging, **(2)** tile enhancement right after a ship
landing, **(3)** exposing game and mod elements the player cannot build
themselves, such as a complex oil refinery already working.

## The owner's position

RimBridge doing **everything** is superior if it can be wired up properly. No
asking the player to save, wait and reload — they click, and the map changes.

**With one caveat: is it fast enough?** Save-editing is likely near-instant once
the content generator has decided what to place. If RimBridge needs minutes of
horsing around to execute the same plan, that is workable but no better than a
save/load cycle.

## ⚡ The measurement that settles it

Measured live, 3-mod game, 2026-08-12:

| operation | time |
|---|---|
| bridge **read** call | **0.002 s** |
| bridge **mutation** call | **0.002 s** |
| `save_game` (13.9 MB) | **0.5 s** |

**Two milliseconds per call.** Extrapolated:

| workload | cells | via bridge |
|---|---|---|
| a crater | ~317 | **0.6 s** |
| a furnished room | ~21 | 0.04 s |
| a whole settlement | ~2,000 | 4 s |
| **every cell of a 250x250 map** | 62,500 | **2.4 min** |

**The speed objection largely evaporates.** Nothing a content generator
realistically produces touches every cell; a dramatic crater is 300 cells and
lands in under a second. Only a full-map terrain replacement is slow, and that
is not what any of the ambitions above actually need.

⚠️ Measured on a **3-mod** game, **paused**. Re-measure on the 568-mod stack
before treating 2 ms as universal — Harmony patch depth and TPS load could
change it. This is the single most important number to re-verify.

## ✅ RE-MEASURED ON 568 MODS, 2026-08-12 — the verdict holds

file:///D:/Luke/dev/Rimworld/observed/2026-08-13_pre-restructure/latency_568mod.json (n=200/class, paused,
same as the baseline, so the comparison is like-for-like).

| call | 3-mod median | 568-mod median | 568 p99 | 568 max |
|---|---|---|---|---|
| `rimbridge/ping` | 0.33 ms | **0.31 ms** | 0.82 ms | 0.94 ms |
| `get_cell_info` | 1.41 ms | 16.67 ms | 18.70 ms | 165.8 ms |
| designator `dryRun` | 2.83 ms | 19.61 ms | **102.1 ms** | **219.9 ms** |
| `jawa/set_terrain` (1 cell) | 4.91 ms | 16.71 ms | 21.62 ms | 54.1 ms |
| **`jawa/set_terrain` 6×6 = 36 cells** | 28.6 ms → 0.79 ms/cell | **18.27 ms → 0.51 ms/cell** | | |

**FPS was verified at 60 during the bench**, by taking a bridge screenshot at
the moment of measurement and reading the counter — not assumed from the
16.67 ms figure, which would have been circular. A separate screenshot four
minutes earlier read 34 FPS with the dev palette open, so the frame rate does
move; the bench was taken idle and parked.

⚠️ **Consistent with frame-locking, not yet proof of it.** 60 FPS and a 16.66 ms
quantum agree, but every sample so far was taken at 60 FPS. The decisive test is
to measure the floor while the frame rate is genuinely lower (zoom right out, or
unpause): if it rises to ~29 ms at 34 FPS the cost is the render frame, and
uncapping the frame rate would lower it; if it stays at 16.66 ms it is a fixed
60 Hz dispatcher tick and no frame-rate change will help.

**Attempted 2026-08-12 with `src/RimMandrake/Utils/frame_lock_probe.py`, and it did not settle
it.** Latency was flat across all five zoom levels (16.62 / 16.80 / 16.75 /
16.78 / 16.91 ms, spread 0.29 ms) — but the FPS counter read **60 at every
level**. Zoom does not move the frame rate on this map; vsync pins it. The
independent variable never varied, so flat medians say nothing. Reporting it as
"flat → fixed tick" would have been a false result from a test that never ran.

A genuine frame-rate change is still needed — vsync off in the driver, or a
frame-cap mod. One indirect data point in favour of frame-locking: with
`runInBackground` off, an unfocused window stops rendering and main-thread
dispatch stops **completely** (see below), which is what a render-driven pump
predicts and an independent OS timer does not.

### ✅ SETTLED 2026-08-12 (evening) — it is NOT a fixed 60 Hz gate

**The variable that finally moved was the colony, not the zoom.** Re-running
`bridge_latency.py` on a fresh dev quicktest map at 573 mods:

| class | busy 21-colonist map (568) | fresh quicktest (573) |
|---|---|---|
| `get_game_info` | 16.656 | **5.673** |
| `get_cell_info` | 16.673 | **5.847** |
| `jawa/set_terrain` | 16.708 | **21.017** |

Both runs **paused**, same bridge version, same probe cell (125,125), so pause
state and mod count are both ruled out. **5.8 ms is neither a multiple nor a
divisor of 16.67**, so there is no fixed dispatcher tick.

**What the suspiciously precise agreement actually meant.** Three different
operations reporting 16.656 / 16.673 / 16.708 was read here as evidence of a
shared 60 Hz gate. It is better read as evidence of a shared *queue* — identical
numbers mean "all waiting on one thing", not "all cost the same".

⚠️ **But the specific story about WHY is withdrawn.** The first version of this
note said the queue was main-thread business and that a busy colony is therefore
slower. A third run the same evening, on the same quicktest map after another
agent had populated it, went the other way: **51 pawns / 11 colonists measured
FASTER than 35 pawns / 3 colonists** (reads 4.36 vs 5.67 ms). Pawn count is not
the driver, and no replacement mechanism has been established. A plausible
untested candidate is time since map generation — run 1 was `ticksGame` ~5,
straight out of the generator; run 2 was 1109.

⇒ **`frame_lock_probe.py`'s question is answered well enough to close.** It stays
parked, and the batch API means a formation stops paying any floor ~100 times, so
the remaining uncertainty is not worth a driver change.

⚠️ **The `jawa/set_terrain` "+26% anomaly" is WITHDRAWN.** It read 21.0 ms in one
run and 13.6 ms in the next, on the same map, with no deliberate change between
them. It was never a stable property, and the instruction not to build on the
single-cell write cost stands for a better reason: **that number moves by 35%
between runs nobody deliberately changed.**

⚠️ **Every latency number in this document is a SAMPLE, not a property.** Three
runs at 573 mods on one map spread 35%. The tables above were measured on the
real 21-colonist map; treat them as one observation under known conditions, and
re-measure rather than quoting them as the cost of an operation.

**The added cost is a frame boundary, not Harmony depth.** Three calls doing
very different amounts of work all land within 0.06 ms of each other at
~16.67 ms, which is exactly one frame at 60 Hz. `ping` — the one call with no
main-thread hop — is *unchanged* from the 3-mod tier. And `get_cell_info`'s
**minimum** is 6.13 ms, far below its own median, which a work-bound cost cannot
produce. So a bridge call costs roughly `one frame + the actual work`, and the
frame is the whole story for anything small.

> ⚠️ **Superseded — read the evening section above.** "One frame" cannot be the
> story: medians of **4.4 ms** were later measured on the same bridge, and no
> 60 Hz boundary produces those. The one line here that aged WELL is the
> observation about the minimum — `get_cell_info` bottoming out at 6.13 ms while
> its median sat at 16.67 was already evidence that sub-frame calls were
> possible, i.e. the 16.67 was a queue the fast samples occasionally skipped
> rather than a gate every call had to pass. **The tell was in the data the day
> it was written; the median hid it and the minimum did not.**

**Which is why the 36-cell rect got FASTER, in absolute terms, than it was on
3 mods** — 18.27 ms against 28.6 ms. Thirty-six cells ride in a single hop and
amortise the one frame between them. Batching is no longer an optimisation; it
is the architecture. A generator that writes cell-by-cell pays ~16.7 ms per
cell and is ~33× slower than the same work batched into rects.

Revised extrapolation, at the measured 0.51 ms/cell for batched writes:

| workload | cells | via bridge, batched |
|---|---|---|
| a crater | ~317 | **0.16 s** |
| a whole settlement | ~2,000 | 1.0 s |
| every cell of a 250×250 map | 62,500 | 32 s |

### ⛔ That extrapolation is WRONG for real formations — measured 2026-08-12

A 411-cell dithered crater, generator → rect decomposition → bridge, took
**5.15–5.75 s**, not the 0.16 s predicted above. Off by ~35×.

| | cells | calls | total | per cell |
|---|---|---|---|---|
| hand-picked 6×6 rect | 36 | **1** | 15.2 ms | 0.42 ms |
| dithered crater | 411 | **103** | 5,150 ms | 12.59 ms |
| same crater, one-at-a-time (est.) | 411 | 411 | ~6,900 ms | 16.7 ms |

**Batching a real formation wins ~1×. Essentially nothing.** The 0.51 ms/cell
figure was real but not general: it measured a shape that packs into a *single*
call. A generator's output does not. A dithered boundary is deliberately
interlocked — that is what stops it reading as a bullseye — and it decomposes to
**~4 cells per rect**, so 411 cells cost 103 calls.

**Cost tracks CALL COUNT, not cell count.** And a call inside a tight sequence
costs ~50 ms, three frames, not the 16.7 ms an isolated call costs. Controlled:
the 6×6 test was re-run on this same map minutes later and still returned
15.2 ms for 36 cells, so it is the sequence that is expensive, not the map or
the mod stack.

Not the mesh refresh, either — that was the obvious suspect and it was tested.
`refresh=false` on all but the last call (the companion already takes the flag)
moved 13.99 → 12.59 ms/cell, about 10%. Worth keeping, nowhere near the cause.

**So the architecture needs a batch API, and it is ours to write.**
`jawa/set_terrain` takes one rect per call. It should take *many* — a list of
rects, or a rect plus a per-cell mask — collapsing a whole formation to one
main-thread hop. On these numbers that turns 5.15 s into roughly one call's
worth, ~20–50 ms. Until then, treat per-call cost as the budget: a generator
gets ~20 calls per second, and everything else follows from that.

⚠️ Companions load only at RimBridgeServer startup, so that change costs a game
restart. It should ride the next one rather than trigger its own.

**Reversibility is proven, and cheap.** Every changed cell's original terrain was
captured before painting and restored through the same machinery: 13/13 sampled
cells verified back to original, `cellsFailedVerify=0`, full paint + exact revert
round trip **7.34 s**. The undo does not depend on the player reloading.

**The one real mod-count signal is the designator path**, not ours: `dryRun`
p99 is 102 ms with a 220 ms max, against 9.4 ms p99 at 3 mods. Placement
validation genuinely does get more expensive with 568 mods' worth of patches.
**Recommendation: keep bulk authoring off `apply_architect_designator`
entirely** and go through the companion, whose p99 is 21.6 ms with no
comparable tail.

Against the decision rule agreed in advance — single-digit medians hold the
verdict, 10–30 ms means re-time a real formation, ≥100 ms reopens it — the
single-call medians land in the middle band, the re-timed formation was run,
and it came back better than baseline. **Verdict holds. Build the generator.**

## Where each path stands today

| | RimBridge | save-editing |
|---|---|---|
| things, buildings, furniture, pawns | ✅ proven | awkward (ID cross-refs) |
| natural terrain, rock, water, roofs | ✅ **proven 2026-08-12** via `jawa/set_terrain`; renders live, no reload | ✅ **proven** |
| destroy what was there | only via floor overlay | ✅ direct |
| runs while playing | ✅ | ❌ needs save/load |
| **reversible if the player hates it** | ✅ **just reload** | ❌ permanent, needs a backup |
| speed | **0.51 ms/cell batched** on the real 568-mod stack (~16.7 ms per unbatched call) | ~0.5 s whole-map |

Proof for save-editing: map grids are base64 + raw DEFLATE arrays of 2-byte def
shortHashes. Lossless roundtrip on all 62,500 cells, 76 cells painted through
`scatter.radial_field`, written, reopened, verified. See
file:///D:/Luke/dev/Rimworld/src/RimMandrake/Utils/rimbench/savemap.py

## The decisive advantage nobody measured: reversibility

RimBridge changes are **live and undoable** — if the player hates the crater,
they reload and try again. Save-editing **permanently changes game state**.
Recoverable with a backup, but that is a safety net, not an undo button.

For **use case (2)**, tile enhancement right after a landing, that difference is
close to decisive. The player should be able to reroll a generated site.

## The verdict

**Pursue RimBridge for everything.** Speed is not the obstacle it looked like,
and reversibility is a real advantage that save-editing cannot match.

~~The only true gap is **natural terrain**~~ — **closed 2026-08-12.**
RimBridgeServer 2.x has a documented, first-class companion-DLL extension point,
and we used it:

* file:///D:/Luke/dev/Rimworld/vendor/mod_sources/RimBridgeServer-main/skills/rimbridge-companion-tools/SKILL.md
* file:///D:/Luke/dev/Rimworld/vendor/mod_sources/RimBridgeServer-main/skills/rimbridge-companion-tools/references/companion-dll-guide.md

```csharp
[Tool("jawa/set_terrain")]        ✅ shipped, proven live, 16.7 ms on both tiers
[Tool("jawa/set_terrain_batch")]  ✅ shipped — a whole formation in ONE call
[Tool("jawa/get_terrain_batch")]  ✅ shipped — a whole region captured in ONE call
[Tool("jawa/destroy_at")]         ❌ not built — real excavation
[Tool("jawa/damage")]             ❌ not built — the graduated-damage bench
```

The two batch tools were not in the original plan. They exist because **cost
tracks call count, not cell count** — the single fact this whole document
under-weighted. A 411-cell formation decomposes to ~103 rects, so at one call
per rect it cost 5.15 s no matter how cheap a cell was. Batching the write made
the *read* the bottleneck (977 captures around a 1-call paint), so the read got
batched too. Both are staged and awaiting their first timing run.

**Keep `savemap.py` regardless.** It stays valuable for authoring a map *before*
a session, for bulk operations where 2.4 minutes matters, and as the fallback if
the companion DLL proves harder than expected. It is proven and costs nothing to
retain.

## What to test next, in order

1. ✅ **Re-measure call latency on the 568-mod stack.** Done 2026-08-12 — see
   the re-measurement section above. Verdict held.
2. ✅ **Build `JawaBench.BridgeTools`** with `set_terrain` and prove one painted
   cell live. Done; 36 cells verified by read-back, renders with no reload.
3. ⏳ **Time a real formation end to end** — generator decides, bridge executes.
   **Half done.** The per-rect path was measured: a 411-cell dithered crater is
   103 calls and **5.15 s**, i.e. 12.59 ms/cell against the 6×6 probe's 0.42 —
   a ~30× gap that was entirely call count. ⚠️ That figure was taken with
   `--defer-refresh`, which under-refreshes (see traps.md); the honest per-rect
   baseline is **13.99 ms/cell**. The one-call batch path is built but has never
   run against a game. `src/RimMandrake/bridgetools/time_formation.py --mode both` closes this.
4. ~~Only if 1–3 disappoint, revisit save-editing as primary.~~ 1 and 2 did not
   disappoint.
5. **New, cheap, worth one test:** the ~16.7 ms floor is one frame at 60 Hz. If
   RimWorld's frame cap were raised, every unbatched hop would get cheaper.
   Low priority precisely because batching already amortises it to 0.51 ms/cell
   — but it would make interactive single-cell tooling feel different.

## Honest open risks

* ~~The 2 ms figure is from a paused 3-mod game and may not survive contact with
  568 mods and a live tick.~~ **Closed 2026-08-12** — re-measured on 568 mods;
  the per-hop cost rose to one frame (~16.7 ms) but batched per-cell cost
  *improved* to 0.51 ms. Still paused, so a live tick remains untested; that is
  now the only part of this risk left standing.
* ~~Companion DLL wiring is documented but unproven **by us**.~~ **Closed
  2026-08-12** — three tools built, loaded and called. The one real hazard the
  guide warns about is enforced mechanically now: `build.py` fails the build if
  any host-provided assembly lands in the bundle.
* ~~`SetTerrain` alone may not refresh what the player sees.~~ **Closed** — it
  renders live with no reload, provided the map mesh is dirtied. But the shape of
  that requirement bit us: the mesh is cached in **17×17 sections**, and
  `RefreshRect` dirties only the cells it was handed. So skipping the refresh on
  all but the last rect leaves most of a formation stale on screen while the
  terrain grid is entirely correct. The batch tool avoids this by collecting
  every changed cell and flushing once. **The reversibility advantage stands.**
* **New, and now the live one:** reversibility is only as good as the capture.
  A revert that silently no-ops looks identical to a clean restore, because a
  `None == None` comparison passes. That already happened once and left a
  permanent crater at (45, 190). `TerrainPainter.capture()` now refuses a partial
  read rather than proceeding, and a full-region verify is affordable — but this
  is the failure mode to watch, not the render.
