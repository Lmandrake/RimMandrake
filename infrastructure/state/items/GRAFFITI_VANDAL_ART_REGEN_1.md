## the ask

Owner ruled 2026-09-16: regenerate all 6 `RM_Graffiti_Vandal` variants
(`src/RimMandrake/Graffiti/Textures/Things/Filth/Art/RM_Graffiti_Vandal/
vandal_0.png` .. `vandal_5.png`, `Graphic_Random` over `RM_BaseGraffiti`,
`ThingDefs_Graffiti.xml`) as punk/urban marks with ZERO real-world lettering,
each ONE readable motif per tile rather than a scatter of tiny doodles that
turn to pixel mush at ~64px play zoom.

## measured: the defect, confirmed by looking

The pre-regen `vandal_0.png` (640x640, RGBA) was not one motif — roughly
fifteen separate tiny marks scattered across the tile, several carrying
genuinely legible English lettering: the donor's own tag "TARTE", "The Cave",
"Archer Tepia", "ROMANES EVNT DONVS", a mock "GRAFFITI REMOVAL NOTICE" block,
plus several more illegible-at-scale doodles.

## art — FILED 2026-09-19, FINISHED, GRADED 2026-09-24

6 jobs `graffiti_vandal_regen_v1_{0..5}` (`infrastructure/artpipe/done/`,
PNGs in `infrastructure/artpipe/_artsrc/graffiti_vandal_regen_v1_N/`),
640x640 transparent, reference-less generate jobs.

Fable-tier grade (FOUNDRY, 2026-09-24), each looked at full size and at
64px/128px over checker and over a sand-coloured ground:

| slot | motif | colour | lettering | one motif | reads at 64px |
|---|---|---|---|---|---|
| 0 | jagged lightning bolt, drips | acid green | none | yes | yes |
| 1 | slashed circle | magenta | none | yes | yes |
| 2 | drip-blob splash | orange | none | yes | yes |
| 3 | crude skull | white / black outline | none | yes | yes |
| 4 | starburst | blue | none | yes | yes |
| 5 | overlapping signature loops | black | none (abstract knots, not letterforms) | yes | yes |

**6 of 6 PASS.** Offline validator (`validate_sprite.py --describe`,
reference-independent family only — a `Graphic_Random` set is the wrong class
for reference-vs-candidate): canvas 640x640 all six, real alpha, corners
`[0,0,0,0]`. Fringe (alpha 1–31) measures 0.4–6.3%, above the 0.05% constant;
that constant was calibrated on chroma-keyed machine cutouts, and here the
faint pixels are the spray-mist speckle the prompt asked for — judged
deliberate art, not a keying defect.

## wiring — DONE 2026-09-24, `b9432641b`

All six copied over `vandal_0.png`..`vandal_5.png` in place (same texPath,
no def edit). `validate_patch.py` skipped: it checks PatchOperation XML and
no XML changed. `deploy_custom_mods.py --mod Graffiti --apply` → VERIFIED in
sync, 6 files. Needs a game restart to show, like any texture change.
