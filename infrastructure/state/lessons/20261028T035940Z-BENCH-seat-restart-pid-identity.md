Killing a Claude window by pid: bind the pid to Claude Code's own registration (sessions/<pid>.json procStart, same clock ticks as /proc/<pid>/stat field 22 — MEASURED equal) and signal through os.pidfd_open after re-checking the start time; any pid recorded later than the registration can already be a reused pid (GPT review4 HIGH).
home: design/RimMandrake/rimflow_v3_golive_wave1.md
