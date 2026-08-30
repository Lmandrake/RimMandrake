# BRIDGE_DEBUGACTION_SWEEP_GEMS_1 — first harvest of a full [DebugAction] sweep

Filed 2026-08-29, FOUNDRY. Owner asked why `GenDebug.ClearArea` never showed up in any
prior roster pass, "this should have shown up in the very first bridge building."
Root cause found and it's structural, not carelessness on one pass: every prior
roster (the original hand-brainstormed one, and this session's own `Find.X` sweep)
searched TOP-DOWN from a named subsystem. `[DebugAction]`-tagged methods need no
`Find.*` linkage at all — the game's dev-tool menu finds them by attribute
reflection. **367 `[DebugAction(` attributes across 17 vanilla files, never grepped
by any pass before this one.** Owner: "Yes, absolutely, right now."

## Spec

New file `JawaBenchDebugGems1.cs` (7 tools):
- `jawa/clear_area` (ungated) — `GenDebug.ClearArea(rect, map)`, the exact method
  behind "Clear area (rect)". Strips roof, destroys every destroyable Thing in the
  rect, leaves terrain untouched. dryRun defaults true.
- `jawa/spawn_fill_area` (ungated) — `GenDebug.SpawnArea(rect, map, def)`, one spawn
  per cell, unconditional.
- `jawa/make_empty_room` (ungated) — reimplements "Make empty room (rect)" with
  configurable wall/stuff/door/floor/roof defs instead of the debug tool's hardcoded
  wood/RoofConstructed/WoodPlankFloor.
- `jawa/destroy_bulk` (ungated, dryRun defaults true) — factionless animals / player
  animals / non-colonists, mirroring the dev-tool menu's own bulk-cleanup actions.
  Predicates are this file's own logic (Faction/RaceProps/IsColonist), not lifted
  from the private debug methods.
- `jawa/explosion_at` (GATED, same tier as `fire_raid`) — `GenExplosion.DoExplosion`,
  the load-bearing subset of its 30+-parameter signature.
- `jawa/ideo_ritual_obligation_remove` (ungated, matches its ADD sibling) —
  `Precept_Ritual.RemoveObligation`, the removal half `jawa/ideo_ritual_obligation`
  never got.
- `jawa/hot_reload_defs` (ungated) — ⭐ **the headline finding.**
  `PlayDataLoader.HotReloadDefs()`, read in full from source: reloads every active
  mod's XML Defs on a LIVE game with no restart — re-resolves cross-references,
  regenerates implied defs, re-matches every spawned Thing's comps to new
  CompProperties, remaps Hediff body parts, rebuilds render meshes. **Scope is
  XML/Defs only — does NOT reload the companion DLL or any C# code.** Runs as a
  QUEUED long event (`doAsynchronously:false`), so the call may return before the
  reload has actually finished — the tool says so plainly rather than claiming
  synchronous completion it cannot prove.

## Verify
Builds clean, 0 errors 0 warnings, first pass. 293 unique `jawa/…` names, no
duplicate alias (full-surface re-scan). **Not deployed** — game up, BENCH holds
bridge. Once deployed, in priority order:
1. `jawa/hot_reload_defs` — edit one XML value in a deployed Jawa mod, call it,
   confirm the new value reads live WITHOUT a restart. This is the load-round
   economics of the whole project if it holds up.
2. `jawa/clear_area` / `jawa/make_empty_room` on a scratch rect.
3. `jawa/destroy_bulk` dryRun on a populated scratch map.
4. `jawa/explosion_at` and `jawa/ideo_ritual_obligation_remove` — lower priority,
   more standard.

## Live-verified 2026-08-30, FOUNDRY — ALL 7 PASS

Full 585-mod list, fresh quicktest map, game paused except deliberate
`step_game_ticks`. `explosion_at` and `hot_reload_defs` were held mid-pass while
the owner was watching the window, then fired on his explicit go-ahead.

### ✅ `jawa/clear_area` — PASS, and the dryRun default is real
```
rect 200,200,12,12   baseline 109 things
clear_area {rect}                    -> dryRun true,  destroyedCount 109, destroyed[] enumerated
  independent re-count               -> 109   (dryRun destroyed NOTHING - the safety rail holds)
clear_area {rect, dryRun: false}     -> dryRun false, destroyedCount 109
  independent re-count               -> 0
```
Also exercised for real a second time over `172,62,8,8`
(`destroyedCount: 40`, incl. `PassableBasalt`/`BoulderBasalt` and a
`VGE_LandingStructure`), confirmed gone by a follow-up `jawa/list_things`.
`roofedCellsBefore: 0` reported on unroofed ground, as expected.

### ✅ `jawa/spawn_fill_area` — PASS
`{rect: "200,200,4,4", thingDef: "Steel"}` → `cellsFilled: 16`; independent
`jawa/list_things` over the same 4x4 returned **16 things, every one `Steel`** —
one per cell, exactly the unconditional per-cell `GenSpawn.Spawn` it claims.

### ✅ `jawa/make_empty_room` — PASS
`{rect: "210,210,7,7", wallDef: Wall, stuffDef: Steel}` on a rect cleared first →
`cellsWalled: 24, cellsFloored: 49, doorAt: {212,210}`. Independent read-backs:
- `jawa/list_things` over the rect → **24 things: 23 `Wall` + 1 `Door`** — a 7x7
  perimeter is exactly 24 cells, one of which became the door. Arithmetic matches.
- `rimworld/get_cell_info` on interior cell 213,213 → `terrainDefName:
  "WoodPlankFloor"`, `roofDefName: "RoofConstructed"` — the floor and roof it
  claimed are really there, and the configurable defs took.

### ✅ `jawa/destroy_bulk` — PASS, both halves
All three filters discriminate correctly on a 41-pawn map:
`factionlessAnimals` → wild only (`VAEWaste_Hydra`, `Raccoon`, `Yobshrimp`…);
`playerAnimals` → the one tamed `BMT_FacetMothLarvae`; `nonColonists` → the
superset. **Pawn count 41 after all three dryRuns — unchanged**, so the rail holds.
Then real: `{filter: playerAnimals, dryRun: false}` → `matchedCount: 1`, destroyed
`BMT_FacetMothLarvae10093` ("York"); independent re-count **41 → 40**.

### ✅ `jawa/ideo_ritual_obligation_remove` — PASS, full round trip
`list` resolves real runtime `Precept_Ritual`s and refuses a non-ritual precept by
name (`IdeoRitualSeat` → *"matches no ritual precept on ideo 'Green Army'"*).
Obligations start empty on a fresh map, so the `remove` half was exercised by
manufacturing one with the ADD sibling on the **player's own** ideo (id 44,
"Boccin Equality" — the only ideo with colonist believers; ADD is a documented
no-op on NPC ideos, and it correctly reported `success: false` on all four tried
there rather than pretending):
```
ideo_ritual_obligation {ideo:44, ritual:AM_FuneralNoCorpse}  -> success true
  list   -> [{obligationId: 55, ticksUntilExpiration: 540000, stillValid: true}]
  remove {obligationId: 55} -> obligationCountBefore 1, obligationCountAfter 0
  list   -> 0 obligations
```

### ✅ `jawa/explosion_at` — PASS (fired on the owner's explicit go-ahead)
Map corner `15,15`, radius 5, `Bomb`, `chanceToStartFire: 0` — ~150 cells from the
colony, nothing of ours in range, game paused throughout.
```
-> success, damAmount: 50   (correctly defaulted from Bomb.defaultDamage; none passed)
immediately after: an `Explosion` Thing exists, 0 things destroyed  <- paused mid-flight
step_game_ticks 120  (resolves it WITHOUT unpausing, per bridge skill 4b)
-> 24 things DESTROYED in radius: Plant_Thornvine x10, Plant_YellowTallGrass x5,
   Plant_YellowGrass x2, Plant_TallGrass x2, Plant_Alocasia, GRimPurpleGrass,
   GRimTreeDead, Plant_Dandelion.  The Explosion Thing consumed itself.
`get_cell_info` 15,15 -> paused: true the whole time.
```
🔑 Worth recording: **a paused explosion looks like a no-op.** The call succeeds,
an `Explosion` Thing appears, and nothing is damaged until ticks run. Reading the
result at that moment would have filed this tool as broken.

### ⭐ `jawa/hot_reload_defs` — PASS. It works on the full 585-mod list, no restart.

The headline claim, tested exactly as this item specified: change one XML value in
a **deployed** mod, call it, read the value back live.

```
live DamageDef/JawaIon_Damage  empAmountDroid  = 24.0
edit  <gamedir>\Mods\JawaIonWeapons\Defs\DamageDefs_JawaIon.xml   24 -> 77   (on disk)
  (re-read before reloading: still 24.0 — the running game does NOT see the file)
jawa/hot_reload_defs {}  -> success, "Queued as a long event - completion is not
                            guaranteed by the time this call returns."
...wait...
live empAmountDroid = 77.0        <-- NEW VALUE, NO RESTART
restore XML to 24, hot_reload_defs again
live empAmountDroid = 24.0        <-- back, both directions proven
```
Read with `jawa/get_defs` on a **fresh connection** each time. Final state: the
deployed XML is byte-identical to its backup (md5 `5a7f6e33…`), the live value is
24.0, and the game is `programState: Playing`, `paused: true`, `playable: true`,
`longEventPending: false`, at the **same `ticksGame` 6022** — no game time lost.

🔴 **The cost, measured, because the note "queued long event" undersells it:** the
reload blocks RimWorld's main thread for roughly **2–4 minutes** on this 585-mod
set. Four consecutive `jawa/get_defs` calls timed out at 30 s each while it ran.
⚠️ **And those timeouts desync the client socket** — the documented "a timeout is
fatal to the CONNECTION, not the call" trap fired exactly as written: the next
four polls each returned `unexpected response id '<guid>'`, reading the previous
call's late reply. **Drop the socket and reconnect; do not poll a hot reload on
the connection that issued it.**

⇒ Still an enormous win: **minutes, against a ~25-minute cold load**, for any
XML/Def change. Scope remains XML only — it does not reload the companion DLL or
any C# (which is why `alerts_list`, `kcsg_place`, `letter_list` and the vehicle
ion patch all still need a game-down deploy).

## criteria
- [x] Root cause of the original miss identified and documented, not just patched.
- [x] Full 367-attribute `[DebugAction]` inventory pulled, triaged for real value
      (most of the 367 are stress-test/debug-visual/already-covered - a small,
      genuinely valuable set survived).
- [x] Every signature read from 1.6 source, not guessed — including the full 30+
      param `GenExplosion.DoExplosion` signature, positionally verified.
- [x] Builds clean, no duplicate alias (full surface re-scanned).
- [x] Deployed — all 7 registered on the live bridge.
- [x] **All 7 proven live**, each by an independent read-back or a before/after
      transition: `clear_area` (dryRun rail non-destructive; real 109 -> 0),
      `spawn_fill_area` (16/16 cells), `make_empty_room` (24 perimeter = 23 Wall +
      1 Door, interior WoodPlankFloor + RoofConstructed), `destroy_bulk` (three
      filters discriminate; 41 unchanged after dryRuns, 41 -> 40 for real),
      `explosion_at` (24 things destroyed in radius after step_game_ticks),
      `ideo_ritual_obligation_remove` (add -> list id 55 -> remove -> 0), and
      ⭐ `hot_reload_defs` (deployed XML 24 -> 77 read back live with NO restart,
      then restored to 24; ~2-4 min main-thread block on 585 mods, and it desyncs
      the issuing connection).

--- history ---
