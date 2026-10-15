# CANAL_SWIM_VERIFY_POISON_POOL_PARTY

FlowWorks: hazardous canal fills keep Water tag, recreational swimming possible

Source: FlowWorks pre-release GPT consult, BENCH 2026-10-15 — `Transient/release_push_2026-10-15/gpt_FlowWorks/TRIAGE.md` (full rows) and the `answer_<slice>.md` named by each finding id.

## findings

- **C9-F8** PLAUSIBLE MEDIUM — Poison/oil/fuel canal fills keep the Water tag and no no-swim marker: colonists may go recreational swimming in them. Defs/Canals/TerrainDefs/FlowWorks_PitFluidTerrain.xml (28 <li>Water</li>); RM_Patch_JoyGiver_GoSwimming_NoSandSwim only vetoes terrains with RM_NoRecreationalSwimExtension. Live: warm map, a colonist with low joy beside a shallow poison canal and no other water; read the GoSwimming job target.

## criteria

- Each CONFIRMED finding: a SelfTest/python case (or a live state read where the row says so) that goes red on today's code, then green with the fix.
- Each PLAUSIBLE finding: run the check written in its row first; close it as not-a-bug with the evidence if it stays green.
