# Yes, do the BIOS upgrade on SteveDesktop: it is worth doing, but it may not cure the fault

**Board:** ASUS ROG STRIX Z490-G GAMING (WI-FI). **Now:** BIOS 0607 (June 2020), ME 14.0.33.1125, microcode 0xC8. **Target:** BIOS 3401 (2026/08/19), ME 14.1.79.2540, microcode 0x100. Go straight to 3401.

## Will it fix the fault?

- **Known:** the running microcode is six years old and Windows is not loading anything newer. 3401 carries Intel's latest for this i9-10900K (read from the file itself). It closes years of security fixes, and ASUS lists stability work in several versions in between.
- **Likely:** a reboot clears the fault, it moved from CPU 18 to CPU 2, and the partner thread stayed clean. That looks more like per-thread state than plain burnt-out silicon. New microcode could plausibly help.
- **Not known:** whether it helps at all. Intel documents no erratum matching this fault, and no release note claims this fix. A degraded CPU is neither proven nor ruled out.
- **The test:** only a run past the old onset time can tell. If the fault returns on 3401, suspect the CPU.
- **13th/14th-gen Vmin problem:** does not apply. This is a 10th-gen chip, with no extended warranty. Boxed Intel warranty is generally 3 years. The install dates from about August 2020, so it has probably lapsed: check at https://supporttickets.intel.com/s/warrantyinfo?language=en_US

## Agents do this first (you do nothing)

Done: both files downloaded, and their hashes match ASUS's published values. BitLocker is off, so there is nothing to suspend. The stick already in the machine has 6.3 GB free. Its files stay; one is added.

Owed just before your visit: pause the test lane, reboot for a clean CPU, copy the files to `C:\SteveDesktop\diag\bios`, run `stage_on_steve.ps1`, run the ME tool (ASUS requires this before the BIOS), reboot, confirm ME 14.1.79.2540, then shut the machine down. **Do not start until the agent says it is ready.**

## At the machine (about 15 minutes; needs a keyboard and monitor)

1. Confirm the PC is off, with the power supply switched on and plugged in. Do this when no storm or power work is likely.
2. Move the USB stick to the **BIOS FlashBack port** on the back: the port marked on the I/O shield, the bottom USB-A port immediately left of the small round button.
3. Hold that small button for **3 seconds**, until its light blinks three times, then let go.
4. **Wait until the light goes out.** The manual gives no duration; expect several minutes. **Do not** unplug anything, press power or clear CMOS while it blinks.
5. Press the power button. The first boot may restart by itself and sit on a black screen for a while. Leave it.
6. At the logo press **Delete**. If you get a message about settings, press **F1**. If it shows EZ Mode, press **F7** for Advanced Mode.
7. Set these. **The flash resets everything, and two of the new defaults would hurt us.**

| Menu | Setting | Set to | Why |
|---|---|---|---|
| Advanced → CPU Configuration | Intel (VMX) Virtualization Technology | **Enabled** | New default is Disabled, which **stops WSL and the agents** |
| Advanced → APM Configuration | Restore AC Power Loss | **Power On** | New default is Power Off, so it would stay dark after an outage |
| Advanced → APM Configuration | ErP Ready | **Disabled** | Already was; check it |
| Advanced → APM Configuration | Power On By PCI-E | **Enabled** | Wake-on-LAN |
| Boot → Boot Configuration | Wait For 'F1' If Error | **Disabled** | Stops a keyboard prompt blocking an unattended boot |
| Ai Tweaker | ASUS MultiCore Enhancement | **Disabled – Enforce All limits** | Optional, your call: holds the CPU to Intel's limits, which is kinder to a suspect chip but costs some speed |

8. Press **F10**, select **OK**. Windows starts by itself. Tell the agent. Leave the stick wherever you like.

**Wake-on-LAN only works over a cable.** The machine is on Wi-Fi and its Ethernet port shows disconnected. Plug in an Ethernet cable on this visit, or the setting does nothing.

**What you lose:** BIOS settings only, restored above. Windows and files are not touched. Treat the upgrade as one-way; going back to 0607 is untested.

## If something goes wrong

- **Light flashes about 5 seconds, then stays solid:** FlashBack did not start. Power off fully, try the stick again in the same port, repeat from step 3. Tell the agent, who can try the fallback below or use another stick.
- **Power lost during the flash, or no picture afterwards:** repeat steps 2 to 4. FlashBack works without the CPU or Windows.
- **Windows will not start:** press **F8** at the logo and pick **Windows Boot Manager**, then check Boot order in the BIOS.
- **Fallback if FlashBack will not run:** in the BIOS, Tool → ASUS EZ Flash 3 Utility, choose the stick, choose `SZ490GW.CAP`, confirm.
- **Still dead:** ASUS service. Do not clear CMOS as a guess. The board manual covers CrashFree BIOS 3.

## Agent, straight after the visit

Confirm remote access returned without a hand. Read BIOS 3401, ME 14.1.79.2540 and microcode 0x100. Confirm VMX and WSL work, the seats are back, and the settings table took. Remove `SZ490GW.CAP` from the stick. Run the memory and CPU checks in `C:\SteveDesktop\diag`, unpause the lane, then watch for the fault past the old onset time.

Files, on this PC: `D:\ClaudeWork\rimmandrake\steve_diag\bios\x3401\ROG-STRIX-Z490-G-GAMING-WIFI-ASUS-3401.CAP` (SHA-256 `27231cff70f52a2b60e0d7d629e7982332e6e1d9ee7b660d623c18e2e6ac52b5`), `D:\ClaudeWork\rimmandrake\steve_diag\bios\files\MEUpdateTool_14.1.79.2540v5_T.zip`, `D:\ClaudeWork\rimmandrake\steve_diag\bios\stage_on_steve.ps1`. Source: https://www.asus.com/us/supportonly/rog%20strix%20z490-g%20gaming%20%28wi-fi%29/helpdesk_bios/
