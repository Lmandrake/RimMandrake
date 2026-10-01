# STILLSAND_EVENT_CREATURES_LIVE_1 — live-prove the krayt attack and the muurrok

The live half of `STILLSAND_EVENT_CREATURES_1`'s criteria. Code:
`src/RimMandrake/Stillsand/Source/RM_SandLeviathan.cs`, `RM_Verb_MirrorBeam.cs`; defs
`src/RimMandrake/Stillsand/Defs/IncidentDefs/RM_SandLeviathanIncidents.xml`,
`src/RimMandrake/Stillsand/Defs/ThingDefs_Races/RM_Muurrok.xml`,
`src/RimUtinni/UtinniPatches/Defs/IncidentDefs/RUT_KraytAttack.xml`. Deploy Stillsand,
CreatureBehaviors and UtinniPatches first. Prove by **state reads**, never a screenshot hunt.

## criteria

1. A wild krayt still spawns on a Stillsand map (WildAnimals_Stillsand.xml unchanged).
2. `RUT_KraytAttack` and `RM_MuurrokEmergence` fire by dev action on a Stillsand quicktest
   (letter arrives; after the warning a pawn of the kind is on the map; it is in
   `RM_MapComponent_SandLeviathans.Visits`) and return false on a non-Stillsand map.
3. The muurrok's beam damages a target with **no exception in `Player.log`** (the reason
   `RM_Verb_MirrorBeam` exists: vanilla `Verb_ShootBeam` throws on a null `EquipmentSource`), and
   does nothing at night or with weather set to `Sandstorm`.
4. A take on sand leaves `RM_Filth_DisturbedSand`, a drag-mark line and a letter naming the taken,
   and the leviathan then dives (funnel + message, pawn gone from the map).
5. The settings panel "Stillsand: event creatures" lists both incidents.
6. **The Long Hunger** (`RUT`, built, never live-fired): live-fire it once on a Stillsand map
   (parent spec §7).
