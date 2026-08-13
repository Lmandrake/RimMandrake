"""game_focus.py - keep RimWorld rendering so bridge calls can complete.

THE REAL FIX IS A PREFERENCE, NOT THIS MODULE
=============================================
RimWorld ships `runInBackground` **False**. Turn it on -- Options -> Run in
background -- and none of the focus juggling below is needed. Set it in the
game's own menu: RimWorld holds prefs in memory and rewrites `Prefs.xml` on
exit, so editing that file while the game runs gets overwritten, exactly like
`ModsConfig.xml`.

Use `preflight()` before any unattended bridge run. Focusing the window is the
fallback for when the pref cannot be changed.

WHY THIS EXISTS
===============
RimWorld does not render while its window is unfocused -- measured at **0.5% of
one core** with the window in the background, against a normal 60 FPS in front.
The bridge dispatches every game-touching call onto the Unity main thread, and
that thread only turns over when the game renders. So an unfocused window does
not merely slow the bridge down, it starves it: `rimbridge/ping` still answers in
0.5 ms off the network thread while every main-thread call times out at 30 s.

That failure is silent and looks exactly like a hung game. It cost this session
two aborted probe runs and one confidently wrong diagnosis ("no map loaded").

Any unattended bridge work -- benchmarks, generators, long authoring runs -- must
therefore hold the game in the foreground for its duration, or measure nothing.

USAGE
    from game_focus import focus_game, restore_focus
    prev = focus_game()
    try:
        ...bridge work...
    finally:
        restore_focus(prev)

`focus_game()` returns the window handle that had focus, or None. It raises if
RimWorld cannot be brought forward, because proceeding would silently produce
30-second timeouts instead of data.
"""
import subprocess

_PS_HELPER = r'''
Add-Type @"
using System;
using System.Runtime.InteropServices;
using System.Text;
public class Fg {
  [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
  [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int c);
  [DllImport("user32.dll")] public static extern bool IsIconic(IntPtr h);
  [DllImport("user32.dll")] public static extern int GetWindowText(IntPtr h, StringBuilder s, int n);
  [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);
  [DllImport("user32.dll")] public static extern bool AttachThreadInput(uint a, uint b, bool attach);
  [DllImport("kernel32.dll")] public static extern uint GetCurrentThreadId();
}
"@
function Get-Fg { $h = [Fg]::GetForegroundWindow(); $sb = New-Object System.Text.StringBuilder 256;
  [void][Fg]::GetWindowText($h, $sb, 256); return @{ handle = [int64]$h; title = $sb.ToString() } }
'''

_SW_RESTORE = 9


def _ps(script):
    out = subprocess.run(
        ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", script],
        capture_output=True, text=True, timeout=60)
    return (out.stdout or "").replace("\r", "").strip()


def foreground_title():
    """Title of whatever window currently has focus."""
    return _ps(_PS_HELPER + "\n(Get-Fg).title")


def focus_game(timeout_s=5):
    """Bring RimWorld forward. Returns the previously-focused handle, or None.

    Raises RuntimeError if the window will not come forward -- callers must not
    silently measure a starved main thread.
    """
    script = _PS_HELPER + r'''
$prev = Get-Fg
$p = Get-Process RimWorldWin64 -ErrorAction SilentlyContinue
if (-not $p) { "ERR|no RimWorldWin64 process"; exit }
$h = $p.MainWindowHandle
if ($h -eq 0) { "ERR|RimWorld has no main window handle"; exit }
if ([Fg]::IsIconic($h)) { [void][Fg]::ShowWindow($h, ''' + str(_SW_RESTORE) + r''') }
# SetForegroundWindow is refused across input queues unless the threads are
# attached; this is the standard workaround, not a trick.
$fgH = [Fg]::GetForegroundWindow()
$tidFg = [Fg]::GetWindowThreadProcessId($fgH, [ref]([uint32]0))
$tidMe = [Fg]::GetCurrentThreadId()
[void][Fg]::AttachThreadInput($tidFg, $tidMe, $true)
[void][Fg]::SetForegroundWindow($h)
[void][Fg]::AttachThreadInput($tidFg, $tidMe, $false)
Start-Sleep -Milliseconds 350
$now = Get-Fg
"{0}|{1}|{2}" -f $prev.handle, $now.handle, $now.title
'''
    res = _ps(script)
    if res.startswith("ERR|"):
        raise RuntimeError(res[4:])
    parts = res.split("|")
    if len(parts) < 3:
        raise RuntimeError("unexpected focus helper output: %r" % res)
    prev_handle, _, now_title = parts[0], parts[1], parts[2]
    if "rimworld" not in now_title.lower():
        raise RuntimeError(
            "could not bring RimWorld forward; foreground is %r. Bridge calls "
            "that touch the game will time out until it is focused." % now_title)
    return prev_handle


def restore_focus(prev_handle):
    """Hand focus back to whatever had it before. Best effort, never raises."""
    if not prev_handle:
        return
    try:
        _ps(_PS_HELPER + "\n[void][Fg]::SetForegroundWindow([IntPtr]%s)"
            % prev_handle)
    except Exception:
        pass


if __name__ == "__main__":
    print("foreground before:", foreground_title())
    prev = focus_game()
    print("foreground now   :", foreground_title())
    print("(previous handle %s)" % prev)
