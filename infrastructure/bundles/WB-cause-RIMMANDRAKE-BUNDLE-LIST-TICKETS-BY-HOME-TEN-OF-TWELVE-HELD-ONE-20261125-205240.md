# Work bundle WB-cause-RIMMANDRAKE-BUNDLE-LIST-TICKETS-BY-HOME-TEN-OF-TWELVE-HELD-ONE-20261125-205240

System: cause:RIMMANDRAKE_BUNDLE_LIST_TICKETS_BY_HOME_TEN_OF_TWELVE_HELD_ONE. One member. State: ENDED (every member has
an outcome), 1:44 PM PST 2026-11-25.

| member | outcome | commit | live reading |
|---|---|---|---|
| RIMMANDRAKE_SEND_LANE_BUNDLES_TO_STEVEDESKTOP_NONE_SINCE_ONE_AM | fixed, closed | df9ae10194 | real ssh `read_remote` of WB-pipeline-test-lane-20261125-192031 reads `ended` (0.44 s); host `./sync --dry-run` WOULD SYNC; rm/dispatch runs the fix; the 1:39 PM PST dry tick had no ready Work row, so no real remote launch is seen yet |

What the next context needs about this system:
- A lane lead row with `host` now launches `ssh mandrake@stevedesktop-wsl 'cd ~/rm/bench && ./sync && ./pipe bundle <ids> --why ...'`
  (`work_bundle.launch_remote`). The store lock is free during the ssh; a placeholder record (`launching`, `host`) holds the
  system, then the marker (the host's bundle id) replaces it.
- `refresh_remote` (called in `list_dispatch.gather`) copies the host's store record into the marker each tick; a host that
  cannot be read ends the marker after `REMOTE_QUIET_S` with no ledger citation.
- SteveDesktop's bench was an hour behind origin at 1:10 PM PST: the `./sync` before the launch is needed.
- The fresh reader (rm-consult, Opus) found one significant thing (the lock held across the ssh would block local finishes);
  fixed with a placeholder, red on a planted fault. Its polish lines were done in the same commit.

Context after the group: 230k of 1M (GO ON).

Not tested live: the first real remote launch by the tick. It happens by itself when a lead row's only room is
SteveDesktop; read `python3 src/RimMandrake/rimflow/work_bundle.py` page or the tick's rows for `on SteveDesktop`.
