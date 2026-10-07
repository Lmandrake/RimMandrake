# Gimme Some Slack: GPT source read, checked against the code (2026-10-06)

The prompt is `gss_gpt_source_read_prompt_2026-10-06.md`. The model was `gpt_consult.py -m gpt-6.1-sol --effort high`.
The 52 production files (probes and selftests left out) were sent in two halves:
- **A**: core, cords and aerial, 35 files, 554 k chars. Answer: `gss_gpt_source_read_A_2026-10-06.md`, 20 findings.
- **B**: hose plus the core it uses, 22 files. Answer: `gss_gpt_source_read_B_2026-10-06.md`, 15 findings.

Both halves ran at the same time. B took about 7 minutes of wall time and A about 10. Every finding below was checked against the
source by reading it. Findings marked **REPRODUCED** were also re-run offline in `SelfTest/GssFuzz.cs`.

Verdicts:
- **CONFIRMED**: the code does what GPT says.
- **CONFIRMED (code)**: the code path is as described, but the effect on a player has not been measured.
- **PLAUSIBLE**: depends on engine or render behaviour that this read did not check.

## Ranked by player impact

| # | finding | verdict | evidence |
|---|---|---|---|
| B4 | **The reel's port cache never initializes.** `portTick = int.MinValue`. `now - portTick` overflows to a negative number, which is `< 60`, so `Port()` returns null and never calls `HosePorts.Find`. Reels read "Not connected" and the inlet feed is never drawn. | **CONFIRMED** | `CompHoseReel.cs:60,85`. Only `HoseProbe` calls `Port(true)`. Every live check ran the probe census first, which hid this. |
| B5 | **Outlet blend causes the tight bends** (the 9 live MX_H FAILs). `StraightenStart`→`StraightenEnd` interpolates *positions* after `Stiffen`, with no curvature bound. | **CONFIRMED, REPRODUCED** | G2 locator: 951 of 965 tight bends lie inside the blend. The same seeds laid without the outlet bend fine in 964 of 965. Failing turn median is 133° (passing 36°). Radius ≤ blend/turn in 965 of 965. |
| B3 | **A laid hose can exceed the hose's length.** `CheckInstall` does not count the outlet lead. `LayOn` only caps the *extra* slack. | **CONFIRMED, REPRODUCED** | Fuzz G1: 40 of 1445 outlet lays. |
| B2 | **Cost-first route search refuses a route that fits.** `RouteCells` minimises step + ExtraCost (water 3/cell). `CheckInstall` judges the result by length. | **CONFIRMED, REPRODUCED** | New G6 probe: a dog-legged water corridor needs 37.4 of a 40-cell hose. The search returns a 59.0 dry detour and the result is "route too long". |
| A19 | **Unpowered power strips draw twice as tall.** `PowerStripDark` uses aspect 1, but its texture is 64×32 like `PowerStrip` (0.5). | **CONFIRMED** | `SectionLayer_RM_MessyCords.cs:163`. Measured both PNGs at 64×32. |
| B1 | **Hose validation and relay flow only run once the hose has been drawn.** `EnsureLay` is called only from `DrawAll` (current map). The 250-tick corridor check needs `layKey != null`. Relay flow needs `f.lay != null`. | **CONFIRMED** | `RM_MapComponent_Hoses.cs:259,324,367`, `HoseFlow.cs:111`. A hose on a map nobody is viewing never retracts. |
| A1 | **Several taps can claim the same surplus.** Each tap reads the victim's gain with *all* tap debits bypassed. | **CONFIRMED (code)** | `CompPowerTap.CompTick` (`bypass++` around the gain read). |
| A2 | **A tap that is switched off or broken still drains the victim.** The debit runs before the flick/breakdown checks and ignores them. | **CONFIRMED** | `CompPowerTap.cs` CompTick: `Debit` runs unconditionally, and `PowerOn` only gates output. |
| B8 | **Changing the hose-length setting does not re-lay existing hoses.** `MaxLength` is missing from `ShapeFingerprint` and from the lay key. | **CONFIRMED** | `HoseSettings.cs:112`, `EnsureLay` key. |
| B11 | **`autoResumeDroppedHose=false` gates only an interrupted Deploy.** An interrupted Move or Retract still resumes. | **CONFIRMED** | `WorkGiver_HoseOrders.cs:71`. |
| B12 | **A refused right-click leaves a live order.** `order(t.Cell)` sets `pending` before `JobFor` can fail, so the "Cannot carry the hose" message hides an order that stays queued. | **CONFIRMED** | `FloatMenuOptionProvider_Hose.TargetThen`. |
| B13 | **A path failure before the grab leaves the order dangling.** `OnFinish` returns early unless the pawn already carries. | **CONFIRMED** | `JobDriver_CarryHoseEnd.cs:152`. |
| B10 | **Two pending orders can form a relay loop.** `Loops` follows only hoses that are already laid. | **CONFIRMED (code)** | `RM_MapComponent_Hoses.Loops` uses `RelayOf` (laid). |
| B7 / A13 | **Tree cost is not in the corridor hash.** This applies to both hoses and cords. A cut tree leaves the old route standing until reload. | **CONFIRMED** | `CorridorHash` hashes walkable+door only. `ExtraCost` 1.5 for trees, 3 for water. |
| B9 | **No cord is drawn for a device wired straight to a battery or other transmitter building.** The adapter skips any connector whose parent is not a conduit target. | **CONFIRMED** | `CordWorldAdapter.cs` connector loop: `!ConduitVisuals.IsTarget(parent.parent.def) → continue`. |
| B6 | **The final outlet or end straightening is not re-checked for wall clearance.** After a failed broad blend, `bl = 0.5` is applied without a `Clear`. | **CONFIRMED (code)** | `HoseMath.LayOn` 334-339. Never observed offline: the fuzz asserts `Clear(Flat/Plump)` on every lay and passed 0 failures. |
| A17 | **Wall brackets never get their wall endpoint.** `SetWallHome` is called only in the connector loop, not the transmitter loop. | **CONFIRMED (code)** | `CordWorldAdapter.cs:94` is the only call. |
| A15 | **Restyling a run crosses a cut span.** `Neighbours` walks every link, including `SpanState.Cut`. | **CONFIRMED** | `RM_MapComponent_ConduitRuns.cs:88`. |
| A6 | **An auto-link queued while paused is lost on save.** `pendingAuto` is not saved, and `respawningAfterLoad` skips the requeue. | **CONFIRMED** | `CompAerialAnchor.cs:178`, `RM_MapComponent_Aerial.cs:26`. |
| A8 | **Fallen-wire lays are cached until `DirtyCell`.** Building a wall across a fallen wire does not clear the cache. | **CONFIRMED (code)** | `lays.Clear()` happens only in `DirtyCell`. |
| A18 | **Span meshes leak.** `Notify_SpansChanged` and `Notify_SettingsChanged` clear `meshes` without `Object.Destroy`. | **CONFIRMED** | `RM_MapComponent_Aerial.cs:52,56`. Drops and fallen wires are destroyed correctly. |
| A7 | **Unroutable cords are still drawn.** `Unroutable` is recorded, and only the probe reads it. | **CONFIRMED (code)** | Grep: no renderer reads `Unroutable`. Live M2b counts unwalkable vertices (it was green at 143/144). |
| A3 | **Unseeded `Rand` in the style getter (preview) and in per-frame sparks.** | **CONFIRMED (code)** | `ConduitStylePicker.cs:159` (`Resolve`), `RM_MapComponent_CordGraph.cs:607-612`. This is a determinism and multiplayer risk, not something a single player sees. |
| A4 | **"Auto-link selected" will string enemy anchors.** It has no player-faction filter, and `CanLink` only requires the two anchors to share a faction. | **CONFIRMED (code)** | `AutoLinkSelected`. Low impact. |
| A5 | **The link targeter can link to a source destroyed mid-targeting.** Neither `Verdict` nor `TryLink` checks Spawned. | **CONFIRMED (code)** | Low impact. |
| A10 | **Whip tails beyond `maxSparkingEnds*3` are drawn neither static nor dynamic.** | **CONFIRMED (code)** | `RM_MapComponent_CordGraph.cs:480` cap, `SectionLayer:133-158` drop. |
| A20 | **"Match its cable run" gives no feedback on an unhooked lamp.** It sets `lastMessage` and returns before any message is shown. | **CONFIRMED** | `RM_MapComponent_ConduitRuns.RestyleLamp:202`. |
| A12 / B15 | **`sprawlCap` does not cap cord length.** | **CONFIRMED** | Already recorded as a design question in `gss_offline_fuzz_B.md` (seed 141). |
| B14 | **Port choice depends on list order on a tie.** `Pick` uses a strict `<`, and `FindAt` returns the first eligible thing. | **CONFIRMED (code)** | Needs two candidates on one contact cell. Low impact. |
| A9 | Roof changes can leave a strand double-drawn or missing (`Sig` has no static/dynamic split). | PLAUSIBLE | Render path. Not measured. |
| A11 | A long rippling cord disappears when its midpoint is off screen. | PLAUSIBLE | Default `floorRipple=false`. |
| A14 | The once-per-frame latch can swallow a second change in the same frame. | PLAUSIBLE | Needs two changes in one frame. GPT itself rates it medium. |
| A16 | Grouped Link/Unlink/Restyle gizmos run once per selected object. | PLAUSIBLE | Depends on how vanilla merges grouped gizmos. The live runner's `ui` scene covers the Auto-link case only. |

**Totals: 35 findings. 31 are confirmed (two rows each merge one A and one B finding), and 5 of those were also
reproduced or measured offline. 4 are plausible. None was refuted.** The 4 plausible render items are left for the
looks board (`gss_states`) to show.

## Status after the fix pass (2026-10-06)

**Fixed** (offline checks: `SelfTest/GptReadFixChecks.cs`, the fuzz in `SelfTest/GssFuzz.cs`, and `validation.py` row
`O7_gpt_read_fixes` for the Verse-bound halves): B1, B2, B3, B4, B5 (owner decision by question card: straight lead-out, see
`gss_offline_fuzz_B.md`), B6 (the unchecked 0.5 blend is gone; the lead-out is wall-checked), B7/A13, B8, B10, B11, B12, B13,
B14, A1, A2, A4, A5, A6, A8, A10, A15, A17, A18, A19, A20. None of these has been run live yet.

**Not changed, and why:**
- B9: a device wired to a battery or switch gets a drawn cable. The B24 hookup patch prints it as the look's straight cable,
  not as a messy cord. Whether it should be a messy cord is a design call.
- A12/B15 (`sprawlCap` does not cap cord length): an open design question in `gss_offline_fuzz_B.md`.
- A7 (unroutable cords still drawn): hiding them would show a powered conduit run with a gap in it. What to draw instead is a
  design call.
- A3 (unseeded `Rand` in the style preview and in the sparks): the preview picks a random colour by design. The sparks are
  cosmetic flecks, which vanilla also throws with `Rand`. This only matters for multiplayer sync, which this pass did not cover.
- A16 (grouped gizmos): checked against the decompiled 1.6 `GizmoGridDrawer`. Each grouped `Command_Action` does run once per
  selected object. Auto-link already guards against that with a per-frame latch. For the targeter and float-menu gizmos, each
  later run replaces the earlier one, so the player sees one menu. Not a defect.
- A14 (the per-frame latch could swallow a second change in the same frame): a player cannot click two gizmos in one frame.
  Not reachable.
- A9 and A11 (render paths, and `floorRipple` is off by default): still unverified. They are left for the looks board.

## What the read did not cover

- Multiplayer sync registration was not in the files sent.
- Whether vanilla Scribe writes a C# job-driver class name of ours into saves was not checked. The live `SL2` row checks
  save names.
- Half B could not see the cord drawer, and half A could not see the hoses. Each said so rather than guessing.
