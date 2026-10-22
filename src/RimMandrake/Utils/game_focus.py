"""game_focus.py - keep RimWorld rendering so bridge calls can complete.

THE REAL FIX IS A PREFERENCE, NOT THIS MODULE
=============================================
RimWorld ships `runInBackground` **False**. Turn it on -- Options -> Run in
background -- and none of the focus juggling below is needed. Set it in the
game's own menu: RimWorld holds prefs in memory and rewrites `Prefs.xml` on
exit, so editing that file while the game runs gets overwritten, exactly like
`ModsConfig.xml`.

Use `preflight()` before any unattended bridge run: it CHECKS the pref and
refuses when it is off. Focusing the window happens only with RM_FOCUS_OPT_IN
set (see OPT_IN_ENV below); minimising anything needs RM_FOCUS_OPT_IN=minimise.

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
import os
import subprocess
import xml.etree.ElementTree as ET

from focus_heal import FocusLost

# FOCUS_HEAL_TAME_HANDS_OFF_HIS_WINDOWS (2026-10-10). Owner ruling 2026-10-04: never fullscreen, maximise or
# focus-steal the game. Nothing here touches a window unless this env var opts in, per process:
#   RM_FOCUS_OPT_IN=focus     focus_game() may bring RimWorld forward (never minimises anything)
#   RM_FOCUS_OPT_IN=minimise  also lets focus_heal minimise the foreground window / minimise-restore the game
# Unset (the default): preflight() CHECKS Prefs.xml runInBackground and refuses loudly when it is off.
OPT_IN_ENV = "RM_FOCUS_OPT_IN"


class FocusRefused(FocusLost):
    """A focus act was needed and not opted into. Subclass of FocusLost so runners record UNMEASURED(FOCUS_LOST)."""

    def __init__(self, msg):
        FocusLost.__init__(self, msg, [("refused", msg[:160])])


def opt_in():
    v = os.environ.get(OPT_IN_ENV, "").strip().lower()
    return v if v in ("focus", "minimise") else ""


def _prefs_path():
    try:
        from game_paths import MODS_CONFIG
    except ImportError:
        return None
    return os.path.join(os.path.dirname(MODS_CONFIG), "Prefs.xml")    # Config/ beside ModsConfig.xml


def run_in_background(prefs_path=None):
    """Prefs.xml runInBackground: True / False (absent = False, RimWorld's default) / None if unreadable.
    The file is what the NEXT start reads and what the game last saved; an in-game toggle shows here on exit."""
    p = prefs_path or _prefs_path()
    try:
        node = ET.parse(p).getroot().find("runInBackground")
    except (OSError, ET.ParseError, TypeError):
        return None
    return node is not None and (node.text or "").strip().lower() == "true"

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


GAME_TITLE = "rimworld by ludeon"      # the game's real window title is "RimWorld by Ludeon Studios"


def is_game_title(title):
    """True only for the game window itself; a browser tab or Explorer folder merely containing "RimWorld" is not it."""
    return (title or "").strip().lower().startswith(GAME_TITLE)


def foreground_title():
    """Title of whatever window currently has focus."""
    return _ps(_PS_HELPER + "\n(Get-Fg).title")


def focus_game(timeout_s=5, attempts=4, pause_s=3):
    """Bring RimWorld forward - ONLY with RM_FOCUS_OPT_IN set. Returns the previously-focused handle, or None.

    Raises FocusRefused (a FocusLost) without the opt-in, touching no window; RuntimeError / FocusLost if the
    window will not come forward -- callers must not silently measure a starved main thread.
    """
    import time
    if not opt_in():
        raise FocusRefused("focus_game refused: bringing RimWorld forward needs %s=focus (owner 2026-10-04: never "
                           "focus-steal). Turn on Options > Run in background instead." % OPT_IN_ENV)
    last = None
    for i in range(max(1, attempts)):
        try:
            return _focus_game_once()
        except RuntimeError as e:             # another window (media player, browser) held focus: try again
            last = e
            if i + 1 < attempts:
                time.sleep(pause_s)
    if opt_in() != "minimise":
        raise FocusLost("could not bring RimWorld forward (%s); minimising other windows needs %s=minimise"
                        % (last, OPT_IN_ENV), [("gentle_retries", str(last)[:160])])
    import focus_heal                         # escalate (minimise the blocker...); raises FocusLost, exit 3
    focus_heal.heal(last)
    return None


def _focus_game_once():
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
    if not is_game_title(now_title):
        # MEASURED live 2026-10-01: with the owner active in Chrome the AttachThreadInput route is refused every time;
        # a synthetic Alt tap (WScript SendKeys '%') followed by AppActivate is accepted.
        _ps("$w=New-Object -ComObject WScript.Shell; $w.SendKeys('%'); Start-Sleep -Milliseconds 100; "
            "[void]$w.AppActivate('RimWorld by Ludeon Studios'); Start-Sleep -Milliseconds 400")
        now_title = foreground_title()
    if not is_game_title(now_title):
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


def preflight(prefs_path=None):
    """Before unattended bridge work: CHECK that Run in background is on; never heal it by focus.

    Returns None and touches no window when the pref is on. When it is off or unreadable: with RM_FOCUS_OPT_IN set,
    falls back to focus_game() (returns the previous handle for restore_focus); without it, raises FocusRefused.
    """
    rb = run_in_background(prefs_path)
    if rb is True:
        return None
    if opt_in():
        return focus_game()
    raise FocusRefused("Run in background is %s in %s: an unfocused RimWorld starves every main-thread bridge "
                       "call. Turn it on in Options (the game rewrites Prefs.xml on exit), or opt in to focusing "
                       "with %s=focus." % ("OFF" if rb is False else "UNREADABLE", prefs_path or _prefs_path(),
                                           OPT_IN_ENV))


if __name__ == "__main__":
    import sys
    print("Run in background:", run_in_background(), "(Prefs.xml %s)" % _prefs_path())
    print("foreground:", foreground_title())
    if "--steal" in sys.argv:                 # an explicit, human-typed opt-in for this one invocation
        os.environ.setdefault(OPT_IN_ENV, "focus")
        prev = focus_game()
        print("foreground now:", foreground_title(), "(previous handle %s)" % prev)
    else:
        print("(checks only; pass --steal to bring RimWorld forward)")
