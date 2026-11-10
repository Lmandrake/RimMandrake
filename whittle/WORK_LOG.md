# Whittle worker record

Scope: FLOWWORKS_PRISON_BUILD_NO_BED_REQUIRED only. No ledger closure or publication. No new/modified code marked CLEAN. No other clone or ModsConfig.xml touched by worker. No worldgen, flight test, game focus or fullscreen.

## Implementation

- `4c99b099f3`: bedless enclosed pit rooms; existing capture-down job and vanilla guest transition; vanilla feeding/tending and food selection adapted to a lip; suppress remote-bed relocation for held pit prisoners. Existing height/depth/width rules unchanged. Added repeatable concept scene and fault tests.
- `f7a52814c0`: corrected player-facing About description to match bedless prison intent. This last metadata change remains undeployed because the trial stopped before a live launch.
- Assembly and .srchash committed together. Standard committed-source stamp checker exit 0. No self-certification of runtime correctness.

## Checks and evidence

- C# winbuild FlowWorks: zero warnings/errors, `evidence/build-final.log`.
- Required selftest runner: `python3 src/RimMandrake/Utils/run_selftests.py --only selftest_hole_prison.py selftest_fixture_pit_prison_cleanup.py --workers 1`; PASS 2/2, FAIL/CRASH/UNMEASURED zero. The first file checks driver faults plus runs actual C# production PitRoom_* cases only; no full sweep. `evidence/offline-tests-stable.log`.
- Earlier direct selftest_flowworks_stock.py --only PitRoom_* invocation passed 3/3; observer reminded worker to use the runner. Subsequent checks used it. Earlier running-test cache refusals were preserved; they did not turn a failed test into a pass.
- Opus high consultation, max $5, tools empty. First inherited WHITTLE stop hook and failed; raw stdout retained. Observer identified the harness cause; second child WHITTLE=0 returned actual risks. Added occupied-save and upright self-feeding probes; fake driver controls exercised, live probes UNMEASURED.
- Read dry deploy plan, took bridge with requested BENCH/WHITTLE_TRIAL env, deployed FlowWorks with deploy_custom_mods.py --apply. VERIFIED in sync for DLL/stamp/English translation then present. No game launch followed.
- Final source/DLL hashes, real test/build outputs reread, and explicit UNMEASURED live fields are in `evidence/final-status.json`, saved after the last implementation/ledger change.

## Harness failures and assistance

1. Live activeMods omitted FlowWorks. Worker read-only measured and requested repair. Observer backed up and enabled it; then repaired order with the existing canonical flowworks tier. All five DLC retained. Worker did not edit config.
2. Preflight O09 local ignored companion comparison artifact absent. Observer verified embedded installed source hash against this clone and copied that proven installed artifact into this clone. No companion live deploy.
3. Preflight O12 misclassified imported .props/.csproj.template test sources. Observer fixed lint discovery and tested a true missing-source control; local commit b230486d9e. This was not worker feature code.
4. Text-only consultation inherited WHITTLE=1; installed Stop hook wrote STALLED. Retained; successful retry child WHITTLE=0. Main checker remains armed.
5. Bridge ledger released but process lock remained assigned to this live Codex parent. Worker read documented RM_DRIVER_PID support and released its own pid 1755864 without force. Final who: both FREE.
6. Remaining preflight NO-GO O10/O13: installed Harmony location differs from stale baseline path, and deployed GimmeSomeSlack DLL embeds source changes absent from clone/origin, owned by another job. Observer confirmed no safe automatic repair this sitting. Worker refused to overwrite someone else's deployment or suppress checks. `evidence/preflight-after.log` and HARNESS_REPLY.md.

No screenshots or fake-bridge outputs claim capture or feeding occurred in a game. No loaded DLL identity, day of prisoner care, real enabled/disabled control or real restore has been measured. Fresh independent Opus judge completed after DONE: CANNOT TELL for bullets 1–3, FALSE for bullet 4, would show: no. Its unmodified verdict and full tool transcript are retained. Original armed checker refused the incomplete claim; a genuine BLOCKED record is filed. Derived decompiled engine text used to verify API names was removed from the worktree rather than published. A blocked trial is not a finished feature.
