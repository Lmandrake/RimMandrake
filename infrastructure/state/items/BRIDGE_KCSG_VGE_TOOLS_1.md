# BRIDGE_KCSG_VGE_TOOLS_1 — KCSG structure placement, closing a gap explicitly deferred earlier this session

Filed 2026-08-29, FOUNDRY. Found via the owner's own live debug-menu screenshots (real
578+ mod list), which named "KCSG" as its own category — a fourth distinct search axis
this session, after the hand-curated roster, the `Find.X` sweep, and the vanilla
`[DebugAction]` sweep. Owner: "Build all that you can without my feedback right now."

## Spec

**This reverses an earlier call in this same session.** `BRIDGE_PIPE_NET_INFO_1` and
the "how many can we build" exchange both treated `kcsg_place`/`layout_generate` as
out of scope for lack of vendored source. Wrong — KCSG ships bundled INSIDE
`VanillaExpandedFramework-main`, which IS vendored
(`vendor/mod_sources/VanillaExpandedFramework-main/Source/KCSG/`).

New file `JawaBenchKcsgTools.cs` (3 tools, ungated, HIGH RISK stated in each
Description rather than gated for it — same tier as `run_basegen_symbol`):
- `jawa/kcsg_place` — one tool, four `layoutType` modes, each the exact call
  sequence KCSG's own debug menu uses:
  - `structure`: `LayoutUtils.CleanRect` → `GenOption.GetAllMineableIn` →
    `LayoutUtils.Generate(StructureLayoutDef, rect, map)`.
  - `settlement`: `SettlementGenUtils.Generate(ResolveParams, map, SettlementLayoutDef)`
    (`ResolveParams` is vanilla, no reflection needed for it).
  - `tiled`: `TileUtils.Generate(TiledStructureDef, cell, map)`.
  - `symbol`: `SymbolUtils.Generate(SymbolDef, null, map, cell, faction, null)`.
  🔑 All four KCSG def types (`StructureLayoutDef`/`SymbolDef`/`SettlementLayoutDef`/
  `TiledStructureDef`) derive from `Verse.Def`, confirmed in source — once resolved
  by reflection they cast directly to the vanilla `Def` type for defName/label reads.
  🔑 A real trap the source caught: `StructureLayoutDef`/`SymbolDef` carry NO
  `Generate()` method themselves — the debug action's own one-liner call is an
  EXTENSION METHOD living in a separate static utility class (`LayoutUtils`,
  `SymbolUtils`). Guessing an instance method here would have failed silently via
  reflection (method not found → refusal), not produced wrong behavior — but it
  cost an extra file read each to find the real home.
- `jawa/vge_spawn_structure_skyfaller` — Vanilla Gravship Expanded's own delivery
  mode for the same KCSG structures: `ThingMaker.MakeThing(VGE_LandingStructure)`,
  set its `layoutDef` field by reflection, `GenSpawn.Spawn`.

Also added, fully verified, low-effort: `jawa/research_reinvented_reset` —
`Find.ResearchManager.ResetAllProgress()` (a vanilla method; Research Reinvented's
own debug action calls this exact one).

**Checked and explicitly NOT built this pass**: Vehicle Framework's "Pop Turret" is
a cosmetic VFX-only debug tool (spawns a flying mote for visual testing, no real
gameplay effect) — skipped as not worth the reflection cost. "Ground All Aerial
Vehicles" / "Spawn Airdrop" reach into `AerialVehicleInFlight`/`VehicleSkyfaller`
internal state and a private `DebugLandAerialVehicle` method whose body was not
read — real capabilities, but a distinct next research task, not built here to
avoid guessing at unread logic.

## Verify
Builds clean, 0 errors 0 warnings, first pass despite the reflection complexity
(extension-method lookup across 4 KCSG def types + 2 mod-specific utility classes).
297 unique `jawa/…` names, no duplicate alias (full-surface re-scan). **Not
deployed** — game up, BENCH holds bridge. Once deployed, in priority order:
1. `jawa/kcsg_place layoutType=structure` on a real StructureLayoutDef from the
   live mod list, confirm it actually resolves KCSG's assembly and generates.
2. `layoutType=settlement` — HIGH RISK, test on scratch first.
3. `jawa/vge_spawn_structure_skyfaller` — confirm the landing structure spawns and
   resolves into the KCSG layout on arrival (per VGE's own design).

## criteria
- [x] Reversed the earlier "out of scope" call on KCSG once its actual vendoring
      location was found — recorded here rather than silently overwritten.
- [x] Every signature read from KCSG's own vendored source, including the
      extension-method traps neither the Def types nor a shallow read would have caught.
- [x] Builds clean, no duplicate alias (full surface re-scanned).
- [x] Vehicle Framework's remaining debug actions explicitly triaged and left
      unbuilt with a stated reason, not silently skipped.
- [ ] Deployed and proven live. Needs the game down, then bridge.

--- history ---
