# BOUNDARY: a live promise on another machine (`host=` on a unit line), Design Version 0.1.0

Code: `src/RimMandrake/rimflow/live_line.py` (`HOSTS`, the `host=` branch of `parse`, `_here`, `_via`, `_remote_mtime`
and their use in `check`). Item: `WORKER_CLONES_MONITOR_POOL_NOT_RABBITS`. Why: on 2026-11-24 a helper on SteveDesktop
could not close an Archmagi item, because `close --live` asked SteveDesktop's own systemd ("is-enabled says
'not-found'"). Each promise has a test of its name in `src/RimMandrake/rimflow/selftest_live_line_host.py`. This page
covers only these parts of the file.

## ACCEPTS (the only inputs this is built for)

- **a-unit-line-with-host.** Any unit line of `live_line.parse` with one more field `host=<key>`, where the key is in
  `HOSTS` (any letter case). A hook, role or once line takes no host.
- **a-reachable-host.** The ssh target in `HOSTS` answers with keys and no prompt (`BatchMode=yes`).

## DOES NOT SURVIVE (not promised)

- **a-host-not-in-HOSTS.** A new machine is added to `HOSTS` by hand. Until then its key is refused.
- **a-machine-whose-hostname-differs.** "This machine" is `socket.gethostname()` (or `RM_LIVE_HOSTNAME`). A host whose
  hostname is not its `HOSTS` name asks itself over ssh, which still works when it can reach itself.

## PROMISES (each one is owed a test of the same name)

- **host-line-parses.** `unit=… reading=… max_age=… host=archmagi` parses to the unit line plus `host`.
- **an-unknown-host-is-refused-by-name.** A key not in `HOSTS` raises ValueError that names it.
- **remote-host-asks-over-ssh.** Off the host, every systemctl call and the reading's mtime go through `ssh <target>`.
- **a-stale-remote-reading-is-broken.** A far reading older than max_age gives a reason, as a local one does.
- **an-unreachable-host-is-a-reason-never-a-pass.** An ssh failure (exit 255) gives a reason, never None.
- **on-its-own-host-it-asks-here.** On the host itself no ssh runs: the deadman on that machine checks locally.
