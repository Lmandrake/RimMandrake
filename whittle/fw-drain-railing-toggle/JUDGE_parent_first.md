**Railing toggle (whittle/fw-drain-railing-toggle): ready to show to the parent for acceptance.**

**Bullet 1: switching off then on before deconstruction cancels the Deconstruct and keeps the railings. Met.**
- **The fix.** `RM_MapComponent_SuspensionBridges.cs:1250-1261`: when a square already has a built railing, `PlaceRailing` now deletes only the Deconstruct designation on each `Building_SuspensionRailing` there, then returns. Nothing new is placed.
- **Raised leaves.** `SetRailings:1230` now also visits squares that already have a railing (`RailedAt || DeckAt`). Railings on a raised leaf are reached, but an empty raised or collapsed square still gets nothing new, because `DeckAt` excludes raised decks (`Building_SpanDeck.cs:27`).
- **Off is unchanged.** `RemoveRailing` is byte-identical to `original_RM_MapComponent_SuspensionBridges.cs:1305-1326`.
- **Callers.** There is no `ToggleRails`. The actual path is the deck gizmo (`Building_SuspensionDeck.cs:290,381`) → `RailingGizmo` → `SetRailings`.

**Bullet 2: regression checks, selftest and shipping build. Met.**
- **Real production code.** At build time, `RailingToggleHarness.targets` copies 10 complete production methods plus `ProofRails` into the test and compiles them against hand-written engine doubles. I checked that the doubles match production `DeckAt`/`StructuralDeckAt` semantics.
- **Defect reproduced.** On the original map code, `fast_expanded_red` fails 5 of 8, including identity, multiple railings, raised leaf and player mode.
- **Repair passes.** `fast_broaden` and `fast_parent_format` both pass 8/8.
- **The tests can catch bad repairs.** The two deliberately broken versions each fail one targeted case: `delete_all` (unrelated designation lost) and `first_only` (multiple railings on one square).
- **Behaviour preserved.** Blueprint/frame duplicates, material/style/faction, missing def, placement refusal, god mode and the legacy god-mode proof (with mode restored by try/finally) are all covered.
- **Suite run.** The suite registers the cases (`Program.cs:2164` plus the csproj import). The single authorized run passed: the 8 RailingToggle cases ok, 1252/1252 main checks, hose 457/457.
- **Build and deploy chain.** The map/proofs hashes in `build_integrity.json` match `integrity_before`. The built DLL (`d70a84…`) matches `publication.json`, `deployed_dlls.json` and the DLL identity the game reported in live attempt 2. The `.srchash` pair matches too.

**Bullet 3: disposable live check. Met.**
- **Setup.** Live attempt 2 runs with god mode false. Four railings exist (IDs 24594–24597), plus a Plan marker at 38,36 and a Deconstruct on a Wall at 48,40.
- **Off.** `off;player` raises the designation total from 2 to 6: four railing Deconstructs plus the Plan and the Wall's.
- **On.** `on;player` brings the total back to 2, with only the Plan and the Wall's Deconstruct left. A repeated on gives the same result.
- **Railings and switch state.** The same IDs, stuff and HP remain throughout. `ProofSpan` reports `railings=False` after off and `True` after each on, matching the switch.
- **Restoration.** The run restores the rectangle hash and all debug settings from its snapshot (status PASS). Canonical, dev and test-site save hashes match their before values.
- **Final state.** The game is DOWN with no process, and the driver lock and bridge are both FREE. The Player log after acceptance has no exceptions.
- **Attempt 1.** It stopped on a KeyError in the Python state reader before any toggle. Its restore passed, and it stays recorded as FAIL.

**Parent formatting pass. The requirements still hold.**
- The C# harness and the code inside the `.targets` file have identical Roslyn tokens (3016 and 434).
- The `.targets` XML outside the embedded code differs only in its comment and layout; I checked this by hand.
- The project XML compares equal, and the driver's AST matches the published driver hash (`5ade0b9…`).
- After formatting, the 8 cases were re-run fresh (8/8), and the driver's success and intentional-failure controls both restore.
- The shipping C# and DLL are unchanged.

**Blockers:** none.

**Limits** (none of these is claimed, and the frozen bullets don't require them):
- Everything live was paused at ticks 3: no pawn did any work. There is no evidence for pawn scheduling after the cancel, a deconstruction already in progress or finished, or a save/reload while off.
- An old save that is already "on" with a leftover Deconstruct is not healed automatically. The fix only acts when someone toggles.
- Live called `SetRailings` through the `ProofRails` hook, not by clicking the gizmo. The gizmo's fixed-at-creation toggle and multi-select handling are covered only against the engine doubles.
- The live designation query reports cell and def name, not railing ID. The ID link comes from the separate railing list.
- Live ran the Windows mirror copy of the driver. It is linked to the published version by its behaviour (no KeyError, the new off screenshot), not by a hash of the file that actually ran.
- The suite runner marked the result "not recordable", saying the test file changed during the run. The receipt's hashes are unchanged, so this looks like a timestamp heuristic, but it means no ledger PASS was recorded.
- Both disposable snapshots (`WHITTLE_RailingToggle_Begin_*.rws`, one per attempt) are still in the user's Saves folder.

would show: yes