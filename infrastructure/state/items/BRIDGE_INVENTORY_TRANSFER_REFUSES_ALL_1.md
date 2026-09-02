# BRIDGE_INVENTORY_TRANSFER_REFUSES_ALL_1 — jawa/inventory_transfer refuses everything on the live list

Found 2026-09-01 while live-verifying `SETTLEMENT_VERBS_WAVE_1`'s claim-fee
gizmo (needed a colonist carrying silver to test the "pay" path).

## spec
`jawa/inventory_transfer` (`mode=add`) refused every attempt this session:
2 different colonists (Dora `Thing_Human1073`, Vie `Thing_Human1077`), 2
different item types (`Silver`, `MealSurvivalPack`), counts from 500 down
to 1 — always `TryAddOrTransfer moved 0 of N <def> into <name>'s inventory
- the container refused it (not acceptable, over capacity, or already
there)`. Both target pawns were freshly-spawned quicktest colonists at full
health with no obvious inventory-blocking trait/hediff. This is on the
owner's real 592-mod full list (not the 13-mod minimal list this tool was
presumably built/tested against) — a mod interaction (e.g.
`mehni.pickupandhaul`, or something else overriding
`Pawn_InventoryTracker`'s container acceptance) is the leading suspect,
unconfirmed.

## verify
- Reproduce standalone (not blocking on another item): spawn a quicktest
  colonist, attempt `jawa/inventory_transfer` add for a trivial item
  (`MealSurvivalPack`, count 1), confirm the refusal reproduces in
  isolation.
- Bisect: try on the 13-mod minimal list first (does it work there at all?
  if yes, the full list is where it broke). If it fails there too, the tool
  itself has a defect regardless of mod list.
- If mod-interaction: find which mod's `ThingOwner`/`Pawn_InventoryTracker`
  override is refusing, per `rimbridge-companion` skill's discipline for
  reading the actual acceptance chain (read `CanAcceptAnyAt`/
  `GetContainerCanStoreDefUnderAmbientTemperature` overrides via Harmony
  patch inspection or source, don't guess).
- Fix or document the real cause (companion tool bug vs. a specific mod's
  restriction that needs a different route to work around).

## criteria
`jawa/inventory_transfer` (or a documented alternative route) can actually
place a common item into a live colonist's inventory on the owner's real
mod list — proven by one successful add, not just an absence of the
refusal message.

## Watch out
This blocked a real verification (`SETTLEMENT_VERBS_WAVE_1`'s pay-and-fire
path) from completing — whoever picks this up should re-run that item's
live test once fixed.
