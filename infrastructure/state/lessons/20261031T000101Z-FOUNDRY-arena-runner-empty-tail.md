arena judge RUNNER: a failing hidden check's vet record had an empty fix_tail (seen on RP_MISSION_FIXTURE before its reads were traced), so a fail/fail vet gives no reason; capture the check's stdout/stderr tail on failure too.
home: src/RimMandrake/Utils/arena/arena_judge.py
