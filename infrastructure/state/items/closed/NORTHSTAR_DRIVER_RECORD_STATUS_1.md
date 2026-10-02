# NORTHSTAR_DRIVER_RECORD_STATUS_1

## spec
`northstar_driver` writes its results JSON but does not record the run in the modcheck status registry, so `modcheck status` cannot show a driver run, and `design/RimMandrake/debug_process.md` defines the new-content pause lifting in terms of a recorded run per mod. Make the driver record each run (mod, hash, verdict per bar, results path, mode) through modcheck's existing status code (`modcheck/status.py`), never by hand-editing the registry file, and without swapping the live mod list (`modcheck run` does).

## verify
Offline selftest with the mock transport; one live Graffiti run, then `python3 -m modcheck.cli status` shows it.

## criteria
`modcheck status` lists driver runs at the mod's current hash; a stale hash reads STALE; a run with UNMEASURED bars is not GREEN.
