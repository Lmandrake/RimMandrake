# Review — hose port to FlowWorks design (2026-10-10)

Target: `design/RimMandrake/hose_port_to_flowworks_design_2026-10-10.md` (commit 7db8d8288).
Reviewer: independent (BENCH subagent), adversarial. Code read at bench HEAD `e0f467412` (hose/FW sources unchanged
since the design's `fe70301c3` for every line cited below). Paths relative to `src/RimMandrake/` unless noted.

## Verdict

**Sound direction, not port-ready.** The split (reel = the one hose, `RM_LiquidHose` = universal pipe), the save-compat
table and the step plan are mostly right and well evidenced. But the flow coupling (§4.1) contradicts its own
"one coupling rule", breaks FlowWorks' no-accidental-merge invariant, cannot seed from the far end and uses a stale
index; the shared-geometry plan collides public types and misses a runtime GSS input; and two moved files (HoseProbe,
the look picker) will not compile/behave as described. 9 must-fix, 12 should-fix. v2 applies all of them:
`design/RimMandrake/hose_port_to_flowworks_design_v2_2026-10-10.md`.

## Must-fix

### M1. The "one coupling rule" promise is false as specified: reel-footprint conduction and `HosePorts` disagree
- **Evidence.** §4.1 rule 1 makes *every* reel footprint cell conduct to everything cardinal to it, while the drawn
  coupling is `HosePorts.Find` → `HosePortRule.Pick`, which chooses exactly **one** neighbour around the perimeter
  (`GimmeSomeSlack/Source/Hose/HosePorts.cs:85-110`). A reel with a pipe on its west side (the picked port) and a tank on
  its east side would draw coupled to the pipe yet carry to both. Also §4.1 says `HosePorts.FindAt` "returns a
  pipe/tank/machine/reel" — false: a thing with `CompHoseReel` is classified `HosePortKind.None` (`HosePorts.cs:44`), so
  relays are found by `RM_MapComponent_Hoses.RelayOf/FeedersOf` (`RM_MapComponent_Hoses.cs:140-146`), never by `FindAt`.
- **Second defect of rule 1:** FlowWorks' net has an explicit invariant that endpoints do not conduct, "so two separate
  runs never merge through a tank by accident" (`FlowWorks/Source/Machinery/RM_LiquidNet.cs:14-17`). A stored reel whose
  footprint conducts silently merges two pipe runs that happen to touch it — exactly the accident that invariant forbids.
- **Fix.** Make the link edge connect the two *port things*, not cells: `RM_HoseLinks` stores, per laid reel,
  `(reelSidePort = HosePorts.Find(reel), farPort = HosePorts.FindAt(end) ?? RelayOf(reel))`. The BFS treats a port thing
  by kind: Tank → add to result; Pipe → enqueue its cells; Machine → it is (or is not) the origin; Reel (relay) → follow
  that reel's own link. The reel footprint does **not** conduct; a stored or open-ended reel is inert. Then "looks
  screwed on" and "carries" are literally the same two `HosePorts` calls.

### M2. Seeding from the far end is unspecified — a pump/converter at the hose's FAR end reaches nothing
- **Evidence.** `TanksFor` seeds only from hose cells 8-adjacent to, or under, the origin (`RM_LiquidNet.cs:79-94`).
  §4.1 rule 2 says "and vice versa, so a pump at the FAR end reaches tanks at the reel end", but the hose end cell is not
  a pipe cell, so `HasHose` never seeds it; nothing in §4.1/§5 says how the origin finds a link whose end touches it.
- **Fix.** `RM_HoseLinks` also indexes `portThing → links`. Seeding: for the origin itself and every pipe/tank reached,
  look up links whose either port is that thing and traverse to the other port (O(1) per thing). Same lookup serves
  converters, adapters, reactions, baths (all `TanksFor` callers). Add a `HoseNetChecks` case: pump at far end, tank beside reel.

### M3. `HoseProbe` is not self-contained — it reads GSS's aerial materials
- **Evidence.** `GimmeSomeSlack/Source/Hose/HoseProbe.cs:174-175` emits `Aerial.AerialMaterials.OverheadQueue` and
  `AerialMaterials.Span.renderQueue` (the RL9 "overhead drawn over hose" read). §5.2 says HoseProbe's "own verbs are
  self-contained" — moved verbatim it will not compile in FlowWorks.
- **Fix.** FlowWorks' probe emits only the hose queue; the overhead-queue half moves to GSS's `AerialProbe`, and the
  cross-mod row `RL9_overhead_drawn_over_hose` reads one value from each probe and compares them in Python.

### M4. The reel's per-build look needs five Harmony patches, not "~40 lines of StylePicker"
- **Evidence.** The reel's style behaviour is carried by `StylePicker`'s patches on `Designator_Build.ProcessInput`,
  the `ThingStyleDefNonPreceptSource` getter, `BuildCopyCommandUtility.BuildCopyCommand`, the `Thing.StyleDef` getter and
  `Frame.CompleteConstruction` (`GimmeSomeSlack/Source/Aerial/StylePicker.cs:162-240`), all gated by `StyleIndex.Is`
  (`:150-160`). The reel is registered into that index (`:36`). Removing the registration (§5.2) silently removes
  pick-on-build, copy-keeps-style and frame-keeps-style from the reel; "the ~40 lines … `StyleFor`, `RawStyle`,
  `LookOfThing`, menu, `IsStyled`" (§5.2 `HoseLook.cs`) omits all five patches.
- **Fix.** Either (a) FlowWorks carries its own five patches gated on `RM_HoseReel` only (two independent postfixes on the
  same vanilla methods, each a no-op for the other's defs; note `Thing.StyleDef` is a hot getter, so the gate must be a
  single `def ==` compare first), or (b) lift the def-agnostic part of `StylePicker` into `_Shared/StylePicker/` (internal,
  linked into both) with each mod registering its own defs. (b) is less code and one behaviour; recommended. Add the
  four style checks (`StyleStage3Checks`) to the step-2 gate and a live row "reel built with a picked look keeps it through
  frame → building → minify → reinstall".

### M5. `_Shared/SlackGeometry` as written puts PUBLIC types with identical full names into two assemblies, unlike its precedent
- **Evidence.** Every precedent file in `_Shared/` is `internal` (`_Shared/SettingsKit/SettingsKitCore.cs:13,23,32`;
  namespace `RimMandrake.Shared`). The files §5.1 moves are `public` (`Core/CordMath.cs:16,25,51,76,123`,
  `CordWorld.cs:8-59`, `CordPlanner.cs:8-32`, `CordLayer.cs:13-77`, `DrawOrder.cs:19,59`). Linked into GSS and FlowWorks
  they become two distinct public types `RimMandrake.Shared.Slack.Cell` etc. The CLR tolerates it, but any by-name lookup
  (`AccessTools.TypeByName`, `GenTypes.GetTypeInAnyAssembly`, a bridge probe, a future `Class=` attribute) silently
  returns whichever assembly loaded first; and any public GSS API that exposes `Cell`/`V2` (e.g. GSS probes) keeps them
  public in GSS, so they cannot simply be flipped to `internal` without CS0050/CS0051 accessibility errors.
- **Fix.** Make the shared files `internal` (as the precedent) and, where a GSS public member exposes one of them, make
  that member internal too (count them in step 0); the SelfTests link source, so `internal` costs them nothing. State the
  rule in the file header: "never name these types by string". Add a step-1 gate: `grep -n "public " _Shared/SlackGeometry` == 0.

### M6. The draw-order "shared contract" depends on a GSS runtime value FlowWorks cannot see
- **Evidence.** `DrawOrder.HoseQueue(strandQueue)` takes `CordMaterials.StrandQueue` (`Core/DrawOrder.cs:48-52`), which GSS
  computes at runtime from its own `Strand_Jawa` texture's material (`CordMaterials.cs:58-71`) and is used by the hose at
  `RM_MapComponent_Hoses.cs` (`CordMaterials.StrandQueue`). §7 says "both mods compile the same constants, so the stacking
  holds" — the input is not a constant and lives in GSS's `CordMaterials`, which does not move.
- **Fix.** FlowWorks derives `strandQueue` exactly as GSS does but without GSS's texture: `ShaderDatabase.Transparent`'s
  render queue (what the `Strand_Jawa` material resolves to; fallback 3000). Move that one derivation into
  `_Shared/SlackGeometry/DrawOrder.cs` as `BaseStrandQueue(Shader)` and have GSS call it too, so the two cannot drift. Keep
  the live cross-mod RL9 row.

### M7. The link index goes stale: `layKey` does not change when the thing at either end is built or removed
- **Evidence.** §4.1 maintains `RM_HoseLinks` "at the same moments that already bump `layKey`"
  (`RM_MapComponent_Hoses.cs:193`). That key is reel position, end cell, relay, trail and shape fingerprint; it carries
  **no port identity**. Deconstruct the tank at the far end, or build one there, and the key is unchanged, so the index
  keeps crediting/conducting into a destroyed tank (or ignores a new one). The code already has the right freshness
  rule: reel-side `CompHoseReel.Port()` re-reads every ≤60 ticks and at once when the cached port is no longer `Spawned`
  (`CompHoseReel.cs:82-89`); the far end is `HoseEnds.Read` (`HoseEnds.cs:36-49`), cached 60 ticks by the map component.
- **Fix.** Build link edges from those two cached reads, not a lay-time snapshot. The index stores reel refs keyed by
  port thing and resolves `Port()` / free end lazily, dropping any port with `!Spawned`. Selftest: "tank removed at far
  end → next BFS finds nothing; tank rebuilt → found within 60 ticks".

### M8. The type alias must land in the SAME commit as the move (steps 2 and 3 cannot be separate)
- **Evidence.** §10 says each step "leaves both mods loading clean", but step 2 moves the job drivers to
  `RimMandrake.FlowWorks.Hose.*` and step 3 adds the alias. A save with a colonist mid-carry/mid-wind fails `curDriver`
  resolution in between: Scribe resolves `Class=` via `BackCompatibility.GetBackCompatibleType` →
  `GenTypes.GetTypeInAnyAssembly` (RimSage, `Verse/BackCompatibility.cs:166-192`, `Verse/GenTypes.cs:272-290`), then
  `Pawn_JobTracker.ExposeData` ends the job (RimSage, `Verse/AI/Pawn_JobTracker.cs:90-110`). That engine line is
  `Log.Warning("Cleaning up invalid job state…")`, not a red error as §6 says; the red line is Scribe's own
  could-not-find-class before it. The step-8 proof must look for both.
- **Fix.** Fold the type alias (6.1) into step 2. Settings import and `loadAfter` can stay in step 3.

### M9. The settings import reads only one of the files a player can have, and its key count is wrong
- **Evidence.** Verse names the file `Mod_<deployed folder>_<Mod class>.xml` (`Core/LegacyName.cs:9-11`); GSS migrates by
  `content.FolderName` (`GimmeSomeSlackMod.cs:447`). §6.3 hard-codes `Mod_GimmeSomeSlack_FireHosesMod.xml`. A Workshop
  install's folder is the Workshop id; a player who never ran GSS after the Messy Conduit rename has only
  `Mod_MessyConduit_FireHosesMod.xml`, and with GSS absent nothing migrates it first. `HoseSettings.ExposeData` writes
  **17** keys (`Hose/HoseSettings.cs:54-75`), so 15 survive (14 user-facing + internal `maxLengthDefaults`), not
  "16 fields / 14 keys".
- **Fix.** Import from any `Mod_*_FireHosesMod.xml` in `GenFilePaths.ConfigFolderPath` (prefer the one whose folder is
  GSS's `content.FolderName` when GSS is loaded, else newest mtime); read keys by name, ignore the `Class=` value. Fixture
  tests for all three file names.

## Should-fix

- **S1 (medium) — `RM_LiquidHose` IS the liquids framework's `RM_HoseSpool`, the tanker raid's portable hose.**
  `FlowWorks/Defs/Machinery/RM_LiquidLogistics.xml:4-6`; `design/RimMandrake/liquids_framework_design.md:177-181`
  ("deploy `RM_HoseSpool` (fast-build, cheap, fragile … with a length cap) from shore to ship tank"). The portable,
  length-capped, deploy-and-wind-back object in that pillar is what the *reel* is. §3 says deleting `RM_LiquidHose` loses
  "the static half of the tanker pillar"; the pillar has no static half. Fix: v2 states the lineage (reel = the pillar's
  spool; universal pipe = the owner's 10-04 static pipe), retunes the pipe's provisional fragile stats (30 HP, 1 steel)
  for a permanent pipe, puts this in the Q1 text, and promotes Q3 (nozzle in liquid) to the pillar's missing half.
- **S2 (medium) — FlowWorks applies Harmony through `PatchApplier`, which requires each patch to gate on a feature
  setting.** `FlowWorks/Source/RM_Patch_SuperdeepShooting.cs:27-36`; `_Shared/HarmonyResilience/PatchApplier.cs:16-18`
  ("every patch must gate on its setting"). The moved patches (save-skip, type alias, style patches) were written for
  GSS's PatchAll. Fix: style patches get a `[PatchFeature]` on `hose_enabled`; the save-skip and type-alias patches must
  never switch off (a failed save-skip writes the component into saves), so they are named in the step-2 gate and a
  failure logs red.
- **S3 (medium) — mixed versions are not fixed by `loadAfter`.** Cross-mod duplicate defNames are replaced **silently**
  (RimSage, `Verse/DefDatabase.cs:22-60`: only an intra-mod duplicate logs), so §6.5's "config error" is false and the
  failure is invisible. An old GSS also keeps its own `CompHoseReel` type, map component, `StylePicker` registration of
  `RM_HoseReel` and save-skip patch. Fix: FlowWorks checks at startup for type
  `RimMandrake.GimmeSomeSlack.Hose.CompHoseReel` and logs one red line "Gimme Some Slack is older than this FlowWorks;
  update both"; step 2's gate includes the defName-in-both-mods script check.
- **S4 (medium) — net-cache invalidation by a spawn/despawn counter needs hooks on vanilla `Building`.** Pipe and reel use
  `thingClass` `Building` (`RM_LiquidLogistics.xml:20`; `RM_Hoses.xml`), so "bumped by those things' SpawnSetup/DeSpawn"
  means a Harmony patch on every building spawn. Fix: drop the counter; a cache keyed on `TicksGame` cannot outlive its
  tick. Cache only topology (tanks, routes), never `CanAccept` — the pump's draw loop calls `TankToFill` per level and
  tanks fill within that loop (`Building_LiquidPump.cs`, draw branch).
- **S5 (low) — `RM_Liquid_Water` does not exist.** The registry has `RM_Liquid_FreshWater`
  (`FlowWorks/Defs/LiquidTypes/LiquidDefs/RM_LiquidDefRegistry.xml:27`); GSS's stub was `RM_Fluid_Water`
  (`HoseSettings.cs:49`). Fix: debug tint uses `RM_Liquid_FreshWater` via DefOf, null-safe.
- **S6 (low) — "exactly 5 per pump cycle" holds only for `levelsPerCycle` 1.** Stations run 2 and 4
  (`RM_PumpingStation.xml:91,132`). Fix: "exactly `levelsPerCycle × 5`", stated for the plain pump.
- **S7 (low) — a bath's cadence is undefined.** Converter, adapter, reaction run on `CompTickRare` (250), the pump on
  `IsHashIntervalTick(250)`; the bath draws per craft (`Kits/RM_LiquidBath.cs:94`). Fix: `Credit` takes the caller's
  cadence; the bath passes `releaseTicks`, so a craft gives one plump pulse, not a flicker.
- **S8 (low) — two liquids through one hose thrash the tint.** `lastLiquid` = last credit wins. Fix: the tint switches
  only after a new liquid has been credited continuously for `minPlumpDwell`.
- **S9 (low) — one route per tank.** The BFS parent chain credits only the first-found route; a parallel hose stays flat.
  Fix: state it as intended and pin it with a selftest.
- **S10 (medium) — proof manifest and modcheck wiring are missing from the move list.** `proof_all.py:61-101`
  `DECLARED_ROWS` is read by `modcheck/required_checks.py declared_rows()` via the walk's `checkout:` header. Moving five
  blocks to `proof_hose.py` needs the FlowWorks walk's `checkout:` to name it and `DECLARED_ROWS` split. Also census the
  `matrix` block for hose scenes (the 10-09 "H0 hose matrix" run); and `SL2_save_names_no_class_of_ours` must allow the
  FlowWorks job-driver prefix in a mid-carry save.
- **S11 (low) — hand counts.** `human_review.py` has 182 hose/reel mentions and `save_review_map.py` 0 (§5.7: "162").
  Step 0's census replaces all such figures; v2 drops the hand counts.
- **S12 (low) — `HosePortKind` ordering.** The enum is `{ Pipe, Tank, Other, None }` (`HoseMath.cs:1389`) and
  `ClassifyComp` keeps the lowest (`HosePorts.cs:60`). Insert `Machine` before `None` and pin ranks in a selftest; a reel
  stays `None`.

## Verified claims

- Line counts: `Hose/*.cs` 5,088; CompHoseReel 720; RM_MapComponent_Hoses 1,110; HoseMath 1,517.
- Scribe keys `rmHose*` at `CompHoseReel.cs:131-155`, all Values/Collections(Value)/References: no class names written.
- Save-skip patch `RM_MapComponent_Hoses.cs:1036-1065`; H10b `validation_hose.py:440-444`; `HPROBE` `:51`.
- `curDriver` is `Scribe_Deep` (RimSage `Pawn_JobTracker.cs:90-110`); Class resolution ends in
  `GenTypes.GetTypeInAnyAssembly` and a prefix runs before its cache, so the alias pattern is valid.
- GSS's prefix rewrites `ref typeName` (`GimmeSomeSlackMod.cs:456-465`), so the two prefixes commute as §6.1 claims.
- `BackCompatibleDefName` returns early when the save matches the environment (RimSage `BackCompatibility.cs:117-148`), so
  the `RM_DefAliases.cs` postfix pattern is the right tool.
- `RM_LiquidNet`: BFS, no cache, cap 1,500, cardinal (`RM_LiquidNet.cs:21-113`).
- Pump: only `int Moved` (saved `RM_pumpMoved`), 250-tick cycle, `TankToFill` per reach cell per level.
- Signal every tick per laid reel (`RM_MapComponent_Hoses.cs:261-275`); reflection 8-way walk (`HoseFlow.cs:54-89`);
  pulse-based window (`:42-52`) vs fixed 250 cycle: the latent flicker bug is real.
- Both walks `state: DRAFT` (`GimmeSomeSlack.md:38`, `FlowWorks.md:33`).
- Reel tab `Misc` (`RM_Hoses.xml:25`); every FlowWorks machine `Production`.
- Art is paused (`Transient/unworked_items_2026-10-10.md:43`).
- UNMEASURED here: SelfTest counts 836/96/129 (not re-run).

## Owner questions assessment

1. **Universal pipe**: sound, but the card must carry S1 (`RM_LiquidHose` was built as the raid's spool hose; the reel
   takes that role). Not previously ruled: the 10-04 notes ask for "universal pipes" but never name `RM_LiquidHose`;
   `HOSE_REEL_WIRE_TWO_HOSES_NO_WATER` planned "owner card first". Keep.
2. **Off = carry nothing**: sound and matches "all-off degrades gracefully". The card should add that reel-plumbed
   liquid stops moving while it is off. Keep.
3. **Nozzle in liquid**: understated. `HoseEndKind.Water` already exists ("intake in <water>", `HoseEnds.cs:30-46`), so
   the hose already *shows* an intake that does nothing. Recommend it as the last step of this item, not a separate
   filing: it is the tanker pillar's core verb (S1). Keep as a question.
4. **Art relocation / default look**: (a) real (art paused); a byte-identical move is a fair "yes"; art-ledger records
   re-pointed through the ledger tool. (b) sound.
5. **Build tab**: not an owner-level question; every FlowWorks machine is `Production`. Default it in the card.
6. **Direction**: sound, low value; default "not now" in the card.
