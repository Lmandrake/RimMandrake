# Traps seen (lessons in infrastructure/state/lessons/)

- log-tail-then-parse (20261028T164801Z): a helper that logs `(stdout+stderr)[-2000:]` fed the tail to a JSON parser;
  the live account came back None and stage 2 never fired. Selftests stubbed it. Probe the real command once.
- failover-soft-line-strands (20261028T181052Z): DARK at the soft line is a trap once a fresh account exists - a DARK fleet
  barely moves the meter, so a switch gated on reaching the floor never fires. Also: do not delete a marker on
  "status unknown" after a failed switch; keep pending until the live account is positively known.
- account-failover-r4-open (20261028T170459Z): first real unattended `use` on Archmagi; `use --dry-run` refuses while
  DISARMED so its preflight is unprobed; a 600 s subprocess timeout SIGKILLs a switch mid-way and leaves journal.json.
- stopping-timers-for-cutover (05:04 incident): stop timers only through timers_guard pause.
- `--n 0` does not stop FOUNDRY; DARK does. DARK left after a reset strands the new week.
- Dormant-account tie: equal newest reading times; never prefer the first key.
- Blind meter on an exhausted account is normal (it cannot be read); that is why the 0% blind rule exists.
