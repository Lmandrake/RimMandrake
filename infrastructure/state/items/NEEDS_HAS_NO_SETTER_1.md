## spec
`needs` decides whether an item is offered. Only `rimflow file` and `rimflow spawn` accept
`--needs`; no verb changes it afterwards. Across the whole ledger exactly 4 events carry a
`needs` value (3 `owner`, 1 `offline`) — every other item renders at the filing default,
`offline`.

Effect on CHECK's board, read 2026-08-21: **38 of 38 items say `needs: offline`**, and the
"WAITING ON A WINDOW" section is empty. Among those 38, offered as offline work:

    ROSTER_SOAK_100_DAYS_1     100 in-game days
    CAST_ROSTER_269_LOAD_1     a load
    W9                         the 21,872-tile import over the bridge
    MORNING_RELOAD_PLAN_1      two loads
    PRELOAD_PREDICTIONS_578_1  a load
    LOAD2_TARGET_IS_SUB7B_1    a load
    INHABITED_ROUTE_ONE_DAY_1  a live day

None can be touched with the game down. The axis POLICY.md introduced specifically so that
"waiting for the game" stops looking like "ready" cannot currently express "waiting for the
game" for any migrated item.

⚠️ This is not a mis-stamp to correct one item at a time — there is no verb to correct it
with. The setter is the deliverable; re-stamping the 38 is CHECK's follow-up.

## verify
A verb sets `needs` on an existing item, appends rather than mutates, and is refused for a
seat that does not own the item. Then, with the game DOWN, `rimflow next --seat CHECK` must
stop offering an item whose `needs` is unmet, and `queue/CHECK.md` must list it under
WAITING ON A WINDOW.

## criteria
- A verb exists that sets `needs` on an existing item and is refused for a non-owner.
- After setting one CHECK item to `game-up` with the game DOWN, that item appears under
  "WAITING ON A WINDOW — nothing is wrong" and is NOT returned by `rimflow next`.
- `rimflow why <ID>` names the unmet `needs` as the reason it is not offered.

## notes
Filed by CHECK, 2026-08-21. Blocks CHECK from stamping his own 38 items honestly.
