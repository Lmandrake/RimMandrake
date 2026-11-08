# Graffiti (RimWorld 1.6 mod), pass 13: broaden before a done claim

The mod paints graffiti on colony walls (tags, throw-ups, stencils, posters, tallies, ideoligion sigils) and makes it matter between people: mockeries of a named colonist, tributes, memorials, raid tags, insults to a faction. Readers get mood and opinion effects shaped by art skill (craft from awful to legendary) and personality (psychopaths numb, sensitive people feel more, clean freaks mind the mess and can break into compulsive cleaning). Pawns answer marks: scrub, cross out, reply in paint, confront the painter (fight chance scales with the confronter's temper, at most one wall fight in 15 days).

## Measured this pass (game B, a six-colonist colony "Ashgate" on day 18-19, played rather than staged except where noted)
- Feud: Karen and Lark painted a mockery over each other's every few hours: 7 mod messages in 7 game hours on one run, 7 in 14 hours on a replay. Fix: a reply in paint is "the last word" (its subject can scrub, cross out or confront, not paint back), a mockery that covers its subject's mockery of the painter counts as one, and one mockery of the same person per painter in 6 days by any route. On the replay after the fix (staged: Lark sent to the mockery), the chain went: mockery, counter-mockery (1 message, the going-over folded in), Karen chose to cross it out, then confronted Lark in words. A three-day unstaged run on the fix is running now.
- A confront that came to blows sent vanilla's message (pointing at the painter only, no wall). Now our own message names both, the wall and the reason.
- Weathering: marks live about 22-44 days (outdoor shorter), fade over the last 40%. Before: a fading mark was a pale uniform ghost. Now the texture erodes in patches (blotches, vertical rain runs, grit at the edges) and chalks slightly (`weather_flaking_and_painted_heads_128.png`, left: a tag at its last step).
- The mockery's subject portrait was the game's crisp pawn sprite inside brushy red horns. Now posterised, muted, its outline broken black brush with grit and a little overspray (same shot, right; both heads are of the same colonist, Lark).
- Message rate on an unstaged day after the fix: 2 messages (a tribute painted, its subject found it).

## Planned verdicts (owner's bars), and my weakest ones
- Weakest: `stories_not_a_tax` (only a 1-day and a 3-day run since the fix), `mark_reads_at_play_zoom` on side faces (marks on vertical, edge-on walls are thin scraps, see the left wall in `lived_in_corridor_day18_playzoom.png`), `marks_visibly_various` in a real colony (of 70 marks: 15 tallies, 11 scratches, 11 "rude little man" scrawls, because most colonists have low art skill and form follows skill).
- Being proven now by a helper: raid tag and retake, visitors charged once per visit, clean-freak fit, classic mode (no ideoligion), rereads at most daily, a newcomer clicking the wall carrying a mockery.

## Images attached
1 `lived_in_south_wall_day19_playzoom.png` (64 px per cell = play zoom), 2 `weather_flaking_and_painted_heads_128.png` (128 px), 3 `lived_in_corridor_day18_playzoom.png`, 4 `social_regard_brick_on_karen.png` (Social tab: "Painted me on the wall x2: -38"), 5 `art_skill_ladder_good_to_legendary_64.png`, 6 `optionD_materials_close128.png`.
