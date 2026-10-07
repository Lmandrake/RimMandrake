# UNFINISHED_LINE_WORLD_FOUNDRY_1 — the line runs in the world

Split from `DROID_MASS_PRODUCTION_QUEST_CHAIN_1` (owner rulings 2026-10-03 in its notes). Design: `design/Jawa/proposals/droid_mass_production_quest_chain_2026-10-02.md` §4.1-4.2, §4.4.
Mod: `src/RimUtinni/UnfinishedLine`. `RUT_LineVolunteer` is NOT a spine beat: `WorldComponent_RUT_EnclaveFoundry`
offers it on its own timer after the spine has ended, so it carries no `epicParent` (read only by
`QuestNode_Root_RelicHunt`) and is not in the spine's `<beats>`.

## criteria
- [ ] Q1=A ruled: WorldComponent_RUT_EnclaveFoundry: Enclave regrowth, Foundry-grade frames/parts in Enclave trader stock, capped volunteer quest (free droid joins, never bolted), line heat -> Imperial strike incident.
- [ ] Never heads, never pawns printed; no player-owned line building (Q1 was A, not B).
- [ ] Settings: line runs in the world on/off (labelled worldgen/world-affecting), volunteer rate, Empire strikes on/off.
- [ ] validate_quest.py 0 errors; validation.py chain extended; Mod Settings for anything tunable.
