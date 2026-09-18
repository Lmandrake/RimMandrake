# FLOWWORKS_BOTTLED_LIQUID_TYPE_MISSING_1 — RM_BottledLiquidExtension type not found

Filed 2026-09-18 (BENCH). Queue description: "RM_BottledLiquidExtension type not
found: RM_LiquidBottles_Base.xml discards + drives ~82 defs / 420 crossrefs on
the full load."

## 2026-09-18 (FOUNDRY, offline/BELT) — root cause was already fixed; independently verified, closing

**Root cause was a DEPLOY GAP, not a missing/uncompiled/misnamed class** — same
family as `ENVHAZARDS_DLL_REBUILD_OWED_1`, and already root-caused and
redeployed by BENCH earlier the same day (ledger note, 2026-09-18T08:30:07Z):
the repo DLL (rebuilt 20:44 the previous night by `LIQUID_BOTTLE_LOOP_1`) had
never been pushed to the game's Mods folder, so the game was loading an older
build that predated the class.

Verified from scratch before trusting that note:

1. **Class exists and is correctly named/namespaced.**
   `src/RimMandrake/FlowWorks/Source/LiquidTypes/RM_BottledLiquidExtension.cs`
   declares `public class RM_BottledLiquidExtension : DefModExtension` in
   `namespace RimMandrake.FlowWorks.LiquidTypes` — an exact match for every
   `Class="RimMandrake.FlowWorks.LiquidTypes.RM_BottledLiquidExtension"` in
   `RM_LiquidBottles_Base.xml` and the generated `RM_LiquidBottles.xml`.
2. **It is in the compile list**: `RimMandrake_FlowWorks.csproj` line 131,
   `<Compile Include="LiquidTypes\RM_BottledLiquidExtension.cs" />`.
3. **Deployed DLL now matches the repo DLL byte-for-byte**: md5
   `1d3aa7c43d34f752c6c35be5742fa5bc` for both
   `src/RimMandrake/FlowWorks/Assemblies/RimMandrakeFlowWorks.dll` (tracked,
   last touched at commit `52b9c584e`, `LIQUID_BOTTLE_LOOP_1`) and
   `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\FlowWorks\Assemblies\RimMandrakeFlowWorks.dll`.
   No rebuild or redeploy was needed this pass — BENCH's redeploy already did
   it.
4. **Stronger than a string grep: genuine reflection-based type resolution.**
   A UTF-16-aware byte scan (`RM_BottledLiquidExtension` present) only proves
   the string exists somewhere in the assembly, not that it is a loadable
   type. Built a standalone throwaway .NET 8 console app
   (`_scratch_typecheck/`, deleted after use, never committed) that
   `Assembly.LoadFrom`s the deployed DLL with an `AssemblyResolve` handler
   redirecting to `RimWorldWin64_Data\Managed` (so `Assembly-CSharp`/`Verse`
   references resolve) and calls `GetTypes()`. Result:
   ```
   FOUND: RimMandrake.FlowWorks.LiquidTypes.RM_BottledLiquidExtension
          isPublic=True isClass=True baseType=Verse.DefModExtension
     field liquid : RimMandrake.FlowWorks.LiquidTypes.LiquidDef
     field dirty : System.Boolean
     field size : RimMandrake.FlowWorks.LiquidTypes.RM_ContainerSize
   ```
   The three fields match exactly what the XML sets (`<liquid>`, `<dirty>`,
   `<size>`) — no speculative fields, nothing missing. This is the same
   resolution Verse's def loader performs (search loaded assemblies for a
   type by full name); it now succeeds.

**What I could NOT confirm offline, and why**: the "82 defs / 420 crossrefs
actually resolve" number can only be re-measured by harvesting a fresh
Player.log from a full-mod-list game load taken *after* the DLL fix. Every
Player.log currently in `Transient/` predates the fix — `ModsConfig.xml` was
last written 2026-09-18T02:25:09 (well before the 08:30 redeploy), and the two
most recent full-load logs (`Player.log.loadB_fullNRE_20260918` and
`Player.log.closedsession_20260918_0129.txt`) are byte-identical copies of the
same pre-fix run (40,425 lines, same last-write timestamp), both still
harvesting DEFS DISCARDED=82 and cross-reference=420 — expected, since a
running game does not hot-swap its own loaded assemblies. This task is
explicitly offline/BELT (no bridge, no restart), so a confirming harvest is
**owed to the next full-list load**, not to this item. Given (1)-(4) above,
expect it to clear to 0/baseline on that load; if it does not, the class
resolving correctly in isolation means the residual would be a *different*
bug, not this one.

**No code or deploy changes were needed this pass** — nothing to commit under
`src/`. This file (writing the missing item prose) is the only change.
