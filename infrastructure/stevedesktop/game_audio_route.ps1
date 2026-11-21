# game_audio_route.ps1: move the lane game's sound off the Sonic Studio mixer the moment it opens
# (RIMMANDRAKE_KEEP_STEVE_LANE_GAME_SOUND_OFF_SONIC_STUDIO_AT_LAUNCH). rw_game.sh up starts this BEFORE the game, waits for
# READY, starts the game, and prints the ROUTED/RESULT line. Record: D:\ClaudeWork\rimmandrake\conductor\night_20261120\
# steve_lane_launch_audio.md; facts: infrastructure/state/facts/steve_fault_diagnosis.md.
#
# Why: on SteveDesktop the register fault follows the game's audio through the Sonic Studio virtual mixer. Unity 2022.3 and
# RimWorld have no switch that opens no audio device. A per-app route saved before the start is ignored by a fresh RimWorld
# (2 of 2), but a route SET while the game's stream exists moves that live stream. So this waits for the game's own session,
# then sets the per-app route for that pid (reset, then set, so the change always fires), and checks the stream moved.
# The system default devices are never touched. Mechanism: the WinRT factory Windows.Media.Internal.AudioPolicyConfig
# (what Settings > App volume and device preferences writes). It must run as the logged-on user in the desktop session:
# from WSL interop (rw_game.sh) it does.
#
#   powershell -File game_audio_route.ps1 -Exe <RimWorldWin64.exe path> -Log <file> [-Endpoint 'Realtek Digital Output']
#   powershell -File game_audio_route.ps1 -SelfTest      the decision table only (no device, no process)
#
# Log lines (UTC): READY, ENDPOINT, PID, STATE (each change in the game's sessions), SEEN, MOVE, HELD, and exactly one RESULT line, which is the verdict:
#   RESULT ROUTED ...                 the game's ACTIVE stream is on the target, nothing ACTIVE elsewhere
#   RESULT NO_ENDPOINT|NO_PID|NO_SESSION|NOT_MOVED|NOT_ACTIVE|ERROR <why>   the game's sound may be on Sonic Studio
# LIMITS (each guards a hidden PowerShell left polling with no game to act on):
#   -WaitPidS 150: rw_game.sh gives up on the pid at 60 s (RW_START_WAIT_S); 150 covers a Steam relaunch.
#   -WaitSessionS 300: the game's session was already open at 1.7, 2.0 and 2.1 min after start in 3 of 3 measured launches.
#   -HoldS 90: after ROUTED, watch that the game does not open a second stream on the mixer, through the 60 s reading.
#   Tries 5, 3 s apart: one set moved the live stream within 30 s in the one measured case; 5 covers a slow switch.
param([string]$Exe = '', [string]$Log = '', [string]$Endpoint = 'Realtek Digital Output', [int]$WaitPidS = 150,
      [int]$WaitSessionS = 300, [int]$HoldS = 90, [switch]$SelfTest)
$ErrorActionPreference = 'Stop'

# The decision, from the game's render sessions: each item is @{ ep = <endpoint name>; st = <0 idle, 1 active, 2 expired> }.
#   none   no session yet: keep waiting
#   routed an ACTIVE session on the target, and no ACTIVE session off it
#   wait   a session on the target, nothing ACTIVE anywhere: the stream is switching; look again
#   move   anything else: the sound is (or may be) on another endpoint
# A function that outputs nothing hands back $null, and @($null) has one element: nulls are dropped first.
function Decide($sess, [string]$target) {
    $s = @($sess | Where-Object { $_ -ne $null })
    if ($s.Count -eq 0) { return 'none' }
    $onActive = @($s | Where-Object { $_.ep -like "*$target*" -and $_.st -eq 1 })
    $on = @($s | Where-Object { $_.ep -like "*$target*" })
    $offActive = @($s | Where-Object { $_.ep -notlike "*$target*" -and $_.st -eq 1 })
    if ($offActive.Count -gt 0) { return 'move' }
    if ($onActive.Count -gt 0) { return 'routed' }
    if ($on.Count -gt 0) { return 'wait' }
    return 'move'
}

if ($SelfTest) {
    $T = 'Realtek Digital Output'; $S = 'Speakers (Sonic Studio Virtual Mixer)'; $R = 'Realtek Digital Output (Realtek(R) Audio)'
    $cases = @(
        @('no session', @(), 'none'),
        @('a function that output nothing ($null)', $null, 'none'),
        @('active on Sonic Studio only', @(@{ep=$S; st=1}), 'move'),
        @('idle on Sonic Studio only', @(@{ep=$S; st=0}), 'move'),
        @('active on target, Sonic idle (moved)', @(@{ep=$S; st=0}, @{ep=$R; st=1}), 'routed'),
        @('active on target and on Sonic', @(@{ep=$S; st=1}, @{ep=$R; st=1}), 'move'),
        @('idle on target only (switching)', @(@{ep=$R; st=0}), 'wait'),
        @('idle on target and Sonic (switching)', @(@{ep=$S; st=0}, @{ep=$R; st=0}), 'wait'),
        @('expired on Sonic, active on target', @(@{ep=$S; st=2}, @{ep=$R; st=1}), 'routed'))
    $bad = 0
    foreach ($c in $cases) { $got = Decide $c[1] $T; if ($got -ne $c[2]) { $bad++; "SELFTEST FAIL $($c[0]): got $got want $($c[2])" } }
    if ($bad) { exit 1 }; "SELFTEST PASS $($cases.Count) cases"; exit 0
}

function Say([string]$m) { $l = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ss.fff') + 'Z ' + $m; Add-Content -Path $Log -Value $l }
if (-not $Exe -or -not $Log) { 'usage: -Exe <path> -Log <file> [-Endpoint name] | -SelfTest'; exit 64 }
Set-Content -Path $Log -Value @()
try {
$src = @'
using System;
using System.Collections.Generic;
using System.Runtime.InteropServices;
namespace GAR {
  [StructLayout(LayoutKind.Sequential)] public struct PROPERTYKEY { public Guid fmtid; public int pid; }
  [StructLayout(LayoutKind.Explicit)] public struct PROPVARIANT { [FieldOffset(0)] public short vt; [FieldOffset(8)] public IntPtr p; [FieldOffset(16)] public IntPtr p2; }
  [Guid("886d8eeb-8cf2-4446-8d02-cdba1dbdcf99"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
  public interface IPropertyStore { [PreserveSig] int GetCount(out int c); [PreserveSig] int GetAt(int i, out PROPERTYKEY k); [PreserveSig] int GetValue(ref PROPERTYKEY k, out PROPVARIANT v); }
  [Guid("D666063F-1587-4E43-81F1-B948E807363F"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
  public interface IMMDevice {
    [PreserveSig] int Activate(ref Guid iid, int ctx, IntPtr p, [MarshalAs(UnmanagedType.IUnknown)] out object o);
    [PreserveSig] int OpenPropertyStore(int access, out IPropertyStore ps);
    [PreserveSig] int GetId([MarshalAs(UnmanagedType.LPWStr)] out string id);
    [PreserveSig] int GetState(out int st); }
  [Guid("0BD7A1BE-7A1A-44DB-8397-CC5392387B5E"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
  public interface IMMDeviceCollection { [PreserveSig] int GetCount(out int c); [PreserveSig] int Item(int i, out IMMDevice d); }
  [Guid("A95664D2-9614-4F35-A746-DE8DB63617E6"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
  public interface IMMDeviceEnumerator { [PreserveSig] int EnumAudioEndpoints(int flow, int mask, out IMMDeviceCollection c); }
  [ComImport, Guid("BCDE0395-E52F-467C-8E3D-C4579291692E")] public class MMDeviceEnumerator {}
  [Guid("77AA99A0-1BD6-484F-8BC7-2C654C9A9B6F"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
  public interface IAudioSessionManager2 { [PreserveSig] int GetAudioSessionControl(); [PreserveSig] int GetSimpleAudioVolume(); [PreserveSig] int GetSessionEnumerator(out IAudioSessionEnumerator e); }
  [Guid("E2F5BB11-0570-40CA-ACDD-3AA01277DEE8"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
  public interface IAudioSessionEnumerator { [PreserveSig] int GetCount(out int c); [PreserveSig] int GetSession(int i, out IAudioSessionControl2 s); }
  [Guid("bfb7ff88-7239-4fc9-8fa2-07c950be9c6d"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
  public interface IAudioSessionControl2 {
    [PreserveSig] int GetState(out int st); [PreserveSig] int GetDisplayName(out IntPtr n); [PreserveSig] int SetDisplayName(); [PreserveSig] int GetIconPath(out IntPtr n); [PreserveSig] int SetIconPath();
    [PreserveSig] int GetGroupingParam(out Guid g); [PreserveSig] int SetGroupingParam(); [PreserveSig] int RegisterAudioSessionNotification(); [PreserveSig] int UnregisterAudioSessionNotification();
    [PreserveSig] int GetSessionIdentifier(out IntPtr n); [PreserveSig] int GetSessionInstanceIdentifier(out IntPtr n); [PreserveSig] int GetProcessId(out int pid); }
  public class Sess { public string Ep; public int Pid; public int State; }
  public static class Core {
    [DllImport("combase.dll")] static extern int RoGetActivationFactory(IntPtr cls, ref Guid iid, out IntPtr f);
    [DllImport("combase.dll")] static extern int WindowsCreateString([MarshalAs(UnmanagedType.LPWStr)] string s, int len, out IntPtr h);
    [DllImport("combase.dll")] static extern int WindowsDeleteString(IntPtr h);
    [DllImport("combase.dll")] static extern int RoInitialize(int t);
    [UnmanagedFunctionPointer(CallingConvention.StdCall)] delegate int SetFn(IntPtr self, uint pid, int flow, int role, IntPtr dev);
    // vtable: IUnknown 0-2, IInspectable 3-5, SetPersistedDefaultAudioEndpoint 25. Slot 27 (ClearAll...) would wipe every app's route: never called.
    static IntPtr factory = IntPtr.Zero;
    static IntPtr F() {
      if (factory != IntPtr.Zero) return factory;
      RoInitialize(1);
      IntPtr cls; WindowsCreateString("Windows.Media.Internal.AudioPolicyConfig", 40, out cls);
      foreach (string id in new string[]{ "ab3d4648-e242-459f-b02f-541c70306324", "2a59116d-6c4f-45e0-a74f-707e3fef9258" }) {
        Guid g = new Guid(id); IntPtr f; if (RoGetActivationFactory(cls, ref g, out f) == 0) { factory = f; break; } }
      WindowsDeleteString(cls);
      if (factory == IntPtr.Zero) throw new Exception("AudioPolicyConfig factory not available");
      return factory; }
    // Route all 3 render roles of pid to the endpoint (short id "{0.0.0.00000000}.{guid}"), or back to the default when null.
    public static string Route(uint pid, string shortId) {
      IntPtr f = F(); var fn = (SetFn)Marshal.GetDelegateForFunctionPointer(Marshal.ReadIntPtr(Marshal.ReadIntPtr(f), 25 * IntPtr.Size), typeof(SetFn));
      string o = "";
      for (int r = 0; r < 3; r++) { IntPtr h = IntPtr.Zero;
        if (!string.IsNullOrEmpty(shortId)) { string full = @"\\?\SWD#MMDEVAPI#" + shortId + "#{e6327cad-dcec-4949-ae8a-991e976a79d2}"; WindowsCreateString(full, full.Length, out h); }
        int hr = fn(f, pid, 0, r, h); if (h != IntPtr.Zero) WindowsDeleteString(h); o += " hr=0x" + hr.ToString("X"); }
      return o.Trim(); }
    static string Name(IMMDevice d) {
      IPropertyStore ps; if (d.OpenPropertyStore(0, out ps) != 0) return "?";
      PROPERTYKEY k = new PROPERTYKEY(); k.fmtid = new Guid("a45c254e-df1c-4efd-8020-67d146a850e0"); k.pid = 14; PROPVARIANT v;
      if (ps.GetValue(ref k, out v) != 0 || v.vt != 31) return "?"; return Marshal.PtrToStringUni(v.p); }
    // The first ACTIVE render endpoint whose name contains the text -> "id|name", or "" when none.
    public static string FindEndpoint(string text) {
      var e = (IMMDeviceEnumerator)(new MMDeviceEnumerator()); IMMDeviceCollection c; e.EnumAudioEndpoints(0, 1, out c); int n; c.GetCount(out n);
      for (int i = 0; i < n; i++) { IMMDevice d; c.Item(i, out d); string nm = Name(d); if (nm.IndexOf(text, StringComparison.OrdinalIgnoreCase) >= 0) { string id; d.GetId(out id); return id + "|" + nm; } }
      return ""; }
    public static List<Sess> Sessions(int want) {
      var o = new List<Sess>(); var e = (IMMDeviceEnumerator)(new MMDeviceEnumerator()); IMMDeviceCollection c; e.EnumAudioEndpoints(0, 1, out c); int n; c.GetCount(out n);
      Guid iid = new Guid("77AA99A0-1BD6-484F-8BC7-2C654C9A9B6F");
      for (int i = 0; i < n; i++) { IMMDevice d; c.Item(i, out d); object m; if (d.Activate(ref iid, 23, IntPtr.Zero, out m) != 0) continue; string nm = Name(d);
        IAudioSessionEnumerator se; ((IAudioSessionManager2)m).GetSessionEnumerator(out se); int k; se.GetCount(out k);
        for (int j = 0; j < k; j++) { IAudioSessionControl2 s; se.GetSession(j, out s); int pid; s.GetProcessId(out pid); if (pid != want) continue;
          int st; s.GetState(out st); o.Add(new Sess { Ep = nm, Pid = pid, State = st }); } }
      return o; } } }
'@
Add-Type -TypeDefinition $src -Language CSharp
Say "READY exe=$Exe endpoint='$Endpoint'"
$ep = [GAR.Core]::FindEndpoint($Endpoint)
if (-not $ep) { Say "RESULT NO_ENDPOINT no ACTIVE render endpoint named like '$Endpoint': nothing routed"; exit 3 }
$epId, $epName = $ep -split '\|', 2
Say "ENDPOINT $epId | $epName"

$t0 = Get-Date; $proc = $null
while (-not $proc) {
    $proc = Get-Process -Name RimWorldWin64 -ErrorAction SilentlyContinue | Where-Object { $_.Path -and ($_.Path -ieq $Exe) } | Select-Object -First 1
    if ($proc) { break }
    if (((Get-Date) - $t0).TotalSeconds -ge $WaitPidS) { Say "RESULT NO_PID no RimWorldWin64 at $Exe within $WaitPidS s"; exit 4 }
    Start-Sleep -Milliseconds 100
}
$gpid = [uint32]$proc.Id; $start = $proc.StartTime.ToUniversalTime()
function Since() { [math]::Round(((Get-Date).ToUniversalTime() - $start).TotalSeconds, 1) }
Say "PID $gpid started=$($start.ToString('HH:mm:ss.fff'))Z"

function Read() { @([GAR.Core]::Sessions([int]$gpid) | ForEach-Object { @{ ep = $_.Ep; st = $_.State } }) }
function Fmt($s) { (@($s | Where-Object { $_ -ne $null }) | ForEach-Object { "$($_.ep)=st$($_.st)" }) -join '; ' }
$firstSeen = $null; $lastF = ''; $tries = 0; $lastMove = $null; $routedAt = $null
while ($routedAt -eq $null) {
    if ($proc.HasExited) { Say "RESULT NO_SESSION the game exited at $(Since) s before its sound was routed"; exit 5 }
    $s = Read; $d = Decide $s $Endpoint; $f = Fmt $s
    if ($f -ne $lastF) { Say "STATE t=$(Since) s $d $f"; $lastF = $f }
    if ($d -ne 'none' -and $firstSeen -eq $null) { $firstSeen = Since; Say "SEEN t=$firstSeen s $(Fmt $s)" }
    if ($d -eq 'routed') { $routedAt = Since; break }
    if ($d -eq 'none' -and (Since) -ge $WaitSessionS) { Say "RESULT NO_SESSION the game opened no audio session in $WaitSessionS s"; exit 6 }
    if ($d -eq 'wait' -and (Since) -ge $WaitSessionS) { Say "RESULT NOT_ACTIVE the game's session is on the target but not ACTIVE after $WaitSessionS s: $f"; exit 8 }
    if ($d -eq 'move' -and (-not $lastMove -or ((Get-Date) - $lastMove).TotalSeconds -ge 3)) {
        if ($tries -ge 5) { Say "RESULT NOT_MOVED $tries route sets did not move the stream: $(Fmt $s)"; exit 7 }
        $tries++; $lastMove = Get-Date
        $r0 = [GAR.Core]::Route($gpid, $null); $r1 = [GAR.Core]::Route($gpid, $epId)
        Say "MOVE try=$tries t=$(Since) s reset=[$r0] set=[$r1] before: $(Fmt $s)"
    }
    Start-Sleep -Milliseconds 100
}
$s = Read
$offLow = if ($firstSeen -ne $null -and $tries -gt 0) { [math]::Round($routedAt - $firstSeen, 1) } else { 0 }
$offHigh = if ($tries -gt 0) { $routedAt } else { 0 }
Say "RESULT ROUTED pid=$gpid t=$routedAt s tries=$tries on_mixer_s>=$offLow on_mixer_s<=$offHigh (from process start) now: $(Fmt $s)"
# Hold: the game must not open a second stream on another endpoint after the move.
$h0 = Get-Date; $again = 0
while (((Get-Date) - $h0).TotalSeconds -lt $HoldS -and -not $proc.HasExited) {
    $s = Read; $f = Fmt $s
    if ($f -ne $lastF) { Say "STATE t=$(Since) s $(Decide $s $Endpoint) $f"; $lastF = $f }
    if ((Decide $s $Endpoint) -eq 'move') {
        $again++; $r0 = [GAR.Core]::Route($gpid, $null); $r1 = [GAR.Core]::Route($gpid, $epId)
        Say "MOVE again=$again t=$(Since) s reset=[$r0] set=[$r1] before: $(Fmt $s)"; Start-Sleep -Seconds 3
    }
    Start-Sleep -Milliseconds 500
}
Say "HELD t=$(Since) s re-moves=$again now: $(Fmt (Read))"
exit 0
} catch { Say ("RESULT ERROR " + ($_.Exception.Message -replace '\s+', ' ')); exit 2 }
