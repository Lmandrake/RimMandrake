# BRIDGE_GEN_AND_STORYTELLER_TOOLS_1 — 11 more bridge tools, owner said "keep building" while the game loads

Filed 2026-08-29, FOUNDRY. Sibling to `BRIDGE_LORDS_AND_GAPS_TOOLS_1` (the first 10).
Written and BUILT during the game's own LOADING window — deploy needs the game closed,
which loading is not, so this batch is source+build only until the next down-window.

## Spec

New file `JawaBenchGenTools2.cs` (4 tools, ungated — map-generation/roof-repair
primitives, same tier as `jawa/prefab_place`/`build_batch`, not incidents):
- `jawa/scatter_at` / `jawa/run_genstep` — `GenStepDef.genStep` (the already-constructed
  instance the XML loader builds — there is no `genStepClass` field to reflect on, a
  guess corrected mid-build by the compiler) `.ForceScatterAt`/`.Generate` on a live map.
- `jawa/run_basegen_symbol` — `BaseGen.globalSettings.map`/`symbolStack.Push`/`Generate()`.
  ⚠️ HIGH RISK, can spawn a full populated settlement per the roster's own `settlement`
  symbol example.
- `jawa/fix_floating_roofs` — `RoofCollapseCellsFinder.CheckAndRemoveCollpsingRoofs`.

New file `JawaBenchStorytellerTools2.cs` (7 tools):
- `jawa/spawn_mech_cluster` (GATED) — `MechClusterGenerator.GenerateClusterSketch` +
  `MechClusterUtility.SpawnCluster`, the exact utility `Verb_MechCluster` calls.
- `jawa/incident_queue_clear` (GATED) — `IncidentQueue.Clear()`; it is the WHOLE
  capability, the backing list has no per-item Remove.
- `jawa/set_game_speed` (ungated, same tier as `time_set_ticks`) — `TickManager.CurTimeSpeed`.
- `jawa/letter_list` (ungated) / `jawa/letter_send_delayed` (GATED, same tier as
  `send_letter`) — `LetterStack.LettersListForReading` / `.ReceiveLetter(..., delayTicks)`.
- `jawa/av_effect` (ungated, cosmetic only) — song/shake/fleck bundled: `ForcePlaySong`,
  `CameraShaker.DoShake`, `FleckMaker.ThrowMetaIcon`.
- `jawa/set_thing_props` (ungated) — retroactive quality/HP/faction/style on an
  ALREADY-SPAWNED thing; `build_batch`/`spawn_batch` only ever set these at spawn time.

## Verify

Built clean: `build.py --gm` → 0 errors, 0 warnings, second pass after fixing two source
mistakes the FIRST build caught (`GenStepDef.genStepClass` doesn't exist — the real field
is `genStep`, an instance, not a Type; and a doubled `BaseGen.BaseGen.` reference). 274
unique `jawa/…` names total, no collisions. **Not deployed — game was LOADING, not down,
when this batch was written; `--apply` needs the process closed.** Deploy at the next
down-window, then prove each live (none of the 11 has ever been observed running):
`run_basegen_symbol` and `spawn_mech_cluster` are the two most worth a careful first call
(irreversible / spawns a hostile threat respectively).

## Criteria
- [x] 11 tools written, every signature read from 1.6 source via rimsage — including the
      one wrong guess (`genStepClass`) the compiler itself caught and forced a correction on.
- [x] Builds clean (0 errors, 0 warnings) second pass.
- [x] No name collision with the existing 263 (253 + the first 10) — 274 confirmed.
- [ ] Deployed. Needs the game down.
- [ ] Each of the 11 proven live. Needs bridge/game-up after deploy.

--- history ---
