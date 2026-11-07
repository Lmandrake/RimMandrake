# Graffiti: done claim, pass 2

Shots are in `D:\ClaudeWork\rimmandrake\ralph_graffiti\shots\`, all from the final build, on `graffiti_solo` with all DLC. 64 px per cell unless marked 128 (close-up). `day3_*` and `night_n` come from one colony with no staging of marks: recreation and idle hands only. `spree_day4_*` and `day4_close` are that same colony after a forced spree (70 marks).

## The owner's two demands

### 1. True perspective on every facing: yes for the walls tested, moderately to highly sure
Close-up `sweep_side_close.png`, `sweep_close.png`. Play zoom `sweep_a.png`, `sweep_b.png`, `sweep_c.png`, `day3_natural_n.png`.

A wall tile is a fake box: dark cap, front face at the south edge, side faces east and west, mitred. Measured off the atlases: the crease is 0.40 cell on Core walls, the side face about 0.22. Marks are now clipped polygons in the wall's plane, not quads, and they stop at the crease, the mitres, corners and doors.
- **Front face:** the whole mark, foreshortened to half height.
- **East and west faces:** a sliver, running along the wall. It reads as a streak of colour, not as a picture. That is the honest answer, and these faces take nothing over 2 cells wide.
- **North face:** does not exist in this camera. Painters no longer choose it. An old save's mark there keeps only a thin lip of paint on the cap's far edge.
- A hand's tilt is a baseline shear, so runs still fall straight down.

Weak spots:
- **My own choice:** the factor of 0.5 assumes a wall 0.8 cell high. The art fixes the band's height on screen, not the wall's real height. I chose it by comparing 0.6, 0.8 and 1.0.
- **Seen in game:** granite, wood, steel, marble, plasteel and slate. **Not seen in game:** natural rock, whose torn crease varies (measured 0.44 to 0.52, clamped to 0.45), and modded walls, whose atlas is read at runtime and is only tested offline against the extracted atlases.
- Far fewer surfaces carry a whole mark than before. Interior walls that aren't a room's north wall show slivers or nothing, so most paint gathers on north walls and outer south walls. That is what the camera allows. The owner may want to weigh in.

### 2. Painted, not stuck on: yes at play zoom, moderately sure; closer up, mostly
Close-up `day3_close.png`, `day4_close.png`. Play zoom `day3_natural_n.png`, `spree_day4_n.png`.

All 80 textures are newly generated as real tool marks (bristle, rag, can, roller, charcoal, stencil, wheat paste), then baked with rim lines broken, dry streaks, weather patches and pigments pulled toward the game's palette. The wall's own atlas is redrawn over the paint at 24% (18% for posters), so brick and plank courses come through the paint and the wall's colour tints it. Bare wall is left visibly unchanged by this.

Weak spots:
- Throw-ups keep a part of their dark line at 128 px, and fills are less streaky than I'd like. I pulled the weathering back because a stronger version went too faint in dim rooms: I traded some paintiness for legibility.
- Posters (`Paste_Gig`) are still the most graphic thing on a wall, though dulled.
- Paint can't be seen to soak into walls at night any differently: it just dims with the wall (`night_n.png`), which is correct but subdued.

## The ten north-star lines

| Line | Verdict | Sureness | Shot |
|---|---|---|---|
| `mark_actually_appears` | True | High | `day3_natural_n.png` (29 marks by day 3 from play; suite `spree_paints_marks` PASS) |
| `mark_reads_as_deliberate` | True | High | `day3_natural_n.png` |
| `mark_reads_at_play_zoom` | True for front faces; thin tags and low-contrast glyphs are weaker; slivers read only as colour | Medium | `gallery_a.png`, `gallery_b.png`, `gallery_c.png` |
| `mark_sits_on_the_wall` | True | High | `sweep_side_close.png` |
| `marks_visibly_various` | True | High | `spree_day4_n.png` |
| `mark_register_is_punk_urban` | True for tags, throw-ups, pieces, posters. Meme glyphs are now crude daubs, but at 25 px tall a few read as blots, not statements | Medium | `gallery_a.png`, `gallery_b.png` |
| `mark_carries_no_earth_signage` | True, by my eye | Medium | `gallery_a.png`, `gallery_b.png`, `gallery_c.png` |
| `mark_ugliness_is_visible` | Mostly true. −15 is the widest, filthiest smear and −3 a tidy tally, but −8 to −5 are not ranked by looks, and −15 is dark enough to sink on a dark wall. The inspect pane now states each mark's Beauty | Medium | `ladder.png` (labels added by me from the defs) |
| `never_real_world_english` | True, by my eye at play zoom and 128 px, not a letter-by-letter check of all 80 at full size | Medium-high | `gallery_b.png`, `day4_close.png` |
| `never_reads_as_dirt` | True for painted marks; a worn rag smear is the closest thing to it | Medium-high | `spree_day4_n.png` |

## The reviewer's other points
- **Tidy emblems:** all redrawn, none centred. I'd want a fresh eye on whether they now read as anything at 25 px tall.
- **Pink mouth:** gone with the rest of the old art.
- **Ugly marks:** see above.
- **Repeats:** each mark picks a drawing and pigment different from neighbours within 9 cells, marks may be mirrored, and the pool rarely repeats a def within 8 cells. This reduces repeats but doesn't end them: `day4_close.png` has two red throw-ups side by side.
- **Staged look:** the colony has generators, fuel, bills, stores, lamps and a crop, and colonists now draw where they really are. Power and fuel are judged by eye (no warning icons in the final shots). The count taken at spawn read 3 powered, 17 dark, and I did not re-read it after time passed.

## What was and wasn't tested
- **Fuzz:** 116472 cases OK on the final kernel, including every link set, face and width against the clipping rules. Five Graffiti selftests pass.
- **North-star suite on the final C#:** PASS 11, FAIL 0, UNMEASURED 10, so its overall verdict is **not green**. All ten bars are UNMEASURED because `judge_cli.py` was not run: their state side passes and they wait on a visual judge. Two compat components are also UNMEASURED, because those mods aren't on the small list. `Transient/northstar/Graffiti_20261107T091309Z.json`.
- **Save and load:** saved and loaded once. Marks survived and play carried on, with no exceptions in the log. My planned pixel comparison crashed because the game was still loading, so this rests on the count, the tick and `night_n.png`.
- **Not tested:** the full mod list, natural rock and modded walls in game, raids tagging under the new rules, balance past day 4, and loading a save from before this pass (old marks there should show as lips or draw on their face).
