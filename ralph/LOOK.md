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
- `first_look_4_open_spiked_pit.png`: the open pit with its spikes, before the cover.

What I'm least sure about:
- The open pit (shot 4) reads as a dark framed box more than a 2 m hole: one north face band, a black outline. I haven't
  judged the pit look at size yet (`pit_reads_as_hole`, `pit_walls_have_visible_depth`, `pit_reads_at_size`).
- In shot 2, whether you can tell he is 2 m down with the walls over his head, or just "standing behind a ledge".
- The seam (shot 3) is my call, not his: a hairline, square, and only from close zoom (it fades in past ~66 px a cell, and
  is always on at a player's own two closest zoom steps, so a 1080p screen still finds it).

Changes to approved things: none yet. The drawbridge got one behaviour fix from the owed-fix list (pawns already on the
floor under a leaf that comes down stay under it); its look is untouched.
