# JUDGE: fw-drain-two-stray-reds

Scope: I judged only `STATEMENT.md` and `NOTES.md` against the raw files in `evidence/` and the current source under `src/RimMandrake/FlowWorks/Source/`. I did not read DONE/BROADEN/FINDINGS/PROMPT, the broaden_* or judge_* evidence, or any builder conclusions. I used no shell and made no edits apart from this file.

`NOTES.md` contains only the heading `# Owner rulings` and no rulings, so no owner decision limits or changes anything below.

## What the raw evidence shows

- **Run identity.** `selftest_receipt.json` ran `run_selftests.py --only src/RimMandrake/Utils/selftest_flowworks_stock.py` with `tested_HEAD` 14b5a573…, and got `returncode: 1`. `BUILD_SOURCE.json` shows a staged build from 14b5a573 with a clean tree (`dirty_n: 0`) at both start and end. `stage_source_identity.json` checked 497 source files in the stage against the clone and found no mismatches. `stage_artifacts.json` records the SelfTest dll/exe hashes, and every compiled source listed has `clone_sha256 == stage_sha256`. `integrity_before.json` hashes the same HEAD. Artifact identity and provenance for this run are adequately tied to 14b5a573.
- **Raw suite result.** `csharp_stdout.txt:1474` reads **`1233/1238 passed`**. It ends with `FAILING CHECKS (rc 1)` and five FAILs:
  - `RiverSwitchFlip_weirWhiteWater` (l.292)
  - `PitCapture_follows_a_held_pawn_that_moves` (l.403)
  - `PipePole_P3_sag_at_the_slider_extremes` (l.1130)
  - `LW1 … TakeLayWorld …` (l.1204)
  - `Thirst_small_pond_drink_admitted` (l.1275)

  `selftest_stdout.txt` agrees: `FAIL 1/1 … RESULT: RED`. The strace capture (`selftest_output_writes.strace`) contains the same `1233/1238` text, and `output_extraction.json` ties the decoded stdout to the wrapper PID.
- **Named tests.** `csharp_stdout.txt:523` reads `ok    Pond_capacity_dug_out_and_back_in_any_order`. `csharp_stdout.txt:771` reads `ok    PipeTankRiser_wiring_link_stops_layer_prints_flange_follows`.
- **Repair provenance.** `git_provenance.json`:
  - Commit 4e9da327 ("stock selftest green again (1190/1190)") changes only two test files, `DeepBedChecks.cs` and `ReelRiserShadowChecks.cs`. It is an ancestor of HEAD and of the local `origin/main` ref, which also points at 14b5a573.
  - There is no diff in those two files between 4e9da327 and HEAD.
  - `production_history.json` shows the production changes that made the old assertions stale, and both are ancestors of 4e9da327:
    - 0aaff523 added `ReleaseRect`, a third `body.capacity = RM_BedMath.CapacityForBeds(unit, BedSum(body, owner));` site.
    - feb753b9 moved the riser strip into the shared `PrintStrip(layer, sm, path, y)`.
- **Cache.** `cache_record_refusal.json` and selftest_stdout line 5 show the result was not recordable, because of a clock read, external `/mnt/c` paths and changes under `__pycache__`. Nothing was answered from a cache: 0 CACHED PASS, and the test ran.

## Statement bullets

### Bullet 1: Pond_capacity passes, keeps the unit×beds sequence, and checks all current sizing sites

**Partly true. "Checks all current sizing sites" is overstated.**

- **Pass and sequence.** The test passes (l.523). `DeepBedChecks.cs:383-389` still asserts the 6 → 4 → 0 → 2 → 6 sequence through `RM_BedMath.CapacityForBeds`. `RM_BedMath.cs` is compiled into the test project (csproj l.47).
- **The count change is not a weakening.** The assertion moved from `Count == 2` to `Count == 3` (`DeepBedChecks.cs:392`). That matches exactly the three current production sites in `RM_LiquidStock.cs`: 455 (Detach), 497 (ReleaseRect) and 524 (Reattach). Both the exact pattern and the exact count are still enforced.
- **Limits of the guard:**
  - It counts regex matches across the whole file. It cannot tell *which* function holds each line, so losing Detach's line while adding a duplicate somewhere else would still pass.
  - It does not check every site that writes capacity. Formation (`RM_LiquidStock.cs:242`, `CapacityOf`) and the two migrations (376, 404, `CapacityOf`) are not checked by this test. Formation is only covered indirectly, through the `levelUnit` line at 243. The truncated-far-square `+=` site (196) is checked by the `Has` at `DeepBedChecks.cs:396`.
  - So the test covers the unit×beds **re-sizing** sites, not "all current sizing sites".
  - ReleaseRect is described as dev-fixture only (commit 0aaff523 message). Counting it is appropriate.

### Bullet 2: PipeTankRiser passes and keeps the westward rim check at the shared strip

**True, with a limit.**

- The test passes (l.771). `ReelRiserShadowChecks.cs:265-267` asserts both of these strings:
  - `return PrintStrip(this, sm, plan.Path, yTile + 0.001f);`
  - `if (LiquidJoinRule.TravelsWest(path)) { float sw = vr; vr = vl; vl = sw; }`
- Both exist in current production at `RM_LiquidJoins.cs:528` and `:540`. Line 540 is inside `PrintStrip`, at 534-554. The swap comes before the UV writes at 545-548, so the original intent (a west-going strip swaps its rims) is kept and follows the moved code.
- **Limits:**
  - This is a source-text guard only. `RM_LiquidJoins.cs` is not compiled into the SelfTest csproj; only `LiquidJoinRule.cs` is, at l.198.
  - The two `Contains` checks are independent. Nothing asserts that the swap sits inside `PrintStrip`, that it comes before the quad loop, or that `vr`/`vl` feed the UVs.
  - No rendered geometry is exercised.
  - The machine-drop caller (`RM_LiquidJoins.cs:434`) also gets the swap through `PrintStrip`, but the test does not assert that.

### Bullet 3: the current production-linked suite is green, the evidence identifies the repair, and it separates stale assertions from a production defect

**False.**

- **Not green.** The raw result is `1233/1238 passed`, rc 1, `RESULT: RED`, with five failing checks other than the two named ones (listed above). No evidence and no owner ruling in NOTES.md excuses them.
- **Repair identified.** This part is supported: 4e9da327 is the test-only repair, it is unchanged at HEAD, and it is an ancestor of the local `origin/main`.
- **Stale assertions vs. a defect.** For these two tests the evidence does support "stale assertions, not a production defect". Production commits 0aaff523 and feb753b9 moved or added the code, and the repair re-pointed the assertions at the new code without loosening them. But that does not make the suite green.

## Defects

1. Bullet 3 claims a green suite. The raw output shows 5 failures out of 1238 (`csharp_stdout.txt:1474`, `:1515-1524`; `selftest_stdout.txt:54-56`).
2. Bullet 1's "all current sizing sites" overstates what the test covers. Formation (`RM_LiquidStock.cs:242`) and the migrations (376, 404) are unchecked, and the count guard is not tied to particular functions.
3. Bullet 2 rests on substring checks against an uncompiled production file. It proves the text is present, not where it is placed or how it renders.

## Uncertainty

- **"Published."** `git ls-remote origin refs/heads/main` returned b7d7d79a…, while the local `origin/main` is 14b5a573. The evidence shows 4e9da327 was published as of the last fetch. It does not directly show it is an ancestor of the remote's current main, though that is likely.
- **Unexplained "changed during the run".** The selftest is marked "not recordable: changed during the run: …/selftest_flowworks_stock.py" (`selftest_stdout.txt:5`). The cache refusal points to `__pycache__`, clock and external-path noise. Git status and stage identity both show a clean, matching tree, so I don't think this affects the result. I could not confirm that with hashes, because I had no shell.
- **Process samples only partly checked.** I confirmed that `process_samples.jsonl` contains SelfTest/wrapper-PID entries. I did not analyse them beyond that.

## Verdict

The pre-existing published repair (4e9da327) does fix the two reported stale failures, and it does so without weakening their intended checks. Both tests now pass on current source and still pin the same behaviour at the moved or added code. However, the statement as written claims a green suite, and the raw result is RED (1233/1238), with an overstated "all sizing sites" claim on top. The statement as a whole is not supported.

would show: no
