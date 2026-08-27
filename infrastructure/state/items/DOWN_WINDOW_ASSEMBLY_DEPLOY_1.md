# DOWN_WINDOW_ASSEMBLY_DEPLOY_1 — two assemblies are built, committed and cannot deploy while the game runs

🔑 **The OS holds a loaded DLL.** Both of these are built clean and byte-different from the
game copy; nothing else stands between them and being live.

## What deploys, and what rides on it

**1. `JawaBench.BridgeTools.dll`** — the companion. Game copy is at commit `70b3b117`, the
build is current. Carries every companion fix made since:

| item | what it fixes |
|---|---|
| `BUILD_BATCH_FACTION_REJECTS_PLAYER_1` | `jawa/build_batch` takes `player`/`hostile`/`none` like `jawa/spawn_pawn`; one shared resolver, and the refusal names the *difference* |
| `ORDERED_JOB_CANNOT_SOW_1` | `plantDef` → `Job.plantDefToSow`; Sow/Replant/PlantSeed refuse without it; `pausedDuringWait` reported |
| `NO_TOOL_REPORTS_MAP_TILE_1` | new `jawa/map_info` returns `Map.Tile` — no tool among the 291 reported it |
| `BUILD_BATCH_OVERWRITES_SILENTLY_1` | `survived` / `lostToLaterOps` / `displaced[]` / `refuseIfDisplaces` |
| `FIRE_RAID_ECHOES_REQUESTED_FACTION_1` | before/after pawn census, and a warning when a non-hostile faction will be substituted |
| `BRIDGE_ARG_SHAPES_INCONSISTENT_1` | five of seven rows: both pawn-id forms, `pawn_gear` named as a WRITE, `defName` beside `def`, the real gene verbs, the head-reroll ordering |

**2. `RimDefDump.dll`** — the def dumper. Carries `DUMPER_SWALLOWS_CACHE_THROW_1`:
`commonalityDeclared` beside `commonalityEngine` plus `commonalityEngineError`, and no bare
`catch { }` left on any published value.

## The commands, in this order

```
taskkill.exe /F /IM RimWorldWin64.exe
python.exe D:\Luke\dev\Rimworld\src\RimMandrake\bridgetools\build.py --gm --apply
"C:\Users\Mandrake\.dotnet\dotnet.exe" build D:\Luke\dev\Rimworld\src\RimMandrake\RimDefDump\Source\RimDefDump.csproj -c Release
python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod RimDefDump --apply
```

⚠️ **Check for the word `deployed`.** `build.py` refuses while the game runs and says so; a
piped `grep` hides the refusal and you then test stale code and conclude the new tool "was
not found".

## verify
- `python.exe src/RimMandrake/Utils/rimbridge_client.py --list-tools` names `jawa/map_info`.
- `md5sum` agrees between repo and game copy for both DLLs.
- The next capture's `biomeAnimals` rows carry `commonalityDeclared` **and** `commonalityEngine`.

## criteria
- [ ] Both assemblies byte-identical to the repo afterwards.
- [ ] `jawa/map_info` answers, and returns a tile id.
- [ ] No `[Tool]` name lost — `build.py` refuses on removal and that refusal is not overridden.

## ✅ PRE-FLIGHTED 2026-08-27, BUILD — the down window is one command, not a debug session

`python.exe src/RimMandrake/bridgetools/build.py --gm` run offline with the game UP (a build is
not a deploy): **compiles clean, 5.2 s**, bundle ships only `JawaBench.BridgeTools.dll`
(2,217,984 B), GM tools present. No `[Tool]` removed, so `build.py`'s removal guard does not fire.

```
game copy : 70b3b1173918        <- unchanged, as this item recorded
this build: 845925abb370
state     : differs -- built from a DIFFERENT COMMIT (expected after any commit)
```

🔑 **`differs` here is the commit stamp, not a code change** — `build.py` says so itself and the
build is deterministic per commit. Nothing new is owed before the window; run the four commands
above as written.
⚠️ **Run it under `python.exe`, not WSL `python3`.** `build.py` refuses under WSL and says why:
`dotnet.exe` cannot accept a `/mnt/...` project path.
