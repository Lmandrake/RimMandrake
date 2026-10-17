# TITANOSLIME_SLIME_BIOME_1 — spec section 8 live gates (2026-10-17, BENCH)

## Setup
- List: the 20-mod walk list + `neku.largepawns` + `mandrake.rm.hugethings` (inserted before `mandrake.rm.biomes`),
  22 mods, all five DLC; `len(env.running)=22` read live. Backup of the walk list:
  `Transient/afk_2026-10-17/ModsConfig.PRE_TITANO_*.xml`.
- Deployed: `mandrake.rm.biomes` compose (GelatinousSlime DLL with the new proof surface), game restarted via Steam.
- Map: fresh dev quicktest (250x250), settings at shipped defaults, `Verse.Log.Clear` at preflight, a Player.log sentinel per gate.
- Script: `src/RimMandrake/GelatinousSlime/northstar/titanoslime_gates.py` (python.exe, bridge held).
  Proof surface: `Source/TitanoslimeProof.cs` (`RM_TitanoslimeProof`, jawa/static_call) + `DevSetMass/DevFeed/DevHeldReport`
  on `RM_CompEngulfer` (the DEV gizmos now call DevSetMass).
- Result JSON (final, mode live): `Transient/afk_2026-10-17/titanoslime_gates_result.json`.

## Gates (final clean run 16:53–16:57)
| # | gate | result | class | evidence |
|---|---|---|---|---|
| 1 | def + spawn + BodySize 6 | PASS | | def resolves live; 5 spawned, stage idx rolled 0/2/0/1/0; stage-1 BodySize 6, every stage matches 6/10.02/16.02 |
| 2 | mass 12 -> BodySize 16, drawSize 6, T2, 3x3; save/reload | PASS | | 16.02 / 6 / T2 / LargePawns GetSize 3, identical after save + load_game_ready |
| 3 | natural swallow <= 60 s, countdown, down releases, timer absorbs | PASS | | 4 replicates; swallows at 120–2160 ticks across runs (one earlier run: 0 of 1 before the slime was downed — single-fight RNG); "Digesting X: 75 s left"; released stunned, acid 2, slimification 0.16; absorbed: no corpse, worn gear on the ground, mass +1, food full |
| 4 | muffalo burst-out (10); cut stage-2 sheds | PASS | | 9/10, 7/10, 9/10 across three runs in 3600 ticks (model ~86 %); default: 14 gelatids, stage HOLDS (permanent-growth ruling); reversible ON: 6 shed and drops to stage 1 |
| 5 | five settings live | PASS | | maxStage 2 refuses stage 3 at mass 12; grows off/on; reversible off/on; engulfs off refuses + mid-hold switch-off releases; sheds off sheds 0 |
| 6 | stage-4 kill -> corpse site, held released | PASS | | stage idx 3, BodySize 24, T3; one new RM_TitanicCorpseSite; held muffalo alive on the map |
| 7 | art at stages 1 and 5, S/E/N | NEEDS OWNER | | renders, three distinct facings, glassy green hill, no eyes/mouth/limbs, drifting entries, scales with stage (my look: matches spec §7). Crops: `Transient/afk_2026-10-17/titano_g7/g7_sheet.jpg`. No owner verdict on this art exists in artpipe. |

Log budget: +0 exception lines and +0 lines naming GelatinousSlime/Titanoslime in every gate, sentinel seen each time.

## Non-PASS rows met on the way (all fixed or classified)
- HARNESS: `get_game_info`/`running_mods` key names; load_game_ready returns before the load (now waits until a step advances);
  `list_things` key is `def`; `set_pawn_rotation` takes `dir`; gear check needed the slime's live position.
- HARNESS (spec): gate 4's "≥3 sheds AND drops to stage 1" is unreachable at mass exactly 4 (two sheds drop it, stage 1
  never sheds) and contradicts the permanent-growth ruling under shipped settings; spec §8 row corrected.
- HARNESS: Verse.Log hit its 10,000-message cap mid-session, so one "all PASS" log budget was blind; now Log.Clear + sentinel.
- **MOD-or-interaction finding: `Destroy(Vanish)` on a titanoslime poisons its cells** (later spawns NRE, Update/OnGUI throw
  every frame, "Cannot register drawable" spam). Titanoslime-only (Thrumbo/Elephant/Muffalo/Gelatid clean), kill is clean.
  Filed `TITANOSLIME_VANISH_DIAGNOSE_GHOST_IN_GRID`. Explains the 700+ exception floods of the earlier g3 runs.

## Left
- Gate 7 needs the owner's look at the art (item stays open).
- `TITANOSLIME_VANISH_DIAGNOSE_GHOST_IN_GRID` (FOUNDRY).
- Code review: `Titanoslime.cs` and `TitanoslimeProof.cs` stay DIRTY (open vanish finding; ProofFind NREs at the main menu).
