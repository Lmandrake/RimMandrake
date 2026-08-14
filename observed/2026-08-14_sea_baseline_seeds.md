# Vanilla sea baseline — 4 generated worlds, 2026-08-14

**Measured by BRIDGE with `src/RimMandrake/bridgetools/sea_seed_sweep.py` and
`jawa/world_stats`. Stopped early at the owner's expense — see §Cost.**

## What this is

VISION's sea spec asks for **~25% water in exactly THREE oddly-shaped bodies**,
and was one commit from authoring a `WorldGenStep` to produce it. The first world
ever measured (`"green"`) landed 25.0% in exactly 2 bodies, which raised the
question this file answers: **does vanilla already do most of the job, or was that
one lucky roll?**

🔴 **This is the sea WITHOUT `JawaSeaShaper.dll`** — S1 is not deployed. It is the
baseline the step would have to beat, not a result.

## The data

All at `planetCoverage 0.3`, 119,904 tiles, quicktest worlds, `minBodySize` 8.

| seed | waterPct | bodiesTotal | bodiesOverMinSize | largestBodyPct | req1 (22–28%) | req2 (exactly 3) |
|---|---|---|---|---|---|---|
| `green` | 25.0 | 2 | 2 | 16.67 | ✅ | ❌ |
| `cards` | 25.0 | 1 | 1 | 25.0 | ✅ | ❌ |
| `guts` | 25.0 | 2 | 2 | 16.67 | ✅ | ❌ |
| `sickle` | **16.74** | 1 | 1 | 16.74 | ❌ | ❌ |

**req1 passes 3 of 4. req2 passes 0 of 4 — the body count is never 3.**

## What it points at, and what it does not

⭐ **Body count is the variable that never lands, and it is low, not high.** Every
world came back as **one or two** connected masses, never three, and never the
"same water smeared into forty blobs" the design feared — `bodiesTotal` equals
`bodiesOverMinSize` in all four, so there are **no puddles at all**. Vanilla is
producing *too few, too large*, not *too many, too scattered*.

⇒ On this evidence, VISION's second scenario is the live one: **S1's job is
PARTITIONING, not writing elevation.** The fraction is roughly right on its own
three times in four; the thing vanilla will not do is split the water into three.

⚠️ **n = 4. This is a direction, not a distribution.** The sweep was specified as
7 and stopped at 4.

## 🔴 The reading I was one sample away from getting wrong

After three worlds — `green`, `cards`, `guts` — all reporting **exactly 25.0%**, I
had formed the conclusion that *the generator pins the water fraction at
`planetCoverage 0.3` and only body count varies*. It was about to go to VISION as
a finding.

**`sickle` came back at 16.74% and refuted it.** Three identical readings of a
value that turns out to vary is not a constant; it is a small sample of a
distribution with a mode. **The fourth sample was worth more than the first
three**, because it was the only one that could have said no.

📌 Generalises: *a run of identical readings is the easiest thing in the world to
mistake for a law.* Ask what sample could refute it, and get that one before
reporting.

## Cost — a read-only sweep is not a free sweep

OPS measured `/proc/loadavg` at **22.58** while the owner was trying to play, with
RAM fine (3 GB of 35). Generating worlds is CPU- and disk-heavy, and it runs on
the same machine and the same physical disk RimWorld streams from. The sweep was
the largest remaining contributor after OPS killed a workshop-tree subagent; **it
was killed at 4 of 7 and load fell to 7.83.**

⚠️ **"Read-only" only ever meant safe for the DATA.** It says nothing about the
machine, and this one had a human on it.

## To finish it

`python.exe src/RimMandrake/bridgetools/sea_seed_sweep.py 4` — **only when the
owner is not playing.** Requirements 3 and 4 (`raggedness`, `centroidLatNorm`)
become collectable in the same pass once the companion redeploys; the units were
wrong in the deployed build and are fixed in `d7e7c6c1`.
