# CLOSE_SHA_FIX_HEAD_FALLBACK_CLAIM_COMMITS

FOUNDRY_CLONE_SYNC_STALE_TIMERS closed at 7ad67fa2fcfd and FOUNDRY_SHARD_RESCUE_STRANDED_EVENTS at 428ae1dd476b. Both are ledger-only claim commits, not the fix: the `close --sha` silent fallback to `git rev-parse HEAD` at call time (see using-rimflow, close --sha rules).

Do: (1) `git show --stat` both shas to confirm; (2) find the real fix commits and `note` them on each item; (3) from now on commit the fix first, then `close --sha $(git rev-parse --short HEAD)`.
