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
