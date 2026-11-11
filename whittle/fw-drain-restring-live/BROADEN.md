# Independent broadening

The first fresh read-only call exceeded 600 seconds and produced no reply. Its raw files and timeout receipt are retained. A second fresh Opus call completed with no history, persistence, project settings or MCP, using Read/Glob/Grep only.

## Exact question

Fresh read-only Opus broadener. Do not drive the bridge or write files. Within 12 tool calls read these exact source regions under /home/mandrake/rm/scratch/BENCH/fw-drain and give a concise response. No history or previous verdicts.
1 whittle/fw-drain-restring-live/STATEMENT.md
2 whittle/fw-drain-restring-live/evidence/live_guard.py and PRELAUNCH.md
3 src/RimMandrake/GimmeSomeSlack/validation_aerial.py lines 180-365 (actual M15f), 600-657 (M15e), 1830-1875 (exit contract)
4 src/RimMandrake/Utils/mod_completion.py lines 321-346, 394-465, 696-719
We will run actual restring_style_proof.py launcher once prepared on guarded saved calm site/current GSS, requiring full driver exit0. Broadener task is missed test scenarios and false-pass/restoration assumptions, not acceptance judgment. Identify bounded observable checks for actual job and distinct-to-joined full style/power runs, complete saved-scene restoration, and actual A3 evidence discovery contract. Existing offline proof is already complete. Do not request unrelated kinetic integration, owner mod-list restoration or art changes. Return specific findings from these regions and up to six scenarios with expected outcomes. Finish with your concrete advice even if some source cannot be read.

## Exact reply

The regions don't show a false pass in the live M15f job/power/style path itself. The real gaps are in what exit 0 and the guard prove, and in how A3 is discovered.

**Can't read:** `restring_style_proof.py` was not in the regions you listed. So I can't tell whether it uses `--out` or writes to `northstar`, or whether it checks that the M15e/M15f rows exist. I used 9 of the 12 tool calls.

## Findings

**M15f (`validation_aerial.py:204-361`)**
- **The job is assigned by the probe.** M15f gets its worker from `restringjob:` ("The probe chooses the nearest eligible worker", line 295). The job really runs: `RM_RestringSpan` is checked, the counters are unchanged at start, and exactly one increment happens at 325-327. But nothing shows a colonist picking up the designation on its own. Either state that as a limit or add an optional check for natural pickup.
- **Net/run 0 counts as valid.** `integer()` accepts 0 (lines 222, 244, 262). If 0 means "no net/run", two Up anchors that both read 0 would pass "one net" at line 246 and "one run" at line 334.
- **The joined style isn't checked against the two starting styles.** Lines 335-338 only require all members to be equal. If the restring resets everything to `defaultKey` or a third style, it still passes.
- **The setup restyles aren't read back.** Nothing confirms `rawStyle` came back as `Modern_Orange`/`Industrial` (286-287). Line 292 only needs the two `[look, colour, raw]` tuples to differ somewhere. PRELAUNCH's "full different" wording asks for more than that.
- **Joined-run coverage only counts members tagged with the same run id** (336-338). Nothing checks that every anchor on the joined power net is in that run.
- **Cleanup doesn't fully restore.** It resets M2/M3 to `defaultKey`, but doesn't compare against the captured `baseline` and doesn't cancel a leftover cut or designation. The scene reload covers this, but only if the reload is checked properly (see the guard section).
- **Tick/bridge errors after line 317 are filed as MOD FAIL**, not harness failures. That doesn't create a false pass, but it does mark the def broken.

**M15e (`validation_aerial.py:600-657`)**
- `"jobDef": "RM_RestringSpan"` is a hard-coded string, not a reading. M15e never checks the worker or which job ran, and it only needs `jobsDone >` (not exactly +1). Because `mod_completion` matches on the row's JSON text, an M15e PASS counts as evidence for `RM_RestringSpan` by itself.
- If `i2` is falsy, M15e is skipped and writes no row.

**Exit contract (`validation_aerial.py:1830-1875`)**
- Exit 0 only means: not aborted, no FAIL, no UNMEASURED. A missing M15e/M15f row, or a SKIP/PARTIAL/ERROR status, still exits 0.
- Without `--out`, the JSON goes straight into `northstar`, which `mod_completion` scans. Failed attempts would land there too.

**A3 (`mod_completion.py`)**
- Only MOD/NONE rows count. A HARNESS-UNMEASURED M15f is ignored, so an M15e PASS alone could make the def "works".
- "Not unverified" is also true when the status is "broken" or "offline-only". A3 should require `works`.
- Runs are sorted by `str(started)`. If `res["started"]` is an epoch float, it sorts before every ISO timestamp, so an older FAIL could count as the latest.
- The script key comes from `d["script"]`, or from the file name with the timestamp stripped. A copy under a different name could leave an older L2 MOD FAIL under another key, which still makes it "broken". Any non-offline JSON counts as L2.

**Guard (`live_guard.py`)**
- **The restore can race the driver.** On timeout, `subprocess.run(timeout=960)` kills only `restring_style_proof.py`. A `validation_aerial` grandchild could keep driving the bridge during the restore reload.
- **The restored scene is read without re-pausing** (127-130). The baseline was paused (103), so the tick could drift.
- **The begin save is created after the save hashes are taken**, so nothing detects the driver overwriting it.
- **Settings are only restored in memory.** If the driver wrote mod settings to disk, the on-disk Config file isn't checked.
- **The guard doesn't check the M15e/M15f rows.** It checks the returncode only, not that the rows exist, are unique, are PASS/MOD, or came from this process and artifact.

## Scenarios and expected outcomes
1. **Grandchild survives a timeout.** Expected: guard FAIL, and before any restore reload the process list shows no `validation_aerial`/`restring_style_proof` python.
2. **Exit 0 but rows wrong.** A post-run check on the untouched JSON should require exactly one M15e and one M15f row, both PASS and class MOD, with zero non-PASS statuses. Anything else fails, whatever the exit code.
3. **Joined style is a reset or third style.** From M15f's evidence: `after[0]` must be one of `before`. Both `splitNets`/`joinedNets` and `splitRuns`/`joinedRuns` must be greater than 0. Every census anchor on the joined net must appear in `joinedRuns[0]` with the same style.
4. **Restyle setup didn't take.** In the readings, the `cstyles` after the `crestyle:` calls show `rawStyle` equal to `Modern_Orange` and `Industrial` on M2/M3. Otherwise the run is invalid.
5. **Restoration.** Hash the begin save right after `save_site` and again before the restore reload (they must match). Pause before `scene()` (tick must match baseline). Hash the GSS Config XML before and after (it must match).
6. **A3 discovery.** Run `mod_completion` before the copy (expect `unverified`) and after. After the copy, `RM_RestringSpan` should be `works` with `n_fail==0`, and an L2 PASS whose path is the copied file and whose row key is M15f. Also confirm `res["started"]` is an ISO string, and that no other GSS JSON has a latest L2 MOD FAIL that mentions `RM_RestringSpan`.

## Advice
Before launching, add three things outside the driver:
- a process-absent check before the guard's restore reload
- pause, then `scene()`, during restore
- a hash of the begin save and of the Config file

After the run, run scenarios 2–4 and 6 as read-only checks against the untouched raw JSON before copying it into `northstar`. Copy only if they all pass, and keep the original file name so `script` and `started` stay the same. In the acceptance write-up, describe the job as probe-assigned rather than picked up by a colonist on its own, and describe the power check as registered-net equality.

## Applied scenarios before live proof

The guardian now checks child-driver absence before restoration, kills only its own timed-out launcher tree, pauses before the final scene read, hashes the guarded begin save and GSS Config files, and retains all cleanup failures. The read-only result inspector requires both unique MOD PASS rows, every row PASS, the actual requested style keys, one of the original styles surviving, pending queues empty, a new link-bridge counter, and all three joined power anchors in one styled run. Results will be appended after the production run.

Net id zero is a valid hash-derived id. RM_MapComponent_Aerial.NetId uses -1 for null and masks RuntimeHelpers.GetHashCode with 0x7fffffff. Run ids come from the first member thingIDNumber. The current >=0 requirement matches those actual representations. The job is probe-assigned through the real WorkGiver/JobDriver path. Natural scheduler pickup remains unverified. A3 will require works and zero fails using the untouched result discovered through the production scanner.

## Independent pilot after the first full-driver nonpass

### Exact question

Fresh independent read-only Opus pilot diagnosis, no game or writes. One full live attempt failed, raw kept under /mnt/d/ClaudeWork/rimmandrake/codex_wsl/fw-drain/restring-live-raw/attempt1/a1-1bm64be3/stdout.txt and stderr.txt; guardian attempt1_guard.json. Root /home/mandrake/rm/scratch/BENCH/fw-drain. Within 12 tool calls assess narrow harness repairs, and flag any acceptance weakening or genuine out-of-unit shipping defect:
1 A.ap now requires cmd exact, but AerialProbe.Net returns cmd=net with x,z. Plan accept legacy net only with exact integer requested coordinates and fresh serial, retain rejection controls.
2 _run_live parameter tap is LogTap but locally overwritten by power-tap dict before AZ_log_budget. Rename local power tap, keep log coverage strict.
3 M14b expects shed blockage, but approved LayFallen now tries AimTurns up to50 degrees and avoids the shed. Plan extend the ROOM west wall across SITE height as a complete barrier so the existing blocked/tip threshold remains, with no shipping/appearance edit. Read AerialMath.LayFallen and barrier coordinates validation_aerial constants.
4 M21c counts old uniform samples25 vs current approved SpanTs adds 0.08,0.16,0.3 per end ->31 for12cells. Update Python expected point count and independent source-tied oracle/controls to actual production SpanTs, keep ON48/OFF31 distinct and verts check.
5 Guard restored identical rectangle, pawns, jobs, tick except Ellison's GotoWander targetA changed on reload from129,123 to126,119. Plan reissue only that baseline GotoWander at waitTicks0 through actual ordered_job then require complete raw scene equality. All protected/existing saves, debug/settings/config hashes match. Alternative bounded exact cleanup if better.
Read actual source and raw files. Source paths src/RimMandrake/GimmeSomeSlack/validation_aerial.py, Source/Aerial/AerialMath.cs/AerialProbe.cs, selftest_gss_proof_drivers.py, whittle/fw-drain-restring-live/evidence/live_guard.py. Return specific diagnosis and necessary negative controls. Do not run, attach or infer pass from truncated row print. M15e/f stdout passed but full driver exit was1 and no result JSON, so no acceptance is claimed. No owner questions, mod-list restoration or art redraw needed.

### Exact reply

Nothing here is accepted. I only read source and raw files. I didn't run anything, attach to the game, or read `stdout.txt`.

**Why the driver exited 1:** `stderr.txt` shows `_run_live` crashed at `validation_aerial.py:793` with `AttributeError: 'dict' object has no attribute 'base'` (item 2). So no result JSON was written, and no row result counts as evidence.

## 1. `A.ap` exact cmd vs `net` replies
- **Diagnosis:** confirmed. `validation_aerial.py:90` requires `parsed["cmd"] == cmd`. `AerialProbe.cs:93` sends `net:` to `Net(map, cmd.Substring(4))`. I didn't read `Net()` itself, so "it returns `cmd=net` with x,z" is your finding.
- **Effect:** every `net_at` call returns a failure dict, so `.get("net")` is None. That makes M13b, M19 and M17 FAIL, and M19n/M19m probably UNMEASURED. Nothing false-passes, so fixing this restores coverage rather than weakening it.
- **Your plan is sound:** accept `cmd == "net"` only when all of these hold:
  - the request fully matches `net:(-?\d+),(-?\d+)`
  - `type(parsed["x"]) is int` and `type(parsed["z"]) is int` (this rejects bool, float and str), and both equal the requested values
  - the existing checks still pass: `success`, `now > before`, and `serial() == now` after the read
- Don't rewrite `parsed["cmd"]`. Tag the reply instead (e.g. `_legacyNetCmd`).
- `:217` and `:1088` run their own `reply.get("cmd") == cmd` checks. Grep whether either one ever sends `net:`.
- **Negative controls (each must be rejected):** wrong x, wrong z, x/z missing, x as bool/float/string, a `cmd:"net"` reply to a non-`net:` request (e.g. `census`), `cmd:"net:…"` with different coordinates, a stale serial, a serial that changes during the read, `success:false`.
- **Shipping:** the probe not echoing the full command is an out-of-unit inconsistency in a debug probe that ships in the DLL. Players never see it, so it's not a defect for them.

## 2. Log tap overwritten
- **Diagnosis:** confirmed. `:704` rebinds the `tap` parameter to `(ct.get("taps") or [{}])[0]`, and `:793` then calls `tap.base`.
- **Fix:** rename the local power tap (e.g. `ptap`) at `:704`, `:715` and **`:752`**. Line 752 is `mtap = next(t … if t.get("id") not in (tap.get("id"),))`. If that one is missed, it either crashes on the LogTap, or M19m stops excluding the M19 tap and could PASS on the wrong clamp.
- **Controls:**
  - an AST/selftest check that `_run_live` never rebinds `tap`
  - M19m still excludes the M19 clamp by id
  - incomplete coverage or a dead log still gives AZ = UNMEASURED/HARNESS
  - an injected error entry still gives AZ = FAIL

## 3. M14b blockage
- **Diagnosis:** consistent with the code. `LayFallen` (`AerialMath.cs:577-589`) tries every SlackLevel × AimTurn and sets `Blocked` only if no aim clears the full `want`. The comment at `:573-576` says the shed-avoiding fall is intended. So the check at `:571` (`blocked and tip[0] < ROOM[0]`) is out of date; this isn't a product defect.
- **Is "west wall across SITE height" enough? Not proven.** `cable = dist` because 12.6 ≥ 0.8 × 12, so `want ≈ 12`. Offsets are clamped to `min(2.6, 0.4·want+0.3) = 2.6`. That gives two bounds:
  - **x bound:** the wall must sit less than about 12·cos50 − 2.6·sin50 ≈ **5.7 cells** east of M1's base, or a +50° aim with an adverse lateral offset may end short of it.
  - **z bound:** the wall must cover M1z ± about (12·sin50 + 2.6) ≈ **±12 cells**, plus a margin. SITE only spans AZ0−2…AZ0+17. If M1 is at room mid-height (around AZ0+5), a −50° aim reaches about AZ0−2 at the wall's x, right at the SITE edge, so it could pass around the end of the wall.
  - I didn't read M1/M2/BAT/LAMP coordinates, the `AimTurns`/`SlackLevels` values, or the pile-up code after `:619`.
- **Before using it:**
  - Run the bound on the real constants. If the wall must extend past SITE, extend the clearing too (destroy/terrain/fog/roof).
  - Check the wall doesn't sit on BAT, LAMP, M1–M3, HCOND/OCOND or CLAMP.
  - Check it doesn't cut off the colonists' path for M15e/f, or those rows go UNMEASURED/FAIL.
- **Controls:**
  - An offline `LayFallen` sweep over both `sgn` values and many seeds with the new walkable grid: Blocked every time, and tip x < ROOM[0] including any pile-up points. Seeds come from thing ids, so they vary from run to run.
  - The same sweep with only the original room: not blocked. This proves the barrier is what M14b measures.
  - Leave the M3 open-ground leg (`not blocked`, `laidLen > 0.85×12.6`) and the net/live checks unchanged.
- Optionally, add a row for the approved behaviour (falls beside the shed, not blocked) so it gets coverage instead of disappearing.

## 4. M21c point count
- **Diagnosis:** confirmed. `drip_expected_points` (`:1023-1032`) still uses `max(4, ceil(len/step)) + 1`. `SpanTs` (`AerialMath.cs:181-191`) adds `d/len` and `1−d/len` for each `d` in {0.08, 0.16, 0.3} with `d < len/4`, then sorts and removes consecutive duplicates within 1e-9. At len 12: 25 + 6 = **31**. Drip on: n′ = ceil(11.1/0.5) = 23, plus 25 = **48**.
- **Fix:** port `SpanTs` exactly, including the strict `<`, the `len > 1e-6` guard and the dedupe. Use it for the OFF branch **and** for the drip-on fallback (depth/reach ≤ 0 or tiny len). That fallback calls `SpanCurve` (`:295`), so it gets the new count too.
- **Controls:**
  - Hand-counted cases: len 12 → 31; len 1.2 → 0.3 not added (`d == len/4`) but 0.08 and 0.16 added; len ≤ 0.32 → no end samples.
  - A reading of 25 for OFF must FAIL (this catches a stale DLL).
  - A reading of 31 when ON must FAIL, and 48 when OFF must FAIL.
  - A `verts ≠ 2·Σpts` mismatch must FAIL; missing `strandPts` must give UNMEASURED/HARNESS.
  - Keep the ±1 tolerance and the "within 2 decides nothing" rule.
  - Tie `SpanEndSamples` to the source by parsing `AerialMath.cs:178`, *and* check it against a literal (0.08, 0.16, 0.3), so a source change breaks the selftest instead of silently moving the oracle.

## 5. Guard scene mismatch
- **Raw data:** in `attempt1_guard.json`, the pawn at (119,111) has baseline GotoWander targetA (129,123) and restored (126,119). The other wanderers, (118,106) and (122,115), match exactly. Both scenes come from reloading the same begin save, whose sha is verified at `live_guard.py:168-169`. So this is load-time nondeterminism (that pawn's job gets re-picked at load), not run contamination.
- **I'd recommend a bounded tolerance instead of re-issuing the job.** An `ordered_job` re-issue mutates the game to match the one field `site_state` exposes. Hidden fields (playerForced, expiry, startTick, job id) would still differ, so "complete raw equality" would overstate what's actually equal.
- **The tolerance:** diff the raw scenes and allow only `jobs[i].targetA` where all of these hold:
  - the same pawn id, with job == GotoWander on both sides
  - every other field of that pawn entry, and every other structure (rect, pawns, autoHome, tick), identical
  - the begin sha unchanged
- Record the diff in a field such as `reload_nondeterministic` and require it to be non-empty only in that shape.
- **Controls (each must FAIL):**
  - a targetA difference on a non-GotoWander job
  - a job def that changed
  - a pawn's position or health that changed
  - targetA missing on one side
  - a tick, rect or autoHome difference
  - an extra or missing pawn

Your other checks (protected saves, debug flags, settings and config hashes) need no change. Settings are restored after the scene check (`:178`), so the ordering is fine.

**Weakening and shipping:** none of items 1–5 weakens acceptance if done with the controls above. The ways it could: skipping the `:752` rename, a barrier that doesn't provably block every aim, or a forged job re-issue. I found no real player-facing shipping defect. The only product-side oddity is the probe's `cmd` echo in item 1.

**Not verified:** the `Net()` body, the scene coordinates, `AimTurns`/`SlackLevels`, `LayFallen` after `:619`, `stdout.txt`, and which job fields `site_state` reports.

### Repairs and controls

The legacy net reply is accepted only with exact integer requested coordinates and stable serial. Wrong coordinates/types/commands and changing serial remain rejected. The local power-tap variable was renamed at all three uses, preserving the journal and mixed-clamp identity. The wall now spans z170 through201 at x96, within4 cells east of M1 and more than12 cells each side, while the original blocked/tip and far-open-leg thresholds remain. The curve oracle includes the approved insulator samples, with31-point OFF,48-point ON and wrong-state/vertex controls. Original changed-driver checks were RED in all three affected scripts. Final focused runner is retained in harness_green2.txt. No shipping executable or art source changed.

The pilot proposed a tolerance for load-time idle-wander target changes. The frozen exact-restoration requirement is retained. The second attempt prepares its disposable guarded baseline with drafted support colonists before saving, records the prior original site pawn state, releases workers for the proof, and reloads the held baseline finally. No job is forged during cleanup and full raw scene equality remains required. Original registered/canonical save bytes remain protected.

## Second nonpass and final preparation

Attempt2 passed38 mechanism rows, including every net/style/job control, with exact full guarded scene equality. AZ remained UNMEASURED because JournalReader required a payload success field that the actual stock rimbridge/list_logs omits. The observed stock reply has logs plus operation.Success true and operation.Status Completed. The narrow adapter now accepts that successful envelope, retains explicit payload failure, malformed data, failure-envelope and lost-log controls, and is RED-before/GREEN-after through the standard runner. Attempt2 remains nonpassing and is never copied into the completion scanner.

The proposed extra Modern_Orange mast assertion was corrected against actual source and observations. Anchors carry four looks with null colour. Conduit definitions carry the Modern colour variants. M15f measures distinct Modern/null/RM_AerialMast_Modern and Industrial/null/RM_AerialMast_Industrial styles, with one original full style winning. The final inspector requires those actual supported identities. This changes an added verification assumption. The frozen acceptance stays intact.

The guardian now reads each source-declared static settings field individually. This avoids the list tool attempting an instance GetSettings for the second class and logging a pre-fixture tooling error. Both original full raw attempts retain that message and exact timing.

## Final observed scenario results

Attempt3 launcher and child driver both exited0. All39 rows passed, including unique MOD M15e/M15f, AZ complete/no failed reads/no lost entries and every unchanged unrelated driver threshold. The read-only extra inspector passed with distinct requested supported mast looks, one original full style winning, three anchors on the joined net in the same styled run, pending0 and linkBridges0 to1. Job counters advanced1 to2 exactly and designation/cut cleared. The guarded baseline and final rectangle/pawn/health/job/draft/auto-home/tick observations are exactly equal. All49 mutable settings observations,47 debug flags, readable difficulty values and three GSS Config file hashes restore. All344 existing save hashes match after shutdown. Actual mod_completion now reports RM_RestringSpan works, n_pass2, n_fail0, via the untouched discovered result.
