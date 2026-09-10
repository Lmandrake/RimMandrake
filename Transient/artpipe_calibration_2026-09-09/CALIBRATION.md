# ART_PIPELINE_DAEMON_1 — Phase 0 calibration, 2026-09-09

Run from `/mnt/d/Luke/dev/Rimworld`, foreground `codex_image.py`/`codex_queue_runner.py`
calls only. All numbers below are MEASURED unless marked UNMEASURED/PROJECTED.

## 0. Baseline meters (MEASURED)

Newest rollout before any generation:
`/mnt/c/Users/Mandrake/.codex/sessions/2026/09/09/rollout-2026-09-09T12-22-18-*.jsonl`

    primary (5h)    = 22%
    secondary (week) = 13%   read at ~12:22 — matches the spec's own cited baseline

HARD STOP was weekly ≥30%. Final weekly reading this session: **20%** (see §3) —
stop never triggered.

## 1. Native-transparency verdict — MEASURED YES

One `generate` call, no `--chroma-key`, prompt asked for a real alpha channel
(`skills/generating-images/scripts/codex_image.py generate`). Landed at
`transparency_test/crate_native_alpha.png`, 1536x1024, PNG colour type 6 (RGBA).

    alpha mix: clear 70.78% | fringe 0.61% | mid 0.21% | solid rest
    corners: [0,0,0,0] (fully transparent, all four)

`preview_alpha.py` composite (`transparency_test/crate_check.png`), looked at:
clean cutout, no green rim, no halo, fringe invisible at display size as expected.
**Verdict: the built-in `image_gen` tool emits real native alpha on this
ChatGPT-auth install. The chroma-key stage is dead weight for the daemon — do
not build it.** (Independently reproduces the design doc's 2026-09-06 addendum
finding, on a fresh session tonight.)

## 2. References used

`src/RimMandrake/WreckedMachines/Textures/WreckedMachines/Factories/AutomatedSmelter/`
— our own mod (no Workshop copy on this machine), two tiers treated as the "2
machines": **Wrecked** (512x640, subject 375x537) and **Repaired** (512x640,
subject 378x537), all 4 facings each.

## 3. Throughput sweep — MEASURED, N ∈ {1,2,4,6}, 8 jobs each (2 tiers × 4 facings)

🔴 **First finding, before the sweep itself: `edit` mode (image-conditioned,
attaching the real reference PNG) failed 3-for-3 this session** —
`codex_image.py edit --image <ref>` at timeouts 240s/360s/480s, all with the
agent's own `wait` tool call still pending when killed, **zero images ever
reached `generated_images/`** on any attempt (confirmed by directory listing,
not inferred from the timeout — the 🔴 harvest-before-declaring-failure rule
was followed and there was genuinely nothing to harvest). No `TooManyRequests`,
no explicit refusal — this is not throttling by the design doc's own diagnostic
(§B), it is `edit` hanging on a PNG that itself already carries real alpha, a
combination the existing skill docs had not tested. Cost: ~23 minutes wall,
weekly meter 13%→14% for **zero output**. **Pivoted the sweep to `generate`
mode**, anchoring each machine's look in the prompt text (word-anchor fallback,
same technique `generating-rimworld-sprites/SKILL.md` already documents for
hung edits) rather than attaching the reference image.

| N | jobs | wall-clock | img/h | failures | weekly meter Δ | 5h meter after |
|---|---|---|---|---|---|---|
| 1 | 8 | 1204.9s | **23.9** | 0/8 | 14%→16% | 15% |
| 2 | 8 | 604.0s | **47.7** | 0/8 | 16%→17% | 25% |
| 4 | 8 | 303.3s | **95.0** | 0/8 | 17%→19% | 35% |
| 6 | 8 | 302.9s | 95.1* | 0/8 | 19%→20% | 44% |

\* N=6's wall-clock is identical to N=4's because 8 jobs only fill 2 rounds at
either concurrency (⌈8/6⌉=2, ⌈8/4⌉=2) — **this run does not distinguish N=6 from
N=4**; a real N=6 measurement needs ≥13 jobs. N=1→N=2→N=4 scaling is clean and
linear (23.9 × 2 ≈ 47.7 ≈ measured; × 4 ≈ 95.6 ≈ measured 95.0) — **no
concurrency ceiling found up to N=6**, no `TooManyRequests`, grumpiness detector
never tripped (`grumpy: false` throughout). Per-image cost over all 32
successful `generate` jobs: weekly 14%→20%, **≈0.19%/image MEASURED**.

## 4. Validator pass rates — MEASURED, 0% pass at every N

Each output conformed (`conform_sprite.py`) then graded (`validate_sprite.py`)
against its matching facing/tier reference.

| N | PASS | WARN | REJECT |
|---|---|---|---|
| 1/2/4/6 | 0/8 | 0/8 | **8/8** |

**32/32 REJECT, same two reasons every time**: subject height/aspect off from
the reference (e.g. "height 394px against 537px (-27%)", "aspect 0.931 against
0.683 — squashed, not redrawn") and, on several, origin offset. **Root cause is
methodological, not a throughput defect**: `generate`-mode word-anchoring
describes the machine but does not condition on the reference's exact
silhouette, so the model draws its own proportions. The validator is doing
exactly its job — it is `edit` (image-conditioned) that would fix this, and
`edit` is the mode that failed 3/3 above. This is the calibration's central
tension for daemon design, not a rejection of the throughput result.

**Quality/style, looked at, is good** — `contact_sheet_wrecked_N4.png` and
`contact_sheet_repaired_N4.png` (both under this directory): four facings per
machine hold a consistent palette, damage language and camera angle, real
clean alpha, no rim/halo. Wrecked reads as torn rusted metal over a dark
red-brown interior; Repaired reads as clean grey-green with amber indicator
lights — exactly the two prompts' intent. Style consistency is not the
blocker; geometric conformance to an *existing* ThingDef's exact footprint is.

## 5. Projection

At the MEASURED 0.19%/image (generate mode, low reasoning effort, ~150s/image
uncontended): **100% of one weekly window ≈ 526 images/week, UNMEASURED beyond
this extrapolation** — 32 samples over ~40 minutes, not a steady week, and the
design doc's own warning applies: usage is *token*-metered, so reasoning
effort and prompt length move the number more than raw image count. The
weekly window is shared with **all** Codex use on the account, not just this
pipeline (design doc §B) — a real daemon budget should reserve well under
100% of the window for art. At N=4 (95 img/h, no ceiling found), a backlog of
several hundred sprites is a same-day job on throughput grounds; the weekly
token budget, not wall-clock concurrency, is the actual constraint the daemon
must watch.

## 6. What blocked / what to fix before the daemon is built

1. **RESOLVED — `CODEX_EDIT_TIMEOUT_1`, 2026-09-09**
   (`infrastructure/state/items/CODEX_EDIT_TIMEOUT_1.md`). Root cause: an
   isolated per-worker `--codex-home` makes `codex exec` spawn a separate
   elevated `--run-as-windows-sandbox` helper process, and a timed-out
   call's own kill never reached it — it leaked as a permanent orphan (4
   found still alive 3+ hours later). The 3 documented failures were 3
   sequential attempts against the SAME already-fouled `w0` worker home,
   not `edit` mode being broken: a fresh, uncontended isolated-home `edit`
   call completed and landed its image (~200s). Fixed in `codex_image.py`
   (`kill_orphaned_sandbox_helpers`, runs on every isolated-home timeout) so
   a worker's home can no longer be handed to its own next job already
   fouled. Residual: the elevated-sandbox path is measurably slower than
   the shared home (~150-250s vs ~71s for an identical job) for BOTH `edit`
   and `generate` — budget isolated-worker timeouts at ≥250-300s, not this
   sweep's 240s floor.
2. Grumpiness detector's `GRUMPY_SECONDARY_PCT=70` / hard-stop-at-90/97 in
   `codex_grumpiness.py` were never exercised (we stayed at 20%) — still
   UNVERIFIED under real load.
3. `codex_queue_runner.py` and `codex_grumpiness.py` already exist in
   `skills/generating-images/scripts/` (built by an earlier pass under
   CODEX_PARALLEL_WORKERS_1) and worked correctly throughout this sweep,
   including per-worker `--codex-home` isolation (`.worker_homes/w0..w5`) —
   no changes made to either file.

## Files

    transparency_test/crate_native_alpha.png, crate_check.png
    N{1,2,4,6}/out/{wrecked,repaired}_{north,south,east,west}.png   — raw generations
    N{1,2,4,6}/conformed/...                                        — conformed to reference canvas
    contact_sheet_wrecked_N4.png, contact_sheet_repaired_N4.png
    queue_N{1,2,4,6}/{done,failed}/*.json                           — per-job manifests + timing
