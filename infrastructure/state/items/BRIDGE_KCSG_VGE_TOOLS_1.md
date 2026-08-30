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

## Live-verify 2026-08-30, FOUNDRY — 2 of 3 tools PASS. `kcsg_place` is BROKEN in every mode that could be tested. Not closed.

Full 585-mod list, fresh quicktest map, bridge live. All three tools registered.

### ✅ `jawa/research_reinvented_reset` — PASS
```
research_finish_project x3  ->  Smithing wasAlreadyFinished true
                                Brewing  wasAlreadyFinished false (finished by this call)
                                ComplexFurniture wasAlreadyFinished true
research_reinvented_reset   ->  success true, projectsResetCount: 515
re-probe the same three     ->  wasAlreadyFinished FALSE on all three
```
`ResetAllProgress()` really cleared the manager — proven by an independent probe
that reads finished-state before it writes, not by the reset's own return value.

### ✅ `jawa/vge_spawn_structure_skyfaller` — PASS, does exactly what it claims
Clean before/after id-diff over a virgin 30x30 rect (`160,50,30,30`), so the
result is attributable:
```
before                     497 things
vge_spawn_structure_skyfaller {defName: AB_KemeticTemple, point: "175,65"}
  -> success true, thingId VGE_LandingStructure46225
after                      498 things
  the ONE new id: VGE_LandingStructure46225  (def VGE_LandingStructure)
```
⚠️ Honest limit, not a failure: after 1,200 stepped ticks the landing structure
was **still sitting there unresolved** — it had not turned into the KCSG layout.
The tool's own Description scopes itself to "sets one field and spawns", and that
is exactly what it did; whatever drives VGE's arrival/descent did not run here.
Whether a landing structure resolves at all outside real map generation is
**UNMEASURED**, not proven either way.

### 🔴 `jawa/kcsg_place` — 3 of 4 modes fail. Every cause identified exactly.

| mode | result | cause |
|---|---|---|
| `structure` | refuses | our reflection lookup asks for a `Generate` arity that does not exist |
| `settlement` | NRE | KCSG static `GenOption.settlementLayout` never primed |
| `symbol` | NRE | KCSG static `GenOption.mineables` never primed |
| `tiled` | untestable | **zero `TiledStructureDef`s exist on this mod list** |

**`structure`** — `jawa/kcsg_place {layoutType: structure, defName: AB_GiantBonesA,
rect: "60,60,20,20"}` → `success: false, "KCSG.LayoutUtils/GenOption method shapes
did not match - names may have changed since vendoring."` The names have **not**
changed. Probed the DEPLOYED `KCSG.dll` with `ilprobe` (workshop `2023507013/1.6`):
`KCSG.LayoutUtils` exists with 3 `Generate` overloads and 2 `CleanRect`;
`KCSG.GenOption` exists with `GetAllMineableIn`/`GetMineableAt`. The lookup at
`JawaBenchKcsgTools.cs:154` is:
```csharp
layoutUtils.GetMethod("Generate", KcsgStatic, null,
    new[] { defType, typeof(CellRect), typeof(Map) }, null);   // 3 parameters
```
but the real overloads declare **5, 6 and 7** parameters
(`LayoutUtils.cs:14/20/23`) — the 3-argument form only exists at a *call site*,
via C# default arguments. 🔑 **Optional parameters are not part of a method's
signature**, so an exact-type `GetMethod` can never match one. The item's own spec
correctly caught that these are extension methods and then wrote the call-site
shape into the reflection lookup anyway. `CleanRect(def, Map, CellRect, bool)` and
`GetAllMineableIn(CellRect, Map)` are genuine declared arities and DO resolve —
only `Generate` is null, and the shared refusal message hides which of the three
failed.
⚠️ **Second, separate defect in the same branch: the call ORDER is inverted.** KCSG's
own debug action (`Utils/DebugActions.cs:29-32`) runs
`GetAllMineableIn` → `CleanRect` → `Generate`; ours runs
`CleanRect` → `GetAllMineableIn` → `Generate`, so `CleanRect` would read an
unprimed `mineables` even once the arity is fixed. It also derives its rect from
`layoutDef.sizes`, not from an arbitrary caller rect.

**`symbol`** — resolves and invokes, then
`"SymbolUtils.Generate threw TargetInvocationException: Object reference not set
to an instance of an object"`, on a virgin cell and again inside a rect. Cause,
read from source and confirmed against the deployed DLL:
`SymbolUtils.Generate` reaches `GenOption.GetMineableAt(cell)`
(`SymbolUtils.cs:60`), and that method is
```csharp
public static Mineable GetMineableAt(IntVec3 cell)
{
    if (mineables.ContainsKey(cell))   // GenOption.cs:51 - NO null guard
```
`mineables` is `private static Dictionary<IntVec3, Mineable>` (confirmed in the
deployed `KCSG.dll` field list) and is assigned **only** in `GetAllMineableIn`.
`symbol` mode never calls it ⇒ guaranteed NRE. Fix: prime with
`GenOption.GetAllMineableIn(CellRect.SingleCell(cell), map)` first, as every KCSG
entry point does.

**`settlement`** — `defName: VFEI2_InsectoidSettlementRatingOne` (a real live def),
rect `40,150,30,30` → `"SettlementGenUtils.Generate threw
TargetInvocationException: Object reference not set to an instance of an object"`;
the rect's thing count was **436 before and 436 after**, so nothing partial was
written. Cause: `SettlementGenUtils.Generate` reads
`GenOption.RoadOptions` (`SettlementGenUtils.cs:67`), declared as
```csharp
public static RoadOptions RoadOptions => settlementLayout.roadOptions;  // GenOption.cs:25 - no ?.
```
`GenOption.settlementLayout` is a static our tool never sets. It also reaches the
same unprimed `GetMineableAt` at line 63 when `avoidMountains` is set.

**`tiled`** — could not be tested and that is a finding, not a gap in this pass:
the tool's own refusal for a bogus name returned `candidates: []`, i.e. **the live
585-mod list contains zero `TiledStructureDef`s**. Nothing exists to place.

🔑 **One sentence for the whole tool:** KCSG's utilities are not standalone
functions — they read a bundle of `GenOption` statics that KCSG's own GenStep and
debug actions prime first. `jawa/kcsg_place` calls the leaves without setting up
that state. The fix for three of four modes is the same shape: prime
`GenOption.mineables` (and `settlementLayout` for settlements) before invoking,
and ask reflection for the real declared arities.

⛔ Not fixable this pass — game UP, companion DLL locked. Rides the next
game-down window.

## criteria
- [x] Reversed the earlier "out of scope" call on KCSG once its actual vendoring
      location was found — recorded here rather than silently overwritten.
- [x] Every signature read from KCSG's own vendored source, including the
      extension-method traps neither the Def types nor a shallow read would have caught.
- [x] Builds clean, no duplicate alias (full surface re-scanned).
- [x] Vehicle Framework's remaining debug actions explicitly triaged and left
      unbuilt with a stated reason, not silently skipped.
- [x] Deployed — all 3 tools registered on the live bridge.
- [ ] Proven live. `research_reinvented_reset` (515 projects, verified by an
      independent finished-state probe) and `vge_spawn_structure_skyfaller`
      (one attributable new `VGE_LandingStructure` on an id-diff) both PASS.
      **`jawa/kcsg_place` fails in all 3 testable modes**: `structure` looks up a
      3-param `Generate` that does not exist (real arities 5/6/7 — optional args
      are not in a signature) and calls CleanRect before GetAllMineableIn;
      `symbol` and `settlement` NRE on unprimed `GenOption.mineables` /
      `GenOption.settlementLayout`. `tiled` has no defs on this mod list.

## Fix built, 2026-08-30, BENCH (offline pass, game UP — no deploy possible)

All three `structure`/`settlement`/`symbol` defects fixed, matching KCSG's own
vendored `DebugActions.cs` call sequence exactly:
- `structure`: `Generate` lookup now asks for the real 5-param declared arity
  (`StructureLayoutDef, CellRect, Map, Faction, bool`) instead of the 3-param
  call-site shape; call order fixed to `GetAllMineableIn` → `CleanRect` →
  `Generate` (was `CleanRect` → `GetAllMineableIn` → `Generate`).
- `settlement`: now sets `BaseGen.globalSettings.map` (vanilla, direct) and
  `GenOption.settlementLayout` (KCSG, by reflection — the field
  `GenOption.RoadOptions` reads with no null guard) before calling
  `GenOption.GetAllMineableIn` then `SettlementGenUtils.Generate`.
- `symbol`: now calls `GenOption.GetAllMineableIn(CellRect.SingleCell(cell), map)`
  before `SymbolUtils.Generate`, priming the `mineables` dictionary
  `GetMineableAt` dereferences with no null guard.
`tiled` untouched — no defect was found in it, only that no `TiledStructureDef`
exists on the live mod list to test against.
Builds clean: `python.exe build.py --gm` → 0 errors, 0 warnings.
**Fixed in source, builds clean, awaiting next game-down deploy + live re-verify**
— criterion above stays unchecked until all three modes are re-proven live
(`tiled` remains untestable on this mod list, not a defect).

--- history ---
