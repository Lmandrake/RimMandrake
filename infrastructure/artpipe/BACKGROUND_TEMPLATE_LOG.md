# Background-template proof-out log — ART_BACKGROUND_TEMPLATE_1

Works/doesn't log for the black-background creature-art template
(`BACKGROUND_TEMPLATE.md`). All jobs run for real against the live
`artpiped.py` daemon, `channel: codex`, canvas 256x256, `background:
"#000000"`. Border-ring scan = every pixel in the outer 20px ring (20,480
px total on a 256x256 canvas), checking max RGB channel and count of pixels
with any channel > 2.

## bgtest_a_v1 — explicit-prohibition wording

Subject: small stocky rodent-like scavenger.

Prompt tail: plain, no backdrop sentence.
Style notes: *"The entire background, edge to edge, is one uniform flat pure
black (#000000) plane. No gradient, no floor plane, no vignette, no light
falloff toward the edges, no shadow under the subject. Every part of the
frame outside the creature's silhouette is the same solid black."*

- Visual: clean, no visible gradient.
- Border-ring scan: max channel **24**/255, **15** px of 20,480 exceeded the
  tolerance.
- Verdict: **WORKS, but not the cleanest** — likely antialiasing bleed near
  the fur silhouette, not a true gradient. Kept as the runner-up.

## bgtest_b_v1 — seamless-paper wording

Subject: small stocky rodent-like scavenger (same as a_v1, for a fair
same-subject comparison).

Prompt tail: *"Backdrop: studio photograph on solid black seamless paper,
evenly lit from the front so the black stays pure black to every edge of the
frame."*
Style notes: none.

- Visual: clean.
- Border-ring scan: max channel **0**/255, **0** px exceeded tolerance —
  perfectly flat.
- Verdict: **WORKS, best result of the three.**

## bgtest_b_v2 — seamless-paper wording, confirmation on a different subject

Subject: small lean avian scavenger (bird, not the rodent used above) — run
specifically to rule out a one-off lucky roll on a single subject.

Prompt tail: identical seamless-paper sentence as b_v1.
Style notes: none.

- Visual: clean.
- Border-ring scan: max channel **1**/255, **0** px exceeded tolerance.
- Verdict: **WORKS.** 2/2 clean results across two different subjects for
  this wording — the seamless-paper phrasing is the standard template
  (`BACKGROUND_TEMPLATE.md`).

## Renders

Kept under `_artsrc/<job id>/<job id>.png` (the daemon's own staging area,
untouched — not deleted as "test cleanup"): `bgtest_a_v1`, `bgtest_b_v1`,
`bgtest_b_v2`.
