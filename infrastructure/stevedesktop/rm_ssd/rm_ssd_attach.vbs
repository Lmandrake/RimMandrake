' rm_ssd_attach.vbs - runs rm_ssd_attach.ps1 with no console window, as seats_watch.vbs does.
CreateObject("WScript.Shell").Run "powershell.exe -NoProfile -ExecutionPolicy Bypass -File ""C:\SteveDesktop\rm_ssd_attach.ps1""", 0, True
