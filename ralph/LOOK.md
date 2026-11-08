# FlowWorks pits: what to look at (Artisan pass 2, 2026-11-07)

NOT READY for him yet. Pass 1's first_look shots were all at rootSize 7.2 (~64 px a cell), closer than a player can zoom
(the game's closest on Steve's 916 px window is root 11; ordinary play is about 18-24). They are in `shots\old\`.

Current shots: `D:\ClaudeWork\rimmandrake\ralph_flowworks\shots\pass2\`, each line at root 11 and root 20
(`bar_<line>_r11_<n>.png`, `bar_<line>_r20_<n>.png`), an ordinary temperate quick-test map, some taken at night. They
show the pits as they stand; none of them is a look I would show him as finished:
- `bar_ladder_state_legible_r20_1`: a 5x5 pit 2 m deep: at r20 a dark outlined square with a thin pale band on its north
  edge. Reads as a hatch or a dark mat as much as a hole. No ladder rails show; the south-wall ladder draws nothing.
- `bar_geared_pawn_climbs_out_r20_1`: colonists standing IN 4 m pits are drawn on the pits' south lip, so they look as if
  they stand in front of the hole.
- `bar_suspension_bridge_reads_hung_r20_*`: bridges are flat straight strips over the pit, no sag, no cables.
- `bar_pawn_walks_under_deck_r20_1`: a pawn walking UNDER a deck is drawn on top of it.
- `bar_climbing_gear_reads_as_kit_r20_1`: worn climbing gear draws nothing.
- `story_replay_after_stall_fix_r7.png`: his covered-pit story after this pass's stall fix (close zoom, 2x2 moments): the
  raiders set the pit spikes alight with their own comrade on them. Spikes are now never-trash (vanilla's rule for traps),
  deployed next pass.

What I'm least sure about: the depth look. Pass 1's contrast sheet (`old\contrast_depth_sink_T0_T1_T2.png`) varied only
settings and is "both wrong": the sink and the far wall disagree (a pawn sinks 1.2 cells at 2 m but the far face stops at
0.62 cell for every drop past 2 m), and the near lip is 85% opaque. Next pass: three genuinely different treatments on one
view, each hole occupied (drafted), at root 11 and 20, before any one is built out.

Changes to approved things: none. Drawbridges untouched.
My calls, not his: pit spikes are never trashed or set alight by raiders (vanilla treats its own traps so); a person the
hole traps can be captured from the lip with no bed (his card said the drained hole is the prison; I applied it to any
hole that physically traps, not only holes 3 m or deeper).
