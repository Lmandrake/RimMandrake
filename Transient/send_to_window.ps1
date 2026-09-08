param([string]$Hwnd, [string]$CmdFile = "", [switch]$SendEnter)
Add-Type -AssemblyName System.Windows.Forms
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class WinFocus {
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
    [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int cmd);
    [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
    [DllImport("user32.dll")] public static extern void keybd_event(byte vk, byte scan, uint flags, UIntPtr extra);
}
"@
$h = [IntPtr][Convert]::ToInt64($Hwnd, 16)
[void][WinFocus]::ShowWindow($h, 9)   # SW_RESTORE
Start-Sleep -Milliseconds 300
$ok = $false
for ($try = 0; $try -lt 4 -and -not $ok; $try++) {
    # An in-flight ALT keypress marks this process as "sending input", which
    # lifts the OS foreground-steal lock that a busy fullscreen app triggers.
    [WinFocus]::keybd_event(0x12, 0, 0, [UIntPtr]::Zero)
    [void][WinFocus]::SetForegroundWindow($h)
    [WinFocus]::keybd_event(0x12, 0, 2, [UIntPtr]::Zero)  # ALT up
    Start-Sleep -Milliseconds 600
    $ok = ([WinFocus]::GetForegroundWindow() -eq $h)
}
if (-not $ok) { Write-Output ("FOCUS FAILED: foreground is {0}, wanted {1}" -f [WinFocus]::GetForegroundWindow(), $h); exit 1 }
if ($CmdFile -ne "") {
    $cmd = (Get-Content -Raw -Encoding UTF8 $CmdFile).TrimEnd("`r", "`n")
    Set-Clipboard -Value $cmd
    [System.Windows.Forms.SendKeys]::SendWait("^v")
    Start-Sleep -Milliseconds 500
    Write-Output "pasted into $Hwnd"
}
if ($SendEnter) {
    [System.Windows.Forms.SendKeys]::SendWait("{ENTER}")
    Write-Output "enter sent to $Hwnd"
}
