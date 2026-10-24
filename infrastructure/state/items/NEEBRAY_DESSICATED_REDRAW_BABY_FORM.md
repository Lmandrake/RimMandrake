# NEEBRAY_DESSICATED_REDRAW_BABY_FORM

Found by the independent judge pass on GEARPACK_TEXTURES_REDRAW_FOREIGN_COPY (FOUNDRY judge, 2026-10-24, delegated: art-eval).

## What is wrong

`src/RimStarWars/SWBestiary/Textures/swanimals/Neebray/Neebray_Dessicated.png` (installed by 4f05221df3 from job
`dregen_RSW_Neebray_NeebrayDessicated_r2`, sha 2a78bb69a9fd) is a dried carcass of the ADULT space-manta neebray: a wide
flat ray body, many membranous wing flaps and whip tendrils under the jaw. RSW_Neebray in this mod is the BABY ground
form: the installed living sprites (`Neebray_east/south.png`) show a red, frog-headed body with six yellow eyes, translucent
light-blue wings and small tail fins. The corpse does not belong to that body, and the canon entry's Must show says
"NEGATIVE: ... not a flat ray for the baby form" (design/RimStarWars/canon_references/neebray/description.md).
It is a dried corpse, it is on a 256x256 canvas with real alpha, and it is painted in the house style. The fault is the subject.

Cause: the r2 job attached only the adult reference images (`bloggathehutt_neebray_adults_flying.jpg`,
`wookieepedia_canon_2.webp`, `wookieepedia_legends_1.webp`). The baby image was deleted on 2026-10-17, so nothing in the
job showed the form this mod uses.

Not uninstalled. A desiccated corpse of the wrong life stage is still better than the belt pack it replaced.

## To do

Redraw through the dregen queue (fill_queue.py with a row built from
`D:\ClaudeWork\rimmandrake\artpipe\done\dregen_RSW_Neebray_NeebrayDessicated_r2.json`). Attach the installed living
`Neebray_east.png` as the reference (or set it as derive_from), not the adult canon images. Prompt: the same baby body
dried and shrunken (red skin gone leathery and dark, wing membranes torn and shrivelled, eyes sunken), at the same scale
as the living sprite. Judge it next to Neebray_east/south, then install with `art install --reason artpipe-collect`.

Evidence: `D:\ClaudeWork\rimmandrake\judge_round3\taskA\neebray_convor.png` (corpse beside the living facings); the r2 job json above.
