param([string]$Hwnd = "1540902", [double]$FracX = 0.704, [double]$FracY = 0.329)
Add-Type 'using System.Runtime.InteropServices;public class DPI2{[DllImport("shcore.dll")] public static extern int SetProcessDpiAwareness(int v);}'
[void][DPI2]::SetProcessDpiAwareness(2)
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class Mouse {
    [DllImport("user32.dll")] public static extern bool GetClientRect(IntPtr h, out RECT r);
    [DllImport("user32.dll")] public static extern bool ClientToScreen(IntPtr h, ref POINT p);
    [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
    public struct RECT { public int L, T, R, B; }
    public struct POINT { public int X, Y; }
}
"@
$h = [IntPtr][Convert]::ToInt64($Hwnd, 16)
$r = New-Object Mouse+RECT
[void][Mouse]::GetClientRect($h, [ref]$r)
$p = New-Object Mouse+POINT
$p.X = [int]($r.R * $FracX); $p.Y = [int]($r.B * $FracY)
[void][Mouse]::ClientToScreen($h, [ref]$p)
[void][Mouse]::SetCursorPos($p.X, $p.Y)
Write-Output ("client {0}x{1} -> cursor at screen {2},{3}" -f $r.R, $r.B, $p.X, $p.Y)
Add-Type 'using System.Runtime.InteropServices;public class Mev{[DllImport("user32.dll")] public static extern void mouse_event(uint f,uint x,uint y,uint d,System.UIntPtr e);}'
Start-Sleep -Milliseconds 200
[Mev]::mouse_event(2, 0, 0, 0, [UIntPtr]::Zero)  # LEFTDOWN
Start-Sleep -Milliseconds 80
[Mev]::mouse_event(4, 0, 0, 0, [UIntPtr]::Zero)  # LEFTUP
Write-Output "clicked"
