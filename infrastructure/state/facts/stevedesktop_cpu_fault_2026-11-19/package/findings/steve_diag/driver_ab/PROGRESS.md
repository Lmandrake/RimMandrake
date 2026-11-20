> HISTORY: retired era, see design/RimMandrake/retired_eras_index_2026-11-18.md. This file's mentions of Relentless, Artisan, Whittle, FOUNDRY, RimPulse or rimflow v3 are history (that machinery no longer runs); the rest is as current as its own status says.

# STEVE_CRASHES_DIAGNOSE_DEFENDER_FALLS_TOO gen1 — driver A/B (Relentless worker)
## Facts
- RAM test owed by title: DONE 10-31 (memdiag basic 1101/1201 clean; in-OS walks 85+108 GB 0 bad).
- BIOS 3401 onsets 3.30/0.88/2.88 h; fault persists until reboot, wanders CPUs -> state reset by reboot => suspect MSR/IO-poking vendor software (AI Suite asComSvc/AsIO2, Corsair iCUE+CpuIdRemote/cpuz154, LightingService/GLCKIO2/ene, MSIO).
- fault_monitor auto-reboots on fault (rm-steve-fault.timer); report: python3 src/RimMandrake/Utils/testq/fault_monitor.py report
## Plan
1 contract 2 record original StartModes (svc.out) 3 disable+stop vendor services 4 snag --wait-hours ~14 5 later: read report, write facts doc, finish
## Log
- 03:40:20Z vendor callers DISABLED on Steve (disable.out; original modes C:\SteveDesktop\diag\driver_ab_original.json; revert C:\SteveDesktop\diag\driver_ab_revert.ps1). Boot 02:45:13Z. Only Corsair device = keyboard (no AIO), fans fall to BIOS curves. NEXT: facts doc, commit, learn, snag wait.
- 3eabe1a4 published facts doc. NEXT worker: after >=12h uptime w/ callers off (boot 02:45:13Z, A/B 03:40:20Z) read fault_monitor report; fill ## Result; if a window opened after 03:40:20Z => hypothesis falsified (consider revert.ps1); finish.
