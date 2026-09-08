Add-Type @"
using System;
using System.Text;
using System.Runtime.InteropServices;
public class WinEnum {
    [DllImport("user32.dll")] public static extern bool EnumWindows(EnumWindowsProc cb, IntPtr lp);
    [DllImport("user32.dll")] public static extern int GetWindowText(IntPtr h, StringBuilder s, int n);
    [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
    [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);
    public delegate bool EnumWindowsProc(IntPtr h, IntPtr lp);
}
"@
$global:rows = New-Object System.Collections.ArrayList
$cb = [WinEnum+EnumWindowsProc]{
    param($h, $lp)
    if ([WinEnum]::IsWindowVisible($h)) {
        $sb = New-Object System.Text.StringBuilder 512
        [void][WinEnum]::GetWindowText($h, $sb, 512)
        $t = $sb.ToString()
        if ($t -ne "") {
            $pid2 = 0
            [void][WinEnum]::GetWindowThreadProcessId($h, [ref]$pid2)
            [void]$global:rows.Add(("HWND=0x{0:X} PID={1} TITLE={2}" -f $h.ToInt64(), $pid2, $t))
        }
    }
    return $true
}
[void][WinEnum]::EnumWindows($cb, [IntPtr]::Zero)
$global:rows | ForEach-Object { Write-Output $_ }
