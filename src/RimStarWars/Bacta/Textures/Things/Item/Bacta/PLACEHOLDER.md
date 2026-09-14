# PLACEHOLDER ART — replace under BACTA_TANK_ART_1

`RSW_Bacta.png` (128x128) was generated procedurally (PIL) to unblock
BACTA_TANK_CORE_1. It is a flat metal canister with a pale-blue fill line. Not
finished art.

## Constraints the real art must keep

- **128x128, transparent background**, silhouette inside roughly the middle 70%
  so it reads at `drawSize 0.85` on a stockpile tile and in the trade window.
- It is a **sealed canister of fluid**, not a pill, not a syringe, not a
  medicine kit — bacta cannot be applied by hand in this mod, only poured into
  a tank. The art should not suggest a usable medical item.
- Pale luminous blue is the fluid's identity colour; it is also hardcoded as
  `BactaTuning.FluidColor` = `Color32(123, 220, 255, 75)` for the tank's fill
  quad. Keep the item and the tank fill reading as the same substance.
- The def references it by texPath `Things/Item/Bacta/RSW_Bacta` — **art binds
  by texPath, not by defName**, so a replacement must land at exactly that path.
