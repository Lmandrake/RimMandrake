# OWNER_PICKS_SHRINK_TO_SIZE_RULE

Owner question-card answers 2026-10-24 07:15 PDT: (a) "TunnelSnake B and Vurra B are 1024 px wide but the size rule
gives 512/256: shrink too?" → "Shrink both". (b) Durrok variant B draws ~1.5x larger than the base, his typed answer:
"I'd like both of them at the bigger size and appropriate resolution please". (c) the Surrik precedent (e14b09bd2d).

Size rule: `src/RimMandrake/Utils/art_eval/fauna_drive.py canvas_for` — smallest power of two >= adult drawSize x 128,
min 256, cap 1024.

## Outcome per texture (all facings E/N/S together, `art.py install --file`, 1024 originals kept in the art store)
| creature | adult drawSize | old → new | authority |
|---|---|---|---|
| RM_TunnelSnake (B) | 2.7 | 1024 → 512 | by card (a) |
| RM_Vurra (B) | 2.0 | 1024 → 256 | by card (a) |
| RM_DurrokV_B | 2.0 | 1024 → 256 | his typed answer (b) |
| RM_Durrok (base) | 2.0 | 1024 → 256; N x1.478, S x1.39 enlarged first | his typed answer (b) + agent reading |
| RM_Bloodlurk (C), RM_Scaldhide (B), RM_Ribbonwhip (B) | 0.85 / 1.15 / 1.1 | 1024, NOT changed | refused: owner-KEPT guard → KEPT_PICKS_SHRINK_AWAIT_OWNER_CARD |
| RM_Bileworm base + V_C | 4.1 | 1024 = rule, untouched | — |

Agent reading of (b) (he may correct it): BOTH Durrok looks draw at the variant-B size, each at its canvas-rule
resolution (256). Measured with the solid (alpha >= 32) bbox: E facings already matched (988x551 vs 992x525 of 1024);
the base N/S were smaller (397x581 / 634x614 vs V_B 730x690 / 995x756). Base N/S were scaled so their solid-bbox AREA
equals V_B's, centred on V_B's solid centre. drawSize untouched. Side effect: base N/S now read taller than base E,
the same proportion V_B already had.

Resize: premultiplied-alpha (PIL RGBa) BOX; LANCZOS raised sub-31 alpha fringe 10% → 17.6% on Bloodlurk, BOX kept it
at source level. Edge luminance before/after equal (no dark halo).
Evidence: script + stats /mnt/d/ClaudeWork/rimmandrake/resize_picks_stats.json (+ _durrok.json), install log
/mnt/d/ClaudeWork/rimmandrake/resize_picks_install.log, sheets Transient/resize_picks_20261024/_sheet_{craft,zoom,scale}.png
(copies + scripts: D:\ClaudeWork\rimmandrake\resize_picks_20261024\). Not deployed.
