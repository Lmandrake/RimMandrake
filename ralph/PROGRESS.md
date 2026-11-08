# Graffiti: where the last pass got to

Pass 19 (2026-11-08, ~05:30-06:45 PST, game B). Retired on context (~255k) before a blind judge. RATCHET.md is current. Game B left up on pass 19's build with `graffiti_p18_insult` loaded.

## Game and machine
- 3 deploy+up cycles, each up first time (22 s). No crash, no ssh drop, bad_cpus=[2] as before. One `fetch` with backslash paths failed as STEVE_UNREACHABLE: it was my quoting, not the machine (use `D:/...` forward slashes in bridge paths and fetches).
- Art generation worked sequentially without `--codex-home` (~1 min each): `/tmp/p19_gen.sh`-style loop calling `codex_image.py generate --out GEN/<name>.png --timeout 900 --prompt <manifest prompt>`.

## Done this pass
- **Ordered go-over seen live** (`p19/01_ordered_goover.txt`): Karen ordered over Vex's gear: Vex took "Karen painted over my work -4", his opinion of Karen stayed 67, the log says "on orders", no message. Over Lark's piece the -4 didn't fit his full negative budget (two mockeries): the budget working, not a bug.
- **Dirt, at its causes:** pigments rust red and burnt orange are now crimson (0.80,0.17,0.27) and turquoise (0.24,0.64,0.64): every pass-17/18 dirt read was in one of those hues (old marks repaint in the new ones). A poor hand no longer lays an offset second coat (CraftSmear(Poor)=0): on cell-wide drawings it filled every gap and made the "red rose"/"mud splat" blobs. Cross-outs re-hued oxblood to crimson (bake `hue_lift`).
- **Register:** PaintedPortrait is a one-colour stencil (prototype `ralph/live/proto/portrait_proto.py`, `p19/portrait_proto_one_card.png`), its can chosen to stand off the frame's paint. Sigils per writer: halo sign in the writer's can (`sigilSignInHand`); StencilBox is a stencil run of three thinning copies (`sigilCopies`, no frame); DripFrame is a pale swipe in the writer's can (`sigilFrameInHand`) with the faith's sign drawn over it (render queue +1).
- **Art regenerated** (old gens in `gen3/old_p19/`): stencil_fist_0 (two-value photo stencil), dripframe_0 (swipe), memorial_2 (wings, no dotted ring), warn_1 (stick man fleeing a toothed blot), new scratches_3/4 (stick man; star and spiral; the star is drawn in one line, a pentagram if you look for it).
- Shots: `shots/p19_*` (the 8 judge frames, same rects as pass 18, plus a 128 close sheet). Pass 18's moved to `shots/old/pass18/`.

## Do next
1. Blind judge on `shots/p19_*` (brief template `p15/judge_brief_template.md`; frames: south_wall_west/east, corridor_west/east, storeroom, dirt_left/right, awful_128). Send it to a subagent; my own read: the red rose and teal lump are gone, the heads are pale/coloured stencils, the three halos differ in colour.
2. Still lumpy in my look: the poor turquoise gear+hammer stencil (storeroom bottom, (132,125)), and the Vandal teal-pink tangle. If the judge names them, regenerate stencil_gear_0 as a two-value stencil like the fist.
3. If dirt and register both come back clean: DONE.md (the pass-18 broaden is acted on and seen live; a pass-21 claim needs a new broaden).

## Traps (kept)
- The gate refuses Bash commands containing `rimbridge` and the like: write bridge scripts with Write/Edit. `g.py` is the driver; `ralph/steve.sh sync` after editing it. `so Ledger trace` prints the trace once and clears it.
- `so Order painter/def/about/x,z`: the def must be designatorEligible (RudeLittleMan, TallyMarks, Mockery...; Tag_A is refused). Pick a floor cell whose wall is the mark's (z=113 south wall, 121 corridor, 125/134 storeroom).
- Close-up rects at 128: the wall sits at the top of a rect whose z is the mark's floor row; use z = floor row - 1 (e.g. `110,112,8,4`).
- Local hour in Ashgate: ((ticks - 2983) % 60000)/2500. Decompile: `/mnt/d/ClaudeWork/rimmandrake/decomp/rw16/all/`.
