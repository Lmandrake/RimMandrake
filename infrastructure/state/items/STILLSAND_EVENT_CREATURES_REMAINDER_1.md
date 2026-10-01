# STILLSAND_EVENT_CREATURES_REMAINDER_1 — the rest of the Stillsand event ladder

The offline remainder of `STILLSAND_EVENT_CREATURES_1` (spec there, §4–§6 and the weighting
half of §2). Design source unchanged:
`design/Jawa/worldbuilding/biomes/stillsand_turn3_development_2026-09-30.md` §2.5.

**Already built by the parent** (`src/RimMandrake/Stillsand/Source/RM_SandLeviathan.cs`,
`RM_Verb_MirrorBeam.cs`, `RM_StillsandEventsMod.cs`):
- `RM_IncidentWorker_SandLeviathan` + `RM_SandLeviathanExtension` (on the IncidentDef): biome gate
  by defName, warning letter + growing rumble (camera shake, dust at the entry edge), arrival at
  the edge nearest the loudest thing (a powered deep drill, else the colony), breach dust column +
  stagger ring, and the dive (fed / burning / off the sand too long / bored) with a funnel and a
  message. A fed leviathan takes the body down a drag line into a funnel. Odds ×(1 + 0.5 per
  powered deep drill), capped at ×3.
- `RM_MuurrokEmergence` (RM) and `RUT_KraytAttack` (Utinni, XML only).
- Settings: toggle + odds slider per leviathan incident (rows built from the def database), and
  the mirror beam toggle.

## spec

1. **The sarlacc swimmer comes to root (RSW).** A Stillsand incident: a `RSW_SarlaccSwimmer` whose
   water is running out swims toward the largest seep (usually a precious cave,
   `STILLSAND_PRECIOUS_CAVES_1`) and roots there. Reuse `src/RimStarWars/Sarlacc/`'s swimmer's-road
   machinery (`RSW_SwimmerRoadExtension`, `RSW_MapComponent_SwimmerRoad`): it already swims to a
   target and roots; what is owed is a Stillsand target finder (the seep, not a dew ring) and the
   IncidentDef. Visibility owner: `CompSarlaccSwimmer` (see `STILLSAND_SAND_SWIM_REMAINDER_1` §3).
2. **The greater krayt den (quest, RSW/Utinni).** QuestScriptDef on the StrandedQuest/LongHunger
   shape: the Deep Desert Tribes and a Jawa crew ask for help; bait (bantha or eopie), the drumming
   lure, charges in the tunnels. The cleared den becomes a precious cave. Needs the caves genstep.
3. **The krayt horn (RSW).** `RSW_KraytHorn`, craftable; plays `RSW_Pawn_KraytDragon_Call`. Routs
   smaller predators and tribal raiders in a radius; every blow rolls the settings' answer chance
   to queue `RUT_KraytAttack` (via `Find.Storyteller.incidentQueue`), and logs the roll. Add the
   answer-chance slider to `RM_StillsandEventsSettings` or an RSW settings page.
4. **The Return's Debt weighting** in `RM_IncidentWorker_SandLeviathan.ChanceFactorNow`, once
   `STILLSAND_RETURN_RITUAL_1` exposes the Debt. Also a landing ship and a charged thumper as
   "loudest" draws in `RM_SandLeviathanUtility.LoudestCell` (the thumper is
   `STILLSAND_SAND_SWIM_REMAINDER_1` §4).
5. **Corpses that do not rot, becoming skeleton landmarks** (turn-3 doc §3.1): krayt and muurrok
   (`RM_MuurrokSkeleton` art is already queued).

## criteria

- The horn routs a test predator and logs its answer roll.
- The sarlacc-roots incident refuses non-Stillsand maps and roots at the seep.
- The den quest generates offline (quest validator in the `rimworld-quests` skill).
