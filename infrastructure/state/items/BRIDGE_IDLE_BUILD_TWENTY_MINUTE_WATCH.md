# BRIDGE_IDLE_BUILD_TWENTY_MINUTE_WATCH

Owner card 2026-10-26 19:06 PDT: "May a seat take the free bridge, deploy and restart the game on its own when a
watcher shows no other seat holds it and you haven't touched the game for 20 minutes, never for flyer flight?" ->
"Free bridge + 20 min idle (Recommended)". Recorded: canon.yml `bridge_free_idle_restart_delegated`;
delegation_policy.md §2.6; CLAUDE.md / standing_rulings.md "The bridge is passed through one file". Evidence:
delegation_candidates_2026-10-26.md §3 card 3.

## Build
- Idle-input probe on Windows: seconds since the owner's last keyboard/mouse input to RimWorld (GetLastInputInfo +
  foreground window, or equivalent), read from WSL; never names a host or account in code.
- Watcher: `rimflow bridge who` shows no other seat holding it (owner hold counts as held) AND idle >= 20 min ->
  reports TAKEABLE; a seat then may `bridge take`, deploy, `./game --why "free bridge + 20 min idle" ...` restart.
- Refuses outright for any flyer-flight purpose (`--for` naming flight / a flyer live test). Never live-test flight.
- Each take/deploy/restart logged `--why "delegated: bridge idle"` and listed in the daily digest.
- Until it lands neither condition can be shown, so the bridge stays his for this purpose.
## Verify
Probe sanity: reads < 60 s right after a real input and grows when idle; watcher refuses at 19 min, at a held
bridge, and for a flight purpose; digest line appears for a take.
