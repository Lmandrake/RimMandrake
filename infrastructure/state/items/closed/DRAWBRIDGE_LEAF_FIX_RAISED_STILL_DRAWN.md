# DRAWBRIDGE_LEAF_FIX_RAISED_STILL_DRAWN

Found live by BENCH during the L1 sweep (ANCHOR_BOLLARD_REDRAW_LIES_DOWN_ON_DUTY A1/A2), 2026-10-25, quicktest map (Archmagi, 320-mod RUT_TheRot config), deployed build at 47dddf7fd7.

## What was seen
Eight 1-wide drawbridges, one timber and one steel per look. Each was built by `RM_DrawbridgeProofs.ProofMakeDrawbridge` with `RM_MachinerySettings.pipeDefaultLook` set to that look. The setting was restored to Scrapper afterwards. Every leaf was then raised with `ProofDevSet x,z;raise;instant`.

- **Modern and Futuristic TIMBER:** `ProofLeaf` reads `target=raised raised=4/4 progress=960/960`. The deck is still DRAWN across the pit, lowered, and the anchor ropes are drawn taut over the pit.
- **Scrapper and Industrial timber, and all four steel looks:** these hide the deck and draw slack coiled ropes, as designed.
- **Reproducible:** the result is the same after 60 more ticks, a camera move, and a lower;instant then raise;instant cycle on Modern timber (54,62).
- **Deck things:** RM_SuspensionDeck_Timber things exist on every trench square in all looks, so the deck is not missing. The problem is the draw state.

## Evidence
- D:\ClaudeWork\rimmandrake\bench_l1_sweep\view\b3c_up.png: all eight raised.
- D:\ClaudeWork\rimmandrake\bench_l1_sweep\view\b3d.png: the reshoot plus the re-cycle.
- D:\ClaudeWork\rimmandrake\bench_l1_sweep\batch3c.py, batch3d.py and their logs.

## Leads (unproven)
- `Building_SuspensionDeck.Print` returns early on `leafRaised`, which `RM_Drawbridges.Apply` sets. The anchor's `AnchorPrintFor` also reads lowered, so suspect the leaf-to-deck apply or redraw for these two styles. No def difference was found between the Industrial, Modern and Futuristic timber ThingStyleDefs.
- Not yet ruled out: an order or position effect. These were the 3rd and 4th timber bridges built, at x=52 and x=68. The steel bridges at the same x were fine.

## Close bar
Live: build a timber drawbridge in each of the four looks and raise each one. Every deck is hidden and every rope lies slack on the bank, and the same holds after one lower/raise cycle.
