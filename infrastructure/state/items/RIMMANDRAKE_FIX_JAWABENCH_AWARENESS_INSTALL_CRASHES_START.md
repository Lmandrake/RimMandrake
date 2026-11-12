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
