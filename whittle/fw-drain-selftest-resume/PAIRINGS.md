# Guard diagnoses and repairs

All paths below start at `src/RimMandrake/`. The only source edits are five files in `FlowWorks/Source/SelfTest`. Existing method extraction comes from DrawbridgeChecks.Body, with ThirstChecks.MethodStatements retained for raw statement parsing.

## Original published repair

Commit `4e9da327df7ba0a60b50837e200efb711fcbfef1` repaired the two originally named stale tests. DeepBedChecks retains production-compiled capacity arithmetic for 6 → 4 → 0 → 2 → 6 and counts THREE copies of the unit-times-beds resizing assignment. At current source these are in DetachBedCell, ReleaseRect and ReattachBedCell. The count itself does not identify each method and does not cover every capacity assignment. ReelRiserShadowChecks follows PrintRiser's call to the shared PrintStrip and requires the west-going path's north/south rim swap there. Neither original test file was edited in this continuation. The raw original diff and ancestry check are preserved in `evidence/history.json`.

## Animated weir water

`FlowWorks/Source/SelfTest/RiverSwitchFlipChecks.cs` pairs with `FlowWorks/Source/Rivers/RM_Weir.cs` DrawAt. Commit `4a0f8616b724ae324ff45c336ac324b4ce92a366` introduced the animated crest sheet. DrawAt reads weirWhiteWater into animate, freezes the crest at frame zero when disabled and draws white water only while enabled. The former inline-condition spelling is stale. The replacement scopes DrawAt, requires that complete linkage and one call for each water layer, and rejects a forced-on local, unconditional white water, an unfrozen crest and a planted second unconditional draw.

## Capture-down pin

`FlowWorks/Source/SelfTest/RelativeRulesChecks.cs` pairs with `FlowWorks/Source/Superdeep/RM_PitRooms.cs`. Commit `6d07391d3b61d9c8aaf09b776434f957088f241d` replaced vanilla ForceWait on an upright victim because its Wait driver could auto-melee the warden at the lip. The dedicated pin retains the victim without that Wait behavior. CaptureDownNext math still distinguishes Hold, Repath and bounded GiveUp, while other existing per-toil tests require the repath sequence in reach and hold independently.

The repaired guard requires the dedicated Pin inside each Hold branch, for CaptureDownTicks + 30 on entry and ticksLeftThisToil + 30 on refresh. Deletions and a refresh moved to Repath fail. The helper must start the dedicated job with the requested expiry, avoid restarting an existing pin, stop movement and hold until capture ends. Mutations delete each lifetime condition or shorten the expiry. These source checks establish wiring and declared lifetime. Engine expiry, resumed-job behavior and successful prisoner capture remain outside this offline run.

## Pipe span sag

`FlowWorks/Source/SelfTest/PipePoleChecks.cs` pairs with `GimmeSomeSlack/Source/Aerial/AerialMath.cs` SpanCurve, Droop and SpanTs. Commit `b05e9ce45db8bacacfee59b6dd51ddbcc92d5449` landed the approved cord source with sin²(πt) droop and dense samples near the insulators. Both parabola and sin² have zero endpoint offsets and unit midpoint droop, but only the current curve has the flat end tangent that motivated the refactor. GSS AerialSelfTest.PipeKind already checks pipe-kind slider extremes through production SpanCurve. Its SittingChecks cover pole-top angle limits. Those GSS tests are read as supporting intent and are outside the authorized FlowWorks execution.

The FlowWorks local formula now mirrors sin² and retains slider clamps, zero/max/default sag, length scaling and fixed ends. A 101-point local sweep checks symmetry and bounds, and a near-end slope discriminates against the parabola. Method-scoped source checks connect that formula to production Droop and its caller and preserve the end-sample declaration and symmetric additions. In-memory mutations break formula, length scaling, endpoints, SpanTs use, end-sample values and quarter-span filtering. The old parabola is explicitly rejected. No GSS production or art bytes are edited. The local formula and source checks provide offline mathematical and wiring evidence. Rendered pixels and fresh GSS angle measurements are unmeasured here.

## Hose swim publication

`FlowWorks/Source/SelfTest/HoseMateEndQueueChecks.cs` pairs with `FlowWorks/Source/Hose/RM_MapComponent_Hoses.cs` SwimCellsPublished, MarkDirty and PatchWorld. Commit `377557044b915356e04fc4d55a7cca87fe1aa18f` made corridor invalidation event-driven. Commit `12c138bd76cede6362f237a1a855559af42ab3de` widened HoseWorldDirty to the whole map, removing the 16,384-cell overflow/rebuild branch that the guard expected. A swim publication touches every corridor cell even without a current snapshot, then marks each cell dirty when the snapshot is current.

The guard now scopes that ordering and rejects missing Touch or MarkDirty calls. It connects MarkDirty to the map-sized storage and PatchWorld to the production patch rule and the new serial for pooled lay copies. Existing HOSEPATCH_DIRTY_HOLDS_WHOLE_MAP_NO_OVERFLOW exercises 16,383 → 16,385 → 160,000 unique cells and drains bounded batches to a full-build oracle. HOSEPATCH_BOUNDED_BATCHES_EQUAL_FULL checks interleaved changes and convergence. LW1 also retains fresh/pooled/rebuilt content-hash equality, World version folds and lay snapshot wiring. Separate ReplayTick.CorridorMoved has a skipped-hash oracle using HoseCorridorVersions. This run does not directly execute that separate replay project or corridor-version math, and does not prove runtime event delivery.

## Small-pond drink admission

`FlowWorks/Source/SelfTest/ThirstChecks.cs` pairs with `FlowWorks/Source/Thirst/RM_ThirstUtility.cs` TryFindDrinkCell and its local Consider callback. Commit `8fb9f7f2b695ca818292ab843a277dbfefe4b2a4` added the far-water search and extracted the candidate walk into Consider. A rejected candidate now returns true, which continues either caller's walk. A successful terminal candidate or exhausted reach budget returns false to stop. The affordability gate precedes reachability and admission, so an unpaid candidate neither becomes the best cell nor consumes the 40-cell reach-failure allowance.

The existing 15-unit affordability boundary, whole-level refusal control, viscosity matrix, search/debit agreement and full CanDebitTerrain statement checks remain. The new gate check is scoped to Consider within the correct overload and pins both callers' continuation contract. Mutations remove refusal, stop the search prematurely, admit the cell first, invert callback continuation and move affordability after reachability. These controls retain rejection semantics while following the production callback extraction. Real map ordering and pawn jobs are outside this offline execution.

## Reference lookup recovered after the first run

The first changed-source run reported 1238/1238 main cases and 455/455 hose assertions, while the wrapper classified it UNMEASURED because Thirst_harmony_target_and_call_sites skipped its signature read at the retired hard-coded decompiled checkout path. Its full output and receipts remain at `evidence/`. That result is retained as an incomplete proof.

The same ThirstChecks file now accepts the repository's existing RIMWORLD_DECOMPILED environment convention, preserving its legacy lookup when unset and its explicit UNMEASURED path when the requested file is absent. The signature assertion is retained exactly. A fresh ILSpy read of the installed Assembly-CSharp.dll generated only Pawn_NeedsTracker into this clone's evidence/reference folder. The assembly, tool and output hashes and command are recorded in reference_provenance.json. Windows Python readback confirms the same bytes are reachable through the WSL UNC path. The next wrapper receives this root via WSLENV, and hashes the reference alongside the source and wrapper inputs. This repairs the reference dependency within this item.

The first stage audit included About/Preview.png in its all-files comparison and flagged that sole missing asset. The normal staging rsync excludes PNG assets. stage_identity.json retains that failed audit, and stage_identity_verified.json explicitly records the expected image exclusion and successful comparison of all stageable inputs. This changes the audit's expectation and preserves its first result.
