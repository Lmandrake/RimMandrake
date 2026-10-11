A live sidecar/server process rewrites its state file and clobbers hand-added top-level keys (the freeze race): freeze, wait, re-read, then PROBE the endpoint (frozen refusal, no leak) before trusting the freeze. Source: BENCH_REBOOT_HANDOFF_202609110230.md
home: skills/frozen-artifacts/SKILL.md
