## Finding
A fresh window that dies during its wake loses the message. Proved by real SIGKILL
(`selftest_seat_restart_death.py`) and by TLC (cases death_wake_safety/live: S5 and L3 fail).

After `woken_at` is stamped, the same generation is refused ("not replayed"). Before it is stamped, the O_EXCL tile
marker refuses a second relaunch, and a no-token window gets only a pointer, not the message.

## Fix idea
Mark woken only after the first answer, and allow replay of an unanswered generation.

## verify
- L0: GAP_WAKE rows in selftest_seat_restart_death.py flip to "message read"; death_wake_safety/live flip to ok.

## criteria
- Killing the fresh window before and after woken_at, a replacement still reads the message.
