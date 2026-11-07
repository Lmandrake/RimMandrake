# First look: the grey ground, answered and fixed

Shots are in `D:\ClaudeWork\rimmandrake\ralph_pyrelands\shots\`. Older ones are in `old\`.

- `first_look_9_grey_layers_old_build.png`: your question, settled on the old build by stripping one burned patch layer by layer at play zoom. The blur was not the grass and not the deep ash. It was the ash filth. Vanilla's `Filth_Ash` (x3) and our loose ash (x4) both drew vanilla's soft ash blob, blown up to 3 cells, one blob per point of thickness, so every burned cell sat under a grey fog. Bare deep ash underneath is crisp and warm brown. Its colour is untinted now, so the "double darkening" is gone too. `Filth_LooseGround` no longer appears at all.
- `first_look_10_grey_ground_before_after.png`: before is the old build; after is this build on a fresh scar on map `p`. Vanilla ash is kept off natural ground. Our loose ash is new crisp art (7 drift shapes at 256 px for 1.5 cells, a mid-light grey), and a fire leaves one drift per cell instead of filling it to the cap.
- `first_look_11_burn_ring_new_ash.png`: the opening fire on map `p` 3.6 hours in, wide. The ring of flame, the scar inside it with pale ash on dark ground, and scorch-fruit pods.
- `p_over_t0.png`: map `p` at night, before the fire.

**The Conductor's four questions (14:31):**
1. LOOK.md is rewritten for `first_look_9` to `11`. The fixes are deployed and seen.
2. The pale hard-edged squares in the old `first_look_1`: **still not identified.** The only ancient concrete on map `p` (a 10x1 strip at 199,92, `p_ancient_concrete.png`) sits inside a scorched ruin and reads dark, not pale. The next pass reads that old map's terrain under the squares.
3. Grass in the bedroom: nothing sows under a roof. Explosive Growth refuses roofed cells (`RM_MapComponent_ExplosiveGrowth.cs:152,199`). That grass stood there before the walls went up and was never cut, as vanilla allows. On this burning ground it is a fire hazard, though (map `m`'s room burned on day 2.9). Not yet fixed: native grass could die back under a new roof within a day.
4. `first_look_5`'s stepped brown block: not proven either way. The composite was saved at 12:25, after the edge-fade commit (11:50), but its panels may be older captures. On this build the mud ring round the new pond blends softly (`p_pond_edge.png`).

**New problem:** the pond's **water** draws as flat, stepped blue-grey blocks with hard cell edges (`p_pond_edge.png`). The noise ponds on map `m` looked the same. This is the next thing to fix.

**What I'm least sure about:** up close, the drifts can read a little like camouflage blotches; a smaller drawSize (1.2) may be better. Ash fall now banks into a drift field, but I haven't seen it on screen yet. Neither has the new ponds' look.
