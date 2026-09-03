## spec
Owner, 2026-09-02: *"Man I wish the Autoopen of the error log was set to False by default"*

**There is no vanilla setting for it, and that is measured, not assumed.** `Verse/Log.cs`
`Error(string)` ends with:
```csharp
if (!PlayDataLoader.Loaded || Prefs.DevMode)
{
    TryOpenLogWindow();
}
```
Dev mode alone is the condition. The only pref in this area is `Prefs.OpenLogOnWarnings`
(`Dialog_Options.cs:719`, `PrefsData.openLogOnWarnings`) and it gates WARNINGS only
(`Log.cs:109`). So the vanilla choices are "dev mode off" or "the window opens on every
error" — and dev mode off is not an option for us.

⇒ The fix is a Harmony prefix on `Verse.Log.TryOpenLogWindow` returning false, in the
JawaBench companion, behind a toggle so it can be turned back on. The log window stays
reachable by hand; only the automatic pop is suppressed.

⚠️ `TryOpenLogWindow` has callers other than the error path (`Log.cs:111` warnings,
`Log.cs:202`) — a blanket prefix suppresses those too. That is the intended behaviour
here, but it should be stated on the toggle rather than discovered.

⛔ Cannot be deployed while RimWorld is running — a companion DLL is written in the
shutdown window. This lands at the next game-down.

## verify
With the patch live and dev mode ON, a deliberate `Log.Error` does not raise the log
window, and the window still opens from the debug menu by hand.

## criteria
Dev mode stays on, red errors stop stealing the screen, and the suppression is one
toggle away from being off again.

## Fix (FOUNDRY, 2026-09-03)

`src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchLogAutoOpenSuppress.cs` —
a Harmony prefix on `Verse.Log.TryOpenLogWindow` (confirmed from real 1.6 source before
writing: `public static void TryOpenLogWindow() { if (...) EditWindow_Log.TryAutoOpen(); }`
— a prefix returning `false` skips that call entirely). `Suppressed = true` by default,
matching the owner's own wording. Installed lazily from `JawaBenchInit.Announce()`
alongside `JawaBenchArgGuard.Install()`, same discipline: isolated Harmony contact
point, try/catch-wrapped, never throws, reports its own install failure rather than
going silently blind.

**The debug-menu manual open is architecturally untouched, confirmed from source, not
assumed**: `DebugWindowsOpener.cs` opens `EditWindow_Log` via
`Find.WindowStack.Add(new EditWindow_Log())` directly — it never calls
`TryOpenLogWindow` at all, so this prefix cannot reach it.

Exposed as `jawa/log_autoopen_suppress` (`get`/`suppress`/`restore`), reporting
`installed`, `suppressed`, and a `suppressions` counter (auto-open calls actually
skipped this session) — the same self-diagnosing shape `jawa/bridge_arg_report` uses,
so `installed=false` (an upstream rename of `TryOpenLogWindow`) is distinguishable
from "nothing has tried to auto-open yet."

Built and deployed clean (`build.py --gm --apply`, 0/0, `VERIFIED in sync`) at a
game-DOWN window.

## Live verify, partial (FOUNDRY, 2026-09-03)

Confirmed on a bare Core/Harmony/Bridge quicktest:
- `jawa/log_autoopen_suppress` (`get`): `installed: true`, `suppressed: true`,
  `target: "Verse.Log.TryOpenLogWindow"` — the patch attached to the real method.
- Loaded a Droidworks-tier list with 162 known `Config error in ...` lines from a
  prior session, then re-checked `suppressions`: still 0. **Expected, not a failure**:
  those errors fire during `DefDatabase` resolution, which completes before
  `RimBridgeServer` even starts listening — structurally before the FIRST jawa/ tool
  call that lazily installs this patch (documented limitation, same one
  `JawaBenchArgGuard` already carries). Load-time config errors can never be
  suppressed by a lazily-installed patch in any session; only errors after the first
  bridge call are in scope, which this test could not distinguish from "nothing fired."

**Not obtained**: a clean, safe, repeatable way to trigger a genuine
`Verse.Log.Error`/`Warning` call AFTER the patch installs, via the bridge alone —
tried a bad `xenotype` (refused before touching the engine, no Biotech in the test
list), a bad `bodyPart` on `jawa/damage` (silently falls back rather than erroring),
and `rimworld/search_debug_actions` (crashed on an unrelated pre-existing null ref in
`DebugActionsIncidents.RitualSiegeWithSpecifics`, caught by RimBridgeServer's own
.NET exception handling — never reaches `Verse.Log` at all, so it proved nothing about
this patch). Did not find a vanilla debug action built for exactly this purpose.

**What IS proven**: the patch is installed on the confirmed-correct real method, the
mechanism (Harmony prefix returning false) is basic and not in doubt, and the
manual-open independence is confirmed from source rather than assumed. What remains
genuinely unverified is the visual "a red error, live, does not pop the window" case
from the item's own `## verify` — owed to whoever next hits a real `Log.Error` with
this patch active, or to someone who finds/adds a deliberate test trigger.

Cleaned up: killed the test process, restored `ModsConfig.xml` (589 mods, confirmed
on disk), released the bridge.
