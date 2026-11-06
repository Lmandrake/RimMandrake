## spec
Owner 2026-11-06 (on the silt trap): "you KNOW that you're not supposed to just use bright red for modern. Make it look like a "modern" building, I.e. one that I would see right now." Now art_judge_brief.md B6.

Census of 169 Modern PNGs under FlowWorks Textures (share of opaque pixels that are bright red): 21 at 10% or more. These are installed art, still red:
- 13 SuspensionBridge Modern textures. Their palette is code-drawn: `art_source/SuspensionLooks/gen.py` lines 12, 259, 326, 410, 430, red=(196,38,34). Script not edited by the silt-trap work.
- Hose/Styles/Modern: Reel_PumpHookup, Reel_PumpHookup_north, Reel_PumpHookup_south, Reel_Deployed.
- Rivers/Modern: RM_BankStake, RM_BankStakeRidge_v.
- Things/Item/Resource/FlowWorks/Modern: RM_Bottle_m, RM_Bucket_m. (Also listed on MODERN_PUMP_REDRAW_SAME_RED_DIFFERENT_DAY; do not draw twice. The pump itself is under that item and is not this item's.)

Related: Industrial Rivers bank stake and ridges still carry hazard stripes, so a silt trap now in raw cement stands beside striped siblings. Check the RiverWorks family reads as one set per look.

Prompt sources stopped asking for red on 2026-11-06 (TankTall/v2/restyle.sh, ReelTapRedraw/gen_one.sh, BridgeRedraw/bridge_redraw.py, Weir/generate.sh, Faucet/artlist.json). Art already drawn from them was not redrawn.

Scratch copy of the table: D:\ClaudeWork\rimmandrake\scratch\silt_ruling_1106\modern_red_census.tsv (the list above is the durable copy).

## criteria
Each listed texture is redrawn or replaced so it reads as something you would see today, with no bright red tier marker, judged per art_judge_brief B6 and installed through art.py. The census re-run reports none of them at 10% or more bright red.
