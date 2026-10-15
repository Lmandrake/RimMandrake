I found eight code-backed issues, all involving the developer/proof surfaces. These can alter live saves or undermine release evidence; the supplied code does not establish an ordinary-play hose persistence failure. Checks below are proposed, not executed.

**F1 — MEDIUM — A queued hose command can execute on a different map**

- **Where:** `Source/Hose/HoseProbe.cs`, `Service`:
  ```csharp
  if (string.IsNullOrEmpty(request) || Find.CurrentMap != map) return;
  ```
  followed by:
  ```csharp
  try { res = Run(map, comp, cmd); }
  ```
- **What happens:** The static mailbox stores command text without its originating map. If the player changes maps before service, the newly selected map consumes the command. Coordinate-based mutations such as `reelin`, `order`, `filltank`, and `settrail` can therefore affect another map’s objects.
- **Repro:** Have reels at the same coordinates on maps A and B. Queue a command while viewing A, then select B before the next `Service` call.
- **Suggested check:** **Cheap live:** use `census` first and compare returned reel IDs with the IDs on A and B. Exercise a mutation only on a disposable save.
- **Confidence:** High for the map-switch race. Whether pending requests also survive loading depends on reset code outside this slice.

**F2 — MEDIUM — Reading a missing liquid look creates session-wide configuration**

- **Where:** `Source/RM_LiquidLooks.cs`, `RM_LiquidLookProof.Show` calls `Find`, whose missing-look branches execute:
  ```csharp
  look = new RM_LiquidSurfaceLook();
  f.surfaceLook = look;
  ```
  and:
  ```csharp
  l.surfaceLook = new RM_LiquidSurfaceLook();
  ```
- **What happens:** `Show` is a mutating query. A fluid with neither its own nor an inherited look acquires one merely by being inspected. Subsequent `Members()`/`ApplyAll()` calls now include that fluid. The write targets a `DefDatabase` object, with no undo for the newly assigned look in this file.
- **Repro:** Inspect a valid lookless fluid through `Show`, then reapply all looks. Its membership has changed despite no tuning request.
- **Suggested check:** **Cheap live:** record the relevant `surfaceLook` reference and `Members()` membership before and after `Show`; repeat after loading an earlier save in the same session.
- **Confidence:** High for the mutation; the shipped roster’s exposure requires a def census.

**F3 — HIGH — A rejected tank replacement can erase the original stock**

- **Where:** `Source/Hose/HoseNetProbe.cs`, `filltank`:
  ```csharp
  t.TryRemoveLiquid(t.storedUnits);
  bool ok = units <= 0 || (l != null && t.TryAddLiquid(l, units));
  ```
  Also `Source/RM_NorthstarProofs.cs`, `ProofTank`: removal precedes the potentially refused `TryAddLiquid`.
- **What happens:** These replacements are destructive before success is established. In `filltank`, an unknown liquid with positive units empties the existing tank and returns `success:false`. `ProofTank` validates the liquid first, but a refused addition still leaves the original contents removed. There is no rollback.
- **Repro:** Put real stock in a tank; issue `filltank:x,z=NoSuchLiquid,5`. For `ProofTank`, request a valid liquid in an amount the tank refuses.
- **Suggested check:** **Cheap live:** snapshot liquid and units, submit each invalid replacement, then read the tank immediately. Assert that rejected requests preserve the snapshot.
- **Confidence:** High. This is proof-hook liquid loss, not evidence of a leak in normal transfers.

**F4 — LOW — Tuning an inherited look leaves other users displaying stale materials**

- **Where:** `Source/RM_LiquidLooks.cs`, `LookOfFluid`:
  ```csharp
  return l.surfaceLook;
  ```
  `RM_LiquidLookProof.Find` selects:
  ```csharp
  members = RM_LiquidLooks.FluidMembers(f);
  ```
  and `Tune` reapplies only those selected members.
- **What happens:** A canal fluid can inherit the actual `LiquidDef.surfaceLook` object. Tuning that fluid mutates the shared object, but rebuilds only its canal terrains. The liquid’s natural-body terrains retain their previous materials. Tuning the `LiquidDef` has the converse problem: only suite terrains are rebuilt. `Show` can consequently report identical configuration for visibly different surfaces.
- **Repro:** Choose a liquid whose canal fluid inherits its look. Change its tint through the fluid name; compare canal and pond material reads. Run `All("on")` and compare again.
- **Suggested check:** **Cheap live:** enumerate all terrains associated with the same look reference and compare `Material()` results immediately after tuning and after a full reapply.
- **Confidence:** High.

**F5 — LOW — Individual tuning bypasses the vanilla-terrain protection**

- **Where:** `Source/RM_LiquidLooks.cs`, `Members` filters with:
  ```csharp
  if (Owned(m.terrain) && seen.Add(m.terrain))
  ```
  but `RM_LiquidLookProof.Tune` directly executes:
  ```csharp
  if (RM_LiquidLooks.Apply(m.terrain, look, m.tier)) n++;
  ```
- **What happens:** Bulk application protects official terrains; individual tuning does not. For a liquid row adopting vanilla water, tuning can replace the official terrain’s graphic, ripple material, flecks, and splash flag. Every use of that shared terrain def is affected, including other loaded maps.
- **Repro:** Find an adopted official terrain in a liquid’s suite, then tune that liquid. Compare the official terrain’s material before and after.
- **Suggested check:** **Offline def query** to identify official member terrains, followed by a **cheap live** snapshot/tune/read/revert check. Assert that protected terrains remain unchanged.
- **Confidence:** High for the bypass; medium for occurrence without the registry XML.

**F6 — MEDIUM — The fluid-row size limit can overflow into billions of iterations**

- **Where:** `Source/RM_PromotionProofs.cs`, `ProofFluidRow`:
  ```csharp
  || !int.TryParse(p[3], out int h) || w * h > 400)
  ```
  followed by nested loops over `h` and `w`.
- **What happens:** The guard neither requires positive dimensions nor calculates area safely. Under unchecked integer arithmetic, `65536 * 65536` becomes zero and passes the 400-cell limit. The method then attempts approximately 4.3 billion iterations; skipping off-map cells does not bound the work.
- **Repro:** Invoke `ProofFluidRow("0,0,65536,65536")` in an unchecked build. This can stall the game thread.
- **Suggested check:** **Offline SelfTest:** extract the dimension predicate and assert rejection of zero, negative, overflowing, and over-limit dimensions. Do not execute the full pathological traversal live.
- **Confidence:** High for the guard defect; the overflow manifestation depends on compiler checked-arithmetic settings.

**F7 — LOW — The hose census reports the wrong reel texture during carrying**

- **Where:** `Source/Hose/HoseProbe.cs`, `ReelTex`:
  ```csharp
  return r.laid && gr.DeployedPath != null ? gr.DeployedPath : gr.path;
  ```
  Compare `Source/Hose/Graphic_HoseReel.cs`, `MatAt`:
  ```csharp
  deployed != null && thing is ThingWithComps tw && tw.GetComp<CompHoseReel>() is CompHoseReel r && (r.laid || r.carry != HoseCarryState.Stored) ? deployed : mat;
  ```
- **What happens:** The graphic selects deployed art for a non-stored carry state, while the census requires `laid`. For a carrying/retracting reel with `laid == false`, `reelTex` reports stored art while the renderer selects deployed art. That can invalidate carry-art proof results.
- **Repro:** Start deployment, sample the census while the pawn carries the end and before the hose becomes laid.
- **Suggested check:** **Cheap live:** compare `reelTex` with the texture returned by `parent.Graphic.MatSingleFor(parent)` during each carry state.
- **Confidence:** High for the predicate mismatch; the carry-state implementation is outside this slice.

**F8 — LOW — Probe string escaping can produce invalid JSON**

- **Where:** `Source/Hose/HoseProbe.cs`, `S`:
  ```csharp
  internal static string S(string s) => s == null ? "null" : "\"" + s.Replace("\\", "\\\\").Replace("\"", "\\\"").Replace("\n", "\\n").Replace("\r", "") + "\"";
  ```
- **What happens:** Tabs and other JSON-forbidden control characters remain literal inside quoted strings. Commands are echoed through this helper, so even an unknown command containing an internal tab produces an unparsable response instead of a valid error object.
- **Repro:** Submit a request containing `unknown<TAB>command`, where `<TAB>` is an actual tab.
- **Suggested check:** **Offline Python:** run representative helper outputs through `json.loads`, covering every character U+0000–U+001F, quotes, and backslashes.
- **Confidence:** High.

## Outside this slice

The following implementations are needed to assess the higher-priority production risks:

- `CompHoseReel`, `RM_MapComponent_Hoses`, hose settings, and their Scribe/load/reset paths.
- `StylePickerCore` and `PatchFeature` application/removal logic: picker state lifetime and mid-game toggle behaviour remain unverified.
- `RM_HoseLinks`, `RM_LiquidNet`, transfer/spill services, and tank methods: network lifetime, cache invalidation, removal handling, and ordinary liquid conservation remain unverified.
- `RM_CompLadder` and its gizmo/invalidation implementation. `ProofLadder` assigns `comp.raised` directly, but its declaration is absent, so I cannot establish whether that bypasses required invalidation.
- `RM_LiquidSurface`, `RM_LiquidSurfaceLook`, registry/style XML, and settings callbacks: material-cache invalidation, default look effects, actual adopted terrains, and toggle wiring remain unverified.

The source-file blocks appear complete. `known_behaviours.md` explicitly contains truncated ledger heads; those excerpts do not provide the complete underlying specifications.