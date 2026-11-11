I've finished the review: the repair meets all three statement bullets with only bounded qualifications, so the unit can go to the parent for independent acceptance.

**Bullet 1: off then on cancels pending removal. Met.**
- **The fix:** `RM_MapComponent_SuspensionBridges.cs:1250-1260`. When the switch goes back on, `PlaceRailing` now deletes only the Deconstruct designation on each existing railing on the cell, then returns. Nothing is destroyed or rebuilt, so the railings keep their identities.
- **Raised leaves:** `:1230` now also calls `PlaceRailing` when a railing already stands (`RailedAt`), even if `DeckAt` finds no usable deck. That covers a raised leaf. An empty raised cell still gets neither test, so no new placement is enabled there.
- **Unchanged behaviour:** the missing-def early return, the blueprint/frame duplicate guard, material choice (`RailingStuffFor`), style, the god-mode spawn path and `RemoveRailing` all match the original word for word (original `:1216-1326`).
- **Proof hook:** `ProofRails` gains an explicit `;player` mode that turns god mode off for the call and restores it in `finally`. The old two-part form still uses god mode, and any other third part is refused.
- **Live run (`live_attempt2.json:9431-9669`):**
  - Player-mode off queued exactly four railing Deconstruct marks.
  - On, and a repeated on, cleared all four.
  - The four railing IDs (24594–24597), material (WoodLog) and hit points (26) were identical before and after.
  - Both control designations, a Plan on a bridge cell and a Deconstruct on a separate wall, were unchanged.
  - The game tick stayed at 3 throughout, and the state reader (`ProofSpan railings=`) agreed with the switch at every step.

**Bullet 2: regression checks, selftest and shipping build. Met.**
- **The checks run real production code.** At each build, the extraction task in `RailingToggleHarness.targets` copies ten complete methods (plus `ProofRails`) from the production files and compiles them against stand-ins for the game engine. Those stand-ins are not the real engine, which is a limit noted below.
- **Defect reproduced on the original code:** `fast_expanded_red` fails exactly the 5 cases that depend on the fix. The 3 cases for preserved behaviour still pass.
- **The checks catch wrong fixes.** I confirmed both deliberate mutations really appear in the generated code (`fast_*/RailingToggle.g.cs`):
  - A mutant that deletes every designation on the railing fails only the "preserve unrelated designation" case.
  - A mutant that clears only the first railing on a cell fails only the multiple-railings case.
- **The normal suite runs the new cases.** `Program.cs:2164` calls them and the csproj imports the targets. `csharp_stdout.txt:369-376` shows all 8 RailingToggle cases ok, with 1252/1252 and hose 457/457 overall, return code 0, and source/test hashes unchanged during the run.
- **Identities line up end to end:**
  - The suite's input hashes (`integrity_before.json`), the build's stamped inputs, the 8/8 broadened run and the 8/8 post-format run all use map `494f92…` and proofs `9c7830…`.
  - The loaded DLL reported `d70a84…`, which equals both the deployed DLL and the repository artifact. The `.srchash` stamp `56e531…` is the matching published pair.
- **Readability changes after the suite:** the Roslyn token comparison found identical tokens (3016 and 434), the project XML compares equal, and the Python AST matches the driver publication that ran live. The current formatted harness re-ran 8/8.
- **Refreshed parent check:** it rehashed 6014 inputs. The only changes since the suite are the formatted files plus the DLL and stamp, as expected.

**Bullet 3: disposable live check. Met.**
- **Setup:** a timestamped begin snapshot on the disposable calm site. The loaded DLL identity was checked before any action, and both preflights were GREEN.
- **Restore:** the rectangle hash went back to `275a5b…`, matching the before value exactly. All debug settings were restored, with god mode false.
- **Saves:** the hashes of all three named saves, including the canonical start and `RM_TestSite_calm_v3`, are unchanged (`save_hashes_after.json` matches `live_inputs_before.json`).
- **Attempt 1:** a genuine failure, retained as FAIL. The driver hit a KeyError before any toggle, and its rectangle and settings were restored. The only fix was `d.get('thing')` in the Python reader. The driver's success and failure paths now both pass offline checks with restoration.
- **Final state:** game DOWN with no process, bridge FREE and driver lock FREE (`game_after_judge_stdout.txt`, `bridge_after_judge_stdout.txt`).

**Blockers:** none.

**Limits** (none were measured, so none can be claimed as passing; the frozen bullets don't require them):
- Only paused, before-work cancellation was exercised (0 ticks). Pawns picking up the job, a deconstruction in progress or completed, and saving or reloading while off are all untested.
- The fix does not repair an old save that is already ON with leftover marks. Cancellation only happens on an off→on change, and `SetRailings` returns early when the switch already matches.
- The live check goes through `ProofRails` → `SetRailings`, not a click on the gizmo. The gizmo's toggle action is covered only by the offline checks against stand-ins.
- The live designation query shows the def and cell for each mark, not the railing's ID. Railing identity rests on the separate before/after railing list, which is consistent.
- The live run covered an ordinary lowered span only. The raised-leaf and multiple-railings-per-cell cases are proven offline only.
- Both screenshots are too zoomed out to show Deconstruct marks. They support only that the bridge looks the same before and after.
- Both attempts left timestamped `WHITTLE_RailingToggle_Begin_*` snapshot saves in the Saves folder. They are not canonical saves, but they were not cleaned up.
- The extraction task in `RailingToggleHarness.targets` finds method ends by counting braces, which would break if a brace appeared inside a string or comment. It's correct for the current methods.

would show: yes