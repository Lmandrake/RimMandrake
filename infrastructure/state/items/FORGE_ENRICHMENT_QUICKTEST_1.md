# FORGE_ENRICHMENT_QUICKTEST_1 — live proof of the Forge enrichment tranche

Split from `FORGE_GPT_ENRICHMENT_1`. The tranche compiles and its defs parse; nothing has loaded in a game.
New mechanisms never seen live: a gravship facility of ours linked by patch, a CompStudiable subclass on a
plant, a Harmony postfix hiding a ResearchProjectDef, and phase sustainers driven by the cycle condition.

## criteria

1. **Keel brace.** On a map with a grav engine, build `RM_FloatstoneKeelBrace` on substructure. The pilot
   console's fuel per tile drops from 10 to 9.5 with one brace (TUNED 5%), and the brace's inspect string shows
   the saving. Switch "Floatstone keelwork" off and save settings: back to 10.
2. **Spunstone.** Before any study, debug action `RMTheForge > Spunstone: report knowledge` prints
   `projectHidden=True`. Grow a garden past 0.9 (`Forge cycle: advance one phase` to Growth, then dev-grow it) and
   let a researcher study it. Points rise; at 12 the "Spunstone bonding" letter arrives and `projectHidden=False`.
3. **Voices.** Step the cycle with `Forge cycle: advance one phase`. Each step plays the stinger, and with the
   visual-cue toggle on, a message names the phase's voice. No sustainer survives leaving the map.
4. **Dhuvvox clock.** In the growth window an awake dhuvvox's inspect string counts down. In the last 625 ticks
   it carries `RM_DhuvvoxRunSlowing`. At window end it seals with a dust puff and one "curling back" message per
   map, and the dhuvvox count is the same before and after (`list_things`).
5. Player.log has no error naming `RM_ForgeVoice_*`, `RM_FloatstoneKeelBrace`, `RM_SpunstoneBonding` or
   `RM_TheForge_KeelBraceLink`.
