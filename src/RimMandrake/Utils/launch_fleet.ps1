<#
launch_fleet.ps1 — open the fleet's windows, each Windows Terminal window placed.

    TOP-LEFT     HESTIA        (separate project, D:\Luke\dev\Hestia)
    TOP-RIGHT    Artist        (purple — the artpipe daemon's console, no LLM, above Server/EMERGENCY)
    TOP-RIGHT    Server        (white — the standalone `claude remote-control` server, no seat;
                                launched FIRST so it is up before any seat, and independent of all)
    TOP-RIGHT    EMERGENCY     (small floating window, D:\Luke\dev)
    BOTTOM-LEFT  CONDUCTOR     (green — with the owner)

Redesign #4, 2026-08-27: the four-seat fleet (DECIDE/CHECK/BUILD/REP quadrants) is
retired, the status board stays removed, and the queue publisher loop is gone too —
rimflow renders the queue views on every write, so nothing needs a background loop.

Third window added 2026-09-03: HESTIA joined the fleet. Its placement is not a
formula split like BENCH/FOUNDRY below — it is hardcoded to the exact rect the
owner had it at by hand (top-left, not a clean quadrant: there's an 8px gap above
BENCH/FOUNDRY and empty screen to its right for other apps). If the owner resizes
it again and wants that new size kept, re-measure and update $place by hand —
there is no "capture current layout" mode in this script.

WHY THE WINDOWS ARE MOVED RATHER THAN SIZED AT LAUNCH
=====================================================
`wt.exe --size` is in CELLS, not pixels, so tiling through it would mean knowing
the font metrics and the DPI scaling — both of which change under you. So each
seat is launched with its profile only, then placed with MoveWindow in real
pixels. Nothing to recalibrate when the font size changes.

DPI IS NOT OPTIONAL HERE — MEASURED 2026-08-14
==============================================
This display is 3840x2160 at 200% scaling. A DPI-UNAWARE process reads the work
area as 1920x1080 and every coordinate it passes is doubled by Windows, so the
tiling lands at four times the intended area and three seats end up off-screen.
`SetProcessDPIAware()` on the first line is what makes the numbers below mean
physical pixels. Do not remove it.

THE INVISIBLE BORDER
====================
A window's MoveWindow rect includes the transparent resize border (~7px * scale),
so tiling to exact quadrants leaves visible gaps. Each window is therefore placed
twice: once to land it, then again corrected by the difference between
GetWindowRect and the DWM extended frame bounds, which is the border width as the
system actually renders it.

USAGE
=====
    powershell -NoProfile -ExecutionPolicy Bypass -File launch_fleet.ps1
    ... -Gap 8               # pixels between tiles (default 0, flush)
    ... -Seats BENCH         # open a subset, in the same places
    ... -Test                # same windows, running `cmd` instead of a seat, so
                             # the layout can be tuned without starting real
                             # sessions. Titled `<name> [test]`, e.g. `HESTIA [test]`.
    ... -CloseTest           # close every test tile; live seats are untouched,
                             # because the marker is what it matches on.
    ... -Survey              # list every fleet window and whether it is live or
                             # dead; changes nothing.

OPEN ONLY WHAT IS MISSING (owner, 2026-11-04)
=============================================
"first close any old versions of its windows that are no longer active, preserve
the ones that are, and restart only the missing items." A seat whose process ended
drops its tile to a bare shell prompt (`mandrake@Archmagi ~dev %`, the profile's
fallback shell) or, on a non-zero exit, to WT's `[process exited with code N]`,
under the same pinned title, so a title alone cannot tell old from live. MEASURED
2026-11-04: 11 fleet windows, 6 of them dead at a prompt. Each fleet window's
visible terminal text is read through UI Automation: a window whose every terminal
ends in either line is DEAD and closed; anything else, an unreadable window
included, is LIVE and kept. A seat with a live window is not
launched again. Retired titles (AGENT FOUNDRY) are swept the same way: closed only
when dead.

Normally invoked by the Desktop shortcut written by install_fleet_shortcut.py.
#>
param(
    [int]$Gap = 0,
    [string[]]$Seats = @('SERVER', 'HESTIA', 'ARTIST', 'EMERGENCY', 'BENCH'),
    [int]$TimeoutSec = 30,
    [int]$DelaySec = 0,
    [switch]$Test,
    [switch]$CloseTest,
    [switch]$Survey
)

$ErrorActionPreference = 'Stop'

# -DelaySec exists for the Startup-folder copy of the shortcut only. At logon the
# desktop is ready long before WSL2, Tailscale and the network are, and the seats
# are WSL sessions whose Server tile wants the network on its first second. A
# double-clicked launch passes 0 and is unaffected.
if ($DelaySec -gt 0) { Start-Sleep -Seconds $DelaySec }

Add-Type @'
using System;
using System.Collections.Generic;
using System.Text;
using System.Runtime.InteropServices;
public class Fleet {
    public delegate bool EnumProc(IntPtr h, IntPtr l);
    [DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc cb, IntPtr l);
    [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern int GetWindowTextW(IntPtr h, StringBuilder s, int n);
    [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
    [DllImport("user32.dll")] public static extern bool MoveWindow(IntPtr h, int x, int y, int w, int t, bool repaint);
    [DllImport("user32.dll")] public static extern bool SetProcessDPIAware();
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
    [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
    [DllImport("user32.dll")] public static extern bool SystemParametersInfoW(uint a, uint b, ref RECT r, uint d);
    [DllImport("dwmapi.dll")] public static extern int DwmGetWindowAttribute(IntPtr h, int attr, out RECT r, int size);
    [StructLayout(LayoutKind.Sequential)] public struct RECT { public int L, T, R, B; }

    public static IntPtr[] WindowsTitled(string title) {
        List<IntPtr> hits = new List<IntPtr>();
        EnumWindows(delegate(IntPtr h, IntPtr l) {
            if (!IsWindowVisible(h)) return true;
            StringBuilder s = new StringBuilder(512);
            GetWindowTextW(h, s, 512);
            if (s.ToString() == title) hits.Add(h);
            return true;
        }, IntPtr.Zero);
        return hits.ToArray();
    }

    [DllImport("user32.dll")] public static extern IntPtr SendMessageW(IntPtr h, uint msg, IntPtr w, IntPtr l);

    // Closes ONLY windows whose title ends with the test marker. A live seat is
    // titled `AGENT BUILD`; a test tile is `AGENT BUILD [test]`. Never widen this.
    public static int CloseTests(string marker) {
        List<IntPtr> hits = new List<IntPtr>();
        EnumWindows(delegate(IntPtr h, IntPtr l) {
            if (!IsWindowVisible(h)) return true;
            StringBuilder s = new StringBuilder(512);
            GetWindowTextW(h, s, 512);
            if (s.ToString().EndsWith(marker)) hits.Add(h);
            return true;
        }, IntPtr.Zero);
        foreach (IntPtr h in hits) SendMessageW(h, 0x0010 /* WM_CLOSE */, IntPtr.Zero, IntPtr.Zero);
        return hits.Count;
    }

    // The transparent resize border, as the compositor actually draws it.
    public static RECT Border(IntPtr h) {
        RECT w, f;
        GetWindowRect(h, out w);
        RECT z = new RECT();
        if (DwmGetWindowAttribute(h, 9 /* DWMWA_EXTENDED_FRAME_BOUNDS */, out f, 16) != 0) return z;
        z.L = f.L - w.L; z.T = f.T - w.T; z.R = w.R - f.R; z.B = w.B - f.B;
        return z;
    }
}
'@

[void][Fleet]::SetProcessDPIAware()

if ($CloseTest) {
    "closed {0} test window(s)" -f [Fleet]::CloseTests(' [test]')
    return
}

Add-Type -AssemblyName UIAutomationClient, UIAutomationTypes

# 'dead' only when every terminal in the window ends, on screen, in a bare shell
# prompt or WT's exit line; 'live' when any does not; 'unknown' when UI Automation
# cannot read it. Only 'dead' is ever closed: an unread window is kept. The tab
# header is a text element too (class TextBlock), so only TermControl is read.
function Get-TermState([IntPtr]$h) {
    try {
        $el = [System.Windows.Automation.AutomationElement]::FromHandle($h)
        $cond = New-Object System.Windows.Automation.PropertyCondition(
            [System.Windows.Automation.AutomationElement]::ClassNameProperty, 'TermControl')
        $terms = $el.FindAll([System.Windows.Automation.TreeScope]::Descendants, $cond)
        if ($terms.Count -eq 0) { return 'unknown' }
        foreach ($t in $terms) {
            $tp = $t.GetCurrentPattern([System.Windows.Automation.TextPattern]::Pattern)
            $s = (($tp.GetVisibleRanges() | ForEach-Object { $_.GetText(-1) }) -join "`n").TrimEnd()
            $last = ($s -split "`n")[-1].Trim()
            if ($last -notmatch '^\S+@\S+ .*[%$#]$' -and $last -notmatch '\[process exited with code') { return 'live' }
        }
        return 'dead'
    } catch { return 'unknown' }
}

# SPI_GETWORKAREA — the screen minus the taskbar, in physical pixels.
$work = New-Object Fleet+RECT
[void][Fleet]::SystemParametersInfoW(0x0030, 0, [ref]$work, 0)
$X = $work.L; $Y = $work.T
$W = $work.R - $work.L; $H = $work.B - $work.T

# All four rects below are literal — the exact DWM extended-frame-bounds
# measured on 2026-09-05 on the 3840x2160 @200% display, per the owner's
# instruction to open at their CURRENT sizes rather than a recomputed split.
# None of them scale with the work area. If the owner reshapes any of these
# and wants the new size kept, re-measure with DWM extended frame bounds (not
# GetWindowRect, which includes the invisible resize border) and update the
# numbers below — there is no "capture current layout" mode in this script.
#
# ⚠️ Every arithmetic expression inside @(...) MUST be parenthesized: the comma
# binds tighter than + in PowerShell, so a bare `$X + 39, $Y + 13` parses as
# `$X + (39, $Y) + 13` and dies with "[Object[]] does not contain op_Addition".
# That single missing pair of parens killed the whole shortcut from 2026-09-03
# to 2026-09-05 — the hidden powershell console flashed and nothing opened.
$place = [ordered]@{
    HESTIA    = @(($X + 4),    ($Y + 42),  1835, 818)
    ARTIST    = @(($X + 1899), ($Y + 42),  1930, 410)
    SERVER    = @(($X + 1899), ($Y + 465), 1000, 374)
    EMERGENCY = @(($X + 2909), ($Y + 465),  923, 374)
    BENCH     = @(($X + 24),   ($Y + 900), 1835, 1151)
    FOUNDRY   = @(($X + 1899), ($Y + 901), 1930, 1151)
}

# The wt profile name IS the live window title (no --title override on a real
# launch — see below), so this has to match each profile exactly. HESTIA's wt
# profile is named plain "HESTIA" (a separate project, not part of the
# "AGENT <seat>" fleet naming), not "AGENT HESTIA" — don't collapse this back
# to a single "AGENT $seat" format string.
$titleFor = [ordered]@{
    HESTIA    = 'HESTIA'
    ARTIST    = 'Artist'
    SERVER    = 'Server'
    EMERGENCY = 'EMERGENCY'
    BENCH     = 'CONDUCTOR'      # seat BENCH's tile is named CONDUCTOR (install_wt_seat_profiles.py TILE_NAME)
    FOUNDRY   = 'AGENT FOUNDRY'
}

$wt = "$env:LOCALAPPDATA\Microsoft\WindowsApps\wt.exe"

# Sweep every fleet title, retired ones included, whatever -Seats names: a dead
# window is dead. -Survey reports and stops; a real launch closes the dead.
if (-not $Test) {
    foreach ($name in $titleFor.Values) {
        foreach ($h in [Fleet]::WindowsTitled($name)) {
            $state = Get-TermState $h
            if ($Survey) { "{0,-14} {1,-8} {2}" -f $name, $state, $h; continue }
            if ($state -eq 'dead') {
                [void][Fleet]::SendMessageW($h, 0x0010, [IntPtr]::Zero, [IntPtr]::Zero)   # WM_CLOSE
                "closed dead $name window $h"
            }
        }
    }
    if ($Survey) { return }
    Start-Sleep -Milliseconds 500
}

foreach ($seat in $Seats) {
    # FOUNDRY is retired (owner, by card 2026-11-02); a stale caller (claude-account's
    # machine.json relaunch list) reopened it after an account switch on 2026-11-03.
    if ($seat -eq 'FOUNDRY') { Write-Warning "FOUNDRY is retired; not launched"; continue }
    if (-not $place.Contains($seat)) { Write-Warning "no placement for $seat"; continue }
    # The ` [test]` suffix is not cosmetic: without it a test window is titled
    # exactly like a LIVE seat, and closing the test fleet would close a running
    # session. The search below uses this same string, so the wait-and-place path
    # under test is still the real one.
    $title = if ($Test) { "$($titleFor[$seat]) [test]" } else { $titleFor[$seat] }
    $r = $place[$seat]

    # Any window still carrying this title after the sweep is a seat that is
    # ALREADY OPEN and live (or unreadable, so kept): leave it where it is.
    $before = [Fleet]::WindowsTitled($title)
    if ($before.Count -gt 0 -and -not $Test) { "kept live $title"; continue }

    # `--title` pins the window title the same way the seat profile's tabTitle
    # does, so the wait-and-place path below is EXACTLY the one being tested.
    # `-w new`, NOT `-w _new`. MEASURED 2026-08-14: `_new` is not a keyword —
    # wt reads any unrecognised token as a window NAME, so all five launches
    # opened as tabs of one window called `_new` and each replaced the last.
    # `new` and `-1` both mean "a new window"; only those two do.
    #
    # Quoted by hand: Windows PowerShell joins -ArgumentList with spaces and adds
    # no quoting of its own, so a bare `AGENT DECIDE` would reach wt as two args.
    $q = '"' + $title + '"'
    # `/k rem`, not a bare `cmd.exe`: MEASURED 2026-08-14, a bare cmd under wt
    # exits within a second or two and takes the window with it, so only the
    # last-launched tile was ever on screen at once.
    $wtArgs = if ($Test) { @('-w', 'new', '--title', $q, 'cmd.exe', '/k', 'rem') }
              else       { @('-w', 'new', '-p', $q) }
    Start-Process -FilePath $wt -ArgumentList $wtArgs | Out-Null

    $deadline = (Get-Date).AddSeconds($TimeoutSec)
    $h = [IntPtr]::Zero
    while ((Get-Date) -lt $deadline) {
        Start-Sleep -Milliseconds 150
        $new = [Fleet]::WindowsTitled($title) | Where-Object { $before -notcontains $_ }
        if ($new) { $h = @($new)[0]; break }
    }
    if ($h -eq [IntPtr]::Zero) { Write-Warning "$title never appeared"; continue }

    [void][Fleet]::MoveWindow($h, $r[0], $r[1], $r[2], $r[3], $true)
    Start-Sleep -Milliseconds 120
    $b = [Fleet]::Border($h)
    [void][Fleet]::MoveWindow($h, $r[0] - $b.L, $r[1] - $b.T,
                                  $r[2] + $b.L + $b.R, $r[3] + $b.T + $b.B, $true)
}

# Leave the focus where the owner starts: BENCH, the window that works with him.
$focus = if ($Seats -contains 'BENCH') { 'BENCH' } else { $Seats[-1] }
$last = if ($Test) { "$($titleFor[$focus]) [test]" } else { $titleFor[$focus] }
$f = [Fleet]::WindowsTitled($last)
if ($f) { [void][Fleet]::SetForegroundWindow(@($f)[0]) }
