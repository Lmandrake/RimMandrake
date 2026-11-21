# FlowWorks: Polish list

Polish improves play but is not part of passing 0.1.0. Each entry here is moved only with his confirmation, marked in the decision (owner, by card 2026-11-13).

*Empty at entry on 2026-11-13: no open judge gap sorted as Polish.*

## From blind challenge cycle 4 (run judge-1795134433), moved here by the Conductor's instruction of 2026-11-19

Source rows: `blind_challenge/cycle_4/lane2/faults.json` (class Polish, status NOTED_FOR_CONDUCTOR). Nobody fixes these for 0.1.0.

- `RIMMANDRAKE_NOTE_FLOWWORKS_OVERSPILL_SHIPS_SWITCHED_OFF` (inv_overflow_sheet): `RM_SheetSettings.sheetOverflowEnabled` ships false ("off until the live walk signs it off"); flip the default after his walk signs the overspill off.
- `RIMMANDRAKE_NOTE_FLOWWORKS_CONVERTER_PARTIAL_MOVE_UNCHARGED` (inv_converters): in `CompLiquidConverter.CompTickRare` a part-made move (0 < moved < n batches) leaves the batches it made uncharged (budget, totals, fuel, rotation).
- `RIMMANDRAKE_NOTE_FLOWWORKS_SPRINKLER_PICKS_BEFORE_RESERVE` (inv_sprinklers): `RM_Sprinkle.MostHeld` picks the liquid by raw stock, then pays from the reserve-reduced stock, so a net whose most-held liquid is all reserved reads Dry while another sprayable liquid is spendable.
- `RIMMANDRAKE_NOTE_FLOWWORKS_FUZZ_BLIND_TO_ONE_SINK_PATH` (inv_flow_level): the kernel fuzz's volume law does not see an unreported sink drain on `RM_FlowKernel.cs:851` (planted `CHANGED_FUZZ_SINK_UNREPORTED`, rc 0).
- `RIMMANDRAKE_NOTE_FLOWWORKS_GLOW_ROOM_RECT_UNPINNED` (inv_looks): `selftest_glow_tank_live.py` does not pin the scene room's size (planted `CHANGED_GLOW_ROOM_SHORT`, rc 0).

- Pawn shadows reach outside a pit (his walk 2026-11-20: "Nice to have if easy, don't go crazy trying for it."): the pawn ground shadow is already skipped for a pawn drawn sunk in a cut (`RM_Patch_PitHidesShadow`, `Source/Superdeep/RM_PitDepthDraw.cs:417-436`); which shadow he saw is unread; no cheap fix found offline. No ticket.

- Pit relief corner pieces (RIMMANDRAKE_REBUILD_FLOWWORKS_PITS_AS_RELATIVE_TERRAIN): under clear water only the dry part of a north corner piece is drawn; its drowned part shows the floor under the sheet (the far wall and side strips have drowned redraws, the corner has none). A scorched corner piece carries no soot. The old flat-look fallback (`excavationWallMaterialEnabled` off) draws no floor shade, corner or face foot.

- Removed row `body_cover_is_a_look` from `PIT_LOOK_1114_LIVE` (RIMMANDRAKE_JUDGE_FLOWWORKS_DROWNED_BODY_COVER_BY_EYE): it was `None` by construction, so the scene read UNMEASURED every visit; it decides no bar (the scene only supports inv_pits, inv_pit_access, inv_looks, ways_in_and_out). The drowned-body cover is a picture and his walk decides it (LOOK_STAGE8: FAIL on 2026-11-20, fix owned by RIMMANDRAKE_REDRAW_FLOWWORKS_SUNK_PAWN_NOT_TWO_BLUE_PATCHES).

- A Gimme Some Slack power switch drowned in a cut keeps its lamp (lens and halo) above the water: SwitchLightDraw draws every frame outside the realtime gate (pit draw census, LISTED gap, 2026-11-21). The bottom distortion the water judge saw in BLEND is not built: the only moving-texture engine shader paints lava colours (water_by_depth_target.json effects.bottom_distortion).

- Frozen-pond crust ice (RIMMANDRAKE_FIX_FLOWWORKS_FROZEN_POND_CUT_LEAVES_NO_CRUSHED_ICE, 2026-11-21): a pond dug in ICE ground, frozen (ThinIce), cut by a machine at superdeep where the deep stone resolves, leaves no crushed ice (CrustYield skips ice ground, IceCut yields to the deep stone); a colonist's 2 m cap never reaches it. The crust's ice melts to a notch of water the pond does not pay for; bounded by the rolled-depth guard (one per depth per square). `FrozenCrustTerrains` names only vanilla ThinIce.

- Flow-sink film (RIMMANDRAKE_FIX_FLOWWORKS_SINK_STOPS_ON_LAST_DECILITRE_FILM, 2026-11-21, fresh reader of 2083f92acb): an edge sink alone still orders the remainder by plain BFS hops, so a shallow edge sink nearer than a deep one would hold a deep body's last dL the way the flow sink did (same class, never seen to fail; left to keep level_water.py's sinkHops twin exact). Also: a filtered sink still names squares of a liquid it never takes (harmless reorder); DeepestSinkHops allocates its key lambda each call and costs n log n on a partition (tens of ms at a 50k-cell cap, default 6000).

- Review-site geyser (RIMMANDRAKE_JUDGE_FLOWWORKS_PALE_BLOCKS_IN_TWO_METRE_PIT, 2026-11-21): `jawa/destroy_batch` skips `destroyable=false` things, so a vanilla SteamGeyser inside the owner review site rect (visit 3: (59,141), 5 cells north of station 21) stays and puffs steam over the shallows row. The pale squares in station 21 were not FlowWorks: they were TheForge's vapour-column haze round that geyser, now drawn on Forge maps only. The geyser and its puffs are vanilla and leave the water readable; not worth a stager change.
