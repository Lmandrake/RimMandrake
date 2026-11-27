# Windows half of load_sample.py: every -Every seconds, one JSON line with each process's cumulative CPU,
# I/O bytes and memory (Win32_Process) and the machine's totals (performance counters).
# Item RIMMANDRAKE_FIND_LOAD_USERS_RM_TIMERS_ONLY_TEN_PERCENT. Started by load_sample.py --win-ps1.
param([string]$Out, [int]$Seconds = 3600, [int]$Every = 30)
$ErrorActionPreference = 'Continue'
$counters = '\Processor(_Total)\% Processor Time', '\Memory\Available MBytes', '\Memory\Committed Bytes',
            '\PhysicalDisk(_Total)\Disk Read Bytes/sec', '\PhysicalDisk(_Total)\Disk Write Bytes/sec',
            '\Paging File(_Total)\% Usage', '\Memory\Pages Input/sec'
$t0 = Get-Date
$paths = @{}
while ($true) {
    $now = Get-Date
    $tot = @{}
    try {
        (Get-Counter -Counter $counters -ErrorAction Stop).CounterSamples | ForEach-Object { $tot[$_.Path] = $_.CookedValue }
    } catch { $tot['error'] = "$_" }
    $ps = @()
    Get-CimInstance Win32_Process -Property ProcessId, ParentProcessId, Name, ExecutablePath, CreationDate,
        KernelModeTime, UserModeTime, ReadTransferCount, WriteTransferCount, WorkingSetSize, PrivatePageCount |
      ForEach-Object {
        $k = "$($_.ProcessId)|$($_.CreationDate.Ticks)"
        $rec = @{ k = $k; n = $_.Name; c = ([int64]$_.KernelModeTime + [int64]$_.UserModeTime);
                  r = [int64]$_.ReadTransferCount; w = [int64]$_.WriteTransferCount;
                  ws = [int64]$_.WorkingSetSize; pv = [int64]$_.PrivatePageCount }
        if (-not $paths.ContainsKey($k)) { $paths[$k] = 1; $rec.p = $_.ExecutablePath; $rec.pp = $_.ParentProcessId }
        $ps += $rec
      }
    $line = @{ t = [math]::Round(($now - $t0).TotalSeconds, 1); tot = $tot; ps = $ps } | ConvertTo-Json -Compress -Depth 4
    Add-Content -Path $Out -Value $line
    if (($now - $t0).TotalSeconds -ge $Seconds) { break }
    $spent = ((Get-Date) - $now).TotalSeconds
    if ($spent -lt $Every) { Start-Sleep -Milliseconds ([int](($Every - $spent) * 1000)) }
}
