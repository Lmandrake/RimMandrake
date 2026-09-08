# Inhabited (local) — validation walk
subject: src/RimMandrake/Inhabited  (packageId `mandrake.rm.inhabited`)
deps: `mandrake.rm.injections` (RimMandrake: Structure Injections, this tier's own mod — not a third-party dependency)
list: minimal+injections
status-hint: gives world-map places a persistent cast of real Pawn objects who live there and are remembered — PLACE (a structure), CAST (the roster), ROUTE (daily behavior), FATE (what could end them, default nothing)

## must be true
- `Inhabited_Place` (WorldObjectDef, `WorldObject_Inhabited`) can be created at a world tile; its structure comes from the tile-mutator layer (`RM_InhabitedPlace` TileMutatorDef), and with no `<mapGenerator>` it falls back to `MapGeneratorDefOf.Encounter`.
- `Inhabited_Settlement` (WorldObjectDef, `WorldObject_InhabitedSettlement`) names its own `mapGenerator` = `Inhabited_SettlementMapGenerator`, so entering it composes a district (`Inhabited_ComposeSettlementDistrict` GenStep) and populates a cast (`Inhabited_Cast` GenStep) without needing a tile mutator.
- The roster is a `ThingOwner<Pawn>` — survivors return to it when the player leaves the map, the dead are simply forgotten, and a pawn sold into a cast stays there.
- Placeless pawns (a cast wiped/dispersed) enter `DisplacedPool`, and a NEW cast being instantiated draws from that pool before generating anyone fresh.
- At least one `RimMandrake.Inhabited.CharacterDef` per named faction roster (e.g. `Inhabited_Jawa_ChiefGhekkUbbUbb` from `CastRoster_JAWA.xml`) resolves to a spawnable pawn carrying its authored name/traits/backstory.

## the walk
1. [L] Player.log after load contains no "Config error in mandrake.rm.inhabited" and no XML error naming any `CastRoster_*.xml`/`GenSteps_Inhabited*.xml`/`WorldObjects_Inhabited*.xml`   # load-time
2. [L] Player.log contains no `Log.Error` line from `DebugActions_Inhabited.cs`'s own guard strings ("no CharacterDefs loaded", "no SettlementManifestDefs loaded", "WorldObjectDef Inhabited_Place did not load", "WorldObjectDef Inhabited_Settlement did not load")
3. [D] def read-back: `WorldObjectDef` `Inhabited_Place` exists; `worldObjectClass` = `RimMandrake.Inhabited.WorldObject_Inhabited`; no `mapGenerator` field set
4. [D] def read-back: `WorldObjectDef` `Inhabited_Settlement` exists; `mapGenerator` = `Inhabited_SettlementMapGenerator`
5. [D] def read-back: `RimMandrake.Inhabited.CharacterDef` `Inhabited_Jawa_ChiefGhekkUbbUbb` exists; `faction` = `JAWA`; `race` = `Jawa`
6. [D] def read-back: `GenStepDef` `Inhabited_Cast` and `Inhabited_ComposeSettlementDistrict` exist
7. [B] rimworld/execute_debug_action `{path naming "RimMandrake.Inhabited/Create place at current tile"}` on a selected world tile → Player.log `"[RimMandrake.Inhabited] created ... at tile ..."`
8. [B] rimworld/execute_debug_action `{path naming "RimMandrake.Inhabited/Spawn authored character"}` on that place's map → Player.log `"[RimMandrake.Inhabited] Inhabited_Jawa_... -> ..."` names the built pawn
9. [B] rimworld/execute_debug_action `{path naming "RimMandrake.Inhabited/Report roster"}` → Player.log shows the roster count including the newly spawned character
10. [B] rimworld/execute_debug_action `{path naming "RimMandrake.Inhabited/Absorb roster into pool"}` then `{... "Report displaced pool"}` → Player.log shows the moved pawn now counted in `DisplacedPool`

## [S]
Whether the eleven Templates/*.txt structure layouts (deepwater/droid/hutt/junkers) actually build as coherent rooms, and whether the settlement district composition reads well at normal zoom, is a human-pass concern.
