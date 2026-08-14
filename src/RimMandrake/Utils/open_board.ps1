<#
open_board.ps1 — put the fleet board on screen, in its own window, on the right.

    powershell -NoProfile -ExecutionPolicy Bypass -File open_board.ps1
    ... -Frac 0.28      # share of screen width (default 0.24)
    ... -Close          # close it again

WHY A SEPARATE FILE AND NOT A SIXTH TILE IN launch_fleet.ps1
============================================================
`launch_fleet.ps1` already fills the work area — four quadrants plus VISION
centred on top of them. There is no free rectangle, and squeezing six windows
into a layout that took DPI and invisible-border work to get right would risk a
working thing to add a new one. **The board also has a different lifetime:** the
seats are restarted together, the board should stay up across all of it.

So it is its own window, placed down the right edge, and the seats are moved
left by the same amount only if `-Reflow` is passed.

WHAT IT RUNS
============
`board.py --watch`, which redraws in place and never scrolls. The window title
is rewritten by the board itself to carry the count of things needing the owner,
so **the taskbar entry is readable with the window covered.**

⚠️ DPI, same as the fleet launcher: this display is 3840x2160 at 200%, and a
DPI-unaware process has every coordinate doubled. `SetProcessDPIAware()` is not
optional. See launch_fleet.ps1's header for the full measurement.
#>
param(
    [double]$Frac = 0.24,
    [switch]$Close,
    [switch]$Reflow,
    [switch]$NoPin      # leave it in the normal z-order; default is always-on-top
)
$ErrorActionPreference = 'Stop'
$TITLE = 'FLEET BOARD'

Add-Type @'
using System;
using System.Collections.Generic;
using System.Text;
using System.Runtime.InteropServices;
public class Board {
    public delegate bool EnumProc(IntPtr h, IntPtr l);
    [DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc cb, IntPtr l);
    [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern int GetWindowTextW(IntPtr h, StringBuilder s, int n);
    [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
    [DllImport("user32.dll")] public static extern bool MoveWindow(IntPtr h, int x, int y, int w, int t, bool repaint);
    [DllImport("user32.dll")] public static extern bool SetProcessDPIAware();
    [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
    [DllImport("user32.dll")] public static extern bool SystemParametersInfoW(uint a, uint b, ref RECT r, uint d);
    [DllImport("user32.dll")] public static extern IntPtr SendMessageW(IntPtr h, uint msg, IntPtr w, IntPtr l);
    [DllImport("dwmapi.dll")] public static extern int DwmGetWindowAttribute(IntPtr h, int attr, out RECT r, int size);
    [DllImport("user32.dll")] public static extern bool SetWindowPos(IntPtr h, IntPtr after, int x, int y, int w, int t, uint flags);
    // HWND_TOPMOST = -1. The board is the one window that must never be buried:
    // a status display you have to go and find is a refrigerator, not a radiator.
    public static void Pin(IntPtr h) { SetWindowPos(h, new IntPtr(-1), 0,0,0,0, 0x0001 | 0x0002); }
    public static void Unpin(IntPtr h) { SetWindowPos(h, new IntPtr(-2), 0,0,0,0, 0x0001 | 0x0002); }
    [StructLayout(LayoutKind.Sequential)] public struct RECT { public int L, T, R, B; }

    // Matches on a PREFIX, because the board rewrites its own title to carry the
    // needs-you count ("2 NEEDS YOU - fleet"). An exact match would lose it the
    // moment the board had something to say, which is the only moment that matters.
    public static IntPtr[] Titled(string prefix) {
        List<IntPtr> hits = new List<IntPtr>();
        EnumWindows(delegate(IntPtr h, IntPtr l) {
            if (!IsWindowVisible(h)) return true;
            StringBuilder s = new StringBuilder(512);
            GetWindowTextW(h, s, 512);
            if (s.ToString().Contains(prefix)) hits.Add(h);
            return true;
        }, IntPtr.Zero);
        return hits.ToArray();
    }
    public static RECT Border(IntPtr h) {
        RECT w, f; GetWindowRect(h, out w);
        RECT z = new RECT();
        if (DwmGetWindowAttribute(h, 9, out f, 16) != 0) return z;
        z.L = f.L - w.L; z.T = f.T - w.T; z.R = w.R - f.R; z.B = w.B - f.B;
        return z;
    }
}
'@

[void][Board]::SetProcessDPIAware()

if ($Close) {
    $n = 0
    foreach ($h in [Board]::Titled($TITLE)) {
        [void][Board]::SendMessageW($h, 0x0010, [IntPtr]::Zero, [IntPtr]::Zero); $n++
    }
    "closed $n board window(s)"; return
}

$work = New-Object Board+RECT
[void][Board]::SystemParametersInfoW(0x0030, 0, [ref]$work, 0)
$X = $work.L; $Y = $work.T
$W = $work.R - $work.L; $H = $work.B - $work.T
$bw = [int]($W * $Frac)
$bx = $X + $W - $bw

$before = [Board]::Titled($TITLE)

$wt = "$env:LOCALAPPDATA\Microsoft\WindowsApps\wt.exe"
# `-w new` (never `_new` — wt reads an unrecognised token as a window NAME and
# every launch becomes a tab of one window). The board is run through bash -lc
# so the seat's own python and repo paths resolve exactly as they do in a seat.
$cmd = 'cd /mnt/d/Luke/dev/Rimworld && exec python3 src/RimMandrake/Utils/board.py --watch'
Start-Process -FilePath $wt -ArgumentList @(
    '-w', 'new', '--title', "`"$TITLE`"",
    'wsl.exe', '-d', 'Ubuntu', '--', 'bash', '-lc', "`"$cmd`""
) | Out-Null

$deadline = (Get-Date).AddSeconds(25)
$h = [IntPtr]::Zero
while ((Get-Date) -lt $deadline) {
    Start-Sleep -Milliseconds 150
    $new = [Board]::Titled($TITLE) | Where-Object { $before -notcontains $_ }
    if ($new) { $h = @($new)[0]; break }
}
if ($h -eq [IntPtr]::Zero) { Write-Warning 'board window never appeared'; return }

[void][Board]::MoveWindow($h, $bx, $Y, $bw, $H, $true)
Start-Sleep -Milliseconds 120
$b = [Board]::Border($h)
[void][Board]::MoveWindow($h, $bx - $b.L, $Y - $b.T, $bw + $b.L + $b.R, $H + $b.T + $b.B, $true)

if ($Reflow) {
    # Squeeze the five seats into the remaining width so nothing sits under the
    # board. Opt-in: it moves windows the owner may have arranged by hand.
    $lw = $W - $bw
    $halfW = [int]($lw / 2); $halfH = [int]($H / 2)
    $place = @{
        'AGENT CREATE'  = @($X,          $Y,            $halfW, $halfH)
        'AGENT BRIDGE'  = @($X + $halfW, $Y,            $halfW, $halfH)
        'AGENT PROJECT' = @($X,          $Y + $halfH,   $halfW, $halfH)
        'AGENT OPS'     = @($X + $halfW, $Y + $halfH,   $halfW, $halfH)
        'AGENT VISION'  = @(($X + [int]($lw / 4)), ($Y + [int]($H / 4)),
                            [int]($lw / 2), [int]($H / 2))
    }
    foreach ($t in @('AGENT CREATE', 'AGENT BRIDGE', 'AGENT PROJECT', 'AGENT OPS', 'AGENT VISION')) {
        $hits = [Board]::Titled($t)
        if (-not $hits) { continue }
        $r = $place[$t]; $wh = @($hits)[0]
        [void][Board]::MoveWindow($wh, $r[0], $r[1], $r[2], $r[3], $true)
        Start-Sleep -Milliseconds 80
        $bb = [Board]::Border($wh)
        [void][Board]::MoveWindow($wh, $r[0] - $bb.L, $r[1] - $bb.T,
                                       $r[2] + $bb.L + $bb.R, $r[3] + $bb.T + $bb.B, $true)
    }
}
if (-not $NoPin) { [Board]::Pin($h) }
$pin = if ($NoPin) { '' } else { ' [always on top]' }
Write-Output ("board placed at " + $bx + "," + $Y + "  " + $bw + "x" + $H + $pin)
