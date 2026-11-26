# Boundary for a lane job whose companion left origin/main

Code: `follow_main` and the part of `admit` that calls it in `src/RimMandrake/Utils/testq/testq.py`. Tests:
`src/RimMandrake/Utils/testq/selftest_companion_stage.py`.

## ACCEPTS

A pending testq job. Its `source_sha` is a commit that the run must include (`submit --sha`).

## DOES NOT SURVIVE

- A companion source commit that lands after the job is admitted. The worker then judges the job at its own sha.

## PROMISES

- **A chains job follows origin main.** Its companion left origin/main while it waited, and its sha is on origin/main: it
  runs at origin/main. It does not die INVALID DEPLOY for the wait that the lane gave it.
- **A follower waits for its companion.** While origin/main's companion is not staged, the job stays pending with its
  reason. It runs once the stager has staged that companion.
- **A build tied job keeps its sha.** A visit's job, a proof build, a checks job, a proofs job and a job at an unpublished
  sha never run at another sha. When the job's own companion is on Steve1, the job runs. On Steve2 the job is admitted
  as before, and the worker judges it, because the probe reads only Steve1's copies.
- **A build tied job whose companion left origin/main is cancelled unspent.** On Steve1, when the job's companion is not
  on SteveDesktop and differs from origin/main's companion, the job is cancelled at admission. The cancel record names
  the reason. The stager stages only origin/main's companion, so the worker could only refuse the job at deploy.

## LIMITS

- The 60 second timeout on the local `git rev-parse` is a hang guard.
