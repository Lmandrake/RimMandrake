// JawaBenchTpsSampler.cs - TPS is measured all the time, not investigated
// (BRIDGE_TPS_REGULAR_REPORT_1, rebuilt by BRIDGE_TPS_CAPTURE_FIXES_1).
//
// Owner, 2026-10-10: he regularly sees very slow (and fast) TPS that agents later "cannot reproduce".
// So the companion keeps a standing record that answers "was it slow at 3 pm, and why".
//
// HOW IT STARTS (item 1) - at game load, with NO bridge call
//   RimBridgeServer, once play data has loaded (Root_Update_Patch -> RimBridgeStartup.OnRuntimeReady ->
//   RimBridgeCapabilities.Initialize -> RimBridgeExtensionDiscovery.BuildProviders, decompiled from the
//   installed RimBridgeServer.dll 2026-10-10), calls Activator.CreateInstance on every companion type that
//   declares an INSTANCE [Tool] method. JawaBenchTpsTools is such a type; its constructor calls Install().
//   So the sampler starts at the main menu of every launch that has brrainz.rimbridgeserver active,
//   before anyone connects. (That first executed code also fires the module initializer, so the
//   JawaBenchInit lines and the other lazily-installed patches now install at load too.)
//
// WHAT IT RECORDS - all through JawaBenchTpsWriter (ordered, bounded, session-named segments)
//   session   once per process: pid, build, engine, mod count/digest; full manifest in session_<id>.json
//   game/menu each time a game is entered (with the save name) or left
//   sample    one WINDOW per ~5 real s of play (JawaBenchTpsMath.FrameAccumulator): ratio against
//             expected ticks integrated frame by frame, raw wall TPS, paused/explained/stall/ambiguous
//             seconds, fps, worst frame gap, tick-work share, coarse attribution (JawaBenchTpsProfiler),
//             writer health
//   incident  every frame gap > GapSeconds: stall (unexplained) or longevent (save / long event), with
//             the context below. Recovered stalls are KEPT - nothing is discarded for being long.
//   context   every 60 s of play: maps (id, size, biome, pawns, things), heap, process memory
//   silence / resumed   from the watchdog thread (JawaBenchTpsWatchdog) when the main thread stops
//   shutdown  on Application.quitting, after which the writer is drained and Player.log archived
//   error     the sampler disabled itself after an exception (it never retries every frame)
//   log       a Player.log was archived to tps/logs (Player-prev.log at start = the PREVIOUS session,
//             which is how a crashed session's log survives the next launch)
//
// SETTINGS - the companion is not a mod and has no settings screen, so the Mod Settings rule is met by
//   JawaBench/tps/tps_settings.json, written with the shipped defaults on first start: sampler,
//   attribution, watchdog, archivePlayerLog on/off, retentionDays, retentionMB, logRetentionMB.
//   All-off degrades to "no record", never to an error.
//
// ⛔ Main-thread patches never throw into the game loop: any exception disables the sampler, writes an
//    `error` line, and is reported by jawa/tps_report.
//
// Doc: design/RimMandrake/tps_record.md

using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Text;
using System.Text.RegularExpressions;
using System.Threading;
using System.Threading.Tasks;
using HarmonyLib;
using RimBridgeServer.Sdk;
using Verse;
using M = JawaBench.BridgeTools.JawaBenchTpsMath;
using W = JawaBench.BridgeTools.JawaBenchTpsWriter;
using WD = JawaBench.BridgeTools.JawaBenchTpsWatchdog;

namespace JawaBench.BridgeTools
{
    internal static class JawaBenchTpsSampler
    {
        private static readonly object Gate = new object();
        private static readonly Queue<string> Ring = new Queue<string>();
        private static readonly List<double> Streak = new List<double>();   // unbroken run-window ratios

        internal static bool Installed;
        internal static string InstallError, RuntimeError, StartedUtc, StartedBy, RecordDir, SettingsNote;
        /// <summary>complete | partial | failed | disabled (MUST 16), with the per-target detail.</summary>
        internal static string InstallStatus = "not-attempted", InstallDetail;
        internal static JawaBenchTpsSettings Settings = new JawaBenchTpsSettings();
        internal static int Windows, Incidents;
        private static bool _attempted;
        internal static readonly string Session = Guid.NewGuid().ToString("N");

        // ---- main-thread state ------------------------------------------------------------------
        private static readonly M.FrameAccumulator Acc = new M.FrameAccumulator();
        private static Game _game;
        internal static readonly JawaBenchTpsLifecycle Life = new JawaBenchTpsLifecycle(JawaBenchTpsProfiler.Stages);
        internal static readonly JawaBenchTpsExplained Explained = new JawaBenchTpsExplained();
        private static bool _leOpen;
        private static double _tmuStart, _lastSim, _lastContext = -1, _lastMarker;
        private static int _ticksPre, _gcAtPre;
        private static string _logPath;     // cached on the main thread at install: ProcessExit may run elsewhere

        internal static void Install(string startedBy)
        {
            lock (Gate)
            {
                if (_attempted) return;
                _attempted = true;
                try
                {
                    RecordDir = Path.Combine(Path.Combine(GenFilePaths.SaveDataFolderPath, "JawaBench"), "tps");
                    Directory.CreateDirectory(RecordDir);
                    Settings = JawaBenchTpsSettings.Load(RecordDir, out SettingsNote);
                    if (!Settings.Sampler)
                    {
                        InstallError = "disabled by tps_settings.json (sampler: false)";
                        InstallStatus = "disabled";
                        Log.Message("[JawaBench] TPS sampler OFF by " + Path.Combine(RecordDir, "tps_settings.json"));
                        return;
                    }
                    W.RetentionDays = Settings.RetentionDays;
                    W.RetentionCapBytes = (long)(Settings.RetentionMB * 1048576.0);
                    W.LogRetentionCapBytes = (long)(Settings.LogRetentionMB * 1048576.0);
                    int pid = System.Diagnostics.Process.GetCurrentProcess().Id;
                    try { _logPath = UnityEngine.Application.consoleLogPath; } catch { }
                    W.Start(RecordDir, Session, pid);
                    StartedBy = startedBy;
                    StartedUtc = W.Utc();

                    // MUST 16: resolve every target, then patch; any failure rolls back THIS recorder's patches
                    // (UnpatchAll of our own Harmony id only) - a half-installed sampler never runs.
                    const string hid = "mandrake.jawabench.tps";
                    var h = new Harmony(hid);
                    var self = typeof(JawaBenchTpsSampler);
                    Func<string, HarmonyMethod> hm = n => new HarmonyMethod(self.GetMethod(n, BindingFlags.Static | BindingFlags.NonPublic));
                    var targets = new List<JawaBenchTpsInstall.Target>
                    {
                        new JawaBenchTpsInstall.Target("TickManagerUpdate", true, () => AccessTools.Method(typeof(TickManager), nameof(TickManager.TickManagerUpdate))),
                        new JawaBenchTpsInstall.Target("Root.Update", true, () => AccessTools.Method(typeof(Root), nameof(Root.Update))),
                        new JawaBenchTpsInstall.Target("LongEventsUpdate", false, () => AccessTools.Method(typeof(LongEventHandler), nameof(LongEventHandler.LongEventsUpdate))),
                        new JawaBenchTpsInstall.Target("SaveGame", false, () => AccessTools.Method(typeof(GameDataSaveLoader), nameof(GameDataSaveLoader.SaveGame), new[] { typeof(string) })),
                        new JawaBenchTpsInstall.Target("LoadGame", false, () => AccessTools.Method(typeof(GameDataSaveLoader), nameof(GameDataSaveLoader.LoadGame), new[] { typeof(string) })),
                    };
                    InstallStatus = JawaBenchTpsInstall.Run(targets, (name, m) =>
                    {
                        var mi = (MethodInfo)m;
                        switch (name)
                        {
                            case "TickManagerUpdate": h.Patch(mi, prefix: hm(nameof(TmuPrefix)), postfix: hm(nameof(TmuPostfix))); break;
                            case "Root.Update": h.Patch(mi, prefix: hm(nameof(RootPrefix)), postfix: hm(nameof(RootPostfix))); break;
                            case "LongEventsUpdate": h.Patch(mi, prefix: hm(nameof(LePrefix)), finalizer: hm(nameof(LeFinalizer))); break;
                            case "SaveGame": h.Patch(mi, prefix: hm(nameof(SavePrefix)), finalizer: hm(nameof(SaveFinalizer))); break;
                            case "LoadGame": h.Patch(mi, prefix: hm(nameof(LoadPrefix))); break;
                        }
                    }, () => h.UnpatchAll(hid), out InstallDetail);
                    if (InstallStatus == "failed")
                    {
                        InstallError = "install failed, rolled back: " + InstallDetail;
                        W.Enqueue("error", "\"where\":\"install\",\"status\":\"failed\",\"error\":" + W.Json(InstallDetail));
                        Log.Warning("[JawaBench] TPS sampler NOT installed: " + InstallDetail);
                        return;
                    }
                    if (Settings.Attribution) JawaBenchTpsProfiler.Install();
                    if (Settings.Watchdog) WD.Start(RecordDir);
                    try { UnityEngine.Application.quitting += OnQuit; } catch { }
                    try { AppDomain.CurrentDomain.ProcessExit += (s, e) => OnQuit(); } catch { }
                    Installed = true;

                    WriteSessionStart(pid);
                    if (Settings.ArchivePlayerLog) ArchivePrevLog();
                    Log.Message("[JawaBench] TPS sampler installed (" + startedBy + "): session " + Session + " pid " + pid +
                                " -> " + W.CurrentPath + (Settings.Attribution ? "; attribution " + JawaBenchTpsProfiler.PatchedStages +
                                " stages" : "; attribution off") + (JawaBenchTpsProfiler.InstallError != null ? " (" + JawaBenchTpsProfiler.InstallError + ")" : ""));
                }
                catch (Exception e)
                {
                    InstallError = e.GetType().Name + ": " + e.Message;
                    InstallStatus = "failed";
                    try { new Harmony("mandrake.jawabench.tps").UnpatchAll("mandrake.jawabench.tps"); } catch { }
                    try { JawaBenchTpsProfiler.Rollback(); } catch { }
                    try { W.Enqueue("error", "\"where\":\"install\",\"status\":\"failed\",\"error\":" + W.Json(InstallError)); } catch { }
                    Log.Warning("[JawaBench] TPS sampler NOT installed: " + InstallError);
                }
            }
        }

        // ---- session metadata (item 6) -----------------------------------------------------------
        private static void WriteSessionStart(int pid)
        {
            string build = "unknown", engine = "unknown", modDigest = "unmeasured";
            int modCount = -1;
            var mods = new List<string>();
            try
            {
                var attr = typeof(JawaBenchTpsSampler).Assembly.GetCustomAttribute<AssemblyInformationalVersionAttribute>();
                if (attr != null) { string v = attr.InformationalVersion; int p = v.IndexOf('+'); build = p >= 0 ? v.Substring(p + 1) : v; if (build.Length > 12) build = build.Substring(0, 12); }
            }
            catch { }
            try { engine = RimWorld.VersionControl.CurrentVersionStringWithRev; } catch { }
            try
            {
                mods = LoadedModManager.RunningModsListForReading.Select(m => m.PackageId ?? "").ToList();
                modCount = mods.Count;
                unchecked
                {
                    uint hsh = 2166136261;
                    foreach (char c in string.Join(",", mods.OrderBy(x => x, StringComparer.Ordinal))) { hsh ^= c; hsh *= 16777619; }
                    modDigest = hsh.ToString("x8");
                }
            }
            catch { }
            string owners = "{}";
            try
            {
                var counts = new Dictionary<string, int>();
                foreach (var m in Harmony.GetAllPatchedMethods())
                {
                    var info = Harmony.GetPatchInfo(m);
                    if (info == null) continue;
                    foreach (var o in info.Owners) counts[o] = counts.TryGetValue(o, out var n) ? n + 1 : 1;
                }
                owners = "{" + string.Join(",", counts.OrderByDescending(kv => kv.Value).Select(kv => W.Json(kv.Key) + ":" + kv.Value)) + "}";
            }
            catch { }
            string logPath = _logPath ?? "";
            W.Enqueue("session", "\"pid\":" + pid + ",\"startedBy\":" + W.Json(StartedBy) + ",\"build\":" + W.Json(build) +
                                 ",\"engine\":" + W.Json(engine) + ",\"mods\":" + modCount + ",\"modDigest\":\"" + modDigest + "\"" +
                                 ",\"playerLog\":" + W.Json(logPath) + ",\"settings\":" + Settings.ToJson() + ",\"settingsNote\":" + W.Json(SettingsNote) +
                                 ",\"install\":{\"sampler\":" + W.Json(InstallStatus) + ",\"samplerDetail\":" + W.Json(InstallDetail) +
                                 ",\"attribution\":" + W.Json(Settings.Attribution ? JawaBenchTpsProfiler.InstallStatus : "disabled") +
                                 ",\"attributionDetail\":" + W.Json(JawaBenchTpsProfiler.InstallDetail) +
                                 ",\"watchdog\":" + (Settings.Watchdog ? "\"started\"" : "\"disabled\"") + "}" +
                                 ",\"segment\":" + W.Json(Path.GetFileName(W.CurrentPath)));
            ThreadPool.QueueUserWorkItem(_ =>
            {
                try
                {
                    File.WriteAllText(Path.Combine(RecordDir, "session_" + Session + ".json"),
                        "{\"session\":\"" + Session + "\",\"pid\":" + pid + ",\"build\":" + W.Json(build) + ",\"engine\":" + W.Json(engine) +
                        ",\"modDigest\":\"" + modDigest + "\",\"mods\":[" + string.Join(",", mods.Select(W.Json)) + "]" +
                        ",\"harmonyOwners\":" + owners + "}\n");
                }
                catch (Exception e) { W.Enqueue("error", "\"where\":\"manifest\",\"error\":" + W.Json(e.Message)); }
            });
            Marker("start");
        }

        /// <summary>A Player.log line that joins the log to the record: session, pid, seq, utc.</summary>
        private static void Marker(string why)
        {
            try
            {
                long seq = W.Enqueue("marker", "\"why\":" + W.Json(why));
                Log.Message("[JawaBench] TPS marker " + why + ": session " + Session + " seq " + (seq < 0 ? "DROPPED (writer full)" : seq.ToString(CultureInfo.InvariantCulture)) + " utc " + W.Utc());
            }
            catch { }
        }

        private static void ArchivePrevLog()
        {
            try
            {
                string cur = _logPath;
                if (string.IsNullOrEmpty(cur)) return;
                string prev = Path.Combine(Path.GetDirectoryName(cur), "Player-prev.log");
                if (!File.Exists(prev)) return;
                DateTime mt = File.GetLastWriteTimeUtc(prev);
                string stamp = mt.ToString("yyyyMMdd'T'HHmmss'Z'", CultureInfo.InvariantCulture);
                W.ArchiveLog(prev, "Player-prev_" + stamp + ".log", PreviousSession(mt));
            }
            catch { }
        }

        /// <summary>The session whose heartbeat last changed closest before the previous log's last write (within
        /// 10 min): the session that log belongs to, recorded on the `log` row (MUST 12).</summary>
        private static string PreviousSession(DateTime logMtimeUtc)
        {
            try
            {
                string best = null;
                double bestGap = 600;
                foreach (var f in new DirectoryInfo(RecordDir).GetFiles("hb_*.json"))
                {
                    string sid = Path.GetFileNameWithoutExtension(f.Name).Substring(3);
                    if (sid == Session) continue;
                    double gap = Math.Abs((logMtimeUtc - f.LastWriteTimeUtc).TotalSeconds);
                    if (gap < bestGap) { bestGap = gap; best = sid; }
                }
                return best;
            }
            catch { return null; }
        }

        private static int _quit;

        private static void OnQuit()
        {
            if (Interlocked.Exchange(ref _quit, 1) == 1) return;
            try
            {
                // MUST 16: intent, bounded drain, bounded log copy, then a completion row that says what finished.
                // No Unity API here: ProcessExit can call this off the main thread (the log path was cached).
                string cur = _logPath;
                W.Shutdown("\"windows\":" + Windows + ",\"incidents\":" + Incidents,
                           Settings.ArchivePlayerLog && !string.IsNullOrEmpty(cur)
                               ? (Func<string>)(() => W.ArchiveLogNow(cur, "Player_" + W.Utc().Replace(":", "").Replace("-", "").Substring(0, 15) + "Z_" + Session.Substring(0, 8) + ".log", Session))
                               : null,
                           2000, 3000);
            }
            catch { }
        }

        private static void Fail(string where, Exception e)
        {
            RuntimeError = where + ": " + e.GetType().Name + ": " + e.Message;
            try { W.Enqueue("error", "\"where\":" + W.Json(where) + ",\"error\":" + W.Json(e.GetType().Name + ": " + e.Message)); } catch { }
            try { Log.Warning("[JawaBench] TPS sampler disabled after an exception: " + RuntimeError); } catch { }
        }

        // ---- Root.Update: heartbeat, menu/game transitions, long-event time (every frame) --------
        private static void RootPrefix()
        {
            WD.Beat();      // always: a disabled sampler must not read as a silent main thread
            if (JawaBenchTpsProfiler.MainThreadId < 0) JawaBenchTpsProfiler.MainThreadId = Thread.CurrentThread.ManagedThreadId;
            if (RuntimeError != null) return;
            try
            {
                double now = WD.Now;
                Explained.RootPre(now);
                Game game = Current.Game;
                bool playing = game != null && Current.ProgramState == ProgramState.Playing;
                var ev = Life.OnFrame(game, playing, now);
                if (ev != JawaBenchTpsLifecycle.Event.None) WD.LastSave = "";     // game-scoped (MUST 6)
                if (ev == JawaBenchTpsLifecycle.Event.Menu)
                {
                    _game = null;
                    Acc.Reset();
                    Explained.Reset();
                    BreakStreak();
                    W.Enqueue("menu", "\"programState\":\"" + Current.ProgramState + "\"");
                }
                if (!playing)
                {
                    if (game == null) WD.Set(WD.PMenu);
                    return;
                }
                if (ev == JawaBenchTpsLifecycle.Event.Game)
                {
                    _game = game;
                    Acc.Reset();
                    Explained.Reset();
                    BreakStreak();
                    _lastContext = -1;
                    var tm = game.tickManager;
                    W.Enqueue("game", "\"game\":" + Life.GameSeq + ",\"save\":" + W.Json(Life.SaveName) +
                                      ",\"ticksGame\":" + (tm != null ? tm.TicksGame : -1) +
                                      ",\"maps\":" + (game.Maps != null ? game.Maps.Count : 0));
                    Marker("game");
                }
            }
            catch (Exception e) { Fail("root-prefix", e); }
        }

        private static void RootPostfix()
        {
            if (RuntimeError != null) return;
            try
            {
                bool waiting = LongEventHandler.ShouldWaitForEvent;
                WD.LastLongEvent = waiting || LongEventHandler.AnyEventNowOrWaiting;
                Explained.RootPost(waiting);
                WD.Set(WD.PGuiRender);
                try { WD.LastFocused = UnityEngine.Application.isFocused; } catch { }
                double now = WD.Now;
                if (now - _lastMarker >= 3600) { _lastMarker = now; if (now > 60) Marker("hourly"); }
            }
            catch (Exception e) { Fail("root-postfix", e); }
        }

        // MUST 15: long-event and save scopes open in a prefix and close in a void FINALIZER, which runs whether
        // the original returned or threw and rethrows the original exception unchanged (Harmony 2.4.2,
        // decompiled). Every body is contained: a telemetry failure disables the sampler, never the game.
        private static void LePrefix()
        {
            _leOpen = false;
            if (RuntimeError != null) return;
            try
            {
                if (!LongEventHandler.AnyEventNowOrWaiting) return;
                _leOpen = true;
                Explained.LongEventBegin(WD.Now);
                WD.Enter(WD.PLongEvent);
            }
            catch (Exception e) { Fail("le-prefix", e); }
        }

        private static void LeFinalizer()
        {
            if (!_leOpen) return;
            _leOpen = false;
            try { Explained.LongEventEnd(WD.Now); WD.Exit(); }
            catch (Exception e) { Fail("le-finalizer", e); }
        }

        private static void SavePrefix(string fileName, out double __state)
        {
            __state = -1;
            try
            {
                __state = WD.Now;
                Explained.SaveBegin(__state);
                WD.LastSave = fileName ?? "";
                WD.Enter(WD.PSave);
            }
            catch (Exception e) { Fail("save-prefix", e); }
        }

        private static void SaveFinalizer(string fileName, double __state, Exception __exception)
        {
            if (__state < 0) return;
            try
            {
                double now = WD.Now, d = now - __state;
                Explained.SaveEnd(now);
                Life.OnSave(d);
                WD.Exit();
                if (RuntimeError == null)
                    W.Enqueue("save", "\"file\":" + W.Json(fileName) + ",\"saveS\":" + M.F(d, 3) +
                                      (__exception != null ? ",\"threw\":" + W.Json(__exception.GetType().Name) : ""));
            }
            catch (Exception e) { Fail("save-finalizer", e); }
        }

        private static void LoadPrefix(string saveFileName)
        {
            try
            {
                Life.OnLoadRequested(saveFileName, WD.Now);
                WD.Set(WD.PLoad);
            }
            catch (Exception e) { Fail("load-prefix", e); }
        }

        // ---- TickManager.TickManagerUpdate: the window (once per played frame) -------------------
        private static void TmuPrefix(TickManager __instance)
        {
            if (RuntimeError != null || __instance == null || _game == null) return;
            try
            {
                double now = WD.Now;
                bool paused = __instance.Paused;
                double mult = __instance.TickRateMultiplier;
                _ticksPre = __instance.TicksGame;
                double ex = Explained.Take(now);
                var g = Acc.Pre(now, paused, mult, _ticksPre, ex);
                if (g.HasValue) Incident(g.Value, __instance, paused, mult);
                // MUST 3: the window closes HERE, before this frame's tick work, so its attribution totals hold
                // exactly the invocations that started inside it.
                var closed = Acc.TakeClosed();
                if (closed != null) Emit(closed, __instance);
                _gcAtPre = GC.CollectionCount(0);
                WD.LastPaused = paused;
                WD.LastMult = M.F(mult, 2);
                WD.LastSpeed = __instance.CurTimeSpeed.ToString();
                WD.LastTicksGame = _ticksPre;
                WD.Enter(WD.PTickUpdate);
                _tmuStart = WD.Now;
            }
            catch (Exception e) { Fail("tick-prefix", e); }
        }

        private static void TmuPostfix(TickManager __instance)
        {
            if (RuntimeError != null || __instance == null || _game == null || !Acc.Open) return;
            try
            {
                double sim = WD.Now - _tmuStart;
                WD.Exit();
                _lastSim = sim;
                int ticks = __instance.TicksGame;
                WD.LastTicksGame = ticks;
                Acc.Post(__instance.TickRateMultiplier, ticks, sim);
            }
            catch (Exception e) { Fail("tick-postfix", e); }
        }

        private static void Incident(M.Gap g, TickManager tm, bool paused, double mult)
        {
            Incidents++;
            string quiet = Interlocked.Exchange(ref WD.QuietPhase, null);
            W.Enqueue("incident", "\"game\":" + Life.GameSeq + "," + M.IncidentFields(g, quiet, _lastSim, GC.CollectionCount(0) - _gcAtPre, Life.SaveTotal,
                                                   WD.LastSave, WD.ContextFields()));
        }

        private static double _streakMono = -1;

        private static void BreakStreak() { lock (Gate) Streak.Clear(); }

        private static void Emit(M.Window w, TickManager tm)
        {
            Windows++;
            var sb = new StringBuilder(900);
            sb.Append(M.WindowFields(w))
              .Append(",\"game\":").Append(Life.GameSeq)
              .Append(",\"speed\":\"").Append(tm.CurTimeSpeed.ToString()).Append('"')
              .Append(",\"tg\":").Append(tm.TicksGame)
              .Append(",\"tickMs\":").Append(M.F(tm.MeanTickTime, 3))
              .Append(",\"focused\":").Append(WD.LastFocused ? "true" : "false")
              .Append(",\"gc\":").Append(GC.CollectionCount(0))
              .Append(",\"heapMB\":").Append(M.F(GC.GetTotalMemory(false) / 1048576.0, 1));
            if (JawaBenchTpsProfiler.Installed) sb.Append(',').Append(JawaBenchTpsProfiler.TakeWindowFields());
            sb.Append(',').Append(W.HealthFields());
            string fields = sb.ToString();
            W.Enqueue("sample", fields);
            string state = w.State;
            lock (Gate)
            {
                Ring.Enqueue("{\"utc\":\"" + W.Utc() + "\"," + fields + "}");
                while (Ring.Count > M.RingCapacity) Ring.Dequeue();
                if (state == M.StateRun && !double.IsNaN(w.Ratio)) { Streak.Add(M.StreakValue(w.Ratio)); if (Streak.Count > M.RingCapacity) Streak.RemoveAt(0); }
                else Streak.Clear();
                _streakMono = WD.Now;
            }
            double now = WD.Now;
            if (_lastContext < 0 || now - _lastContext >= 60) { _lastContext = now; Context(); }
        }

        /// <summary>Periodic colony context (item 6): cheap counts only, no full-map enumeration.</summary>
        private static void Context()
        {
            var sb = new StringBuilder(400);
            sb.Append("\"maps\":[");
            int i = 0;
            foreach (var map in Find.Maps)
            {
                if (i >= 8) break;
                if (i++ > 0) sb.Append(',');
                sb.Append("{\"id\":").Append(map.uniqueID)
                  .Append(",\"size\":\"").Append(map.Size.x).Append('x').Append(map.Size.z).Append('"')
                  .Append(",\"biome\":").Append(W.Json(map.Biome?.defName))
                  .Append(",\"pawns\":").Append(map.mapPawns?.AllPawnsSpawnedCount ?? -1)
                  .Append(",\"things\":").Append(map.listerThings?.AllThings?.Count ?? -1)
                  .Append(",\"current\":").Append(ReferenceEquals(map, Find.CurrentMap) ? "true" : "false")
                  .Append('}');
            }
            sb.Append("],\"mapCount\":").Append(Find.Maps.Count);
            sb.Append(",\"worldPawns\":").Append(Find.WorldPawns?.AllPawnsAliveOrDead?.Count ?? -1);
            sb.Append(",\"heapMB\":").Append(M.F(GC.GetTotalMemory(false) / 1048576.0, 1));
            try
            {
                var p = System.Diagnostics.Process.GetCurrentProcess();
                sb.Append(",\"workingSetMB\":").Append(M.F(p.WorkingSet64 / 1048576.0, 1));
            }
            catch { }
            sb.Append(",\"save\":").Append(W.Json(Life.SaveName));
            W.Enqueue("context", sb.ToString());
        }

        // ---- the [Tool] -----------------------------------------------------------------------------
        internal static object Report(int last)
        {
            List<string> lines;
            List<double> streak;
            lock (Gate) { lines = Ring.ToList(); streak = Streak.ToList(); }
            if (last <= 0) last = 60;
            var tail = lines.Skip(Math.Max(0, lines.Count - last)).ToList();
            var rat = new List<double>();
            foreach (var l in tail)
            {
                if (l.IndexOf("\"state\":\"run\"", StringComparison.Ordinal) < 0) continue;
                double r;
                if (TryField(l, "ratio", out r)) rat.Add(r);
            }
            return new
            {
                success = Installed && RuntimeError == null,
                installed = Installed,
                installStatus = InstallStatus,
                installDetail = InstallDetail,
                installError = InstallError,
                runtimeError = RuntimeError,
                writeError = W.LastError,
                startedBy = StartedBy,
                samplerStartedUtc = StartedUtc,
                session = Session,
                note = "Starts at game load (RimBridgeServer companion registration), no bridge call needed. Judge ratio " +
                       "(ticks / expected ticks integrated frame by frame over unpaused time); only state=run windows are judged. " +
                       "Stalls are kept as incidents. Read history with src/RimMandrake/Utils/tps_record.py --at/--since.",
                cadenceSeconds = M.CadenceSeconds,
                recordDir = RecordDir,
                segment = W.CurrentPath,
                writer = new { enqueued = W.Enqueued, written = W.Written, dropped = W.Dropped, writeErrors = W.WriteErrors, queue = W.QueueDepth, lastError = W.LastError },
                watchdog = new { phase = WD.PhaseName, silenceLines = WD.SilenceLines, heartbeat = WD.HeartbeatPath },
                attribution = new
                {
                    installed = JawaBenchTpsProfiler.Installed,
                    stages = JawaBenchTpsProfiler.PatchedStages,
                    status = JawaBenchTpsProfiler.InstallStatus,
                    detail = JawaBenchTpsProfiler.InstallDetail,
                    error = JawaBenchTpsProfiler.InstallError,
                    runtimeError = JawaBenchTpsProfiler.RuntimeError,
                    costPerTimerPairUs = Math.Round(JawaBenchTpsProfiler.CostPerPairSeconds * 1e6, 4),
                },
                settings = Settings.ToJson(),
                windows = Windows,
                incidents = Incidents,
                samplesInMemory = lines.Count,
                returned = tail.Count,
                runWindows = rat.Count,
                ratioMin = rat.Count > 0 ? (double?)rat.Min() : null,
                ratioMedian = rat.Count > 0 ? (double?)M.Median(rat) : null,
                ratioMax = rat.Count > 0 ? (double?)rat.Max() : null,
                sustained = M.SustainedFresh(streak, _streakMono < 0 ? double.MaxValue : WD.Now - _streakMono),
                samplesJsonl = tail,
            };
        }

        private static bool TryField(string line, string key, out double v)
        {
            v = 0;
            string k = "\"" + key + "\":";
            int i = line.IndexOf(k, StringComparison.Ordinal);
            if (i < 0) return false;
            i += k.Length;
            int j = i;
            while (j < line.Length && line[j] != ',' && line[j] != '}') j++;
            return double.TryParse(line.Substring(i, j - i), NumberStyles.Float, CultureInfo.InvariantCulture, out v);
        }
    }

    /// <summary>
    /// The TPS tool, deliberately an INSTANCE [Tool] on a type with a public parameterless constructor:
    /// RimBridgeServer constructs such types when it registers companions at game load
    /// (RimBridgeExtensionDiscovery.TryCreateInstance), and the constructor starts the sampler. This is
    /// what makes the record independent of any bridge call (BRIDGE_TPS_CAPTURE_FIXES_1, item 1).
    /// ⛔ Keep the constructor public, parameterless and non-throwing; make the tool static and the
    /// sampler goes back to starting only on the first jawa/ call.
    /// </summary>
    public sealed class JawaBenchTpsTools
    {
        public JawaBenchTpsTools()
        {
            try { JawaBenchTpsSampler.Install("bridge-registration"); }
            catch { }
        }

        [Tool(
            "jawa/tps_report",
            Description =
                "The standing TPS record (BRIDGE_TPS_CAPTURE_FIXES_1): starts at game load with no bridge call. One window " +
                "per ~5 real seconds of play: ratio = ticks / expected ticks (60 x the effective multiplier, integrated frame " +
                "by frame over UNPAUSED time), raw wall tps, paused/explained/stall seconds, fps, tick-work share, coarse " +
                "attribution (tick lists, world, maps, components). Frame gaps > 2 s are kept as incidents (stall or " +
                "longevent). Read-only. The on-disk record (recordDir, session-named segments, 7+ days) survives restarts; " +
                "read history with src/RimMandrake/Utils/tps_record.py --at/--since --tz.",
            ResultDescription =
                "success, startedBy, samplerStartedUtc, session, recordDir, segment, writer health, watchdog phase, " +
                "attribution status, samplesJsonl (last N windows), ratioMin/Median/Max over run windows, sustained " +
                "(low|high|ok|unknown over an unbroken run streak), errors if any.")]
        public Task<object> TpsReport(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "How many of the most recent windows to return (default 60 = 5 minutes; max 720).")] int last = 60)
        {
            JawaBenchTpsSampler.Install("tool-call");
            return Task.FromResult(JawaBenchTpsSampler.Report(Math.Min(last, M.RingCapacity)));
        }
    }
}
