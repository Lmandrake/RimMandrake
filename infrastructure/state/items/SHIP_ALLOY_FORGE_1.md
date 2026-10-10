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
   question card 2026-10-09). Its home is **The Forge** (`RM_TheForge`; owner, question card 2026-10-09), and it
   may ALSO come from asteroids — owner, typed 2026-10-09: *"I like the forge makes that mineral. We had
   also said asteroids. It's ok if it's both or another minerals in space either way."* Builder's call:
   zersium in both, or a different space mineral for the asteroid side (see ASTEROID_DESERT_ORES_1).
4. Place the forge in the ship layout once its stage in the deck plan is set.
5. Mod Settings: the progressive gate and each recipe can be toggled.

Built 2026-10-09 (FOUNDRY):
- **Forge gate (RM tier, `mandrake.rm.wreckedmachines`):** `RM_WM_AlloyForgeRestoration` (Industrial, follows only
  `RM_WM_AutomatedSmelterRestoration`: the forge comes right after the smelter) replaces the forge's stock
  `VFE_ComplexFactories`; `RM_WM_PlasteelAlloying` (Spacer, follows the forge's project + `AdvancedFabrication`) gates
  `VFEFactory_AlloyPlasteel`, patched in place (`Patches/WreckedMachines_AlloyForgeGates.xml`, research in
  `Defs/ResearchProjectDefs/ResearchProjects_WreckedMachines.xml`). Settings `alloyForgeProgressiveGate` and
  `plasteelAlloyEnabled` (both default on), applied by `WreckedMachinesPatcher` through reflection on VFE's field names.
- **Durasteel (RSW tier, `mandrake.rsw.armoury`):** `RSW_AlloyDurasteel` ProcessDef (Steel + `RSW_Zersium` →
  `RSW_Durasteel`, no research beyond the forge) prepended to the forge's processes by
  `Patches/RSW_AlloyForge_Durasteel.xml`. 🔴 The whole patch is conditional on `RSW_Durasteel`, which
  `CANON_MATERIALS_BUILD_1` defines and which does not exist yet: until it lands the patch adds nothing. Setting
  `durasteelAlloyEnabled` (default on) removes the process at startup (`Source/AlloyForge/RSW_AlloyForgeDurasteel.cs`).
- **PROVISIONAL numbers** (no calibration, no ruling): research 1500 / 4000; durasteel 10 steel + 2 zersium → 10,
  9000 ticks (one Forge map's ~660 zersium ⇒ ~3300 durasteel). Plasteel recipe kept at VFE's stock ingredients.
- **Not done here:** spec point 4 (placing the forge in the ship layout; the deck plan already puts it in Wing E,
  the export has no forge). L2 stays open until `RSW_Durasteel` exists. The forge building still needs VFE factory
  floor (`VFE_BasicFactories`), as the smelter ladder does. No art owed (VFE's forge art; no new item).
- **First scripts:** `WreckedMachines/validation.py` (`alloy_forge_gated` + two setting drives + static checks),
  `Armoury/validation.py` (`alloy_forge_durasteel`); both walks carry the new `## must be true` lines.

## criteria
- L1 L4: zersium's home biome is The Forge (ruled 2026-10-09)
- L2 L0: `RSW_Zersium` exists with a canon description and the confirmed source; steel + zersium makes `RSW_Durasteel` on the confirmed building
- L3 L0: the alloy forge's plasteel recipe is the only fabricated plasteel route and unlocks after the durasteel one
- L4 L0: settings toggles exist and default to the shipped behaviour
- L5 L1: a minimal-list load shows the forge's recipes gated as specified, with no config errors

## verify
Record with `rimflow verify SHIP_ALLOY_FORGE_1 --criterion <ID> ...`. Process defs are VFE ProcessDefs, not
RecipeDefs: patch them, do not duplicate them.
