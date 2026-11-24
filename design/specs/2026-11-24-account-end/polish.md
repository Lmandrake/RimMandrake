# Polish: the end of an account

- `simulate()` and `pool()` still model an account as burning to its own line, not to its warning line (at most 2 points a week).
- The order text can read "about 1 minutes" (singular).
- A role run (`rm-role-*`) gets the orders but is not waited for; the drain waits for `rm-detached-*` only, as before.
- The emergency order still says "At <time> the run is killed" after a HOLD or a lapsed switch (fresh reader, 2026-11-24).
- A newer account-end order masks an earlier `pipe stop` order on the same unit: the hook reads the newest row only.
- The "stop in place of the switch" path leaves `account_end` in the state until the next episode end.
- After a HOLD of hours in the pause, a resumed emergency gives new runs no pause.
- A ledger note that is refused each time is tried again each 5 min.
- With another account at exactly 3%, the live account's wait floor can read 1 for 2.
