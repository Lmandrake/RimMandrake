# BOUNDARY: a login's fixed deadline is warned before it kills the machine's sessions, Design Version 0.1.0

Code: `src/RimMandrake/rimflow/login_watch.py` (`login_deadlines`, `host_login_deadlines`, the deadline call in
`step`) and `src/RimMandrake/rimflow/dispatcher.py` (`login_obs`, keys `deadlines` and `host_deadlines`).
Item: `RIMMANDRAKE_TRACE_WINDOW_LOGIN_EXPIRED_HE_THOUGHT_IT_FIXED`, written 2026-11-22.
Each promise has a check of its name in `src/RimMandrake/rimflow/selftest_login_deadline.py`.

The owner, 2026-11-22 about 11:21 AM PST: "Why did I just have to re-login? It said the login expired. I thought we
fixed that."

What happened (measured 2026-11-22). The lukas sign-in carried `refreshTokenExpiresAt` = 2026-11-22 06:06:40 PST
(`~/.claude-accounts/health.json`: the value was the same before and after the 2026-11-21 rotation). Claude Code 2.1.323
merges a refresh as `min(old, new)` for that field, so a refresh never moves it: it is the sign-in's fixed deadline.
The last refresh before it (02:47 PST) gave an access token to about 10:42 PST. From then on the refresh was refused.
login_watch saw the login dead at 10:42:04 PST and alarmed at 10:44 (`login:expired:1795372924`). No account could take
over (steven 5% left, system 3% left). The Conductor window's next turn, 11:16, ended on "Login reached its time limit ·
Please run /login". He ran `/login` at 11:20. login_watch (LOGIN_LOSS_FIX_DEAD_SIGNALS, 2026-10-31) only answers a
login after it dies. This page adds the warning before the deadline.

## ACCEPTS (the only inputs this is built for)

- **a-vault.** claude-account's vault (`vault_root`, default `~/.claude-accounts`): one `<account>/.credentials.json`
  per enrolled login, and `live.json` naming the live account. The capture timer keeps the live login's vault copy
  current.
- **a-remote-vault.** SteveDesktop's `~/.claude-accounts`, read by `login_deadlines` itself over SSH. Only account
  names, the live name and deadline epochs come back, never a token. `health.json` there holds no deadline (read
  2026-11-24).

## DOES NOT SURVIVE (not promised)

- **a-dead-capture-timer.** If `claude-account-capture.timer` stops, the live login is read from its last captured
  copy. A sign-in since then is not seen until the next capture.
- **a-server-side-revoke.** A login revoked early by Anthropic, before its stated deadline, is not foreseen. The
  probe in `step` still finds it dead.

## PROMISES (each one is owed a check of the same name)

- **a-login-near-its-deadline-alarms.** A login whose deadline is within `deadline_warn_s` raises one alarm kind,
  `login:deadline:<host>:<account>:<deadline epoch>`, into the ledger and the Conductor log. The alarm gives the deadline in
  Pacific time and the way to renew. The Dispatcher repeats the kind every `alarm_every_s` until the login is renewed.
- **one-deadline-read-a-second-apart-is-one-alarm-kind.** For each host and account, a reading within three whole seconds
  of the stored warning epoch reuses its kind. On the first warning with this rule, the most recently told matching kind
  in Dispatcher state supplies that epoch if one exists. A new sign-in with a deadline days away gets its own kind.
- **the-live-login-renews-from-a-plain-terminal.** For the local live account, the alarm says so and names
  `claude auth login` from a plain terminal, not /login in a window. A vault account is told to use
  `claude-account enroll <account>`.
- **a-past-deadline-says-expired.** A login past its deadline alarms with EXPIRED and the time. A switch to that
  account is refused.
- **a-login-far-from-its-deadline-is-quiet.** A login with more than `deadline_warn_s` left raises nothing.
- **an-unreadable-deadline-is-unmeasured-not-quiet.** A credential with no deadline field, or one that cannot be read,
  raises `login:deadline:unmeasured:<account>`. A vault that cannot be listed returns None, never an empty set, and
  raises `login:deadline:blind`.
- **the-deadline-check-never-reads-a-token.** The reader returns only the deadline number and a reason. No token is
  in its result or in any alarm text.
- **a-renewed-login-ends-the-warning.** A new sign-in moves the deadline, and the old kind is not raised again.
- **a-broken-deadline-check-never-stops-the-login-probe.** If the deadline reader raises, `step` alarms
  `login:deadline:watch` and the probe of the live login runs as before.
- **the-dispatcher-wires-the-reader.** `dispatcher.login_obs` gives `step` a `deadlines` reader whenever login_watch
  is enabled.
- **each-vault-host-warns-of-its-own-deadlines.** The Dispatcher checks Archmagi and SteveDesktop, with distinct
  alarm kinds even for equal account names and deadlines. SteveDesktop's alarm names the host and how to enroll
  there.
- **an-unreadable-host-names-its-cause.** An unreadable host gives no reading (`None`) and an UNMEASURED alarm
  with its cause. A failed command or invalid reply is distinct from unavailable access. An empty vault is quiet
  and zero is a measured epoch.

## LIMITS

- `deadline_warn_s` = 3 days. Danger: a login dies mid-session, and every window and run on it stops until he signs in
  again. Evidence: 2026-11-22, the lukas login, dead 10:42 to 11:21 AM PST (above). Three days gives him several
  sittings to renew the login at a time he picks.
- The three-second match covers the observed whole-second variation on 2026-11-24, when epochs ending in 366, 367
  and 368 for one login produced separate incident metrics and called Operations again. The stored epoch stays fixed
  across matching readings.
- The SSH read has an 8-second connection timeout and a 10-second total timeout so SteveDesktop cannot indefinitely
  delay the local login probe. The connection timeout matches the account usage poller's.
