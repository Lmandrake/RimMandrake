# bridge_art_enact — BENCH art helper, 2026-10-21

Item: BRIDGE_ART_REDRAW_CABINETS_GROW_SADDLES

## Steps
- [ ] commit decisions json
- [ ] enact dry run
- [ ] enact --apply
- [ ] facings for picked anchors/jetties/gates/winches
- [ ] per-tier texPaths in defs
- [ ] raised-leaf edge thinness owed note
- [ ] audit (fresh ledger+artpipe), gates, selftests
- [ ] deploy + live look owed list

## Log
- 23:20 enact applied (holds on 48 overwrite/per-tier rows): 49 rulings ingested, PitCover B installed; published b75a419784
- 23:33 wave 2 published 0a587c4cc3: 84 picks installed (36 per-tier at new paths, 48 drawbridge), 36 style defs repointed, 18 atlases, raid plank item def. Next: facings wave 7
- 23:33 wave 7 (facings, 74 jobs) gen started
- 23:39 anchors/jetties north/east = exact rotations of picked south (shipped convention, measured): 36 installed. 18 drawn anchor facings discarded. Winch N/E + gate E (28 jobs) next
- 23:42 wave 7 gen: 15/28 raw
- 23:46 wave 7 done: 28/28 PASS, installed (winch N/E x9, gate E x10)
- audit (fresh): art doctor 0 disagreements; art guard b790494793ed..HEAD 0 unledgered; 85 picks live in ledger AND on disk (sha match), 0 mismatch; all texPaths in RM_SuspensionStyles/RM_Drawbridge resolve, every Graphic_Multi has south/north/east; 28 wave-7 artpipe done jobs, 0 stray anchor jobs
- selftests GREEN: enact, art, artwrite, sheet_freshness, texture_gap_lint, facing_scale_lint, flowworks_suspension_art, flowworks_suspension_linked
- sheet bridge_art_redraw: freshness req 15 FAILS as expected (his picks are now installed; sheet is fully ruled, not rebuilt)

## CONFLICT for him (one card): 12 rows held, nothing done
His B/C pick would overwrite a picture auto-kept by the standing "new FlowWorks art is accepted the first time, install it"
(2026-10-18): Tower x4 (picked C), Railing Base+4 looks (B), Wreck_Modern (B), GratedHeavy_Base (B), GratedSteel_Base (B).
On "yes": art.py enact <decisions> --apply --no-deploy with only those rows unheld needs his words for the keep -> install each
with art.py install ... --owner-said "<his words>"; railing/tower/wreck/grated base paths are single (no per-tier change).

## Owed
- deploy FlowWorks (deploy_custom_mods.py --mod FlowWorks --apply) when the game is down; then a live look: styled bridges
  in each look x tier, drawbridge raised/lowered (leaf, planks, winch facings), raid plank item, pit-cover lattice
- raised-leaf EDGE views (5 picked: Timber/Steel/+looks) read thin at 32 px - he picked them; owed a thickness pass, not changed
- drawbridge per-LOOK art (Scrapper/Industrial/Modern/Futuristic winches, leaves, planks) is installed but RM_DrawbridgeArt.cs
  reads only Timber/Steel: needs C# look lookup; leaf look files are named LeafUp_<View>_<Look> (material ones LeafUp_<Mat>_<View>)
- gate art (10 x south+east) installed at contract paths but RM_DrawbridgeGate still draws the vanilla door: needs wiring
- RM_RaidPlank_Laid / _LaidEnd installed, def still draws the timber deck atlas: needs a draw change (rotation, bank ends)
- 23:51 owner card "Yes, install my picks": 12 held rows installed over auto-kept art (--owner-said), grated base atlases rebuilt; filed DRAWBRIDGE_LOOKS_WIRE_PICTURES_IN_WINGS (BENCH, offline)
