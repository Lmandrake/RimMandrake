## 1. **Concept review**

**C1.1 — Verdict: sound merge, incomplete proof of gameplay.** One engine for “size has consequences” is coherent, and the two master switches preserve plant-only and animal-only play. The kernels provide useful arithmetic and decision tests. They do **not** establish that the game supplies the correct inputs, applies decisions safely, or survives save/load.

This review uses the inlined files; I did not run the projects or the live suite. External engine cross-checks used an Odyssey-aware decompilation, whose exact build is not pinned to your installed binary. Build-sensitive conclusions below are marked **“verify on 1.6.”**

**C1.2 — The trunk/canopy distinction is the strongest design choice.** Blocking ground contact while allowing movement under the canopy gives giant plants a physical presence without turning their entire picture into a wall. Shared claims, deferred closure and item preservation support that experience.

**C1.3 — “Smashes while passing” and “smashes through” are different capabilities.** `GiantSmash.Owners` implements damage near an already-moving titan. It does not provide a route through an impassable obstruction or continued smashing while movement is stalled. The settings text currently promises more than this kernel establishes.

**C1.4 — The yield curve has a conspicuous tier discontinuity.** `YieldFloor` resets the reference floor at T2. With shipped thresholds, normalized yield rises from approximately **5.66 immediately below body size 8 to 8 at body size 8**: a 41% jump. The tests check monotonicity within each tier, hiding this boundary. This may be intentional, but a continuous curve would make animal growth and threshold tuning feel less arbitrary.

**C1.5 — Settings are extensive, but “superb” needs clearer effective-state feedback.** Add reset-to-defaults, localized labels, and a visible distinction between applied values and changes awaiting restart. The animal master promises vanilla behavior immediately even though the Large Pawns bridge is explicitly startup-only.

## 2. **Implementation review**

**C2.1 — The project split is structurally good.** Both projects compile the same four production kernel files directly. The net8 harness excludes Verse, Unity and Harmony; the net472 mod excludes SelfTest. The explicit production compile list matches the supplied manifest. No obvious missing compile item appears here.

The remaining gap is substantial: a successful SelfTest build says nothing about compilation or execution of the adapters, Harmony patches, comps or jobs.

**C2.2 — Kernel fidelity is strongest for pure geometry, weakest at the game boundary.**

| Finding | What the tests establish | What remains unproved |
|---|---|---|
| **C2.2a — Footprint** | Transform arithmetic, contact mapping, containment and an independently expressed forward oracle. | Actual `Plant.Print` RNG replay, active graphic/variant selection, mesh alignment and renderer patches. |
| **C2.2b — Claims** | Claim-set union and deterministic primary ownership. | Safe physical blocker realization, owner reassignment, grid notifications and save/load reconstruction. |
| **C2.2c — Titanic** | Tier, damage, roof and pool formulas. | Correct race/runtime inputs, crush-rule precedence, actual damage application, job output and Scribe persistence. |
| **C2.2d — Seam/settings** | Boolean gate truth tables and owners selected from supplied `SolidCell` records. | Production gate consumers, collection of every overlapping owner, real movement and production source-key generation. |

The base single-mesh plant transform agrees with the inspected `Plant.Print` implementation. However, `Plant.Graphic` can select immature, leafless or polluted graphics; matching the transform alone does not establish matching masks. [Engine plant implementation](https://github.com/Chillu1/RimWorldDecompiled/blob/master/RimWorld/Plant.cs).

**C2.3 — `validation.py` proves a narrow smoke test.** Its driven behavior is principally def resolution, field access, patch-owner presence, one giant’s blocker counts, and an Elephant/Rat wake comparison. It explicitly leaves selection, damage forwarding, item movement, trapping, save/load, T2/T3 behavior, butcher yield, corpse harvesting, flight and Large Pawns unmeasured.

Running `python validation.py` executes **static checks only**. A `STATIC: PASS` must never be reported as in-game acceptance.

**C2.4 — The settings “roundtrip” does not test Scribe.** `settings_roundtrip` writes and reads static fields through reflection. It never demonstrates persistence, loading defaults for omitted keys, sanitization, or restart behavior. `Mod.GetSettings` and `LoadedModManager.ReadModSettings` use a separate serialized path. [Mod settings entry point](https://github.com/Chillu1/RimWorldDecompiled/blob/master/Verse/Mod.cs), [settings serialization](https://github.com/Chillu1/RimWorldDecompiled/blob/master/Verse/LoadedModManager.cs).

**C2.5 — Several tests overstate their independence or coverage.**

- `CasePlanner` floods the **same planning window**, despite its introductory claim of a whole-board check.
- `CaseSmashStep` directly calls `DamageDedup` twice with a deliberately identical key; it never drives the production forwarding routes.
- `CaseCache.Fresh` returns `"-"` whenever blocking is disabled, discarding selection despite the independent selection toggle. It also never verifies that an equal signature avoids recomputation.
- The C# harness does not exercise `PawnHitbox`; Python tests its sizing helpers, not the complete footprint-union behavior.
- Checking measured output against the same measurement tool detects stale generated data, but cannot independently validate the tool’s interpretation of ground contact.

**C2.6 — Boundary fuzz excludes the cases it most needs to adjudicate.** `CaseBoundary` nudges by `1e-4`, while `CheckOracle` excludes cells within `2e-3` of relevant edges. Those nudges generally remain inside the ambiguity exclusion. Keep the double oracle, but add exact float boundary fixtures that specify inclusion at each side and at equality.

**C2.7 — Planner cost is the principal performance concern.** For window area `V` and `N` candidates, each attempted closure allocates and performs another flood over `V`. Fixpoint retries permit worst-case work approaching `O(N²V)`. `RootServed` also creates direction arrays repeatedly.

Reuse scratch buffers, use visitation stamps, move directions to static storage, and measure milliseconds and allocation per refresh. Budget by work performed as well as plants refreshed; one exceptionally large plant can exceed a per-plant budget.

**C2.8 — Selection has map-wide work even when features are disabled.** Startup keeps opted-in defs in `WithCustomRectForSelector`; `GenUI.ThingsUnderMouse` scans that group, and its property check can evaluate a custom rectangle twice. Your postfix adds a `HashSet` and predicate allocation to every result with two or more things.

First ensure disabled paths return cheaply; then profile dense Rot maps and stacked selections. A spatial candidate index is justified only if measurements show this path matters. [Engine mouse selection](https://github.com/Chillu1/RimWorldDecompiled/blob/master/Verse/GenUI.cs).

**C2.9 — Save compatibility is plausible, not demonstrated.** Preserving namespaces and def names is appropriate. Part C contains no tests of reference resolution, reconstruction order, orphan blockers, corpse pools or resumed jobs. The transient design’s assertion that existing saves load cleanly needs the specified cold-load exercise.

## 3. **Potential bugs**

**C3.1 — Local-border reachability can permit a globally trapping closure.**

- **File + symbol:** `Kernel/RM_HugeClaimsKernel.cs` — `Planner.Plan`, `Planner.Reach`; `SelfTest/HugeThingsFuzz.cs` — `CasePlanner`.
- **Mechanism:** Every passable window-border cell is an independent flood seed. Close the middle of a narrow corridor crossing the window: both halves still reach a border, so closure passes. Outside the window, one half can terminate in a sealed cave containing a pawn. RimWorld’s actual `Reachability.CanReach` evaluates connectivity beyond this artificial border.
- **Severity:** visible. **Confidence:** high.
- **Fix:** Preserve relevant connectivity using map/region information or an adaptive search that resolves exterior connections. Add a larger-board corridor fixture whose far end lies beyond the planning window. A fixed larger margin cannot provide the advertised guarantee. [Engine reachability gate in `Pawn_PathFollower.StartPath`](https://github.com/Chillu1/RimWorldDecompiled/blob/master/Verse.AI/Pawn_PathFollower.cs) — **verify on 1.6**.

**C3.2 — Item assignments can reserve capacity for cells the planner subsequently refuses.**

- **File + symbol:** `Kernel/RM_HugeClaimsKernel.cs` — `ItemMover.Assign`, `Planner.Plan`; `SelfTest/HugeThingsFuzz.cs` — `CaseItems`.
- **Mechanism:** The modeled sequence assigns destinations before deciding which sources close. Suppose source A sorts first, but closing it would remove a giant’s last accessible neighbor. A reserves the only destination; source B receives none. The planner rejects A and leaves B open. Repeating that sequence repeats the starvation while the destination remains unused.
- **Severity:** visible. **Confidence:** high for the modeled algorithm; medium for game impact because the map adapter is outside Part C.
- **Fix:** Recompute capacity assignments after excluding sources rejected for closure, until assignments and accepted closures agree. Preserve deferred claims. Add a liveness assertion showing B eventually closes without external intervention.

**C3.3 — Pawn hitboxes use the default body graphic rather than the active rendered graphic.**

- **File + symbol:** `HugeThingsCore.cs` — `HugeThingsApi.PawnHitbox`.
- **Mechanism:** It always reads `CurKindLifeStage.bodyGraphicData.drawSize`. `PawnRenderNode_AnimalPart.GraphicFor` can instead choose female or alternate graphics, and its mesh size follows that selected graphic. A larger female/alternate body therefore retains the smaller default hitbox.
- **Severity:** visible. **Confidence:** high for the mismatch.
- **Fix:** Resolve the active animal graphic and relevant rendered transform, then retain the existing union with `OccupiedRect`. Test differing default/female/alternate dimensions. [Animal graphic selection and mesh sizing](https://github.com/Chillu1/RimWorldDecompiled/blob/master/Verse/PawnRenderNode_AnimalPart.cs) — **verify on 1.6**.

**C3.4 — Def qualification does not actually answer whether a race can ever become tiered.**

- **File + symbol:** `Kernel/RM_TitanicKernel.cs` — `DefQualifies`; `SelfTest/TitanicFuzz.cs` — `Tier`.
- **Mechanism:** The tests feed the same `b` to def qualification and runtime tiering. The game distinguishes `RaceProps.baseBodySize` from `Pawn.BodySize`, which includes the current life-stage factor. A modded race with base size 3 and a stage factor 2 reaches T1 at runtime but fails startup qualification.
- **Severity:** visible. **Confidence:** medium; contingent on the production caller using base size as documented and on such content.
- **Fix:** Qualify against the maximum supported life-stage size, or attach a lightweight dormant wake comp broadly enough to cover runtime growth. Test base size and stage factor independently, including juvenile down-tiering. [Engine `Pawn.BodySize`](https://github.com/Chillu1/RimWorldDecompiled/blob/master/Verse/Pawn.cs) — **verify on 1.6**.

**C3.5 — A movement-triggered smash cannot guarantee breaching a blocked route.**

- **File + symbol:** `Kernel/RM_HugeTitanKernel.cs` — `GiantSmash.Owners`, `Reach`; `SelfTest/HugeTitanFuzz.cs` — `CaseSmashStep`.
- **Mechanism:** The test manually advances the titan through all 32 positions. Normal `Pawn_PathFollower.StartPath` can reject an unreachable destination before movement starts. An impassable giant barrier can therefore prevent the steps that trigger damage. A surviving plant can also halt further useful smashing.
- **Severity:** visible. **Confidence:** medium; the movement adapter is not supplied here.
- **Fix:** Either describe this as incidental damage when brushing trunks, or add a breach behavior that approaches a reachable trunk, damages its owner while stationary, and retries the route after destruction. Test an obstruction with no alternate path. [Engine path-start checks](https://github.com/Chillu1/RimWorldDecompiled/blob/master/Verse.AI/Pawn_PathFollower.cs) — **verify on 1.6**.

**C3.6 — Most numeric settings accept unsafe persisted values.**

- **File + symbol:** `RM_HugeThingsSettings.cs` — `ExposeData`.
- **Mechanism:** Only the two scales and smash tier are sanitized. Scribe-loaded values bypass sliders: negative session sizes can stop harvesting, invalid work times can break job expectations, and non-finite damage/yield values can reach downstream arithmetic. `ThresholdsValid` also accepts an infinite T3 threshold.
- **Severity:** visible; downstream crash risk depends on adapters. **Confidence:** high for the missing validation.
- **Fix:** Reject NaN/infinity and enforce documented ranges for every numeric field on load and at settings mutation boundaries. Keep the documented shipped-tier fallback for invalid ladders. Add malformed-config fixtures, including zero and infinity.

**C3.7 — Validation restores shipped defaults instead of the user’s original settings.**

- **File + symbol:** `validation.py` — `_restore`, `trunk`, `wake`.
- **Mechanism:** Wake fields restore from `DEFAULTS`; trunk restores `plantTrunkEnabled=True`. A validation run can therefore change an intentionally disabled feature or custom multiplier. The underlying static state is immediately gameplay-visible and may later be persisted.
- **Severity:** visible. **Confidence:** high.
- **Fix:** Snapshot original values before mutation, restore them in `finally`, verify restoration success, and restore the original pause state. Use a disposable test map/save for destructive staging.

**C3.8 — Some fuzz invocations pass without executing any cases.**

- **File + symbol:** `SelfTest/Program.cs` — `Main`; `HugeThingsFuzz.Run`, `HugeTitanFuzz.Run`.
- **Mechanism:** `--fuzz-only any --fuzz-scale 0` returns success; the seam families behave similarly. The Titanic runner instead rejects zero cases. With a replay seed and zero scale, plant/seam `Family` can even print “1 cases” although its loop ran zero times.
- **Severity:** minor, with material false-confidence risk. **Confidence:** high.
- **Fix:** Validate finite, nonnegative scale and arguments centrally. Let seed replay explicitly run one case. Report intentional zero-scale runs as skipped, and never print “ALL PASS” for zero checks. **Engine mechanism:** none; this defect occurs before Verse is involved.

**C3.9 — Python optimization can disable almost every offline assertion.**

- **File + symbol:** `selftest_hugethings_footprint.py` — decorated tests and `main`.
- **Mechanism:** `python -O` or `PYTHONOPTIMIZE` removes `assert` statements. The runner can increment every test’s success count despite incorrect measurements or geometry.
- **Severity:** minor, with false-confidence risk. **Confidence:** high.
- **Fix:** Refuse execution when `__debug__` is false, or use explicit check functions that raise independently of optimization. **Engine mechanism:** none; this is an offline runner defect.

**C3.10 — Explosion redirection bypasses an ignored blocker’s exclusion.**

- **File + symbol:** `HugeThingsCore.cs` — `Patch_DamageWorker_ExplosionDamageThing.Prefix`.
- **Mechanism:** The prefix replaces blocker `t` with its plant without inspecting `ignoredThings`. The original `DamageWorker.ExplosionDamageThing` then checks whether the **plant** is ignored. An explosion excluding the blocker alone can consequently damage its owner.
- **Severity:** visible. **Confidence:** high for that input condition.
- **Fix:** Respect an ignored original blocker before redirection, while retaining the owner dedup and the original explosion cell for falloff. Add fixtures excluding the blocker, owner and neither. [Engine explosion exclusion and damage path](https://github.com/Chillu1/RimWorldDecompiled/blob/master/Verse/DamageWorker.cs) — **verify on 1.6**.

## 4. **Unforeseen challenges + mitigations**

**C4.1 — Rendering patches can invalidate measurements without overriding `Print`.** `ValidateRenderer` checks the declaring class, but a Harmony patch on vanilla `Plant.Print` still passes that check. Log relevant patch owners and provide an overlay comparing the replayed quad with measured contacts; disable blocking for known incompatible transforms.

**C4.2 — Dense overlapping plants need an integration model.** A ledger’s union is order-independent; physical realization involving per-owner planning windows and item moves need not be. Test shuffled registration/refresh orders through a model combining ledger, planner, mover and realized blockers.

**C4.3 — Runtime settings changes can leave mixed effective states.** Root-only plants retain startup-mutated passability until restart, and Large Pawns retains startup configuration. Show the effective state and pending restart explicitly; refresh every affected map after live changes without depending on the settings window being open.

**C4.4 — Save/load must preserve ownership, not merely blocker counts.** Verify overlapping plants, destruction of the primary owner, deferred cells, pushed items, corpse pools and an interrupted harvest job through save/load/save. Inspect owner identities and resource totals, plus subsequent pathing.

**C4.5 — A `Thing.Position` hook sees more than walking.** Unsticking, relocation and ExplosiveKnockback can set position too. Verify that the adapter distinguishes movement modes and does not invent damage along a teleport path. Dedup identity should match an action; a pawn ID plus tick may merge separate same-tick actions.

**C4.6 — Flight requires a ground-contact policy.** Flying titans should use vanilla 1.6 flight through `MaxFlightTime`. Their airborne movement should not automatically trample ground plants or leave rubble; test takeoff, landing, flight expiry and roof interactions.

**C4.7 — Live wake tests are vulnerable to randomness and repeated exposure.** Zero rubble after 15 single-cell rolls at 35% has probability about 0.16%. Conversely, several visits can kill a 5-HP plant even at two damage per visit. Use deterministic trail settings and one controlled movement event for damage assertions; verify starting counts, HP and actual movement.

**C4.8 — Deferred retries and disabled features need scale measurements.** Profile a sparse map, a dense Rot map, several loaded maps and the full modlist. Record refresh latency, worst tick, allocation, pending-cell count and selection cost; include all-off operation and a mass settings refresh.

**C4.9 — Exact-namespace patch discovery is a maintenance trap.** Moving a patch into a subnamespace silently excludes it from `PatchNamespace`. Add a startup assertion that every intended Harmony patch class has exactly one assigned owner and was installed once.

## 5. **Opportunities to leverage**

**C5.1 — Add semantic debug probes.** Expose desired claims, realized blockers, owner sets, selection rectangles, runtime tiers and pending refusals. These would let validation measure currently unmeasured behavior without relying entirely on simulated clicks.

**C5.2 — Add a footprint inspection overlay.** Show claimed, realized and deferred cells, with refusal reasons such as pawn, item, protected object or access preservation. This would make art measurement and compatibility debugging much faster.

**C5.3 — Publish distinct read-only queries.** Other mods need to distinguish canopy coverage, desired ground contact, realized solid cells and owners. That prevents consumers from treating an unmaterialized claim as a wall.

**C5.4 — Emit sparse consequence events.** Plant smashed, titan breached an obstacle, corpse site created and harvest completed are useful hooks for Traces, Aftermath, RimProperty and ideology content. Emit events for consequences rather than polling every footprint.

**C5.5 — Improve the harness with coverage requirements.** Require full `PawnHitbox` tests, cross-tier yield boundaries, finite-value rejection, independent whole-map connectivity checks and a corpse-site state machine. Report skipped and ambiguous cases explicitly.

**C5.6 — Provide a small set of presets.** “Plants only,” “size and selection,” and “full consequences” could configure the existing controls. Preserve individual tuning and make the shipped preset exactly reproduce current defaults.

## 6. **Extensions WELL beyond the mod**

**C6.1 — TheRot: decomposer cycles.** A corpse site attracts the Rot’s decomposers; their feeding transfers resources from the corpse pool into nearby fungal growth. Giant mushrooms then become obstacles those same titans can smash.

**C6.2 — ExplosiveGrowth: dramatic, safe expansion.** Feed rapid growth into the existing dirty-footprint queue. Its countdown can preview impending contact cells, letting colonists clear access before the plant expands.

**C6.3 — FlowWorks: trunks as hydraulic obstacles.** Realized contacts divert shallow flow; uprooting or smashing a giant releases a blocked channel. Keep hydraulic geometry separate from passability so fluid can seep through some root systems.

**C6.4 — OasisMaker and SolarMirrors: useful canopy geometry.** Canopy queries could influence oasis placement and reveal where mirrored sunlight reaches vegetation. Any resulting heat must feed vanilla temperature and heatstroke.

**C6.5 — CreatureBehaviors: controlled titan movement.** A reusable behavior steers friendly titans away from colony infrastructure and gives hostile ones explicit breach targets. This would also resolve the current movement-triggered-smash limitation.

**C6.6 — HostileFlora: anchored versus mobile stages.** An anchored plant claims a footprint; its mobile stage releases it and uses pawn behavior. Re-rooting uses the same safe realization checks, preserving items and access.

**C6.7 — Long Shade and Stillsand: titan migration incidents.** Warn of a grazer crossing the current map toward food or water. Migration supplies the in-game reason for temporarily leaving its single home biome.

**C6.8 — FloodedCanyon: flood-driven obstruction.** Floods uproot selected giants and deposit them as harvestable debris at narrow crossings. Map-generation and incidents can use authored placements on the existing frozen world.

**C6.9 — WeepingStones: stone-crab husbandry.** Gorrask breeding becomes a space-management challenge: adults need broad pens, and controlled breeding grounds offer valuable harvest sites without incidental colony destruction.

**C6.10 — Scarlands and RustCathedral: machinery with physical consequences.** Apply curated wake rules to giant machines, with salvage-site pools replacing meat and leather. WreckedMachines can supply dangerous residual mechanisms.

**C6.11 — Traces and Aftermath: readable aftermath.** Smash events leave species-appropriate splinters, fungal dust or bent metal; Aftermath records the titan’s contribution to a battle and resulting infrastructure losses.

**C6.12 — Inhabited and RimProperty: accountable damage.** Settlements remember a visiting titan and identify responsibility for destroyed property. Escort contracts can pay for a safe crossing and penalize damage.

**C6.13 — Quests: clear a living route.** A caravan requests a passage through giant vegetation before a deadline. Players can harvest an access corridor, redirect the travelers or enlist a titan to breach it.

**C6.14 — Factions: titan keepers.** A faction maintains carefully managed colossi, trades handling expertise and hires colonies to prepare suitable stopping grounds. Its animals keep species-specific biome homes.

**C6.15 — Items: guide stakes and restraint equipment.** Place bait, guide stakes or tether infrastructure to influence a titan’s next destination. They should affect behavior through CreatureBehaviors rather than erase its physical consequences.

**C6.16 — Ideology: reverence for giants.** Precepts reward preserving ancient plants or respectful corpse-site harvesting. Rituals could protect a mature giant or hold a communal harvest, with explicit history events for deliberate destruction.

**C6.17 — Gravship landing: inspect the actual clearance consequences.** Preview which giants the landing policy will remove and where colony-tamed titans can disembark. Test blocker cleanup against the exact 1.6 `GravshipPlacementUtility.ClearArea` contract.

**C6.18 — KeelHoist: giant cargo in portions.** Harvest or salvage sessions prepare manageable bundles for hoisting from inaccessible maps. Preserve one resource pool so repeated hoist/harvest actions cannot duplicate yield.

**C6.19 — `RM_SeabedLayer`: reefback falls.** Reefbacks and lanternwhales belong to their seabed habitat; their deaths create benthic harvest sites accessible through layer travel. Give seabed remains suitable decay and access rules instead of inheriting terrestrial assumptions.

**C6.20 — DivingInteraction and AcousticScanner: locating giant remains.** Acoustic sounding identifies a submerged carcass or root mass; a dive map exposes a limited work area linked to the parent site’s resource pool. Every extracted unit is deducted once across both maps.