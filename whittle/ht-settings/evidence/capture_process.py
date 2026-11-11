from session_control import *
import sys
name=sys.argv[1]
# Read-only Windows CIM uses genuine Powershell, never the Steam adapter for identity.
ps="Get-CimInstance Win32_Process -Filter \"Name='RimWorldWin64.exe'\" | Select-Object ProcessId,ParentProcessId,CreationDate,ExecutablePath,CommandLine | ConvertTo-Json -Compress"
run(name,['powershell.exe','-NoProfile','-Command',ps])
