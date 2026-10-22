# Bridge art redraw — all 12 (owner by card 2026-10-21 ~21:32 PDT: "Redraw all 12 now")

Source: Transient/pile_2026-10-21/bridge_art_gpt_review.md · Item: `BRIDGE_ART_REDRAW_CABINETS_GROW_SADDLES` (filed --by-card, claimed BENCH)
Tool: src/RimMandrake/FlowWorks/art_source/BridgeRedraw/bridge_redraw.py (list | guides | gen --wave N | finalize | manifest)
Raw renders: D:\ClaudeWork\rimmandrake\bridge_redraw\raw · conformed: art_source/BridgeRedraw/out · results.json there
Registered as artpipe done jobs (done/<id>.json + _artsrc/<id>/) with rimflow_item_id = the item. Install NOTHING until he picks.

## Resume
`python3 bridge_redraw.py list` shows which jobs have raw; `gen --wave N` skips existing raw and runs <=12 per call
(re-run until "0 job(s)"); then `finalize --wave N`; `manifest`; art.py backfill artpipe; art_sheet.py --textures <manifest>.

## Existing art checked
- artpipe find drawbridge: 144 hits = the 2026-10-20 commission (seen by him on all_bridge_art sheet); 34 manifest rows had
  >=1 job in _held_429 / failed (the "26 never arrived" rows). Rerendered here with GPT's fixes folded into the prompts.
- decisions: no owner ruling on any bridge row (all_bridge_art, suspension_four_looks, drawbridge_art sheets: prefill only).
- Styled tiers share one texture per look today (RM_SuspensionStyles.xml); per-tier candidates need new texPaths at install.

## Waves (101 jobs; one candidate each, towers two)
1. rank 1 towers x4 looks x2 · rank 2 drawbridge decks x6 · rank 3 raid plank laid/end/item  (17)
2. rank 4 timber decks I/M/F · rank 5 anchors 3 tiers x 4 looks, south view (15)
3. rank 6 raised leaf face/underside/edge x Timber/Steel/4 looks, one shared span guide (18)
4. rank 7 futuristic decks+jetties · rank 8 lattice · rank 9 timber winch x5 (10)
5. rank 10 scrapper decks · industrial decks+jetty · rank 11 grated decks base+4 looks x2 (15)
6. rank 12 steel jetties, modern steel deck, railings x5, modern wreck, gates x10, steel winches x4, icons x2 (26)

## Log
- 22:00 wave 1 gen started
- 22:07 wave1: 9 towers+planks raw OK; dw1-4 homes 401 -> swapped to pyr0-3
- 22:11 wave 1 done: 17/17 raw, 17 PASS finalize, registered done jobs
- 22:12 wave 1 published 89e285c0f6; wave 2 gen
- 22:16 wave 2 done: 15/15 PASS (pyr0-3 homes also 401 -> 9 workers)
