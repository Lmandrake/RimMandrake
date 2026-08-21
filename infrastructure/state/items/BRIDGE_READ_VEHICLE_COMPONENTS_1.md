# BRIDGE_READ_VEHICLE_COMPONENTS_1 — no bridge route reaches a vehicle's health tab

## spec

`VEHICLE_RESKIN_LIVE_LOOK_1` could not test its own third criterion — that a damaged
vehicle's health tab reads Left/Right **Bantha** / **Ronto** / **Dewback** from
`VehicleBeastLabels.xml`. **Two independent routes were tried live on full-583 and both
close.**

**1. Selection refuses vehicles.**

    rimworld/select_pawn {"pawnId":"AV_OxCart69647"}
      -> "Could not find player-controlled colonist id 'AV_OxCart69647'."
    rimworld/select_pawn {"pawnName":"Ox cart"}          -> same
    jawa/set_pawn_faction {"pawn":"AV_OxCart69647","faction":"PlayerColony"}
      -> "Pawn is already in PlayerColony - SetFaction warns and returns on a no-op."

The vehicle IS the player's; `select_pawn` filters on colonists and a `VehiclePawn` is not
one. No selection ⇒ `rimworld/list_inspect_tabs`, `open_inspect_tab` and `get_ui_layout`
have nothing to read.

**2. The def readers cannot descend into the list.**

    jawa/get_defs {"defs":"ThingDef/AV_OxCart","fields":"components"}
      -> "components": ["VehicleComponentProperties" × 5]

The reflective reader flattens list elements to their class name. `jawa/get_def` returns
`comps` — the `CompProperties` list — which is a **different field** from `components`, the
vehicle's damageable parts, and it is `components` that carries the labels.

⇒ Either would fix it. **The def route is the cheaper and the more general:** teach the
reflective reader to emit named scalar fields of list elements rather than their class name,
so `components` returns `[{key, label, health, …} × 5]`. That also unblocks every other
nested-list question without a new tool. The selection route is worth doing too, but it is
UI automation and it only answers this one question.

⚠️ Companion change ⇒ the game must be DOWN. Batch it with any other companion work.

## verify

    jawa/get_defs {"defs":"VehicleDef/AV_OxCart","fields":"components"}

## criteria

- `components` comes back as five objects carrying at least `key` and `label`, not five
  class-name strings
- the five labels on AV_OxCart name **Bantha**, and AV_CoveredCarriage **Ronto**, and
  AV_Chariot / AV_WarChariot **Dewback**, matching `VehicleBeastLabels.xml`
- ⛔ and the `key` values are UNCHANGED — `VehicleBeastLabels.xml` patches `label` and
  deliberately not `key`, because `key` is what the vehicle's own code addresses components
  by. If a key moved, the label patch overreached and that is the finding.

## notes

Filed by CHECK 2026-08-21 from `VEHICLE_HEALTH_TAB_UNREACHABLE_1`, off
`VEHICLE_RESKIN_LIVE_LOOK_1/run-1@full-583`.
⛔ Nothing is yet known about whether those labels are right. This item unblocks the
measurement; it does not assert a defect.
