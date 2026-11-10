# LOG_BOUND deployment and remaining close proof — 2026-11-10

Item: `LOG_BOUND_DECIDE_COLD_LOAD_ALWAYS_GUILTY`; implementation: `ce04ffdae346f2f6f9c825a7c162233fa4b3b4a0`.

## Completed

- Took the free bridge for `LOG_BOUND deploy` at 16:09:53Z; released at 16:10:48Z.
- `game_instance.py status` identified game A as PID 52408. `game_instance.py stop` (without `--force`) signalled that PID; the next status measured A stopped. No other process was targeted.
- Recorded `./game --why "LOG_BOUND companion DLL deploy" down` at 16:10:26Z. Game left down; no relaunch, focus, fullscreen, mod-list write, or Operations enablement.
- `python3 src/RimMandrake/bridgetools/build.py --gm --apply` succeeded: 0 warnings/errors, GM tools included, source hash verified, shared-type closure scan clean.
- Built from clean published `446ec4d7dbb5b4f280143e75a2079e02921f3bd7`; deployed `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\BridgeTools\JawaBench\JawaBench.BridgeTools.dll`.
- Deployed DLL equals the built DLL byte for byte: SHA-256 `d76ec2b1e18929ea8ba81fe360690811774befe9f5a30f81839df8f478c5e083`; size 5171712 bytes. `companion_identity.py <deployed DLL> --repo . --rev HEAD` returned FRESH, embedded source hash prefix `48258bf21f61`.
- `python3 src/RimMandrake/Utils/run_selftests.py --only selftest_game_health_check`: GREEN, PASS 1/1, FAIL/CRASH/UNMEASURED 0. Runner reported no cached result recorded (input changed during run); direct test execution passed.

## Close remains unproven

The actual close with `--sha ce04ffdae346f2f6f9c825a7c162233fa4b3b4a0 --live "role=Operations max_age=2d"` refused without changing the item: Operations last launched 2026-11-06T23:51:01Z, before the fix. Operations is OFF by the owner's choice and was left OFF.

The alternate recurring collector also cannot prove the close: `rm-metronome.timer` and `rm-ops-watch.timer` are disabled/inactive. `live_line.check("unit=rm-ops-watch.timer reading=/mnt/d/ClaudeWork/rimmandrake/ops_watch/status.json max_age=15m", not_before=<implementation commit time>)` refused because the owning metronome is disabled. `status.json` mtime is 2026-11-07T02:23:24Z; its TPS health observation is 02:09:36Z and still names `log.errors_lower_bound`. This predates the LOAD/PLAY split and is not current proof. A one-off reading or `once:` promise would not establish the recurring operational behavior.

UNVERIFIED: the newly deployed DLL has not run; no new context row demonstrates its per-scan `logEvicted`, and no current recurring collector demonstrates the split in operation.

NEXT: keep the item open. When ongoing monitoring is authorized again, obtain a post-fix Operations run or a proven active recurring collector with a fresh TPS health reading from the split reader. On the next independently needed launch, confirm companion source identity and a context row containing `logEvicted`; judge LOAD at `log.load_messages > 4500` and PLAY at `log.play_evicted == true`, retaining the sticky flag only as a fact. Close on the implementation SHA with the actual running role/unit and its fresh reading. Do not enable Operations merely to satisfy this item.
