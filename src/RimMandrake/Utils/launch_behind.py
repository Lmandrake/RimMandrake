#!/usr/bin/env python3
r"""launch_behind.py - a game that we launch opens behind his windows and takes no focus.

The owner, 2026-11-27: "When you launch Rimworld for testing, can you launch it not as the most foreground window? It's
very distracting to have it steal focus and be in front all the time." (RIMMANDRAKE_LAUNCH_GAME_BEHIND_HIS_WINDOWS_IT_STEALS_FOCUS)

ONE SHARED FUNCTION. Every start of a game on Archmagi (game_instance.py: the Steam URL, the direct start of ArchBig, the
start of a named game) calls `guarded(fire, ...)`. No launch path has its own copy; selftest_launch_behind.py turns red on
a start that skips it.

    guarded(fire, player_log, front=None)   start the guard, wait for its READY, then fire() the launch
    start_script(exe, cwd, args, ...)        the PowerShell of a direct start: through WMI, first window not activated

WHAT TOOK THE FOREGROUND (focus_probe.py, MEASURED 2026-11-27 on both games, parent code):
  - the game's first window, at its process start (about 5 s after the command), kept until the run ended;
  - Steam's "Launching..." window, when the Steam URL fires; and when it closes, Windows hands the foreground to a game
    window (the new one, or the other game), with no foreground event;
  - the new game's window sat above all his windows for the whole run.
A map load took no focus.

THE DIRECT START (start_script) runs RimWorldWin64.exe through WMI (Win32_Process.Create) with SW_SHOWNOACTIVATE, so
the game is not a child of a shell that WSL started (such a shell can count as started by his terminal's process, and so
may give the game the right to take the foreground). It removes most of the steal; Windows still fires one foreground
event for the new window, which the guard undoes. Steam's own start of ArchBig cannot be shaped: there the guard alone
acts.

THE GUARD is one hidden Windows process (started through WMI, no window) that starts BEFORE the launch. At its start it
records the foreground window, every top-level window, and his windows (those on screen). Its hooks run on their own
thread (EVENT_SYSTEM_FOREGROUND, EVENT_OBJECT_SHOW, EVENT_OBJECT_HIDE); its polling thread reads the foreground and the
z-order every 10 ms. It acts on a NEW window (one that did not exist at its start) of a watched process
(RimWorldWin64, steam, steamwebhelper), and on a watched window of before the launch that comes forward with no input of
his in the last second or in the 400 ms after a new watched window hid:
  - such a window in the foreground: the previous foreground window goes back in front (plain call, then an Alt tap,
    then a thread attach; nothing waits on the game's own thread);
  - a new window above one of his windows: it goes to the bottom (asynchronous HWND_BOTTOM), and each of his windows
    below it is lifted to just above it, in their own order.
A foreground change to any other window (his own click) becomes the new "previous" window. The game is never minimised:
"behind" answers his words, and a game behind his windows was measured to draw (a bridge screenshot after the map load,
taken behind, has content). Run in background (Prefs.xml runInBackground, game_instance._seed_prefs, and the bridge's
own setting) keeps the game advancing while it has no focus.

The guard ends when: the game's Player.log has the bridge's start line (the main menu comes with it) and GRACE_S have
passed; every new game process seen has exited; no new game process came in NO_GAME_S; or BOUND_S passed.
  - NO_GAME_S 1200: danger, a guard left running for a launch that never started a game. Steam's slowest measured start
    was 29 s (STEAM_SEEN_S 120 in game_instance.py); 1200 is 10 x that bound.
  - BOUND_S 3600: danger, a guard that keeps pushing a game that he wants in front, when the start line never comes (a
    list with no bridge). It equals game_instance.WAIT_S, which is past the slowest measured cold load (about 25 min).
  - GRACE_S 120: the main menu and its first dialogs come after the start line. Danger without it: a dialog at the main
    menu that takes the foreground after the guard ended.

AN EXPLICIT FLAG. A launch for a named reason that must come to the front (an owner sitting) passes front="<reason>"
(game_instance.py launch --front "<reason>", or RM_LAUNCH_FRONT="<reason>" in the environment). Nothing else does.

The guard's log is a JSON-lines file under the agent storage root: scratch/launch_behind/guard_<stamp>.jsonl. Each act
is one line; its last line says why it ended.
"""
import json
import os
import subprocess
import sys
import time

FRONT_ENV = "RM_LAUNCH_FRONT"
WATCH = ("RimWorldWin64", "steam", "steamwebhelper")
DONE_MARKER = "[RimBridge] STARTUP_TIMING phase=bridge-start.total"
GRACE_S = 120
NO_GAME_S = 1200
BOUND_S = 3600
# The wait for the guard's READY line. Danger: a launch that never starts because the guard never answers. A cold
# PowerShell with Add-Type took about 3 s (MEASURED on Archmagi 2026-11-27); 60 s is past 10 x that.
READY_S = 60

# C# 5 (Windows PowerShell 5.1 compiles Add-Type with the old compiler): no string interpolation, no => members.
CS = r'''
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Runtime.InteropServices;
using System.Text;
using System.Threading;

public static class RmWin {
  public delegate bool EnumProc(IntPtr h, IntPtr l);
  public delegate void WinEventProc(IntPtr hook, uint ev, IntPtr h, int obj, int child, uint thread, uint time);
  [StructLayout(LayoutKind.Sequential)] public struct MSG { public IntPtr hwnd; public uint message; public IntPtr w; public IntPtr l; public uint time; public int x; public int y; }
  [StructLayout(LayoutKind.Sequential)] public struct RECT { public int L; public int T; public int R; public int B; }
  [DllImport("user32.dll")] static extern bool EnumWindows(EnumProc f, IntPtr l);
  [DllImport("user32.dll")] static extern bool IsWindowVisible(IntPtr h);
  [DllImport("user32.dll")] static extern bool IsWindow(IntPtr h);
  [DllImport("user32.dll")] static extern bool IsIconic(IntPtr h);
  [DllImport("user32.dll")] static extern IntPtr GetForegroundWindow();
  [DllImport("user32.dll")] static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);
  [DllImport("user32.dll", CharSet=CharSet.Unicode)] static extern int GetWindowText(IntPtr h, StringBuilder s, int n);
  [DllImport("user32.dll", CharSet=CharSet.Unicode)] static extern int GetClassName(IntPtr h, StringBuilder s, int n);
  [DllImport("user32.dll")] static extern bool GetWindowRect(IntPtr h, out RECT r);
  [DllImport("dwmapi.dll")] static extern int DwmGetWindowAttribute(IntPtr h, int a, out int v, int sz);
  [DllImport("user32.dll")] static extern bool SetWindowPos(IntPtr h, IntPtr after, int x, int y, int cx, int cy, uint f);
  [DllImport("user32.dll")] static extern bool SetForegroundWindow(IntPtr h);
  [DllImport("user32.dll")] static extern bool BringWindowToTop(IntPtr h);
  [DllImport("user32.dll")] static extern bool AttachThreadInput(uint a, uint b, bool at);
  [DllImport("user32.dll")] static extern void keybd_event(byte vk, byte scan, uint flags, UIntPtr extra);
  [DllImport("kernel32.dll")] static extern uint GetCurrentThreadId();
  [DllImport("user32.dll")] static extern IntPtr SetWinEventHook(uint min, uint max, IntPtr mod, WinEventProc cb, uint pid, uint tid, uint flags);
  [DllImport("user32.dll")] static extern bool UnhookWinEvent(IntPtr h);
  [DllImport("user32.dll")] static extern IntPtr GetAncestor(IntPtr h, uint flags);
  [DllImport("user32.dll")] static extern bool IsHungAppWindow(IntPtr h);
  [DllImport("user32.dll")] static extern int GetMessage(out MSG m, IntPtr h, uint a, uint b);
  [DllImport("user32.dll")] static extern bool PostThreadMessage(uint tid, uint msg, IntPtr w, IntPtr l);
  [DllImport("user32.dll")] static extern bool PeekMessage(out MSG m, IntPtr h, uint a, uint b, uint r);
  [DllImport("user32.dll")] static extern bool TranslateMessage(ref MSG m);
  [DllImport("user32.dll")] static extern IntPtr DispatchMessage(ref MSG m);

  [DllImport("user32.dll")] static extern uint MsgWaitForMultipleObjects(uint n, IntPtr[] handles, bool all, uint ms, uint mask);

  // Waits `ms`, and runs each window event the moment it comes (QS_ALLINPUT wakes the wait), so the probe's event
  // lines carry the time that each event came, not the time of its next sample.
  public static void PumpWait(int ms) {
    long end = Now() + ms;
    while (true) {
      MSG m;
      while (PeekMessage(out m, IntPtr.Zero, 0, 0, 1)) { TranslateMessage(ref m); DispatchMessage(ref m); }
      long left = end - Now();
      if (left <= 0) return;
      MsgWaitForMultipleObjects(0, null, false, (uint)left, 0x04FF);
    }
  }

  static Dictionary<uint, string> names = new Dictionary<uint, string>();
  public static string Name(uint pid) {
    string n;
    lock (names) { if (names.TryGetValue(pid, out n)) return n; }
    try { n = Process.GetProcessById((int)pid).ProcessName; } catch { n = "?"; }
    lock (names) names[pid] = n;
    return n;
  }
  public static string Esc(string s) {
    if (s == null) return "";
    StringBuilder b = new StringBuilder();
    foreach (char c in s) {
      if (c == '"' || c == '\\') { b.Append('\\'); b.Append(c); }
      else if (c < ' ') b.Append(' ');
      else b.Append(c);
    }
    return b.ToString();
  }
  public static long Now() { return (long)(DateTime.UtcNow - new DateTime(1970, 1, 1)).TotalMilliseconds; }
  public static string Title(IntPtr h) { StringBuilder s = new StringBuilder(256); GetWindowText(h, s, 256); return s.ToString(); }
  public static string Cls(IntPtr h) { StringBuilder s = new StringBuilder(128); GetClassName(h, s, 128); return s.ToString(); }
  public static uint Pid(IntPtr h) { uint p; GetWindowThreadProcessId(h, out p); return p; }
  public static bool Cloaked(IntPtr h) { int v = 0; try { DwmGetWindowAttribute(h, 14, out v, 4); } catch { } return v != 0; }

  // A window that a person can see: visible, not minimised, not cloaked, titled, not the desktop.
  public static bool OnScreen(IntPtr h) {
    if (!IsWindowVisible(h) || IsIconic(h) || Cloaked(h)) return false;
    string c = Cls(h);
    if (c == "Progman" || c == "WorkerW" || c == "Shell_TrayWnd" || c == "Shell_SecondaryTrayWnd") return false;
    RECT r; if (!GetWindowRect(h, out r) || r.R - r.L <= 0 || r.B - r.T <= 0) return false;
    return Title(h).Length > 0;
  }
  // Top-level windows, front first (EnumWindows walks the z-order from the top).
  public static List<IntPtr> ZOrder() {
    List<IntPtr> all = new List<IntPtr>();
    EnumWindows(delegate(IntPtr h, IntPtr l) { all.Add(h); return true; }, IntPtr.Zero);
    return all;
  }
  // A window of a watched process, or one titled as the game: Windows' "Not Responding" ghost of a loading game is a
  // dwm window with the game's title (MEASURED 2026-11-27: it took the foreground 2.3 s after the game's own window).
  public static bool Watched(IntPtr h, string[] watch) {
    string n = Name(Pid(h));
    foreach (string w in watch) if (string.Equals(n, w, StringComparison.OrdinalIgnoreCase)) return true;
    return Title(h).StartsWith("RimWorld by Ludeon", StringComparison.OrdinalIgnoreCase);
  }
  public static string Win(IntPtr h) {
    uint p = Pid(h);
    return "{\"h\":" + h.ToInt64() + ",\"pid\":" + p + ",\"name\":\"" + Esc(Name(p)) + "\",\"title\":\"" + Esc(Title(h)) + "\"}";
  }

  // ---- the probe: what is in front, and where each watched window sits ----
  // His windows (on screen at the start) below the highest new visible watched window; 0 when none is above any.
  static int AboveCount(HashSet<long> start, HashSet<long> existed, string[] watch) {
    List<IntPtr> z = ZOrder();
    int below = 0, worst = 0;
    for (int j = z.Count - 1; j >= 0; j--) {
      IntPtr h = z[j];
      if (start.Contains(h.ToInt64())) { if (OnScreen(h)) below++; continue; }
      if (!existed.Contains(h.ToInt64()) && IsWindowVisible(h) && !IsIconic(h) && Watched(h, watch) && Title(h).Length > 0) worst = below;
    }
    return worst;
  }

  public static int Probe(string outPath, int seconds, int periodMs, string stopFile, string watchCsv) {
    string[] watch = watchCsv.Split(',');
    HashSet<long> start = new HashSet<long>();      // on screen at the start
    HashSet<long> existed = new HashSet<long>();    // every top-level window at the start: "new" is not in this set
    List<IntPtr> z0 = ZOrder();
    StringBuilder sb0 = new StringBuilder(), all0 = new StringBuilder();
    foreach (IntPtr h in z0) {
      existed.Add(h.ToInt64()); if (all0.Length > 0) all0.Append(','); all0.Append(h.ToInt64());
      if (OnScreen(h)) { start.Add(h.ToInt64()); if (sb0.Length > 0) sb0.Append(','); sb0.Append(Win(h)); }
    }
    using (StreamWriter w = new StreamWriter(outPath, false, new UTF8Encoding(false))) {
      w.AutoFlush = true;
      w.WriteLine("{\"k\":\"start\",\"t\":" + Now() + ",\"fg\":" + Win(GetForegroundWindow()) + ",\"onscreen\":[" + sb0 + "],\"existed\":[" + all0 + "]}");
      // Each foreground event is logged with what GetForegroundWindow says at that moment ("now"), and so is each
      // new watched window that is shown ("show"). Both start a burst: every 5 ms (about 16 ms: the Windows timer) for
      // 300 ms, a "b" line holds the foreground and "above", the count of his windows below the highest new watched
      // window. So the length of a short steal, in front or in the z-order, is measured, not only bounded by the next
      // 100 ms sample.
      long burstUntil = 0;
      WinEventProc cb = delegate(IntPtr hook, uint ev, IntPtr h, int obj, int child, uint thread, uint time) {
        try {
          w.WriteLine("{\"k\":\"event\",\"t\":" + Now() + ",\"fg\":" + Win(h) + ",\"now\":" + Win(GetForegroundWindow()) + "}");
          burstUntil = Now() + 300;
        } catch { }
      };
      IntPtr hk = SetWinEventHook(3, 3, IntPtr.Zero, cb, 0, 0, 2);
      WinEventProc showCb = delegate(IntPtr hook, uint ev, IntPtr h, int obj, int child, uint thread, uint time) {
        try {
          if (obj != 0 || h == IntPtr.Zero || GetAncestor(h, 2) != h || existed.Contains(h.ToInt64()) || !Watched(h, watch)) return;
          w.WriteLine("{\"k\":\"show\",\"t\":" + Now() + ",\"win\":" + Win(h) + "}");
          burstUntil = Now() + 300;
        } catch { }
      };
      IntPtr hkShow = SetWinEventHook(0x8002, 0x8002, IntPtr.Zero, showCb, 0, 0, 2);
      long end = Now() + seconds * 1000L;
      while (Now() < end && !File.Exists(stopFile)) {
        MSG m;
        while (PeekMessage(out m, IntPtr.Zero, 0, 0, 1)) { TranslateMessage(ref m); DispatchMessage(ref m); }
        IntPtr fg = GetForegroundWindow();
        List<IntPtr> z = ZOrder();
        int i = 0;
        StringBuilder ws = new StringBuilder();
        int[] below = new int[z.Count + 1];      // below[i]: windows on screen at the start that sit below z[i - 1]
        for (int j = z.Count - 1; j >= 0; j--) below[j] = below[j + 1] + ((start.Contains(z[j].ToInt64()) && OnScreen(z[j])) ? 1 : 0);
        foreach (IntPtr h in z) {
          if (Watched(h, watch) && IsWindowVisible(h) && Title(h).Length > 0) {
            int above = below[i + 1];   // windows that existed at the start, on screen, below this one
            if (ws.Length > 0) ws.Append(',');
            ws.Append("{\"h\":" + h.ToInt64() + ",\"pid\":" + Pid(h) + ",\"title\":\"" + Esc(Title(h)) + "\",\"z\":" + i +
                      ",\"new\":" + (existed.Contains(h.ToInt64()) ? "false" : "true") + ",\"iconic\":" + (IsIconic(h) ? "true" : "false") +
                      ",\"start_below\":" + above + "}");
          }
          i++;
        }
        w.WriteLine("{\"k\":\"s\",\"t\":" + Now() + ",\"fg\":" + Win(fg) + ",\"watched\":[" + ws + "]}");
        long sampled = Now();
        while (Now() - sampled < periodMs) {
          if (Now() < burstUntil) {
            PumpWait(5);
            w.WriteLine("{\"k\":\"b\",\"t\":" + Now() + ",\"fg\":" + Win(GetForegroundWindow()) + ",\"above\":" + AboveCount(start, existed, watch) + "}");
          }
          else PumpWait((int)Math.Max(1, periodMs - (Now() - sampled)));
        }
      }
      UnhookWinEvent(hk); UnhookWinEvent(hkShow);
      w.WriteLine("{\"k\":\"end\",\"t\":" + Now() + "}");
      GC.KeepAlive(cb); GC.KeepAlive(showCb);
    }
    return 0;
  }

  // ---- the guard: keep the previous window in front and new watched windows at the bottom ----
  static readonly object gate = new object();
  static StreamWriter glog;
  static void G(string kind, string rest) { lock (gate) try { glog.WriteLine("{\"k\":\"" + kind + "\",\"t\":" + Now() + (rest.Length > 0 ? "," + rest : "") + "}"); } catch { } }
  static IntPtr prev;
  static HashSet<long> startWins = new HashSet<long>();
  static HashSet<long> shownNew = new HashSet<long>();
  static HashSet<long> startOn = new HashSet<long>();
  static long hideUntil = 0;                                // the 400 ms after a new watched window hid       // his windows: on screen when the guard started      // new watched windows that the guard saw shown
  static string[] gwatch;
  static int restores = 0, pushes = 0;

  static bool IsNewWatched(IntPtr h) { return h != IntPtr.Zero && !startWins.Contains(h.ToInt64()) && Watched(h, gwatch); }

  // Puts the previous window back in front and the thief at the bottom. Nothing here waits on the thief's thread: a
  // loading game does not pump messages, and a synchronous SetWindowPos or AttachThreadInput on it blocked the guard
  // for 0.7 s (MEASURED 2026-11-27). So: an asynchronous move, then the plain call, then an Alt tap (which gives this
  // process the right to set the foreground), and the thread attach last.
  static string PutBack(IntPtr thief) {
    if (prev == IntPtr.Zero || !IsWindow(prev)) return "no previous window";
    // The foreground first; the z-order is ZCheck's, on the polling thread, so this never waits on a window's thread.
    if (!startWins.Contains(thief.ToInt64())) SetWindowPos(thief, new IntPtr(1), 0, 0, 0, 0, 0x0001 | 0x0002 | 0x0010 | 0x4000);
    if (SetForegroundWindow(prev) && GetForegroundWindow() == prev) return "plain";
    keybd_event(0x12, 0, 0, UIntPtr.Zero); keybd_event(0x12, 0, 2, UIntPtr.Zero);
    if (SetForegroundWindow(prev) && GetForegroundWindow() == prev) return "alt";
    uint tidFg = GetWindowThreadProcessId(GetForegroundWindow(), out _dummy), tidMe = GetCurrentThreadId();
    AttachThreadInput(tidMe, tidFg, true);
    SetForegroundWindow(prev); BringWindowToTop(prev);
    AttachThreadInput(tidMe, tidFg, false);
    return GetForegroundWindow() == prev ? "attach" : "failed";
  }
  static uint _dummy;

  // Puts a new game window below his windows. The game's own move (HWND_BOTTOM) is asynchronous and waits for the
  // game's thread, which is busy for about 0.65 s after its first window shows (MEASURED 2026-11-27). So each of his
  // windows that sits below the game, top first, is also lifted to just above it: his windows answer at once, and
  // their order among themselves is kept. A hung window of his is left where it is (the call would wait on it).
  static void Sink(IntPtr game, string how) {
    SetWindowPos(game, new IntPtr(1), 0, 0, 0, 0, 0x0001 | 0x0002 | 0x0010 | 0x4000); pushes++;
    List<IntPtr> z = ZOrder();
    int gi = z.IndexOf(game);
    if (gi < 0) return;
    IntPtr after = gi > 0 ? z[gi - 1] : IntPtr.Zero;   // HWND_TOP when the game is the top window
    int lifted = 0;
    for (int j = gi + 1; j < z.Count; j++) {
      IntPtr w = z[j];
      if (!startOn.Contains(w.ToInt64()) || !OnScreen(w) || IsHungAppWindow(w)) continue;
      SetWindowPos(w, after, 0, 0, 0, 0, 0x0001 | 0x0002 | 0x0010); after = w; lifted++;
    }
    G("bottom", "\"how\":\"" + how + "\",\"lifted\":" + lifted + ",\"win\":" + Win(game));
  }

  [StructLayout(LayoutKind.Sequential)] public struct LASTINPUTINFO { public uint cbSize; public uint dwTime; }
  [DllImport("user32.dll")] static extern bool GetLastInputInfo(ref LASTINPUTINFO li);
  // Milliseconds since his last key or mouse input (system-wide), or a large number when it cannot be read.
  static long SinceInput() {
    LASTINPUTINFO li = new LASTINPUTINFO(); li.cbSize = (uint)Marshal.SizeOf(li);
    if (!GetLastInputInfo(ref li)) return long.MaxValue;
    return (long)unchecked((uint)Environment.TickCount - li.dwTime);
  }

  // A new watched window above one of his windows goes down (Sink). The scan runs outside `gate`, so a hook never
  // waits on it (a hook that waited on a 50 to 100 ms scan acted 90 ms late, MEASURED 2026-11-27). It reads only his
  // windows' state (a dozen or so), so it is cheap enough to run every 10 ms.
  static void ZCheck() {
    List<IntPtr> z = ZOrder();
    int lowest = -1;
    for (int i = 0; i < z.Count; i++) if (startOn.Contains(z[i].ToInt64()) && OnScreen(z[i])) lowest = i;
    for (int i = 0; i < lowest; i++) {
      if (IsNewWatched(z[i]) && IsWindowVisible(z[i])) { Sink(z[i], "poll"); return; }
    }
  }

  static void OnFg(IntPtr h, string how) {
    if (h == IntPtr.Zero || h == prev) return;
    // A game or Steam window that was open before the launch, brought forward in the 400 ms after a new watched
    // window hid, or with no input of his in the last second, is the launch's doing too: MEASURED 2026-11-27, when
    // Steam's "Launching..." closed, Windows handed the foreground to the other game (ArchSmall), and the guard then
    // kept it as his window.
    bool thief = IsNewWatched(h) || (Watched(h, gwatch) && (Now() < hideUntil || SinceInput() > 1000));
    if (thief) {
      long t = Now(); string route = PutBack(h); restores++;
      G("restore", "\"how\":\"" + how + "\",\"thief\":" + Win(h) + ",\"prev\":" + Win(prev) + ",\"route\":\"" + route +
        "\",\"ok\":" + (route == "failed" || route == "no previous window" ? "false" : "true") + ",\"ms\":" + (Now() - t));
    } else {
      prev = h;                        // his own move to another window: that window is now the one to keep
      G("prev", "\"fg\":" + Win(h));
    }
  }

  public static int Guard(string logPath, string playerLog, string marker, int graceS, int noGameS, int boundS, string watchCsv, string readyPath) {
    gwatch = watchCsv.Split(',');
    glog = new StreamWriter(logPath, true, new UTF8Encoding(false)); glog.AutoFlush = true;
    prev = GetForegroundWindow();
    foreach (IntPtr h in ZOrder()) { startWins.Add(h.ToInt64()); if (OnScreen(h)) startOn.Add(h.ToInt64()); }
    HashSet<int> startPids = new HashSet<int>();
    foreach (Process p in Process.GetProcessesByName("RimWorldWin64")) startPids.Add(p.Id);
    DateTime startUtc = DateTime.UtcNow;
    G("ready", "\"prev\":" + Win(prev) + ",\"windows\":" + startWins.Count + ",\"pid\":" + Process.GetCurrentProcess().Id);
    File.WriteAllText(readyPath, "READY");
    // The hooks live on their own thread, which does nothing but run them, so an event is acted on the moment it
    // comes. On the polling thread the window scan held events back: the guard acted 88 to 118 ms after a new game
    // window showed (MEASURED 2026-11-27). Both threads take `gate` before they touch the shared state.
    uint hookTid = 0;
    ManualResetEvent hooked = new ManualResetEvent(false);
    WinEventProc cb = delegate(IntPtr hook, uint ev, IntPtr h, int obj, int child, uint thread, uint time) {
      try { lock (gate) { OnFg(h, "event"); } } catch { }
    };
    // A new window of the game that is shown is remembered, so that its hiding (below) can be watched. Its move to the
    // bottom is ZCheck's: lifting his windows waits on their threads (90 ms for eight, MEASURED 2026-11-27), and on
    // this thread that wait held back the foreground events.
    WinEventProc showCb = delegate(IntPtr hook, uint ev, IntPtr h, int obj, int child, uint thread, uint time) {
      try { if (obj == 0 && h != IntPtr.Zero && GetAncestor(h, 2) == h && IsNewWatched(h)) lock (gate) shownNew.Add(h.ToInt64()); } catch { }
    };
    // When a new window of a watched process hides (Steam's "Launching..." closes), the foreground is read without a
    // pause for 400 ms: MEASURED 2026-11-27, the game took the foreground at that moment with no foreground event, and
    // a 10 ms poll still left a steal of 10 to 30 ms that a probe sample caught.
    WinEventProc hideCb = delegate(IntPtr hook, uint ev, IntPtr h, int obj, int child, uint thread, uint time) {
      try {
        if (obj != 0 || h == IntPtr.Zero) return;
        lock (gate) { if (!shownNew.Remove(h.ToInt64())) return; }     // only a window that the guard saw shown
        long until = Now() + 400;
        hideUntil = until;
        while (Now() < until) { lock (gate) OnFg(GetForegroundWindow(), "hide"); Thread.Yield(); }
      } catch { }
    };
    Thread hookThread = new Thread(delegate() {
      hookTid = GetCurrentThreadId();
      IntPtr hk = SetWinEventHook(3, 3, IntPtr.Zero, cb, 0, 0, 2);
      IntPtr hkShow = SetWinEventHook(0x8002, 0x8002, IntPtr.Zero, showCb, 0, 0, 2);
      IntPtr hkHide = SetWinEventHook(0x8003, 0x8003, IntPtr.Zero, hideCb, 0, 0, 2);
      MSG hm;
      PeekMessage(out hm, IntPtr.Zero, 0, 0, 0);    // makes this thread's message queue before the poller can post to it
      hooked.Set();
      while (GetMessage(out hm, IntPtr.Zero, 0, 0) > 0) { TranslateMessage(ref hm); DispatchMessage(ref hm); }
      UnhookWinEvent(hk); UnhookWinEvent(hkShow); UnhookWinEvent(hkHide);
    });
    hookThread.IsBackground = true;
    hookThread.Start();
    hooked.WaitOne(10000);
    long t0 = Now(), doneAt = -1, lastLogCheck = 0, firstSeen = -1; HashSet<int> seen = new HashSet<int>(); string why = "bound";
    while (true) {
      lock (gate) OnFg(GetForegroundWindow(), "poll");
      ZCheck();
      long now = Now();
      foreach (Process p in Process.GetProcessesByName("RimWorldWin64")) if (!startPids.Contains(p.Id)) seen.Add(p.Id);
      if (seen.Count > 0) {
        bool any = false;
        foreach (int id in seen) { try { if (!Process.GetProcessById(id).HasExited) any = true; } catch { } }
        if (!any) { why = "the game exited"; break; }
      } else if (now - t0 > noGameS * 1000L) { why = "no new game in " + noGameS + " s"; break; }
      // The log is read whole, and only from 5 s after the new game appeared: by then Unity has moved the last
      // session's log aside (Player-prev.log), so its old start line cannot end the guard early.
      if (firstSeen < 0 && seen.Count > 0) firstSeen = now;
      if (doneAt < 0 && firstSeen >= 0 && now - firstSeen > 5000 && now - lastLogCheck > 2000 && playerLog.Length > 0) {
        lastLogCheck = now;
        try {
          if (File.Exists(playerLog) && File.GetLastWriteTimeUtc(playerLog) > startUtc) {
            using (FileStream fs = new FileStream(playerLog, FileMode.Open, FileAccess.Read, FileShare.ReadWrite | FileShare.Delete)) {
              string text = new StreamReader(fs).ReadToEnd();
              if (text.Contains(marker)) { doneAt = now; G("marker", "\"grace_s\":" + graceS); }
            }
          }
        } catch { }
      }
      if (doneAt >= 0 && now - doneAt > graceS * 1000L) { why = "main menu + " + graceS + " s"; break; }
      if (now - t0 > boundS * 1000L) { why = "bound " + boundS + " s"; break; }
      // Between scans the foreground is read every 10 ms: a steal can come with no foreground event (MEASURED
      // 2026-11-27: when Steam's "Launching..." window closed, the game took the foreground and no hook saw it; the
      // 100 ms scan put it back after 55 to 160 ms).
      for (int k = 0; k < 10; k++) { Thread.Sleep(10); lock (gate) OnFg(GetForegroundWindow(), "poll"); ZCheck(); }
    }
    PostThreadMessage(hookTid, 0x0012, IntPtr.Zero, IntPtr.Zero);   // WM_QUIT: the hook thread unhooks and ends
    hookThread.Join(5000);
    G("end", "\"why\":\"" + Esc(why) + "\",\"restores\":" + restores + ",\"pushes\":" + pushes);
    GC.KeepAlive(cb); GC.KeepAlive(showCb); GC.KeepAlive(hideCb);
    glog.Close();
    return 0;
  }
}
'''

PS1 = r'''
param([string]$Mode, [string]$A1, [string]$A2, [string]$A3, [string]$A4, [string]$A5, [string]$A6, [string]$A7, [string]$A8)
$ErrorActionPreference = 'Stop'
Add-Type -TypeDefinition (Get-Content -Raw -LiteralPath (Join-Path $PSScriptRoot 'rmwin.cs'))
if ($Mode -eq 'probe') { [void][RmWin]::Probe($A1, [int]$A2, [int]$A3, $A4, $A5) }
elseif ($Mode -eq 'guard') { [void][RmWin]::Guard($A1, $A2, $A3, [int]$A4, [int]$A5, [int]$A6, $A7, $A8) }
'''


def _storage():
    try:
        out = subprocess.run([sys.executable, os.path.expanduser("~/dev/Lodestar/bin/lib/agent_storage.py")],
                             capture_output=True, text=True, timeout=30)
        root = out.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        root = ""
    if not root:
        raise RuntimeError("agent_storage.py printed no root")
    return os.path.join(root, "scratch", "launch_behind")


def win_path(p):
    import game_instance
    return game_instance.win_path(p)


def _exe(name):
    import game_instance
    return game_instance._exe(name)


def scripts():
    """Write rmwin.cs and rmwin.ps1 into the scratch folder (derived files) -> that folder."""
    d = _storage()
    os.makedirs(d, exist_ok=True)
    for fn, text in (("rmwin.cs", CS), ("rmwin.ps1", PS1)):
        p = os.path.join(d, fn)
        try:
            with open(p, encoding="utf-8") as f:
                if f.read() == text:
                    continue
        except OSError:
            pass
        with open(p, "w", encoding="utf-8") as f:
            f.write(text)
    return d


def ps_argv(mode, *args):
    d = scripts()
    return [_exe("powershell.exe"), "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-File",
            win_path(os.path.join(d, "rmwin.ps1")), mode] + [str(a) for a in args]


def _spawn_hidden(argv):
    """Start a Windows process with no window, outliving this call -> its pid or None.
    Through WMI (Win32_Process.Create, ShowWindow 0; WMI refuses CREATE_NO_WINDOW with 21): the process is WMI's child, outside this
    shell's interop job. MEASURED 2026-11-27: a .NET Process.Start child held this call open for the child's whole life
    (16.3 s for a 15 s probe), even with its own pipes; Start-Process -WindowStyle Hidden opens a console host, which
    can flash, and a flash takes the foreground."""
    exe, rest = argv[0], argv[1:]
    win_exe = "powershell.exe" if exe.lower().endswith("powershell.exe") else exe
    cmd = " ".join([win_exe] + ['"%s"' % a.replace('"', '\\"') for a in rest]).replace("'", "''")
    script = ("$su = New-CimInstance -ClassName Win32_ProcessStartup -ClientOnly -Property @{ShowWindow=[uint16]0}; "
              "$r = Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments "
              "@{CommandLine='%s'; ProcessStartupInformation=$su}; 'PID|' + $r.ProcessId + '|' + $r.ReturnValue" % cmd)
    r = subprocess.run([_exe("powershell.exe"), "-NoProfile", "-NonInteractive", "-Command", script],
                       capture_output=True, text=True, timeout=60, stdin=subprocess.DEVNULL)
    for ln in (r.stdout or "").splitlines():
        parts = ln.strip().split("|")
        if len(parts) == 3 and parts[0] == "PID" and parts[2] == "0" and parts[1].isdigit():
            return int(parts[1])
    return None


SW_SHOWNOACTIVATE = 4


SW_SHOWNORMAL = 1


def start_script(exe, cwd, args, env_set=(), env_remove=(), front=None, show=None):
    """PowerShell that starts exe (Windows paths) and prints 'PID|<pid>|0', or 'PID||<WMI error>' when it could not.

    Through WMI (Win32_Process.Create), so the game is WMI's child, not a child of this shell: a shell that WSL started
    can count as started by the foreground window's process (his terminal), and a process with that lineage may take
    the foreground. Its first window is shown with `show` (default SW_SHOWNOACTIVATE; SW_SHOWNORMAL with a front
    reason). WMI gives the process only the environment that it is handed (MEASURED 2026-11-27: EnvironmentVariables
    replaces the whole block), so the script hands it this shell's own environment, less env_remove, plus env_set.
    Single quotes only: double quotes do not survive the WSL interop command line ($q makes them in PowerShell)."""
    q = lambda v: "'%s'" % str(v).replace("'", "''")      # noqa: E731
    if show is None:
        show = SW_SHOWNORMAL if front_reason(front) else SW_SHOWNOACTIVATE
    drop = [n.upper() for n, _ in env_set] + [n.upper() for n in env_remove]
    words = ["$q + %s + $q" % q(exe)] + [("$q + %s + $q" % q(a)) if (not a or " " in a) else q(a) for a in args]
    return ("$q = [string][char]34; "
            "$e = @(Get-ChildItem Env: | Where-Object { @(%s) -notcontains $_.Name.ToUpper() } | "
            "ForEach-Object { $_.Name + '=' + $_.Value }) + @(%s); "
            "$su = New-CimInstance -ClassName Win32_ProcessStartup -ClientOnly -Property @{ShowWindow=[uint16]%d; "
            "EnvironmentVariables=[string[]]$e}; "
            "$r = Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{CommandLine=(%s); "
            "CurrentDirectory=%s; ProcessStartupInformation=$su}; "
            "'PID|' + $r.ProcessId + '|' + $r.ReturnValue; if ($r.ReturnValue -ne 0) { exit 1 }"
            % (",".join(q(n) for n in drop) or "''", ",".join(q("%s=%s" % (n, v)) for n, v in env_set) or "",
               show, " + ' ' + ".join(words), q(cwd)))


def start_guard(player_log, sleep=time.sleep, clock=time.time):
    """Start the guard and wait for its READY -> (ok, text). Never raises: a launch never fails on its guard."""
    try:
        d = scripts()
        stamp = time.strftime("%Y%m%dT%H%M%S") + "_%d" % os.getpid()
        log = os.path.join(d, "guard_%s.jsonl" % stamp)
        ready = os.path.join(d, "guard_%s.ready" % stamp)
        pid = _spawn_hidden(ps_argv("guard", win_path(log), win_path(player_log) if player_log else "", DONE_MARKER,
                                    GRACE_S, NO_GAME_S, BOUND_S, ",".join(WATCH), win_path(ready)))
        if pid is None:
            return False, "guard: COULD NOT START (no pid from the hidden start)"
        t0 = clock()
        while clock() - t0 < READY_S:
            if os.path.exists(ready):
                return True, "guard pid %d, log %s" % (pid, win_path(log))
            sleep(0.2)
        return False, "guard: no READY in %d s (pid %d, log %s)" % (READY_S, pid, win_path(log))
    except Exception as e:      # noqa: BLE001
        return False, "guard: COULD NOT START (%s: %s)" % (type(e).__name__, e)


def front_reason(front=None):
    return (front or os.environ.get(FRONT_ENV, "") or "").strip()


def guarded(fire, player_log=None, front=None):
    """THE shared function: every start of a game calls this with the start as `fire` -> (fire()'s result, note).

    With no front reason, the guard is up before fire() runs, so the game's first window already meets it. With
    front="<reason>" (or RM_LAUNCH_FRONT), no guard starts and the note names the reason."""
    why = front_reason(front)
    if why:
        return fire(), "in front on purpose: %s" % why
    ok, note = start_guard(player_log)
    return fire(), ("behind his windows, %s" % note) if ok else note


if __name__ == "__main__":
    print(json.dumps({"scripts": scripts(), "front": front_reason()}))
