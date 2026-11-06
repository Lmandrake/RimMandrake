# ARCHMAGI_BACKFILL_WIRE_UNIT_RUNNER_WANTED — host state (2026-11-06)

The section 2 trial switch for the Archmagi backfill is ON. Both pieces live on the host, outside the repo:

- **Runner clone** `/home/mandrake/rm/archrunner` (`\\wsl$\Ubuntu\home\mandrake\rm\archrunner`): its own clone, origin
  `git@github.com:Lmandrake/RimMandrake.git`; not a pool, seat, agent or dispatch clone (`testq.py runner_problem`).
  The backfill detaches and pulls it per attempt; nobody else writes it.
- **Unit** `~/.config/systemd/user/testq-tick.service` carries `Environment=TESTQ_ARCHMAGI=1` (line after
  `WorkingDirectory`). Pre-change copy: `D:\ClaudeWork\rimmandrake\testq-tick.service.bak-20261106`.
  To switch the trial off: remove that line and `systemctl --user daemon-reload`, or touch
  `D:\ClaudeWork\rimmandrake\testq\archmagi.stop`.

First reading after the change: `D:\ClaudeWork\rimmandrake\testq\archmagi_state.json` `switch.read_at`
2026-11-06T19:41:20Z, `last_gate` "bridge held by RELENTLESS" — the gate got past the runner-clone check
(an absent clone reads "no runner clone at …", the switch unset reads "off (…)").
