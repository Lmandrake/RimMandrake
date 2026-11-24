# BOUNDARY: the art daemon asks the one Codex door for each picture

Code: `src/RimMandrake/Utils/artpipe/imagecall.py` (the call and the ready check),
`src/RimMandrake/Utils/artpipe/signin_health.py` (the dead-sign-in reading), and their use in `artpiped.py` and
`ops_watch.py` (`artpipe_signin_reading`, key `queues.artpipe.signins_bad`). Tests of the same names:
`src/RimMandrake/Utils/artpipe/selftest_artpipe_signin.py`. The door itself, its sign-in renewal and its picture
ownership: `~/dev/Dispatch/design/specs/2026-11-23-one-codex-door/boundary.md`.

The split: the queue, the prompt, the gates, the meter reading, the retries and the registry stay in the daemon. Finding
Codex, the sign-in, the image slots, the picture's ownership and the failure causes are the door's. The daemon names no
sign-in folder, and it never reads or writes an `auth.json`.

## ACCEPTS

- **a-worker-command.** A script with the command line of `codex_image.py` (MandrakeWorkflows). Its last stderr line
  `[image] VERDICT=<OUTCOME> KIND=<kind> exit=<n>` is the typed result. A worker without that line reads kind None, and
  the daemon's older text rules decide.
- **a-codex-home-for-tests.** `--codex-home DIR` overrides the one sign-in folder. Production passes none.
- **the-door-log.** One JSON file for each call under `<log dir>/<YYYY-MM-DD>/`, with `t`, `home`, `outcome`.

## PROMISES

- **a-could-not-start-call-spends-no-attempt.** A worker that could not start (no sign-in, no door, full queue) sends the
  job back to `pending/`, files nothing as failed, and turns the Codex channel off until the ready check passes.
- **a-dead-login-fails-no-job.** A worker whose verdict is AUTH does the same. On 2026-11-20 one dead login failed 60 of
  60 jobs.
- **a-channel-comes-back-without-a-restart.** The running daemon turns the channel on when the ready check passes, and
  the waiting job renders.
- **a-home-without-a-signin-is-not-ready.** The ready check refuses a missing or unreadable sign-in by name. It is a file
  read; it launches nothing.
- **n-workers-share-one-home.** N jobs run at the same time on one sign-in folder, and all of them finish.
- **a-dead-signin-reads-red.** The reading is MEASURED 1 when the sign-in is gone or unreadable, or when the last call
  that could tell ended AUTH. A call that says nothing about the login does not clear it.
- **a-live-signin-reads-green.** A sign-in with no such failure reads MEASURED 0. No token is printed.
- **a-later-answer-clears-it.** A later answered call, or a renewed sign-in, reads 0.
- **a-log-that-cannot-be-read-is-unmeasured.** A log or a door that cannot be read is UNMEASURED with its cause, never 0.
- **the-call-is-typed.** The worker's verdict line decides the kind; a hung worker is killed; production names no
  sign-in folder.

## LIMITS

- `SLOT_WAIT_S` 3600 s: how long a picture waits for one of the door's image slots. Danger: a stuck holder would hold a
  daemon worker for ever. The outer kill is the picture deadline plus this wait plus 30 s.

## DOES NOT SURVIVE

- A login that the server revoked with no call since: it reads live until a call fails on it.
- A login that stays dead: the channel tries one job each `PREFLIGHT_RECHECK_S` (300 s). The alarm rings.
