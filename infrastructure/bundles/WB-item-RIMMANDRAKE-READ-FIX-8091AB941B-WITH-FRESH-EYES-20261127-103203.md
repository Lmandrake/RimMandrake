# WB-item-RIMMANDRAKE-READ-FIX-8091AB941B-WITH-FRESH-EYES-20261127-103203

Done, one group, no restart.

| ticket | outcome | commit |
|---|---|---|
| RIMMANDRAKE_READ_FIX_8091AB941B_WITH_FRESH_EYES | REAL, fixed: no check called `game_instance.prepare`, so a prepare that dropped a seed call passed (promise-untested). Test added; three planted faults in prepare each red, real code ALL PASS (71 ok). File FLAGGED. | e80ac9a651 (test), aa92da9b15 (flag) |

Next: nothing. No reader ticket: a FLAGGED file is never read again.
