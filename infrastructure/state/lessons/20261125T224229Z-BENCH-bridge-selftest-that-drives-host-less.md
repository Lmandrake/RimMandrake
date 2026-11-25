A bridge selftest that drives a host-less take (game a) must pin RM_HOST=archmagi in its env: on SteveDesktop a host-less take means Steve1 and takes no Archmagi driver lock, so such tests went red there for the machine, not the code (fixed in 955d54f81c for driver_lock, pipe_hold, no_owner_presence)
item: BRIDGE_LOCK_HARDEN_ALIVE_MEANS_A_PID
home: NONE
