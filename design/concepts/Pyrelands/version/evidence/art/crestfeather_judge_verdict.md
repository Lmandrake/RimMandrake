# Crestfeather art judge verdict: RM_PristineFirehawkCrestfeather

- Verdict: **KEEP**
- Judge: rm-judge/opus, a fresh judge that did not make the picture (made_it: false). Judged 2026-11-27T02:36:31Z.
- Brief: `design/RimMandrake/art_judge_brief.md` @ 9ad7d729e5 (clone HEAD 051fdfaf06). I read the whole brief. There is no canon entry, because this is not a Star Wars subject.
- Maker: artpiped/codex, job `RM_PristineFirehawkCrestfeather`, made 2026-11-13T20:57:40Z. Art list: `infrastructure/artpipe/art_lists/pyrelands_firehawk_crestfeather_2026-11-13.csv`.
- Picture: `candidate_RM_PristineFirehawkCrestfeather.png`, 256x256 RGBA. I verified its sha256 with sha256sum: `38d0ed3bce8dd1019b623c8677c64f04b7039b316cf6ef5650eef4f95162eead`.
- Slot: `src/RimMandrake/Pyrelands/Textures/Things/Item/Special/RM_PristineFirehawkCrestfeather/RM_PristineFirehawkCrestfeather.png`.
- Target bar: `crestfeather_has_its_own_look`. A pristine crestfeather from a hunted fire-hawk shows a fire-hawk's feather, never a borrowed horn.

## What I looked at

All the inputs are in `D:\ClaudeWork\scratch\pyre020\cf_judge\`.

- `candidate_RM_PristineFirehawkCrestfeather.png`: I viewed it at full resolution. I also measured its alpha, bounding box, edge-ring luminance and connected components.
- `cf_scale_full.png`: the true-scale strip on the default ground. It shows the vanilla human, max zoom, 32 px/cell, 32 px/cell x4 nearest, 18 px/cell and 18 px/cell x4.
- `cf_scale_ash_full.png`: the same strip on the Pyrelands heavy-ash ground (66,61,56).
- `thrumbo_scale_full.png`: the vanilla ThrumboHorn (1 cell) at the same true scale, for size and finish.
- `donor_ThrumboHorn_vanilla.png`: the donor horn that the def draws today, tinted.
- `sibling_FireHawk_east.png`: the fire-hawk, which is the source animal and the sibling for palette.
- `red_today.txt`: the offline wiring test, which today reports 5 of 5 FAIL. That test is about the def wiring, not this picture (see "Owed" below).
- I made a 2.4x nearest crop of the feather tip on both grounds to check for fringe and halo. It was a throwaway file and I deleted it.

I did not view `cf_scale.png` and `cf_scale_ash.png` on their own, because the `_full` strips contain them.

## Inputs complete (checklist 1)

Every input was given:

- the candidate at full resolution;
- its only facing (the item is not rotatable and uses Graphic_Single);
- the true-scale panel beside a human;
- the 32 px/cell copy;
- the def facts (drawSize is the default 1x1, footprint 1x1);
- the sibling (the fire-hawk);
- the donor (the ThrumboHorn);
- the owner's notes, verbatim.

So this verdict is not UNSURE.

## Constraints applied

| id | finding |
|---|---|
| E3 | Not owner-kept: this is a new candidate in an empty slot, so the brief's rule that a kept picture always gets KEEP does not apply. |
| A1-A5 | Not applicable. This is not a Star Wars subject and it has no canon entry. |
| B1 | Pass. The feather is painted with soft value modelling and visible barb texture, in the same render register as the fire-hawk sibling. It is matte, with no hard specular. It is not flat cel. |
| B1a | Pass. It has no outline or keyline. The mean luminance of the 2 px edge ring is 119.8, against 129.9 in the interior, and 0% of the edge pixels are darker than 60. Colour and value carry the silhouette on both grounds. |
| B2 | Pass. At 32 px/cell it reads as two bold shapes: a diagonal plume and its quill. The ember-orange tip is strongly apart from both grounds. The ash-grey half is lighter than the heavy-ash ground, and cooler and lighter than the default tan ground. It is not grey mud by either fault. It reads as a feather, not as a horn, a leaf or a flame. Four things carry that reading: the shaft runs out past the vane as a bare quill, the vane separates into barbs at the base, the curve is a feather's S-curve rather than a horn's solid tapered cone, and the grey half rules out a flame. This holds at max zoom (211-256 px/cell) and at 32 px/cell. |
| B3 | Pass. The orange-red on the vane tip matches the ember-orange of the fire-hawk's plumage. The quill half is a lighter ash grey than the hawk's charcoal body. The def description states this exactly: "ash-grey at the quill to a living ember-orange at the tip". It reads as the same artist and as a fitting item size class. |
| B4, B6 | Not applicable. This is not a built thing or a tier. |
| B5 | Noted. The palette is judged as an option, not as a ban. |
| C1, C2, C4 | Not applicable beyond the single facing. The item is not rotatable and has one facing. |
| C3, C5, C5a, C6 | Not applicable. This is not a building, a flyer or a pipe. |
| D1 | Judged at true scale beside the vanilla human at max zoom (211/256 px/cell), at 32 px/cell and at 18 px/cell, on both grounds. |
| D2 | Pass. The canvas is 256 px for a 1x1 cell, which is more than 128 px per cell, so it errs generous and is not down-resolved. |
| D3 | Pass. The alpha>8 bounding box is x 4-251, y 22-228. The feather lies corner to corner in its 1x1 cell. It neither overflows the cell nor floats small in it. Beside the human it reads as a hand-held object about as large as the vanilla ThrumboHorn it replaces, which also fills its 1 cell. |
| D4 | Pass. The alpha is real. All four corners are (0,0,0,0) and the image has one connected component. It has no backdrop, ground, cast shadow or halo. The interior alpha is 254, which is visually opaque. The anti-aliased fringe composites cleanly on light and dark ground: I checked it in the tip crop. |
| E1, E2 | Pass. This is newly drawn art. It is not the donor ThrumboHorn, not a tint of the horn, not a borrowed vanilla texture, and not a script-drawn stand-in. |
| E4 | Pass. The owner's notes are "Pristine ... Crestfeather is a valuable object of beauty to further reward the hunt." and "No, I meant Firehawk". The picture is a fire-hawk feather, and it is clearly an object of beauty. It also keeps the def's promise that "in any light it seems to glow from inside": the orange half has a warm inner gradient that runs to a hot red-orange at the tip. |
| F1 | Not applicable. This is not a pawn cosmetic. |

Bar `crestfeather_has_its_own_look`: **met by this picture.** It shows a fire-hawk's feather, never a borrowed horn.

## Verdict and why

**KEEP.** The picture plainly reads as a feather at max zoom and at 32 px/cell. It shades ash-grey to ember-orange as the def says, and it matches the fire-hawk's palette. Its alpha is real, with no outline, ground or shadow. It fills its 1x1 cell at the size of the vanilla horn that it replaces. No constraint is violated, so there are no refusal records.

## Polish (blocks nothing)

- At 18 px/cell (zoomed out), the feather reduces to a grey-to-orange streak. This is acceptable for a 1-cell item, and no constraint judges at that zoom.
- On the default tan ground, the ash-grey half is closer in value to the ground than the orange half is. It still reads, and on the Pyrelands ash ground it reads well.

## Proposals (these never decide a verdict)

- None.

## Owed (outside this picture verdict)

`red_today.txt` (T_CRESTFEATHER_OWN_ART_OFFLINE) fails today for def-wiring reasons:

- the def's texPath is still `Things/Item/Special/ThrumboHorn`;
- the def still has the colour tint (230,120,40);
- the PNG is not yet in the slot.

This KEEP does not close the bar. The bar closes only after someone places the picture in the slot, points the def's texPath at it, removes the tint, and re-runs the test.
