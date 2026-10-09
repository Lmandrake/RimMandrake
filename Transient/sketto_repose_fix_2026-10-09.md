# Sketto re-pose gate fix — 2026-10-09 (BENCH design helper)

Status: DONE (design + offline experiment only; nothing filed, nothing installed, `flyer_lock.py` unchanged).
Diagnostics: `D:\Luke\dev\RimMandrake\Transient\sketto_repose_fix_2026-10-09\` (overlay_sheet.png: grey = both, red = plate bare, blue = frame only).

## Summary — three blockers, not one

1. **The re-pose gate is mostly measuring outline jitter, not re-posing** (M1, M2). The body is 3–4 px half-width, so the 1-px outline ring is 15–19 % of the plate. The "redraw broke it" hypothesis is only partly right: plate v1 failed too (S 0.85/0.80/0.94, N 0.80/0.83/0.87). The frames are edits of master v3; the plate is a separate drawing, and any separately drawn plate is ~1 px off everywhere.
2. **The lock leaks the frame's body back in** (M5). Its wing rule walks through any body pixel with L1 > 60 that touches a wing, and a 1-px stripe offset makes most of the body qualify. That is why wing frames fail canon on tusks and legs after the lock: the frame's own head comes back as "wing" (double head on south wing2, `head_crops_stray.png`).
3. **The S/N floor of 0.38 cannot be reached with these wings, even by a perfect lock** (M6). Our wings are about 2/3 of the frame area. Plate area ÷ mean frame area = 0.338 S, 0.318 N. Locked share can never exceed that.

South wing2 is a real re-pose at the head (bare to 13 px deep). It is already canon-failed and needs a regen under every option.

## Options

| | What | Measured | Cost | Risk |
|---|---|---|---|---|
| **A. Derive the plate from master v3 offline** | plate = master pixels inside the plate-v2 trunk + plate v2's thin legs pasted as a fixed overlay (`plateA_*.png`) | Gate unchanged at 0.92: N passes all three (0.974/0.939/0.955), S master 0.981 and wing3 0.973 pass, S wing2 0.836 | A small offline script; 1 regen (S wing2, edited from master v3); the owner looks at the plate once | Wing roots at the shoulders are master's wing colour inside the plate (a few px). The body is master's, not the redraw's; only the legs come from the redraw. Doesn't fix blockers 2 or 3 alone |
| **B. Keep plate v2 and measure the gate on a 1-px-eroded plate** | Ignore the outermost ring when counting cover (the lock repaints that ring from the plate anyway) | N 0.948/0.933/0.960 pass; S 0.932/0.821/0.975 (wing2 fails) | ~5-line `flyer_lock.py` change + selftest | It **changes the gate's meaning** (a 1-px re-pose becomes invisible). Not implemented, owner/design call. Keeps the redrawn body, so the plate-v2 outline still mismatches every frame, giving more fringe |
| **C. Tighten the lock's wing rule (needed with A or B)** | Outside the plate, keep a wing pixel only if it joins a wing reaching > 4 px from the body. Inside the plate, only within 12 px of that wing (bounded reconstruction) | Plate px taken from the frame: N wing3 1213 → 354, S wing2 1431 → 497. Locked share N 0.129 → 0.260, S 0.116 → 0.279. Still < 0.38 (blocker 3) | ~15 lines + selftest; re-run east (its filed output would change) | It tightens, so it doesn't loosen the gate. The parameters (4, 12) were tuned on S/N only and need an east re-check |
| ~~Scale search~~ | ±6 % scale in align | Picks 1.06 almost every time. It just fattens the body over the outline (M3) | — | Games the metric, rejected |

**Recommendation: A + C, and the owner rules on the S/N floor.** Why: A is the only route where the unchanged 0.92 gate passes by construction, and C is what actually makes "the body is the plate" true. B weakens a gate to rescue a plate that will never line up.

## What the owner must decide (plain language)

1. **Plate source.** May the flying Sketto's body come from the already-approved flying master picture, with only your thin tucked legs copied in from tonight's redraw? This makes the body line up by construction. The alternative is to keep the redraw and accept a looser alignment test.
2. **Stability bar for front and back views.** Our wings are large, so the body is only about a third of each frame. Even a perfect lock scores 0.32–0.34 against the 0.38 bar copied from the donor. Choose one: lower the S/N bar to about 0.28 (measured after C: 0.26–0.28, close), judge it by "body pixels never under a wing are 100 % identical" (already checked, 1.0), or ask for smaller wings in S/N.
3. **One regen.** South wing-level frame (wing2) is re-posed at the head and needs one more render, made from the master.

NEXT: on his answers, write `derive_plate` into flyer_lock (A), implement C with a selftest, re-run E/S/N locks in scratch.

---
### Running log (filled as measured)

**Inputs.** Plate v1/v2, master v3, wing2 v1, wing3 v1 per facing from `D:\Luke\dev\_artpipe\_artsrc\sketto_fly_*`. Scratch: `/home/mandrake/rm/scratch/BENCH/sketto/repose_2026-10-09/` (diag.py, edge.py, overlay_sheet.png).

**M1 — cover per frame vs plate v2 (lock's own align, ±8 px).** Reproduces the refusals: east master 0.72 (align hit the −8,−8 search edge), wing2 0.974, wing3 0.992; south master 0.819, wing2 0.777, wing3 0.931; north master 0.831, wing2 0.867, wing3 0.921. Plate v1 (pre-redraw) is NOT better: south 0.85/0.80/0.94, north 0.80/0.83/0.87 — so "the redraw broke it" is false as the main cause.

**M2 — the body is too thin for a 0.92 silhouette gate.** Plate median half-width is 3–4 px; the 1-px outline ring alone is 15–19 % of the plate's area (south 556 of 3628, north 547 of 3015). A frame whose outline sits one pixel inside the plate loses that much cover with no re-pose at all. Bare pixels at depth ≤ 2 px from the plate edge: south master 608/657, north master 492/509, north wing2 329/402, south wing3 230/251. Cover measured on the plate eroded by 1 px: south master 0.932, wing2 **0.821**, wing3 0.975; north master 0.948, wing2 0.933, wing3 0.960; east master **0.768**. Only south wing2 (bare 13 px deep, at the head/tusks) and east master are genuine re-poses.

**M3 — scale search games the metric, reject.** A 0.94–1.06 scale search (about the plate centroid) picks the top of the range almost every time (south 1.06 ×3, north 1.06/1.05/1.03): scaling up a 3–4 px-half-width body just fattens it over the plate's outline. North wing2/wing3 would cross 0.92 (0.931/0.950) but south master stays 0.838 and wing2 0.870. It changes the wing size too. Not a fix.

**M4 — a plate derived OFFLINE from master v3 passes by construction for master, and mostly for the wing frames.** `plateA_<facing>.png` = master v3 pixels inside the plate-v2 trunk (opening r=2, dilated 2) + plate v2's thin legs pasted as a deterministic overlay (70 px south, 88 px north). Real `flyer_lock.py lock` gate covers: north master 0.974, wing2 0.939, wing3 0.955 (PASS the unchanged 0.92 gate); south master 0.981, wing3 0.973, wing2 **0.836** (south wing2 is genuinely re-posed at the head — bare 13 px deep — and is already canon-failed; it needs a regen whatever we do). East master v3 does not match plate v2 east (align hits −8,−8) — east frames came from master v2; east is already filed, leave it.

**M5 — a SECOND blocker behind the gate: the lock leaks the frame's body through the "wing" rule.** With plate A, north passes the gate but `check` fails: locked share 0.129 vs floor 0.38 (south 0.116 with the gate bypassed). Cause: `lock_frame` classes body pixels differing from the plate by L1 > 60 as wing when 4-connected to wing outside the plate, and a 1-px stripe/outline misregistration makes most of the body differ by > 60, so the reconstruction walks the whole tail. Plate pixels overwritten by "wing": north wing2 891 / wing3 1213 of 2674; south wing2 1431 / wing3 1040 of 3104 (master frames 3–11). This is also why wing frames fail canon on tusks/legs although the lock "overwrites the body": the frame's own head, tusks and legs come back as wing. Plate-v2 locks would do the same (stray head ghost visible in `head_crops_stray.png`).

**M6 — floor ceiling.** With plate A and the bounded wing rule (C: far 4, depth 12), the real `check` gives a locked share of 0.279 S and 0.260 N (depth 8: 0.295 / 0.273). Plate v2 with the same rule gives 0.297 / 0.277. The ceiling is plate px ÷ mean frame area: S 3104/9175 = **0.338**, N 2674/8400 = **0.318**. That is below the 0.38 floor even with zero leakage, so the S/N floor cannot be met with these wing sizes. Prototype code: `bounded.py`, `deriveA.py` in the scratch dir. Locked frames: `lockB_frames.png`.
