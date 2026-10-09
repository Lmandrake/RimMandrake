# DUST_DEVIL_ITEM_LOSS_FIX_1 — SS-4: dust devil finds landing spot before lifting an item

## spec

Filed from `design/RimMandrake/gpt_reviews/DESIGN_PASS_2026-10-08.md` (remaining rows, helper pass 2026-10-09; owner 'Queue all' card 2026-10-08). Row SS-4 there is the spec; its 'Checked' column says what was read to confirm it is unbuilt. Re-check src before building.

| SS-4 | **(hygiene)** A dust devil can lose an item it lifts: it takes the item off the map before checking it can put it down, and if both drops fail the item is gone. Find the landing spot first, then move. | nothing | S | low | Stillsand | `RM_DustDevil.cs:162-166` `DeSpawn` then two unchecked `TryPlaceThing`. Skeleton conversion (same GPT bullet) already finds the spot first (`RM_GiantSkeletons.cs:561`) — not kept. |

Every invented number is PROVISIONAL. Every feature gets a Mod Settings toggle; names follow the three-tier scheme.

## verify

Record each owed criterion with `rimflow verify DUST_DEVIL_ITEM_LOSS_FIX_1 --criterion <ID> --result pass|fail|partial --config <list> --evidence <path>`:
- A1 (L1): with a dust devil lifting an item whose landing spot and devil cell both refuse placement, the item is back at
Evidence is the Player.log line or bridge state read the criterion names.
