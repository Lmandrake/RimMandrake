# ARTPIPE_WORKER_AUTH_STALENESS_1

Stale worker-home `auth.json` capped real artpipe concurrency at 3 via refresh-token races.

## What is true

MEASURED 2026-09-26. Raising `artpiped.py -N` from 3 to 8 produced 5 instant failures
(6-16 s), identical verbatim on all five:

```
ERROR: Your access token could not be refreshed because your refresh token was
already used. Please log out and sign in again.
2026-09-26T20:21:27.528214Z ERROR codex_login::auth::manager: Failed to refresh token
```

Each worker slot leases its own `CODEX_HOME` (`w0`..`w63`, `common.acquire_codex_home_lease`)
and each holds its own `auth.json`. Decoding them:

| Home | `last_refresh` | token `exp` | `chatgpt_plan_type` | outcome |
|---|---|---|---|---|
| w0, w1, w2 | 2026-09-26 11:04 | 10-06 | `prolite` | all succeeded |
| w3, w4, w5 | 2026-09-24 06:02 | 10-04 | `plus` | failed on refresh |
| w6, w7 | 2026-09-14 00:35 | 09-24 (expired) | `plus` | failed on refresh |
| base `~/.codex/auth.json` | 2026-09-14 00:35 | 09-24 (expired) | `plus` | — |

Exactly three homes held a live token; exactly three of eight jobs succeeded. **The
observed concurrency ceiling of 3 was this, not the subscription** — the account meter sat
at 12% throughout and refused nothing.

Codex attempts a refresh when `last_refresh` is more than roughly a day old (w0-w2 at ~9 h
did not refresh and worked; w3-w5 at 2 days did and failed) even when the access token is
still valid. ChatGPT refresh tokens are single-use and rotate, so several homes sharing one
lineage cannot refresh concurrently — the first wins and the rest get the error above.

## What was done

Every `auth.json` under `C:\Users\Mandrake\.codex_workers\artpipe\` was backed up to
`C:\Users\Mandrake\.codex_workers\artpipe_authbackup_1790454277\`, then `w1`..`w31` were
re-seeded from `w0`'s live `prolite` token. N=8 then ran 8/8 concurrent cleanly, and N=32
ran 32/32 with no auth error at all.

## Why it is still open

Those 31 homes now share ONE refresh-token lineage. They do not need to refresh while the
seeded access token is valid (`exp` 2026-10-06), so this will recur as that date
approaches, and the failure will look exactly like a rate limit again.

## NEXT

Make the daemon keep worker homes fresh rather than relying on a manual re-seed: on start,
re-seed each slot's `auth.json` from the most recently rotated home, and **stagger first
use** so no two homes attempt a refresh simultaneously. A home whose `last_refresh` is
older than ~12 h should never be handed a job concurrently with another such home.

🔑 Diagnostic for whoever hits this next: an auth-plumbing ceiling and a rate-limit ceiling
look identical from the queue. Tell them apart by reading `primary_used_percent` (it did
not move) and the worker's verbatim stderr (it names the refresh token, not a 429).
