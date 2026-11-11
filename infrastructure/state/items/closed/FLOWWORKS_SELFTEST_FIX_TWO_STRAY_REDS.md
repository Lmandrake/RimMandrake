## what this item owns
The full FlowWorks C# selftest (`python3 src/RimMandrake/Utils/selftest_flowworks_stock.py`) is red on two cases neither
touched by SUMP_TAR_FIRE_NETWORK_1 (found 2026-11-03 on 94402346e5 + that item's fire-gate diff; 1187 ok, 2 FAIL):

- `Pond_capacity_dug_out_and_back_in_any_order` (`Source/SelfTest/DeepBedChecks.cs`): "detach and reattach both size the pond by unit x beds"
- `PipeTankRiser_wiring_link_stops_layer_prints_flange_follows` (`Source/SelfTest/ReelRiserShadowChecks.cs`): "a west-going strip keeps the tile's north rim on the north"

Log: `D:\ClaudeWork\rimmandrake\scratch\sump_fire\full.txt`.

## verify
`python3 src/RimMandrake/Utils/selftest_flowworks_stock.py --only Pond_capacity_dug_out_and_back_in_any_order,PipeTankRiser_wiring_link_stops_layer_prints_flange_follows` passes; first confirm whether the cases or the production code are wrong.
