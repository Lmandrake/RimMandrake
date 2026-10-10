# SHIP_ALLOY_FORGE_1 — the alloy forge aboard, with progressive unlocks

## spec
Spec: `design/RimMandrake/canon_materials_design_2026-10-09.md` §3.2, §3.3, §3.4. Owner, typed 2026-10-09:
*"Yes, I think we will need an alloy forge. Maybe even earlier, but the recipies will unlock later in the game
for more difficult alloys. Durasteel earlier, plasteel later..."*; and, as a question on a card: *"Re-melt
salvage, but durasteel is just steel + a mineral, so that seems like it could fit on the ship smelter too?"*
Parent: CANON_MATERIALS_BUILD_1 (which defines `RSW_Durasteel` and removes the other plasteel routes).

**Already in the mod set:** VFE Factory's `VFEFactory_AutomatedAlloyForge` (5×5) and its
`VFEFactory_AlloyPlasteel` process (steel + chemfuel + gold → 5 plasteel), `ProcessDefs_AlloyForge.xml`,
workshop 3686924415; ship tooling names it (`src/RimMandrake/Utils/rimbench/shipbuild.py`). The exported ship
(`The_Utinni.xml`) has `VFEFactory_AutomatedSmelter` and no alloy forge. The deck plan places an alloy forge in
Wing E (`design/Jawa/worldbuilding/ship_deck_plan.md`).

1. The alloy forge is reachable early (research, cost) and its recipes unlock progressively: durasteel early,
   plasteel late. Exotic metals (duranium, beskar, cortosis) are never forged.
2. Plasteel: keep or retune `VFEFactory_AlloyPlasteel` as the one fabricated plasteel route, gated by a late
   research.
3. Durasteel: steel + `RSW_Zersium` → `RSW_Durasteel`. Runs as **the forge's first recipe**, not on the ship
   smelter (owner, question card 2026-10-09). Zersium is a **rare local ore in ONE home biome** (owner,
   question card 2026-10-09). Its home is **The Forge** (`RM_TheForge`; owner, question card 2026-10-09).
4. Place the forge in the ship layout once its stage in the deck plan is set.
5. Mod Settings: the progressive gate and each recipe can be toggled.

## criteria
- L1 L4: zersium's home biome is The Forge (ruled 2026-10-09)
- L2 L0: `RSW_Zersium` exists with a canon description and the confirmed source; steel + zersium makes `RSW_Durasteel` on the confirmed building
- L3 L0: the alloy forge's plasteel recipe is the only fabricated plasteel route and unlocks after the durasteel one
- L4 L0: settings toggles exist and default to the shipped behaviour
- L5 L1: a minimal-list load shows the forge's recipes gated as specified, with no config errors

## verify
Record with `rimflow verify SHIP_ALLOY_FORGE_1 --criterion <ID> ...`. Process defs are VFE ProcessDefs, not
RecipeDefs: patch them, do not duplicate them.
