# FlowWorks pits: what to look at (Artisan pass 1, 2026-11-07)

Shots: `D:\ClaudeWork\rimmandrake\ralph_flowworks\shots\`. Ordinary quick-test map (temperate forest) on game A, the
flowworks list, ~64 px a cell. His covered-pit-trap story: a walled compound with one doorway, a 3-wide passage to it, a
3 x 2 pit dug 2 m across the passage, spikes in it, a woven-scrap cover over it, then a real tribal raid.

- `first_look_1a_passage_before.png` / `first_look_1b_passage_covered.png`: the passage before digging and with the covered,
  spiked pit in it. They should look the same. Before today's fix the lid showed as a framed box with the spikes drawn on top
  of it (the wall faces, outline and stakes ignored the lid).
- `first_look_2_raider_in_pit.png`: a raider who fell through the cover, now on the spikes 2 m down, with two raiders
  waiting on the lip in front of him. Before today's fix his legs hung out over the lip onto the ground whenever someone
  stood on the lip (the lip band was skipped so as not to paint over them).
- `first_look_3_seam_closeup.png`: the same kind of covered pit, zoomed right in: a faint cut line and a slight
  discolouration, so the player who laid it can find it. At play zoom it draws nothing.
- `first_look_3b_seam_at_game_max_zoom.png`: the same, at the game's own closest zoom on a 916 px window (~42 px a cell).
  My call, not his: it may read a little like a selection square; I can make it fainter.
- `first_look_4_open_spiked_pit.png`: the open pit with its spikes, before the cover.

What I'm least sure about:
- The open pit (shot 4) reads as a dark framed box more than a 2 m hole: one north face band, a black outline. I haven't
  judged the pit look at size yet (`pit_reads_as_hole`, `pit_walls_have_visible_depth`, `pit_reads_at_size`).
- In shot 2, whether you can tell he is 2 m down with the walls over his head, or just "standing behind a ledge".
- The seam (shot 3) is my call, not his: a hairline, square, and only from close zoom (it fades in past ~66 px a cell, and
  is always on at a player's own two closest zoom steps, so a 1080p screen still finds it).

Changes to approved things: none yet. The drawbridge got one behaviour fix from the owed-fix list (pawns already on the
floor under a leaf that comes down stay under it); its look is untouched.

## Contrast sheet: how deep a pawn reads (not decided, nothing shipped from it)

`contrast_depth_sink_T0_T1_T2.png`: one ordinary row of 2x2 holes, left to right undug, 0.5, 1, 1.5, 2, 4, 8 m, a colonist
in each hole's south-west square. Settings only, no new art:
- T0 (shipped): sink 0.3 cell a level, near-lip band 85% opaque. The legs show through below the lip as ghosts.
- T1: the same sink, the band opaque. Only heads poke over the near lip. Reads as "peeking out", not "2 m down".
- T2: half the sink, the band opaque. Chest-deep in the hole: reads as standing in a trench, not trapped.
- Both wrong is an option. My read: none of them shows "the walls are higher than their head by 20%" in a 2-wide hole,
  because the pawn is drawn over the near lip instead of inside the hole. What I'd try next (not built): keep the whole
  sprite inside the hole's square, shade it darker with depth, and draw the far wall face tall enough to stand above the
  head. Also seen here: 4 m and 8 m holes look alike (bar `pit_depth_ladder_legible`).
`first_look_5_big_pit_and_occupied.png`: a 6x5 pit 2 m deep, empty, beside a 3x3 with a colonist in it. The big one reads as
one dark excavated place; its walls are a thin rim band, which I think is too slight for 2 m.
