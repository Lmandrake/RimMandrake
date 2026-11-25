# run_host.py boundary: a detached list run on SteveDesktop

## ACCEPTS

 a host name in any letter case, an item, a brief path, and the facts read from the host.
- LOCAL: this machine. REMOTE: one systemd user unit on the host, in `~/rm/list/<ITEM>`.

`read_facts()` gets the remote login from `account_live.read`. Its banner and status fixtures are in
`src/RimMandrake/Utils/selftest_account_live.py`.

## DOES NOT SURVIVE

- ssh that hangs past its timeout (a fact stays None).

## PROMISES

- **refused-by-name.** REFUSED, by name: an unknown host; a login that is not the Dispatcher's pick; no push route; a test-lane clone (`~/rm/runner`, `~/rm/runner_b`).
- **could-not-look-named.** COULD NOT LOOK, naming the fact: any fact that is None; a host that is down. Never "ended".
- **no-spend-stated.** The plan never states a spend. `stop_argv` stops the unit over ssh.
Tests: `src/RimMandrake/rimflow/acceptance/list_run_on_steve_accept.py` (12 checks).
