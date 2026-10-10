// JawaBenchTpsSampler.cs - TPS is measured all the time, not investigated (BRIDGE_TPS_REGULAR_REPORT_1).
//
// Owner, 2026-10-10: he regularly sees very slow (and fast) TPS that agents later "cannot reproduce".
// So the companion keeps a standing record: every 5 real seconds of play, one sample of
// ticks-per-real-second with the speed setting, its effective multiplier and the paused share, so a
// speed-1 reading is never mistaken for slowness at speed 4.
//
// HOW IT RUNS
//   * A Harmony POSTFIX on Verse.TickManager.TickManagerUpdate - called once per frame by
//     Game.UpdatePlay, on the main thread, only while a game is being played. Per frame it does a
//     handful of field reads and one float compare; the sample maths runs once per 5 s and the file
//     append is handed to the thread pool, so the main thread never touches the disk.
//   * Installed from JawaBenchInit.Announce, which is LAZY: it fires on the first jawa/ call of a
//     session (JAWABENCH_INIT_LINE_IS_LAZY_1). Play before that call is NOT sampled. belt_watchdog's
//     probe calls jawa/tps_report, which starts it. The tool reports samplerStartedUtc so a gap is
//     never read as "TPS was fine".
//   * Record: <SaveData>/JawaBench/tps/tps.jsonl, rotated to tps.1.jsonl at 1 MB (outside git).
//   * The maths (window, paused/speed normalisation, rotation, sustained judgement) is
//     JawaBenchTpsMath.cs, selftested offline against the Python reader (selftest_tps_record.py).
//
// ⛔ The postfix must never throw into the game loop: everything is inside a catch, and a
// failure disables the sampler and is reported by the tool rather than retried every frame.
//
// Doc: design/RimMandrake/tps_record.md

using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using HarmonyLib;
using RimBridgeServer.Sdk;
using Verse;
using M = JawaBench.BridgeTools.JawaBenchTpsMath;

namespace JawaBench.BridgeTools
{
    internal static class JawaBenchTpsSampler
    {
        private static readonly object Gate = new object();
        private static readonly object FileGate = new object();
        private static readonly Queue<string> Ring = new Queue<string>();
        private static readonly List<float> RunRatios = new List<float>();   // ratios of state=run, capped

        internal static bool Installed;
        internal static string InstallError;
        internal static string RuntimeError;
        internal static string StartedUtc;
        internal static string RecordPath;
        internal static string WriteError;
        internal static int SamplesWritten;
        internal static int WindowsDropped;
        private static bool _attempted;
        private static readonly string Session = Guid.NewGuid().ToString("N").Substring(0, 8);

        // ---- window state: main thread only -------------------------------------------------
        private static bool _open;
        private static Game _game;
        private static float _t0;
        private static int _tick0;
        private static int _gc0;
        private static int _frames;
        private static int _pausedFrames;
        private static float _frameMax;
        private static TimeSpeed _speed0;
        private static bool _speedChanged;

        internal static void Install()
        {
            lock (Gate)
            {
                if (_attempted) return;
                _attempted = true;
                try
                {
                    string dir = Path.Combine(Path.Combine(GenFilePaths.SaveDataFolderPath, "JawaBench"), "tps");
                    Directory.CreateDirectory(dir);
                    RecordPath = Path.Combine(dir, "tps.jsonl");

                    var m = AccessTools.Method(typeof(TickManager), nameof(TickManager.TickManagerUpdate));
                    if (m == null)
                    {
                        InstallError = "TickManager.TickManagerUpdate not found";
                        Log.Warning("[JawaBench] TPS sampler NOT installed: " + InstallError);
                        return;
                    }
                    new Harmony("mandrake.jawabench.tps").Patch(m, postfix: new HarmonyMethod(
                        typeof(JawaBenchTpsSampler).GetMethod(nameof(Postfix), BindingFlags.Static | BindingFlags.NonPublic)));
                    Installed = true;
                    StartedUtc = DateTime.UtcNow.ToString("yyyy-MM-ddTHH:mm:ssZ");
                    Log.Message("[JawaBench] TPS sampler installed: one sample per " + M.CadenceSeconds +
                                " s of play -> " + RecordPath);
                }
                catch (Exception e)
                {
                    InstallError = e.GetType().Name + ": " + e.Message;
                    Log.Warning("[JawaBench] TPS sampler NOT installed: " + InstallError);
                }
            }
        }

        private static void Postfix(TickManager __instance)
        {
            if (RuntimeError != null) return;
            try
            {
                Game game = Current.Game;
                if (game == null || __instance == null) { _open = false; return; }
                float now = UnityEngine.Time.realtimeSinceStartup;
                TimeSpeed speed = __instance.CurTimeSpeed;
                if (!_open || !ReferenceEquals(game, _game))
                {
                    Open(game, __instance, now, speed);
                    return;
                }
                _frames++;
                if (__instance.Paused) _pausedFrames++;
                if (speed != _speed0) _speedChanged = true;
                float dt = UnityEngine.Time.unscaledDeltaTime;
                if (dt > _frameMax) _frameMax = dt;

                float dReal = now - _t0;
                if (dReal < M.CadenceSeconds) return;

                int dTicks = __instance.TicksGame - _tick0;
                if (M.WindowUsable(dReal, dTicks))
                    Emit(__instance, dReal, dTicks, speed);
                else
                    WindowsDropped++;
                Open(game, __instance, now, speed);
            }
            catch (Exception e)
            {
                RuntimeError = e.GetType().Name + ": " + e.Message;
                try { Log.Warning("[JawaBench] TPS sampler disabled after an exception: " + RuntimeError); } catch { }
            }
        }

        private static void Open(Game game, TickManager tm, float now, TimeSpeed speed)
        {
            _open = true;
            _game = game;
            _t0 = now;
            _tick0 = tm.TicksGame;
            _gc0 = GC.CollectionCount(0);
            _frames = 0;
            _pausedFrames = 0;
            _frameMax = 0f;
            _speed0 = speed;
            _speedChanged = false;
        }

        private static void Emit(TickManager tm, float dReal, int dTicks, TimeSpeed speed)
        {
            float mult = tm.TickRateMultiplier;
            var s = M.Compute(dTicks, dReal, _frames, _pausedFrames, mult, _speedChanged);
            int gc = GC.CollectionCount(0) - _gc0;
            var sb = new StringBuilder(320);
            sb.Append("{\"utc\":\"").Append(DateTime.UtcNow.ToString("yyyy-MM-ddTHH:mm:ssZ")).Append('"')
              .Append(",\"session\":\"").Append(Session).Append('"')
              .Append(",\"tg\":").Append(tm.TicksGame)
              .Append(",\"dReal\":").Append(M.F(dReal, 3))
              .Append(",\"dTicks\":").Append(dTicks)
              .Append(",\"tps\":").Append(M.F(s.Tps, 2))
              .Append(",\"speed\":\"").Append(speed.ToString()).Append('"')
              .Append(",\"mult\":").Append(M.F(mult, 2))
              .Append(",\"target\":").Append(M.F(s.Target, 2))
              .Append(",\"ratio\":").Append(M.F(s.Ratio, 3))
              .Append(",\"state\":\"").Append(s.State).Append('"')
              .Append(",\"pausedFrac\":").Append(M.F(s.PausedFrac, 3))
              .Append(",\"frames\":").Append(_frames)
              .Append(",\"fps\":").Append(M.F(dReal > 0f ? _frames / dReal : 0f, 1))
              .Append(",\"frameMaxMs\":").Append(M.F(_frameMax * 1000f, 1))
              .Append(",\"tickMs\":").Append(M.F(tm.MeanTickTime, 3))
              .Append(",\"gc0\":").Append(gc)
              .Append('}');
            string line = sb.ToString();

            lock (Gate)
            {
                Ring.Enqueue(line);
                while (Ring.Count > M.RingCapacity) Ring.Dequeue();
                if (s.State == M.StateRun)
                {
                    RunRatios.Add(s.Ratio);
                    if (RunRatios.Count > M.RingCapacity) RunRatios.RemoveAt(0);
                }
            }
            ThreadPool.QueueUserWorkItem(_ => Append(line));
        }

        private static void Append(string line)
        {
            try
            {
                lock (FileGate)
                {
                    byte[] bytes = Encoding.UTF8.GetBytes(line + "\n");
                    long cur = File.Exists(RecordPath) ? new FileInfo(RecordPath).Length : 0L;
                    if (M.ShouldRotate(cur, bytes.Length))
                    {
                        string old = Path.Combine(Path.GetDirectoryName(RecordPath), "tps.1.jsonl");
                        if (File.Exists(old)) File.Delete(old);
                        File.Move(RecordPath, old);
                    }
                    using (var fs = new FileStream(RecordPath, FileMode.Append, FileAccess.Write, FileShare.ReadWrite))
                        fs.Write(bytes, 0, bytes.Length);
                    SamplesWritten++;
                    WriteError = null;
                }
            }
            catch (Exception e)
            {
                WriteError = e.GetType().Name + ": " + e.Message;
            }
        }

        internal static object Report(int last)
        {
            List<string> lines;
            List<float> ratios;
            lock (Gate)
            {
                lines = Ring.ToList();
                ratios = RunRatios.ToList();
            }
            if (last <= 0) last = 60;
            var tail = lines.Skip(Math.Max(0, lines.Count - last)).ToList();
            // Stats over the run samples among the returned tail, parsed back from our own lines.
            var tps = new List<float>();
            var rat = new List<float>();
            foreach (var l in tail)
            {
                if (l.IndexOf("\"state\":\"run\"", StringComparison.Ordinal) < 0) continue;
                float t, r;
                if (TryField(l, "tps", out t)) tps.Add(t);
                if (TryField(l, "ratio", out r)) rat.Add(r);
            }
            return new
            {
                success = Installed && RuntimeError == null,
                installed = Installed,
                installError = InstallError,
                runtimeError = RuntimeError,
                writeError = WriteError,
                samplerStartedUtc = StartedUtc,
                note = "Sampling starts on the first jawa/ call of a session; play before samplerStartedUtc is not recorded. " +
                       "Judge tps against target (60 x effective speed multiplier); paused/mixed samples are never judged.",
                cadenceSeconds = M.CadenceSeconds,
                recordPath = RecordPath,
                samplesInMemory = lines.Count,
                samplesWritten = SamplesWritten,
                windowsDropped = WindowsDropped,
                returned = tail.Count,
                runSamples = tps.Count,
                tpsMin = tps.Count > 0 ? (float?)tps.Min() : null,
                tpsMedian = tps.Count > 0 ? (float?)M.Median(tps) : null,
                tpsMax = tps.Count > 0 ? (float?)tps.Max() : null,
                ratioMin = rat.Count > 0 ? (float?)rat.Min() : null,
                ratioMedian = rat.Count > 0 ? (float?)M.Median(rat) : null,
                ratioMax = rat.Count > 0 ? (float?)rat.Max() : null,
                sustained = M.Sustained(ratios),
                samplesJsonl = tail,
            };
        }

        private static bool TryField(string line, string key, out float v)
        {
            v = 0f;
            string k = "\"" + key + "\":";
            int i = line.IndexOf(k, StringComparison.Ordinal);
            if (i < 0) return false;
            i += k.Length;
            int j = i;
            while (j < line.Length && line[j] != ',' && line[j] != '}') j++;
            return float.TryParse(line.Substring(i, j - i), System.Globalization.NumberStyles.Float,
                                  System.Globalization.CultureInfo.InvariantCulture, out v);
        }
    }

    public sealed partial class JawaBenchTerrainTools
    {
        [Tool(
            "jawa/tps_report",
            Description =
                "The standing TPS record (BRIDGE_TPS_REGULAR_REPORT_1): one sample per 5 real seconds of play - ticks per " +
                "real second, the speed setting, its EFFECTIVE multiplier, target (60 x multiplier), ratio, paused share, " +
                "fps, worst frame, mean tick ms, gen-0 GCs. Read-only. TRAP: the sampler starts on the first jawa/ call of " +
                "a session (this call starts it), so play before samplerStartedUtc was never measured. Judge against target, " +
                "never 60: 170 tps is fine at speed 3 and dire at speed 4. The on-disk record (recordPath) survives restarts; " +
                "read it with src/RimMandrake/Utils/tps_record.py.",
            ResultDescription =
                "success, samplerStartedUtc, recordPath, samplesJsonl (last N lines), tpsMin/Median/Max and " +
                "ratioMin/Median/Max over the run samples among them, sustained (low|high|ok|unknown), errors if any.")]
        public static Task<object> TpsReport(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "How many of the most recent samples to return (default 60 = 5 minutes; max 720).")] int last = 60)
        {
            JawaBenchTpsSampler.Install();
            return Task.FromResult(JawaBenchTpsSampler.Report(Math.Min(last, M.RingCapacity)));
        }
    }
}
