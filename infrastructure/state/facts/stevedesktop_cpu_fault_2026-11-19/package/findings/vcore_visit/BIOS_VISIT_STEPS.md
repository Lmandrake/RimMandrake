DONE 2026-11-17 7:28 AM PST by the owner at +0.100 V (the ceiling), not 0.050. Offset mode, sign +, 0.100 V; saved; rebooted. There is no second voltage visit.

# SteveDesktop: one BIOS visit, raise CPU core voltage one small step (about 10 minutes)
Board ASUS ROG STRIX Z490-G GAMING (WI-FI), BIOS 3401, CPU i9-10900K. Menu names are from ASUS's own BIOS manual for this
board (E16801) and user manual (E16474), downloaded 2026-11-15. You need a wired USB keyboard (Bluetooth does not work in BIOS).
Why: the CPU makes errors at about 1.01-1.03 V and 42-46 C, a low-voltage pattern. A little more voltage may stop that.

## Do this
1. In Windows: Start > Power > **Restart** (Restart, not Shut down). As soon as the screen goes black, tap **Delete** about
   twice a second until the BIOS screen appears. (F2 also works.) Missed it? Press Ctrl+Alt+Delete and try again.
2. If the screen is the simple "EZ Mode" page, press **F7** to switch to **Advanced Mode**.
3. Along the top menu bar (My Favorites, Main, Ai Tweaker, Advanced, Monitor, Boot, Tool, Exit), choose **Ai Tweaker**.
   (On this board it is "Ai Tweaker", not "Extreme Tweaker".)
4. Scroll down past the memory items and the "Tweaker's Paradise" line to **CPU Core/Cache Voltage**. It should say [Auto].
   Set it to **[Offset Mode]**. Two new lines appear right under it:
5. **Offset Mode Sign**: set to **[+]**.
6. **CPU Core Voltage Offset**: select it, type **0.050**, press Enter. It must read 0.050 (not 0.500, not 0.005).
7. That is the only change. Do NOT touch anything else, in particular:
   - the lower block **CPU Graphics Voltage Mode**, which has its own "Offset Mode Sign" and offset (wrong one);
   - DRAM Voltage, CPU VCCIO Voltage, CPU System Agent Voltage, Ai Overclock Tuner, SVID Behavior, Extreme Over-voltage;
   - F5 / "Load Optimized Defaults" (resets every setting), and the CPU_OV jumper on the board.

## Check, save, boot
8. Before saving, the three lines should read: CPU Core/Cache Voltage [Offset Mode]; Offset Mode Sign [+];
   CPU Core Voltage Offset 0.050. Nothing else on the page should have changed.
9. Press **F10** (= Exit > Save Changes & Reset). A confirmation window appears; it should list only those three items
   (the listing is UNVERIFIED for this board; if it shows anything else, press Esc and fix it). Select **OK**.
10. Normal boot: the machine restarts, the small Q-LEDs on the board (CPU, DRAM, VGA, BOOT) may flash briefly and go out,
    the ROG logo shows, Windows reaches its usual login or desktop within about a minute or two. Leave it there.
11. Tell Luke (or the Conductor) the time you pressed OK. That is all; you are done.

## Undo (if asked, or if Windows misbehaves)
- Restart, tap Delete, F7, Ai Tweaker, set **CPU Core/Cache Voltage** back to **[Auto]** (the two extra lines disappear),
  F10, OK. That is exactly the old state.

## If it does not boot (black screen, or a Q-LED stays lit for more than 2 minutes)
A. Hold the power button 5 seconds to turn off. Power on and tap Delete. If the BIOS appears, do the Undo above.
   (Some ASUS boards show "Overclocking failed, press F1 to enter setup"; if you see it, press F1 and do the Undo. UNVERIFIED here.)
B. If the BIOS will not appear: clear CMOS. Shut down, unplug the power cord. Find the 2-pin header printed **CLRTC** on the
   bottom edge of the board, near the bottom-right corner (user manual page 1-17). Touch both pins together with a
   screwdriver tip or jumper cap for 5-10 seconds. Remove it (never leave a jumper there: the board will not boot).
   Plug in, power on, tap Delete, press F10, OK. Still nothing: also take out the coin battery for a minute, then repeat.
   Clearing CMOS returns every BIOS setting to factory defaults. Measured today: memory already runs at default 2666 MT/s
   1.2 V, so nothing important is lost; Windows date/time may need a resync.

## If step one does not cure it (for us, not the person)
- There is no second voltage visit: +0.100 V was set at once (the ceiling). If faults continue at +0.100, voltage is not the fix
  and the next route is the replacement CPU (option A).

## What we measure afterwards (remote, nothing for the person to do)
- fault_monitor fault windows on SteveDesktop for 24 h after the boot, against the prior rate of about 2.5 a day
  (8 windows 2026-11-12T16Z..2026-11-15T20Z, onsets 0.13-0.88 h after boot). Any window = step one did not cure it.
  Zero in 24 h is a good sign but can happen by luck (about 8% at the old rate), so we keep counting to 72 h (luck under 0.1%).

Why the ceiling at once (owner and Conductor, 2026-11-17): the voltage cost is tiny (turbo is off, the chip runs 3.6 GHz near 1.0-1.1 V, well below the
~1.3 V+ it ran at stock turbo for years), while every visit costs a person's trip. One visit at +0.100 V gives a clean answer: if it does nothing, low voltage is not the cause and we replace the CPU.
