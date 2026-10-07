# Explosive Knockback review save — grid key

Save: `RM_knockback_review_20261006_2137` (Saves folder). Debug quicktest map, 250x250, tier `explosiveknockback`.
Each scene is a cleared 15x15 patch centred on the blast cell below; the blast went off at the centre, aimed east (+x)
unless noted. Everything you see is the aftermath, 300 ticks later. Run record: `run_20261006T213453.jsonl` (18/18 PASS).

| blast cell | scene | what to look at |
|---|---|---|
| 12,12 | calibration | colonist thrown 3 cells east (13 -> 16) |
| 27,12 | wall_stop | colonist stopped against the granite wall at x 30, bruised |
| 42,12 | door_stop | colonist stopped at the closed door (x 45), door damaged |
| 57,12 | over_sandbags | colonist thrown OVER the sandbag line at x 59, landed at 61 |
| 72,12 | pit_colonist | colonist landed in the 3x3 pit (75..77), held |
| 87,12 | pit_enemy | raider landed in the pit, held |
| 102,12 | no_cross | colonist stopped IN the 1-wide pit at x 104, not on the far lip |
| 117,12 | cover_breaks | both covered decks broken (rubble); the colonist on one is in the hole |
| 132,12 | items | steel stack thrown 4, component 5 north, 150 kg minified building did not move |
| 147,12 | corpse_into_pit | corpse on the pit floor |
| 162,12 | killed_by_blast | three corpses thrown |
| 177,12 | shelf | steel on the shelf stayed |
| 192,12 | in_pit_skip | colonist already in a pit was not thrown |
| 207,12 | heavy_skip | thrumbo (removed after the check) |
| 222,12 | caps | 10 colonists + 59 steel stacks; 40 throws max |
| 237,12 | tick_cap | 9 stacks, max 3 per tick |
| 12,27 | settings_off | master off: nothing moved |
| 27,27 | emp_no_throw | EMP: nothing moved |
