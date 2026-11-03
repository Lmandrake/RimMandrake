' heartbeat.vbs: runs heartbeat.ps1 with NO console window (window style 0). The scheduled task
' \RimMandrake-Heartbeat launches wscript.exe on this; powershell.exe -WindowStyle Hidden still flashes a console
' (HEARTBEAT_FLASH_FIX_BLACK_WINDOW_EVERY_TEN). Same pattern as the WSL Keepalive task.
Dim sh, dir
Set sh = CreateObject("WScript.Shell")
dir = Left(WScript.ScriptFullName, InStrRev(WScript.ScriptFullName, "\"))
sh.Run "powershell.exe -NoProfile -ExecutionPolicy Bypass -File """ & dir & "heartbeat.ps1""", 0, True
