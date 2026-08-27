# VOID_AWAKENING_SCRIPTING_1 — drive the Anomaly endgame from outside

Row 3 of 5 split out of `BRIDGE_TOOLS_HARD_BLOCK_1`.

## spec
`VoidAwakeningUtility` plus the `QuestScriptDefOf` roots.

🔑 **This fires a QUEST CHAIN, not a state change**, which is what makes it different from every
other tool in the companion: the effect unfolds over many ticks through QuestParts that talk only
by signal string, so nothing you read back immediately after the call is evidence that it worked.

## Gates
- `ModsConfig.AnomalyActive` — refuse, naming the DLC, when it is off.
- ⛔ **A half-started awakening is a save nobody can finish.** The tool must refuse on a colony
  that already has an awakening in progress rather than starting a second.

## verify
Build clean; then on a SCRATCH map only, fire it and read the quest list back over several
hundred ticks, not immediately.

## criteria
- [ ] Refuses without Anomaly, naming it.
- [ ] Refuses a second awakening.
- [ ] The description says the effect is a quest chain and that an immediate read-back proves nothing.
