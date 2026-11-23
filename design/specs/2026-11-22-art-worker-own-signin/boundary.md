# BOUNDARY: one Codex sign-in per art worker home, never copied, and the dead-sign-in alarm, Design Version 0.1.0

Code: `src/RimMandrake/Utils/artpipe/signin_health.py` (`lineage`, `record_outcome`, `check`, `main`),
`src/RimMandrake/Utils/artpipe/artpiped.py` (`worker_signin_startup`, `codex_image_base_home`, `_StaleRefreshGuard`'s
exit), `src/RimMandrake/Utils/ops_watch.py` (`artpipe_signin_reading`, called by `c_queues`) and the target
`queues.artpipe.signins_bad` in `src/RimMandrake/Utils/ops_watch_rules.json`. Item:
`RIMMANDRAKE_TEST_ART_WORKERS_SHARING_ONE_CODEX_LOGIN_NOT_FIVE`, written 2026-11-22 from the study
`design/specs/2026-11-22-art-pipeline-and-dispatch/study.md` §4 ("smallest safe act", step 1). The copy sites removed
live outside this repo, in `~/dev/MandrakeWorkflows/skills/generating-images/scripts/codex_image.py`
(`seed_codex_home` no longer copies `auth.json`; `resync_stale_worker_homes` is deleted); this page's tests exercise
them through the daemon. Each promise has a test of its name in
`src/RimMandrake/Utils/artpipe/selftest_artpipe_signin.py`. The red run of the first three promises on the parent
(`1210e043a0f3`'s code) is `red_run_parent.txt` beside this page.

Why: OpenAI, "Use one auth.json per runner or per serialized workflow stream. Do not share the same file across
concurrent jobs" (developers.openai.com/codex/auth/ci-cd-auth). ChatGPT refresh tokens rotate; two homes on one
lineage cannot both refresh. All five worker homes held copies of the GPT consults' lineage and died 2026-11-20 (60 of
60 jobs: "refresh token was already used"); the owner signed in all five by device on 2026-11-21. The daemon's
start-up resync would have copied one of those five over the other four at its next restart.

## ACCEPTS (the only inputs these readers are built for)

- **a-worker-home-root.** A folder (default `~/.codex_workers/artpipe` on the Linux route, from
  `common._default_codex_home_root`) whose worker homes are the subfolders named `w<N>`. Other names are not homes.
- **a-codex-auth-json.** A home's `auth.json` in Codex's ChatGPT shape: `tokens.refresh_token` a string. Its value is
  read only to make a 16-hex digest (the lineage); it is never printed, logged or stored.
- **a-base-home.** The shared Codex home (`codex_image.base_codex_home`, `~/.codex` on the Linux route), or none.
- **the-outcome-record.** `<home>/.artpipe_signin.json`, written by the daemon after each codex job: `ts`,
  `auth_failed`, `lineage` (the digest at the job's end), `job`.

## DOES NOT SURVIVE (not promised)

- **a-sign-in-revoked-with-no-job-since.** A sign-in the server revoked reads live until a job on that home fails on
  sign-in. The reader makes no network call and never refreshes a token: a probe that refreshed would race the worker
  using the same file.
- **the-running-daemon-before-its-restart.** The daemon started 2026-11-19 holds the old code in memory: its mid-run
  guard can still copy a rotated sign-in over the other homes, and it writes no outcome record. Both change when it
  next starts (its unit runs `./sync` first).
- **a-windows-worker-home.** The Windows `codex.exe` route is not read or tested here. Its seeding also stops copying
  `auth.json` (the same function), so a new Windows home is refused before any sandbox step.
- **a-new-slot-before-its-sign-in.** Raising `-N` past the signed-in homes leaves a new `w<N>` with no sign-in: its
  jobs fail and the alarm counts it, until someone runs the device sign-in for it.

## PROMISES (each one is owed a test of the same name)

- **a-restart-leaves-every-worker-signin-untouched.** The daemon's start-up sign-in step (`worker_signin_startup`)
  reads every worker home and writes no `auth.json`: five homes with five lineages of different ages are
  byte-identical after it, and five live own sign-ins raise no warning.
- **a-mid-run-rotation-copies-no-signin.** A guarded job whose own home rotates its token changes no other home's
  `auth.json`.
- **a-new-worker-home-is-never-seeded-with-a-signin.** `codex_home(<a home with no auth.json>)` and `seed_codex_home`
  copy config but never `auth.json`, and refuse by name with the device sign-in command (`codex login --device-auth`);
  `auth.json` is not in `HOME_SEED_FILES`.
- **a-dead-signin-reads-red.** Each planted fault reads its own verdict and counts in the point: no `auth.json`
  (`no_signin`, also a bare leased `w<N>` folder), a torn file (`unreadable`), a lineage also held by another worker
  home or by the base home (`shared`, both homes), and a last job that failed on sign-in on the current lineage
  (`auth_failed`). `queues.artpipe.signins_bad` is MEASURED and equals the count of bad homes.
- **a-live-signin-reads-green.** Five own lineages, a base on a sixth and clean last jobs read `live` for every home;
  the point is MEASURED 0; neither the point nor the command line prints a token, and the command exits 0.
- **a-new-signin-clears-an-auth-failure.** The guard's exit writes the outcome record for every job that ends without
  an exception (`auth_failed` as `process_codex_job` set it); a home that failed reads `auth_failed` until a device
  sign-in gives it a new lineage, then `live`. The record holds no token.
- **a-root-that-cannot-be-read-is-unmeasured.** An absent root makes the point UNMEASURED with its cause (never 0) and
  the command exit 2; a root with no homes is MEASURED 0 with `homes` 0.
