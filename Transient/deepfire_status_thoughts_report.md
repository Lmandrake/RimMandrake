# Deepfire: proxy storage fix + status thoughts — 2026-09-30

## 1. DEEPFIRE_PROXY_BLOCKS_STORAGE_1

Status: BUILT, NOT live-proven. Proof (not run):
`python.exe src\RimMandrake\bridgetools\prove_deepfire_proxy_storage.py --start`

- Fix: `RM_DeepfireLightProxy` goes from category **Item** to **Ethereal** (+ `fillPercent 0`,
  item-only `stackLimit` dropped). The altitudeLayer stays **Item**, which is the layer that
  was proven live not to wipe a wall. It is the same shape as the worn proxy.
- Why the wall stays safe (RimSage `GenSpawn.SpawningWipes`): only the category changes. The
  rules that read the category are these: the early returns for
  Attachment/Mote/Filth/Projectile/Plant/PsychicEmitter, the Item-vs-Impassable rule (we are
  Standable), IsEdifice (we have no `building`) and BlocksPlanting (fillPercent 0). None of
  them fires. The altitude rules, which are what wiped the wall, see the same Item layer as
  before.
- Why storage works now (RimSage): `GenSpawn.Spawn`'s move-aside branch only runs for an
  Item-category new thing. `GridsUtility.GetItemCount` counts only Item-category things.
  `StoreUtility.NoStorageBlockersIn` passes a Standable thing with no surface.
- Clustering code is untouched, so 36 coated cells still make 4 proxies.
- Proof actions `T: Proxy: ...` (`Source/DeepfireProxyStorageDebugActions.cs`) plus
  `FloorLightCells()` in the Clusters partial. The proof puts 36 Steel stacks on a stockpile,
  coats under them, and asserts 4 proxies, Ethereal, 0 displaced, GetItemCount 1 on each
  proxy cell. After the stockpile is emptied, every proxy cell must accept a WoodLog. A
  coated Steel wall must survive its own proxy. The log must be clean.
- Build: 0 warnings / 0 errors. XML parses and py_compile is OK.

## 2. DEEPFIRE_STATUS_THOUGHTS_1

Status: BUILT, NOT live-proven. Proof (not run):
`python.exe src\RimMandrake\bridgetools\prove_deepfire_status_thoughts.py --start`

| piece | where |
|---|---|
| Comp-based detection: `SumptuaryUtility.GoodLevel` reads `CompDeepfire.coats` first, then `StatusGoodExtension` | `Source/SumptuaryEngine.cs` |
| Room display score (spec §4.1): Σ coats of coated non-wall Buildings in or bordering the room, plus (coated wall cells + coated floor cells) / 10 | `SumptuaryUtility.RoomDisplayScore` |
| `RM_DeepfireBedroom`: titled pawn, the better of its bedroom (`ownership.OwnedRoom`) and throne room (`AssignedThrone`'s room). Score ≥3 gives +4, ≥8 gives +6 | `ThoughtWorkers_Sumptuary.cs`, `RM_SumptuaryThoughts.xml` |
| `RM_ImpressedByDeepfire`: runs every 2500 ticks. It needs a titled visitor (title/role, or the faction leader) of a non-player, non-hostile faction, plus any public room (enclosed; not a bedroom, barracks or prison) scoring ≥8. Result: +2 goodwill (HistoryEventDef reason), capped once per faction per quadrum. The cap is saved in `GameComponent_Deepfire` | `MapComponent_DeepfireStatus.cs` |
| Room score cache per Room.ID, 250 ticks | same |
| Constants `DeepfireStatusDefaults`; dev actions `T: Status: ...` | `SumptuaryEngine.cs`, `DeepfireStatusDebugActions.cs` |

Notes:
- **Worn case:** the display score reads `pawn.apparel.WornApparel` and the primary weapon, so
  it relies on step 8's real worn-while-equipped path. Loose apparel on the floor counts for
  nothing. The proof dresses pawns through `Pawn_ApparelTracker.Wear` and coats through
  `CompDeepfire.AddCoat`.
- The spec row's "no DLC → only the wearer's thought" bar is not proven. Every DLC is a hard
  prerequisite (owner, 2026-09-26), so no DLC-absent configuration exists to test.
- The spec's "stage 1" for 2 coats is the first stage (+3), which is StageIndex 0.
- `RM_SawCommonerInDeepfire` is still situational, as shipped before this item. The spec's
  "(24 h)" duration is not modelled.
- Engine APIs were confirmed via RimSage: `Room.ContainedAndAdjacentThings` (walls register
  in adjacent touchable regions), `Pawn_Ownership.OwnedRoom`/`AssignedThrone`,
  `RegionGrid.AllRooms`, `Faction.TryAffectGoodwillWith` (+2 is not adjusted: RoundToInt of
  ≤0.5 is 0), `SituationalThoughtHandler.AppendMoodThoughts(def, list)`/`AppendSocialThoughts`,
  `Pawn_RoyaltyTracker.SetTitle`, `GenDate.TicksPerQuadrum`.
- Build: 0 warnings / 0 errors. XML parses and py_compile is OK.

## Selftests (both items)

`run_selftests.py`: 77/79 passed, 1 unmeasured (`selftest_tool_metadata.py` needs the bridge).
1 failed: `selftest_deployed_biome_refs.py`. That test checks the **deployed** game Mods folder
(19 dangling biome references) and does not touch LuminousPigment. The failure was the same
before either change.
