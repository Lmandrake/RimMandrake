# Steve CPU-fault diagnosis (helper, 2026-11-15)
Items: RIMMANDRAKE_DIAGNOSE_STEVE_WORLD_START_SIX_MODS_ONE_FAILURE, STEVE_LANE_UNSTICK_BRAKED_UNOWNED_EB2A
## Steps
1 read prior evidence (FIX_STATE.md, fault_monitor) - in progress
2 reach Steve read-only: WHEA, WER, CPU/BIOS, disk
3 six crashes compare
4 advisory check (web)
5 affinity experiment? (one job max)
6 notes on items + commit shards
## Findings
- prior: facts/steve_fault_diagnosis.md: i9-10900K, ROG STRIX Z490-G, 4x32GB F4-2666C18, BIOS 3401. SIMD wrong results acquired in uptime, held till reboot, wander CPUs. RAM clean, no WHEA (10-31). vendor MSR callers A/B falsified 11-04 (System-start drivers AsIO2/GLCKIO2/ene/MsIo64 stayed loaded).
- idea: kernel driver clobbering XMM/AVX state w/o save (software!) fits wander+persist-till-reboot. Test: per-core check w/ affinity... 
- route: ssh stevedesktop (Windows), ssh mandrake@stevedesktop-wsl
- step2 DONE evq.out (hw_20261115/): WHEA-Logger System 0 events/21d (System log 45801 events, sanity ok; Kernel-WHEA op has only boot id 5/42). No BugCheck; KP41 only 11-07. disk 157 hourly (likely WSL vhdx, check). Mem diag clean 10-31 & 11-06. Disks healthy. pagefile 8GB auto, C 113GB free.
  CPU 10900K CPUID A0655 microcode rev bytes ->0x100?, cores=9 lp=18 (core disabled / numproc?). BIOS 3401. RAM 4x32 @2666 1.2V (no XMP).
  App crashes 21d: RimWorld 122, dotnet 49, stevecheck 37, MsMpEng 31(!), python 31. RimWorld mostly 0xe0000001@KERNELBASE+0x25369 (Unity abort), plus AV in burst/d3d11/unknown.
- idea discriminator: run stevecheck-equivalent inside WSL2 guest (separate VP register context) during a Windows-side bad window.
- six crashes (WER, all RimWorld 0xe0000001 KERNELBASE+0x25369 = mono/Unity abort): 11-14 18:14:57Z, 22:56:38Z, 11-15 03:56:48Z, 04:16:40Z, 05:21:52Z, 13:57:54Z. First 5 inside fault windows (after first_bad); #6 outside: boot 08:57Z canary clean before AND after (through 14:05Z), temps 32-39C now.
- windows cover ~68% of the period -> 5/6 inside not significant alone. NEXT: all-app crash times 21d vs fault_windows.json (rate in/out); Defender/stevecheck crashes.
- MEASURED inout.out (scripts/inout.py): watch span 11-01..11-15, window 225 h / clean 123 h. Crashes in-window vs clean: RimWorld 109/4 (15x rate), MsMpEng 14/2, dotnet 13/0, python 12/0, powershell 7/0; all non-RimWorld non-canary apps 56 vs 2 (expected ~38/20). => machine-wide, not mods.
- NEXT: hardware vs machine-wide software (kernel driver/hypervisor clobbering SIMD state). WSL2 guest check during a window?
- microcode running 0x100 = Intel latest for 06-a5-05 (bios/relnote.md, bios/PROGRESS_bios.md); BIOS 3401 = ASUS latest. 10900K is Comet Lake, NOT in Intel 13/14th-gen Vmin advisory. No fw fix exists to apply.
- hypothesis: "per-boot coin flip" (onset 0.13h on 5/9 recent boots, current boot clean 5h) -> boot-time state (uncore/ring/IMC training/voltage), errors on any core -> shared uncore fits better than a core. check stevecheck working set.
- MEASURED mism_parts.out: 10730 canary MISMATCH lines; 3875 differ ONLY in FP part (64 doubles=512 B, L1-resident FMA/div/sqrt) -> not RAM/L3/IMC; core execution or register-state corruption.
- NEXT: WSL2 guest (separate register context under Hyper-V) segfault/trap log vs windows = hw vs root-driver discriminator.
- WSL guest journal (11-14 01:35 PST on): 0 segfault/trap lines, but guest runs ~no compute -> NOT discriminating (low exposure).
- NEXT: crash #6 job J20261115T135012Z-7ecbdd (FlowWorks plot_H_depth_ladder) vs Archmagi control in testq history.
- no Archmagi testq control exists (archmagi_worker has 0 job records); prior helper: game/Harmony/HAR dlls md5-identical Steve vs Archmagi.
- crash #6 job note tail = mono_profiler_init_etw (known: mono JIT abort tail, facts file says read crash.dmp). Side finding: ingest failed to file HARNESS_REPAIR_CAUSE_13905C1C (name check error) - file it.
- MEASURED perjob.out: Steve jobs since 11-01: crash share 15.4% (33/214) overlapping windows vs 5.3% (8/152) outside; 5 of the 8 outside crashes came 6-40 min BEFORE a canary onset (game load detects first) -> ~2% truly clean. Crash #6 (13:57Z) is one of the 3 truly-clean ones so far (no onset through 14:05Z).
- affinity workaround: NOT justified: no WHEA names a core; canary faults hit all 18 LPs (F20261112T222613Z). Not run.
- side bug: ingest repair spawn (ingest.py:395, name from retest.repair_slot = HARNESS_REPAIR_CAUSE_<hex>) refused by mint rule (must be RIMMANDRAKE_...) on 10 jobs since 11-05 -> harness repairs silently not filed. File RIMMANDRAKE_RENAME_INGEST_REPAIR_ITEMS_MINT_REFUSES_THEM.
- verdict: hardware-class ~90%; residual machine-wide sw (driver/hypervisor clobbering vector regs) -> guest canary proposal. Lane stays paused (monitor PASSIVE).
- NEXT: file item, lesson, notes on both items, commit shards.

## 14:20Z DONE
Item RIMMANDRAKE_RENAME_INGEST_REPAIR_ITEMS_MINT_REFUSES_THEM filed; notes on both items + bug item; lesson 44a7c44303 published; BENCH notes landed in d403120931 (another session committed the shard). Lane left paused. Nothing owed by me; owner card owed.
