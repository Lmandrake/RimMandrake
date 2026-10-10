param([int]$Pid_, [string]$Op)
Add-Type -Namespace N -Name P -MemberDefinition '[DllImport("ntdll.dll")] public static extern int NtSuspendProcess(IntPtr h); [DllImport("ntdll.dll")] public static extern int NtResumeProcess(IntPtr h);'
$p=[System.Diagnostics.Process]::GetProcessById($Pid_)
if($Op -eq 'suspend'){[N.P]::NtSuspendProcess($p.Handle)}else{[N.P]::NtResumeProcess($p.Handle)}
