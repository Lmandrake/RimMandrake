# RIMMANDRAKE_FIX_JAWABENCH_AWARENESS_INSTALL_CRASHES_START

## spec
SteveDesktop game A (FlowWorks tier, 12 mods) crashed natively ("Crash!!!" in Player.log, UnityPlayer stack) during
startup on 2 of 4 launches, 2026-11-11 21:11 and 21:27 PST; an immediate `steve.sh restart` came up clean both times.
Both crashes follow the last JawaBench startup line `[JawaBench] map awareness: complete by bridge-registration ...`;
the 21:27 stack runs `JawaBench.BridgeTools.JawaBenchAwareness/<>c__DisplayClass32_0:<Install>b__11` <-
`JawaBenchTpsInstall:Run` <- `JawaBenchAwareness:Install` <- `RimBridgeServer.RimBridgeExtensionDiscovery:TryCreateInstance`
(the 21:11 stack showed the same TryCreateInstance path). So the awareness/TPS Harmony install, run from the bridge's
provider construction, intermittently takes the game down. Both crashes were on the first `up` after `steve.sh deploy`
(game down + FlowWorks deploy); the restart includes another `down` first. Unproven whether that matters.

Found by CLAUDE_STEVEDESKTOP_FWLIVE while proving PIT_DEEPSTONE_BUILD_DIGGING_FINALLY_PAYS. Logs:
`D:\ClaudeWork\rimmandrake\whittle_claude\CLAUDE_STEVEDESKTOP_FWLIVE\up.log`, `...\up3.log`.
NEXT: read the crash report under `C:\Users\sjlewis\AppData\Local\Temp\Ludeon Studios\RimWorld by Ludeon Studios\Crashes` on
SteveDesktop and the `<Install>b__11` lambda in JawaBenchAwareness.cs; check whether it patches from a non-main thread.

## 2026-11-11 22:00 -0800 — third crash, a pattern
A third crash at 21:58 PST, this time earlier (right after `[FlowWorks] hose essential patches`, before the FlowWorks
Harmony count line), so the JawaBench awareness frame is not the only crash site. Across this sitting the first `steve.sh up`
after a `steve.sh deploy` crashed 3 of 3 times, and every `steve.sh restart` (down, init, up) came up clean (4 of 4).
Separately, run 4/5 at 21:29 and 21:33 had a fresh quicktest map come up with `Verse.MapDrawer.get_SectionCount` NRE
in FinalizeInit (every bridge batch op then NREs); a restart cleared it.
