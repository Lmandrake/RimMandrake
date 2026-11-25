# run_host.py boundary: a detached list run on SteveDesktop

## ACCEPTS

- A host name in any letter case, an item, a brief path, the facts read from the host, and the call's model, spend cap,
  seat, next-act owner and RM_ variables.
- LOCAL: this machine. REMOTE: the host's own `detached_helper.py launch` in `~/rm/bench`, through the WSL door
  (`mandrake@stevedesktop-wsl`) with `~/.local/bin` on PATH. The host's launcher makes the clone
  (`~/rm/relentless/clones/<ITEM>.det`), the footer, the host's run record, the finish note and the publish.
- `read_facts()` gets the remote login from `account_live.read`. Its banner and status fixtures are in
  `src/RimMandrake/Utils/selftest_account_live.py`.

## DOES NOT SURVIVE

- ssh that hangs past its timeout (a fact stays None; a live state reads live).
- A host whose `~/rm/bench` is far behind origin: it launches with its own launcher code.

## PROMISES

- **refused-by-name.** REFUSED, by name: an unknown host; no spend cap; a login that is not the pick; no push route; no
  launcher in `~/rm/bench`; a test-lane clone (`~/rm/runner`, `~/rm/runner_b`).
- **could-not-look-named.** COULD NOT LOOK, naming the fact: any fact that is None; a host that is down.
- **no-spend-stated.** The plan never states a spend to the run.
- **wsl-door.** Every command goes through the WSL door, never the bare alias, which lands in Windows PowerShell.
- **login-path.** Every fact command runs with `~/.local/bin` on PATH.
- **every-fact-reads.** On a host that answers, every fact reads and the plan is REMOTE.
- **account-from-the-machine.** The account is `live` of the host's `claude-account --json status`; the pick defaults to it.
  The code names no account.
- **launch-argv.** The brief goes over stdin to `~/rm/list_briefs/<ITEM>.md`; the launch carries the call's model and cap.
- **record-names-host-unit-item.** The record on this machine names host, unit and item.
- **live-until-the-host-says-ended.** A remote run is live while its unit is live or the host cannot be read; its end
  state is the host record's status, copied into this machine's record (`host_end`).
- **stop-runs-the-hosts-pipe.** `stop_argv` runs the host's own `./pipe stop <unit> --<mode>`.
- **pipe-stop-routes-a-remote-unit.** `./pipe stop <unit>` on a unit whose record names a host runs that stop, nothing here.
- **host-room-for-the-lane.** `list_dispatch.py` places a lane run on a host only when its own slots are full, under the
  host's `max_live`, and while the host's live account has more than `min_left_pct` of the week left. An unread reading is
  no room.

Tests: `src/RimMandrake/rimflow/selftest_run_host.py` (one test per promise, by name);
`src/RimMandrake/rimflow/selftest_list_dispatch.py` `t_a_full_lane_places_on_a_host_with_room`;
`src/RimMandrake/rimflow/acceptance/list_run_on_steve_accept.py` (12 checks).
