I'm a read-only judge here, so I made no writes and ran no commands. **Verdict: all three frozen bullets are met, with no blockers. The unit is ready for parent review.**

**The fix** (`Source/Pits/Suspension/RM_MapComponent_SuspensionBridges.cs:1230,1250-1261`, matching `evidence/tested_tracked.patch`):
- When railings are switched on, a square that already has a built railing now deletes only that railing's own Deconstruct designation, then returns. The railing object itself is kept.
- `SetRailings` now also visits squares that have a railing but no walkable deck (a raised leaf). Empty raised squares still get nothing new, since `DeckAt` excludes them.
- `RemoveRailing`, the duplicate check for pending blueprints/frames, material choice, the style/look and god-mode placement are byte-identical to the original.
- The `;player` option on `ProofRails` must be spelled exactly. Unknown words are refused, and god mode is restored in `try/finally`. The legacy two-part form still uses god mode.
- The reported `ToggleRails` doesn't exist; the actual caller is `RailingGizmo` → `SetRailings`.

**Bullet 1 — off then on before deconstruction cancels Deconstruct: met.**
- Offline: `RailingToggle_player_off_on_identity` toggles twice each way and checks that each of the 4 railings is marked once, then cleared with the same objects, wood and look. The railing's other designation and a Deconstruct on an outside railing survive, and no duplicate is built.
- Multiple railings on one square and a raised leaf are covered by their own cases.
- Live (`live_attempt2.json`), player off produced `on=False` with Deconstruct on exactly the 4 railings (IDs 24594–24597). On, and on again, produced `on=True` with 0 railing marks. IDs, WoodLog and HP 26 were unchanged, and the Plan at 38,36 and the wall Deconstruct at 48,40 were kept.
- `ProofSpan` agreed with the switch each time, god mode read false after each toggle, and every read was at tick 3.

**Bullet 2 — regression checks, selftest and shipping build: met.**
- **Real tests of whole methods:** `RailingToggleHarness.targets` copies the complete production methods out of source at each build, including `ProofRails`. The engine doubles stand in for the game; nothing copies the toggle logic.
- **Old source fails:** the original map failed 5 of 8 cases (`fast_expanded_red`).
- **Current source passes:** 8/8 (`fast_broaden`), with input hashes equal to current source.
- **Both mutants are caught:** "delete every designation on the railing" and "cancel only the first railing" each fail their intended case.
- **The normal suite runs them:** the cases are registered in `Program.cs:2164` and imported in the csproj. `csharp_stdout.txt` shows all 8 `ok` and 1252/1252 passed; `selftest_stdout.txt` is GREEN.
- **Build and identity chain:** `winbuild` succeeded with 0 warnings. The staged compile inputs match the tested hashes, and the DLL `d70a84da…` and `.srchash` `56e5…` match through build, publication and deployment. The in-game Identity call returned the same SHA. `gss_unchanged` is true.

**Bullet 3 — disposable live check: met.**
- A new snapshot was taken and reloaded. The rectangle hash `275a5b…` was restored exactly, and all debug settings were restored with god mode false.
- The canonical, dev-parity and calm-site save hashes all match the pre-run values (`save_hashes_after.json`).
- Cleanup: the game is DOWN, the driver lock and bridge are both FREE, and the game exited.
- Attempt 1 failed with KeyError before any toggle. It is kept as FAIL, and its own restore passed with the same rectangle hash.
- The Python-only republish (`16caafc`, driver sha `5ade0b…`) came after the suite, so the suite ran the earlier driver `a867e5…`. Only the driver changed: the C#, tests and DLL did not.
- The driver's canned success and failure paths both pass their restoration checks.

**Limits (not measured, so not counted as passing):**
- No pawn was allowed to work. A deconstruct job already claimed or in progress, a completed deconstruction, and a save/reload while railings are off are untested.
- An old save that is already stuck with the switch on and Deconstruct pending is not repaired automatically. Pressing "on" does nothing because the switch already reads on; the player has to switch off and back on.
- The raised-leaf case, a second designation on the same railing, and blueprint/frame/material/god-mode behavior are checked only against engine doubles, not in the live game.
- `ProofRails` treats any word other than `on` as off. That was already true before this change.
- With the railing definition missing, switching on leaves the Deconstruct in place, as the original code did.
- A railing on a collapsed deck now has its Deconstruct cancelled when switched on. That is slightly new, but only affects railings that already exist.
- The suite run is marked "not recordable" by the runner's results ledger, but the integrity manifests before and after are identical.
- The live receipt doesn't hash the driver file at run time. It ran after publication, and the DLL identity was checked inside the game.
- The off screenshot is too zoomed out to show the marks; the designation queries are the actual evidence.

The frozen bullets only require cancellation before work, so none of these limits block.

would show: yes