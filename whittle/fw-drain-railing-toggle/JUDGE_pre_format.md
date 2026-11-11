The only changes are in `PlaceRailing` and `SetRailings`, and the evidence supports all three statement bullets. I found no blockers.

**Bullet 1: off then on, before deconstruction, cancels Deconstruct and keeps the railings**
Met.
- **Fix:** `RM_MapComponent_SuspensionBridges.cs:1250-1260` now deletes only the Deconstruct designation on each `Building_SuspensionRailing` in the cell, then returns without placing anything.
- **Raised leaves:** `SetRailings` at `:1230` now also visits cells that already have a railing (`RailedAt(...) || DeckAt(...)`). This reaches railings on raised leaves, which the walking-only `DeckAt` skips. An empty raised cell still fails both tests, so it gets no new railing or blueprint.
- **Live proof:** `evidence/live_attempt2.json` shows the real engine doing this on the deployed DLL.
  - Player-mode off queued exactly four railing Deconstructs (railing IDs 24594 to 24597).
  - On cleared all four and kept the same IDs, WoodLog material and 26 HP.
  - A repeated on was identical.
  - The Plan at 38,36 and the wall's Deconstruct at 48,40 were untouched.
  - The switch result (`RAILS on=`) and the state read (`SPAN railings=`) agreed every time.
  - All reads were at game tick 3, paused.
  - God mode stayed false after each toggle. The off step adding Deconstructs to the same IDs rules out the god-mode path, which would have destroyed them.

**Bullet 2: regression checks, preserved behaviour, suite and build**
Met.
- **Real production code:** `RailingToggleHarness.targets` copies 10 complete production methods plus the whole `ProofRails` method out of the source files at each build. The fakes are only engine stand-ins. Their `DeckAt` matches the real `Decked = !collapsed && Spawned && !Raised`.
- **Old source fails:** `fast_red` scored 4/6 and `fast_expanded_red` 3/8 against the original map. Both fail the identity, multiple-railing, raised-leaf and player-mode cases.
- **Mutants fail:** each negative control fails exactly its targeted case.
  - `fast_delete_all` breaks "preserve unrelated designation".
  - `fast_first_only` breaks "cancel all matched built railings".
- **Final probe:** `fast_broaden` passes 8/8. Its input hashes (494f92…, 9c7830…, 639fa8…, a7e3cd…) equal the suite's integrity manifest and `build_integrity.json`.
- **Covered cases:** blueprint/frame duplication, material/style/faction, missing def, placement refusal, god-mode vanish versus player cancel, the explicit `;player` mode, and the legacy god default. God mode is restored in a `finally` block.
- **Normal suite:** `Program.cs` registers the cases. `csharp_stdout.txt:369-376` shows all 8 `ok`, with 1252/1252 passed and a GREEN result.
- **Shipping build:** the build returned 0 with 0 errors and GSS was unchanged. The published DLL d70a84… and its `.srchash` 56e531… match the deployed copies (`verified_pair: true`) and the loaded identity's sha256.

**Bullet 3: disposable live check**
Met.
- **Disposable snapshot:** the run took a new begin snapshot and reloaded it before staging.
- **Restoration:** the restored rectangle sha 275a5b… equals the "before" value, and all 47 debug settings match exactly.
- **Saves untouched:** the canonical, current-world and calm-site save hashes match before and after (`match_before: true`).
- **Cleanup:** the after-judge and final reads both show the game DOWN, and the driver lock and bridge FREE. The post-acceptance Player log has only normal calm-site load messages.
- **Attempt 1:** it is kept as FAIL. The driver crashed with `KeyError('thing')` before any toggle, its restore was PASS with the same rectangle sha, and its shutdown and free receipts are kept. The only change was in the Python driver (`.get('thing')` and an off screenshot), published separately as 5ade0b…, which is the hash in the current manifests. The C# source, tests and DLL are the bytes the suite and build used.

**Significant limits (not claimed, and not required by the "before deconstruction" wording)**
- **Pawn work not tested:** no pawns ran, so nothing shows a pawn picking up or finishing the deconstruction, or a job in progress being interrupted. The same goes for save/reload while off.
- **Old stuck saves don't heal:** a save already ON with Deconstruct marks is not fixed automatically. `SetRailings` returns early when the switch already matches, so the player has to toggle off and on.
- **Raised and collapsed leaves are unit-tested only:** they ran in the build-time check, not live. Separately, a railing on a collapsed or missing deck now also has its Deconstruct cancelled. The old code skipped that cell. This fits "existing railings", but it is a small behaviour change.
- **Screenshots prove little:** they are zoomed out, so the Deconstruct marks aren't legible, and the tool reported them `verified: false`. They are supporting evidence only.

would show: yes