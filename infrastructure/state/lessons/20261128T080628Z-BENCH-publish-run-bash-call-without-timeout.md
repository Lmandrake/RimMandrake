A ./publish run in a Bash call without a timeout parameter is moved to the background after 120 s and killed at 10 min; its commit stays local and unpushed. Run ./publish with timeout 3420000 under waitalive.py; a bare ./publish then lands the local commit.
item: OPS_SCRATCH_DIRT_MEASURE_AT_END_YOGQ
