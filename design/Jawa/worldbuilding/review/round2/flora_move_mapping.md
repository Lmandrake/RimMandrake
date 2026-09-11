# Flora move-target mapping — the 6 rows the applier could not parse

Resolved at the BENCH sitting 2026-09-11 (owner present; one card, five
mechanical translations of his own notes against the live rosters). The other
9 flora `move` rows in `flora_assignment_register.decisions.json` parse
directly — the applier resolves them; only these 6 needed this table. Row key =
the decisions.json key; the owner's note is verbatim.

| row key | owner's note | resolution |
|---|---|---|
| `flora:the_forge:AB_GiantGamma` | to crags | REMOVE from the_forge (already in forsaken_crags) |
| `flora:the_forge:AG_Gamma` | to crags | REMOVE from the_forge (already in forsaken_crags) |
| `flora:the_forge:AG_Septimum` | elsewhere, not heat resistant | REMOVE from the_forge (already in forsaken_crags — "elsewhere" satisfied) |
| `flora:the_propane_lakes:AB_CrystalFlower` | This was placed elsewhere, so it can't also be here… | REMOVE from the_propane_lakes (the elsewhere = poison_forest, kept) |
| `flora:poison_forest:AB_CrystalHorn` | propane lakes and blue desert only | REMOVE from poison_forest; KEEP the_propane_lakes; ADD the_blue_desert (no regime conflict — Blue Desert is cold nightside like the Lakes) |
| `flora:the_pyrelands:AB_HardyGrass` | the grass here has to be unique | REMOVE from the_pyrelands — and 🟢 owner extended the ruling by card 2026-09-11: **Plant_YellowGrass and Plant_YellowTallGrass are evicted from the_pyrelands too**. The unique grass is the commissioned quickgrass (+ scorch-fruit, flora commission ledger). Pyrelands ground layer = quickgrass + commissioned fire-chain flora only. |

Consumed by `ROSTER_MOVE_APPLY_1` alongside `move_mapping_v2.md`. Every ruling
lands in the roster JSONs; this table is the target authority for these 6 rows,
never re-derived from the free-text notes.
