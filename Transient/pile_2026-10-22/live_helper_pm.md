# BENCH live helper PM — 2026-10-22

## A. DEEP_DIG remaining rows (deployed DLL 5ebfd259b2, walkthrough game in memory, not saved)
- Row 5 settings text: PASS. FlowWorks: Excavation & Flow > Digging reads "Deepest colonist dig: 2 m (2 m to 20 m; shipped 2 m)" and "Deepest machine dig: 20 m (2 m to 20 m; shipped 20 m)". Capture Transient/pile_2026-10-22/live_pm/row5_settings_text.png.
- Right-click reason: PASS. Ashley (undrafted, selected) right-click on the standing RM_DigCanal at 27,77 (d=6, 3 m): one disabled option "Cannot dig area: Colonists dig to 2 m; deeper needs machine labour (a mechanoid or a droid)." State read: live_pm/rightclick_options.json (the screenshot did not catch the menu). Ashley re-drafted.
- Row 3 Droidworks droid: UNMEASURED. No Droidworks opt-in patch exists (no RM_MachineDigger on any XML; only C# refs), and Droidworks is not on tier fw_gss_sitting (14 mods). Item stays open: owed = the FindMod-guarded patch on RSW_DW_FleshType_Droid, then the row on a tier with Droidworks.

## B. FlowWorks deploy — DONE 15:3xZ
- Pit-cover/survey C# had landed: 41fb948b5e (lids invalidate path/reach; drill+bleed well refused on empty survey; bleed-well strings). HEAD dd2e3981c2 also holds 73b8805755/dbb60e7e50 (reel turns, pipe riser, hose shadow) and d03ca752f4.
- Plan: 10 files (DLL+srchash, RM_LiquidDrill, RM_HoseReel, RM_PipePoles, Keyed, 4 PipeSpan.png), no '-' lines, all committed on main. Game stopped by PID 16452, --apply VERIFIED in sync, relaunched via Steam on fw_gss_sitting (14 mods, marker kept). Bridge token at ~115 s, main menu reached.

## C. Live checks (deployed DLL 41fb948b5e, tier fw_gss_sitting 14 mods)
### TESTENV_PREFLIGHT_HARDEN_TRISPIKE_AT_ARM — PASS (criterion), closed
- lines_proof --fresh-map: site_calm ok=True, threatStructures.threatsAfter=0, 53 wild animals removed, wildSpawner blocked. BUT every row UNMEASURED/SITE: prepare_site read back Plant_Grass standing in lines_site rect 16,22,36,116 (HARNESS/SITE, presumed: grass re-grows during reveal ticks on a 21x95 rect). live_pm/lines_proof_pm.{json,log}
- drawbridge_proof --fresh-map: site_calm ok=True, threatsAfter=0. 9 rows PASS (RAISE_PATH .. WINCH_DESPAWN_CRASHES); RAID_UP aborted: GovernorStop in RAID_UP's prepare_site reveal, 'hurt: health 1 -> 0.68; newest hediff Cut/Head age 15'; no hostile or non-player pawn on the map afterwards (list_pawns: 12 player pawns). Class HARNESS/SITE, presumed, unproven (no threat; cause untraced). live_pm/drawbridge_proof_pm.{json,log}

### Joints / survey / cover rows (script live_pm/joints_live.py, evidence live_pm/joints_live.json + images)
- REEL_OUTLET 4 facings: PASS (rot 0-3 read back; straight lays len 6.75-6.81; control west-reel-to-east loops len 17.87). Build preview exit line: PASS (reel_build_preview.png, West default). Old reels: PASS (13/13 walkthrough reels saved North load West at x+1, footprint kept, laid ones layOk). Noted, NOT closed (N/S art owed, owner's eye).
- PIPE_TANK riser: PASS by capture (pipe_tank_riser.jpg). Noted, not closed (fittings half on owner sheet).
- HOSE_GIRTH shadow: state PASS (alpha 0.80/0.85, width 1.35/1.5), capture hose_shadow_scrapper_empty.jpg. Noted, not closed (owner decides girth).
- Bleed well label: PASS ('bleed well' in game). Settings section 'Drilling and bleed wells' UNMEASURED (search 'bleed' drew blank rows, section not reached). BLEED_WELL_STRINGS noted, open.
- DRILL_PLACEMENT empty survey: PASS (drill + bleed well refused with the survey text; tank allowed on same square). CLOSED at 41fb948b5e.
- PIT_COVER partly covered: PASS (path to covered square 7 cells, across 12, open square found=False; colonist stood on the cover). CLOSED at 41fb948b5e.
- Side note: drawbridge map showed a 'Death: Eli' letter (debug map, after RAID_UP GovernorStop); not traced.

## D. Exit state
Game up on RM_fw_walkthrough_20261022 (reloaded, paused), tier fw_gss_sitting 14 mods, swap-active marker kept, FlowWorks DLL 41fb948b5e deployed. Bridge HELD by BENCH 'holding for the owner's walkthrough'. Mod Settings search field cleared.
