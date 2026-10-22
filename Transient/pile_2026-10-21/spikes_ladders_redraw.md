# Spikes and rail ladders — redraw (BENCH art helper, 2026-10-21)

Items: `PIT_SPIKES_REDRAW_SPOKES_NOT_LOGS`, `RAIL_LADDER_REDRAW_CLIMB_NOT_CRAWL`

## Status
- [ ] claim items
- [ ] read current art + defs
- [ ] check existing candidates (artpipe_state find, .decisions.json)
- [ ] generate spikes candidates
- [ ] generate ladder candidates (north/east/west)
- [ ] build sheet spikes_ladders_redraw (gate / deliver / freshness)
- [ ] serve, URL 200
- [ ] commit + publish

## Log
- read: RM_Ladder Graphic_Multi drawSize 1.5 (384 px, offsets N/E/W z+0.25, S z-0.25), current = art_source/Ladder/v2 composite; RM_Spikes Graphic_Single 1x1 256 px (top-down log cluster, rejected)
- existing candidates: RM_Spikes_halfman_v1..v6 + fwart (all seen, sheet 2026-10-16); ladderhung_a/b (seen). None match the new ask -> generate.
- plan: work dirs src/RimMandrake/FlowWorks/art_source/{Ladder,Spikes}/v3; guides by guide.py; codex_image edit; register as artpipe done jobs (ladderhung pattern)
- 21:11 generating 9 candidates (ladder north A/B, east A/B/C; spikes A-D) via art_source/Ladder/v3/gen.sh
- 21:17 9/9 raw renders landed
- 21:18 conformed (Ladder/v3/finalize.py) + registered 15 artpipe done jobs: railladder_v3{a,b,c}_{n,e,s,w}, RM_Spikes_spokes_v3{a,b,c}; spikes_D dropped (chonky, off-brief)
- 21:18 claimed both; backfill artpipe + build sheet
- 21:25 sheet built: Transient/biome_ffar/spikes_ladders_redraw_sheet_2026-10-21.html (hide-sets halfman, fwart_: seen sets off); gate PASS v1, game_art deliver OK, sheet_freshness verify exit 0; served (serve.log), URL 200
- NOT installed: art.py install / enact only after his pick. Raised-state art (RM_LadderRaised_*) not redrawn: owed after he picks a set.

## Status (final)
- [x] claim items · [x] read art+defs · [x] existing candidates checked · [x] spikes A/B/C · [x] ladder sets a/b/c · [x] sheet · [x] served
