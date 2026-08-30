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

## Live-verify 2026-08-30, FOUNDRY — PARTIAL. 2 of 7 proven, 5 not yet run.

Full 585-mod list, fresh quicktest map. **Pass suspended mid-item**: the owner was
watching this game window live and paused it, so the visually dramatic and
game-wide calls in this batch (`explosion_at`, `hot_reload_defs`) were deliberately
NOT fired. See "held" below — this is a decision, not an oversight.

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

### Not yet run
- `jawa/make_empty_room`, `jawa/destroy_bulk` (dryRun), `jawa/ideo_ritual_obligation_remove`
  — safe, simply not reached before the pass was suspended.
- 🔴 **held deliberately, needs an owner heads-up before firing:**
  - `jawa/explosion_at` — visually dramatic on a screen he is watching.
  - `jawa/hot_reload_defs` — reloads every active mod's XML on a **585-mod** live
    game as a queued long event. If it stalls or throws it costs a ~25-minute cold
    load of a game other seats are using. Worth doing, worth doing deliberately and
    announced — not slipped into a verification sweep.

## criteria
- [x] Root cause of the original miss identified and documented, not just patched.
- [x] Full 367-attribute `[DebugAction]` inventory pulled, triaged for real value
      (most of the 367 are stress-test/debug-visual/already-covered - a small,
      genuinely valuable set survived).
- [x] Every signature read from 1.6 source, not guessed — including the full 30+
      param `GenExplosion.DoExplosion` signature, positionally verified.
- [x] Builds clean, no duplicate alias (full surface re-scanned).
- [x] Deployed — all 7 registered on the live bridge.
- [ ] Proven live. `clear_area` (dryRun rail verified non-destructive, real mode
      verified by independent re-count 109 -> 0) and `spawn_fill_area` (16 of 16
      cells) PASS. `make_empty_room`, `destroy_bulk`, `ideo_ritual_obligation_remove`
      not yet run; `explosion_at` and `hot_reload_defs` held pending an owner
      heads-up (he is watching the window; hot_reload_defs risks a 25-min reload).

--- history ---
