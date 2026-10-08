# Placeholder follow-through (2026-10-07 night)
- [x] 1 daemon restart: `systemctl --user restart --no-block rm-artpiped`; artpiped sets stop_event on SIGTERM/SIGINT, stops claiming, drains in-flight jobs, exits; unit has TimeoutStopSec 15min, so no job lost. Draining at 23:25, systemd then starts the new process with the placeholder_output validator.
- [x] 2 58 jobs queued (phfix_*), 29 textures x a/b, priority 0. Reuse: RM_SekkulaathTank <- RM_SekkulaathYoungCask, RM_GlowTank <- RM_SunSphere_v2_south.
- [x] 3 placeholder_plants.md updated (section C).
