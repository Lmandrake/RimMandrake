---
state: ready
needs: offline
---

# RIMMANDRAKE_GIVE_GODMODE_LIQUID_POUR_DRAIN

## spec

Owner live look 2026-11-12 ~18:00 PST (words: D:\ClaudeWork\rimmandrake\conductor\godmode_liquid_20261112\OWNER_WORDS.md):
"we need some God Mode capabilities to allow the debug player the ability to drop large units of various liquids on the
terrain or in a pit as well as remove it."

Dev-mode debug actions, category "FlowWorks: liquids":
- pour: pick any liquid FluidDef (enumerated from DefDatabase, never a list), pick an amount in litres (100 L, 1,000 L,
  10,000 L, 100,000 L, fill this pit to the brim, set exact depth...), click cells (repeat-click). Through the engine's real
  pour path (TryPourDl), so it flows, levels and conserves.
- remove: 1,000 L / 10,000 L here, drain this connected body, drain this pit dry, remove ALL liquid on the map.
- readout: click a cell, print bed depth, liquid kind + depth, body volume.
- the same operations as bridge proof tools (one code path).
Existing debug actions read first: Debug/FlowWorksDebugActions.cs, Debug/FlowWorksTankDebug.cs, MapControls.

## acceptance test

SelfTest cases GodLiquid_* (pure parts, RM_GodLiquidMath): amount menu parses to decilitres exactly ("1,000 L" = 10,000 dL);
add then remove returns to zero; litres to fill a pit of N squares x D notches == N*D*1,000 L; exact depth d m on N
squares == N*d*2,000 L. Fails on base (no RM_GodLiquidMath). Click paths: live proof owed.
