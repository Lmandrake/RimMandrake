# GPT pre-review record — fountain v1 candidates (2026-10-23)

Round 1: `gpt_consult.py --prompt-file gpt/prompt_r1.md -i A/B/C_checker.png` (gpt default model, high effort);
answer verbatim in `gpt/answer_r1.md`. Verdict: A FIX, B FIX, C FIX; ranking A > B > C; "None currently communicates
water falling out onto the ground." No C3/C6 violation seen (no convergence, no tilted water plane).

Fixes applied (one edit round, raw/*_v2.png -> cand/*.png):
- all: a front spillway notch with a broad sheet of water pouring out down the basin's outer face; cooler, calmer
  neutral stone (stuff tint reads better); generator mist haze (alpha < 32) cleared on the master.
- A: curtains broader and translucent (were "glass rods"). B: top jet halved, fainter column cracks, softer arcs.
- C: trickles consolidated into one front cascade; ring opened. Side effect: cairn ~13% taller (still inside 1x1.5).
Checks after the fix: validate_sprite --describe (canvas 256x384, real alpha, corners clear, fringe <= 0.48%),
basin_ratio.py 0.54 / 0.52 / 0.56 (instrument reads the 0.56 guide as 0.55). Ref-vs-v1 validator REJECTs (origin,
span) are the deliberate redesign, recorded in validator_v2.txt.
