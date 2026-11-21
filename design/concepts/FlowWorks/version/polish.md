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
