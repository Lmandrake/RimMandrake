"== uefi vars"
$src=@'
using System;using System.Runtime.InteropServices;
public class U{
[DllImport("kernel32",SetLastError=true,CharSet=CharSet.Unicode)] public static extern uint GetFirmwareEnvironmentVariableExW(string n,string g,byte[] b,uint s,out uint a);
[DllImport("advapi32",SetLastError=true)] static extern bool OpenProcessToken(IntPtr h,uint a,out IntPtr t);
[DllImport("kernel32")] static extern IntPtr GetCurrentProcess();
[DllImport("advapi32",SetLastError=true,CharSet=CharSet.Unicode)] static extern bool LookupPrivilegeValueW(string s,string n,out long l);
[StructLayout(LayoutKind.Sequential,Pack=4)] struct TP{public uint c;public long l;public uint a;}
[DllImport("advapi32",SetLastError=true)] static extern bool AdjustTokenPrivileges(IntPtr t,bool d,ref TP n,uint b,IntPtr p,IntPtr r);
public static bool En(){IntPtr t;OpenProcessToken(GetCurrentProcess(),0x28,out t);long l;LookupPrivilegeValueW(null,"SeSystemEnvironmentPrivilege",out l);TP p;p.c=1;p.l=l;p.a=2;bool r=AdjustTokenPrivileges(t,false,ref p,0,IntPtr.Zero,IntPtr.Zero);return r&&Marshal.GetLastWin32Error()==0;}
}
'@
Add-Type -TypeDefinition $src
"priv " + [U]::En()

$L=@(@('CpuSetup','b08f97ff-e6e8-4193-a997-5e9e9b0adb32'),@('SaSetup','72c5e28c-7783-43a1-8767-fad73fccafa4'),@('PchSetup','4570b7f1-ade8-4943-8dc3-406472842384'),@('MeSetup','5432122d-d034-49d2-a6de-65a829eb4c74'),@('VARSTORE_OCMR_SETTINGS_NAME','a3a3b874-7636-4182-ba1e-f52c584494e3'),@('ASUSAiSetup','5e4ca5e2-c07f-455a-a4eb-d28550884e47'),@('Setup','ec87d643-eba4-4bb5-a1e5-3f3e36b20da9'))
foreach($p in $L){ $b=New-Object byte[] 65536; $a=0; $r=[U]::GetFirmwareEnvironmentVariableExW($p[0],'{'+$p[1]+'}',$b,65536,[ref]$a); $e=[Runtime.InteropServices.Marshal]::GetLastWin32Error(); "$($p[0]) ret=$r err=$e"; if($r -gt 0){ "VAR $($p[0]) " + [Convert]::ToBase64String($b,0,$r) } }
