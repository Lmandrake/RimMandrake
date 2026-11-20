# No core-voltage change was made on SteveDesktop — 2026-11-15 ~20:40Z (12:40 PST)
Item STEVE_LANE_UNSTICK_BRAKED_UNOWNED_EB2A. Before state: BEFORE_STATE.md (this folder). Nothing to undo.

Why stopped (brief: "if no unattended reversible route exists, stop and report"):
1. MEASURED: Intel's servers refuse scripted downloads of XTU. winget install Intel.IntelExtremeTuningUtility 7.14.2.69 on Steve:
   0x80190193 Forbidden (403) (install_xtu.out). Direct fetch of xtusetup_7.14.2.69/.93.exe and the intel.com download page:
   403 AccessDenied from both Archmagi (curl, browser UA + referer) and Steve (Invoke-WebRequest) (dl_xtu.out). XTU was NOT installed.
   Left behind on Steve: empty folder C:\SteveDesktop\diag\xtu and log C:\SteveDesktop\diag\logs\xtu_install.log (if winget wrote it). Harmless.
2. MEASURED: a Windows hypervisor runs on Steve, because WSL2 (VirtualMachinePlatform, Ubuntu running) hosts Steve's
   seat-server (claude remote-control) and seat-runner (SteveDesktop-Run) tmux sessions (probe2.out, probe3.out).
   GUESS ~80% (forum evidence, consistent but not Intel-documented): while the hypervisor runs, Windows blocks MSR 0x150,
   the one register XTU and ThrottleStop use for a core voltage offset, so XTU would install and then show voltage locked
   or silently not apply. Workaround in every report: `bcdedit /set hypervisorlaunchtype off` + reboot, which stops WSL2,
   i.e. takes down Steve's Claude seats. That is a bigger change than the brief allowed, so it was not made.
   Sources: community.intel.com "Intel XTU and Microsoft Windows WSL2 are incompatible" (m-p/1414021),
   "XTU Vcore offset adjustment lost after Hyper-V role installed" (m-p/1329396); techpowerup ThrottleStop threads.
3. UNMEASURED: whether the BIOS has set the overclocking lock (would block the offset even with the hypervisor off).

What a working route would need (Conductor's call, not taken):
  a) a browser-side XTU download (Intel blocks scripts), copied to Steve, Authenticode-checked as Intel;
  b) `bcdedit /set hypervisorlaunchtype off` + reboot (undo: `bcdedit /set hypervisorlaunchtype auto` + reboot; sshd is native
     Windows OpenSSH, so ssh survives), accepting Steve's WSL2 seats are down while it is off;
  c) XTUCLI offset +25 mV, read back, re-applied at every boot by a startup task (XTU offsets do not persist through a reboot by
     themselves; the fault monitor reboots Steve routinely).
  Or the BIOS route (one hands-on visit: +vcore offset there persists and needs no hypervisor change).
Reading to watch if anything is applied: fault_monitor windows per day vs ~2.5/day (2026-11-12T16Z..2026-11-15T20Z).
