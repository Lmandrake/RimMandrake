## the ask

Owner ruled 2026-09-16: regenerate all 6 `RM_Graffiti_Vandal` variants
(`src/RimMandrake/Graffiti/Textures/Things/Filth/Art/RM_Graffiti_Vandal/
vandal_0.png` .. `vandal_5.png`, `Graphic_Random` over `RM_BaseGraffiti`,
`ThingDefs_Graffiti.xml`) as punk/urban marks with ZERO real-world lettering,
each ONE readable motif per tile rather than a scatter of tiny doodles that
turn to pixel mush at ~64px play zoom.

## measured: the defect, confirmed by looking

`vandal_0.png` (640x640, RGBA) is not one motif — it is roughly fifteen
separate tiny marks scattered across the tile, several carrying genuinely
legible English lettering: the donor's own tag "TARTE", "The Cave", "Archer
Tepia", "ROMANES EVNT DONVS", a mock "GRAFFITI REMOVAL NOTICE" block, plus
several more illegible-at-scale doodles. Exactly the complaint: real-world
text that should not be here, and a dozen marks that read as noise rather
than a single tag.

## art — FILED 2026-09-19

6 fresh jobs, `graffiti_vandal_regen_v1_{0..5}`
(`infrastructure/artpipe/pending/`), 640x640 transparent canvas (matches
`vandal_0.png`'s current dimensions and the sibling `graffiti_scratches_p1`
job's shape), channel gemini. Each prompt is explicit: **one** bold
spray-paint motif filling most of the frame, "no lettering, no words, no
readable text of any kind, no other marks anywhere else in the frame" —
six distinct motifs for `Graphic_Random` variety (lightning-bolt tag,
slashed-circle scrawl, drip-blob splash, crude skull, starburst scribble,
illegible signature loop), six different spray-paint colors so the set
reads as varied vandalism rather than one repainted shape.

## wiring — OWED once reviewed

Once the daemon finishes these and they've been looked at (this project's
own convention: art candidates go to a review sheet or the owner's eye
before wiring, not straight from generation), copy the kept PNGs over
`vandal_0.png`..`vandal_5.png` in place (same texPath, same `Graphic_Random`
folder — no def edit needed, only the texture bytes change) and
`validate_patch.py` + a deploy. If any variant is rejected, re-file just
that one job rather than regenerating all 6 again.

## needs: harvest

Nothing left to build until the art lands and is reviewed.
