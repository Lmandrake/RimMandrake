// JawaBenchCompanionSafety.cs - the Verse/Harmony half of the companion's safety surface.
//
//   COMPANION_PROFILE_ENFORCE_SAFE_BY_DEFAULT   a gate prefix on EVERY [Tool] method of this assembly: in the CAMPAIGN
//                                               profile (the default) a tool in a denied family (debug-invoke, test-only,
//                                               heavy-diagnostic, quiet-world) returns a refusal instead of running;
//                                               authoring tools run. Rules + per-profile policy: JawaBenchSafetyCore.cs.
//   BRIDGE_TARGETS_HARDEN_STALE_AFTER_RELOAD    game epochs + the reserved expect* arguments (checked in the binder
//                                               hook, JawaBenchArgGuard.Prefix).
//   COMPANION_HANDSHAKE_BUILD_SAY_WHAT_LOADED   jawa/companion_handshake. Schema: design/RimMandrake/companion_handshake.md.
//
// WHY PER-METHOD PREFIXES, NOT THE HOST'S BINDER: the binder (RimBridgeServer's private BindArguments) is a third-party
// private method that an upstream rename turns into a no-op, so a gate there would FAIL OPEN. Our own [Tool] methods
// are ours; a gate patch that fails on one of them is named in `gate.unguarded` and makes the gate status "partial".
// ⛔ The gate never throws: a gate that cannot decide refuses (fail closed) and says why.
//
// ⚠️ UNVERIFIED (offline build only, 2026-10-10): the install cost of ~400 prefixes on Mono (reported live as
// gate.installMs), whether every async stub accepts a `ref Task<object> __result` prefix on the installed Harmony,
// and the thread RimBridgeServer invokes tools on (the gate reads only a cached profile and a string, so any thread).

using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Security.Cryptography;
using System.Threading;
using System.Threading.Tasks;
using HarmonyLib;
using RimBridgeServer.Sdk;
using Verse;
using S = JawaBench.BridgeTools.JawaBenchSafetyCore;

namespace JawaBench.BridgeTools
{
    internal static class JawaBenchCompanionSafety
    {
        internal const string HarmonyId = "mandrake.jawabench.profilegate";
        // gm | standard: whether the JAWA_GM_TOOLS world-acting tools were COMPILED in (no #else: tool_metadata.py models #if only)
        private static bool _gm = false;     // declared BEFORE CompileProfile: static initializers run in text order
        internal static readonly string CompileProfile = GmCompiled() ? "gm" : "standard";
        private static bool GmCompiled()
        {
#if JAWA_GM_TOOLS
            _gm = true;
#endif
            return _gm;
        }
        private static readonly object Gate = new object();
        private static readonly Dictionary<MethodBase, string> ToolOf = new Dictionary<MethodBase, string>();
        internal static string GateStatus = "not installed", GateDetail;
        internal static int Guarded;
        internal static readonly List<string> Unguarded = new List<string>();
        internal static double InstallMs = -1;
        internal static long Refusals, GateErrors;
        internal static string LastRefusal;
        private static bool _attempted;
        private static string _dir;

        internal static readonly S.GameEpochs Epochs = new S.GameEpochs();

        // ------------------------------------------------------------------ profile (cached, re-read every 2 s)
        private static readonly Stopwatch Clock = Stopwatch.StartNew();
        private static double _readAt = -10;
        private static string _effective = S.Campaign, _why = "not resolved yet: campaign", _declared = "none";
        /// <summary>The policy of the last resolved profile: a volatile read for hot hooks (GeneratePawn, the wild
        /// spawner). Refreshed by Effective(), i.e. by every jawa tool call and at install.</summary>
        internal static volatile S.Policy CurrentPolicy = S.CampaignPolicy;

        internal static string ProfilePath
        {
            get
            {
                if (_dir == null) { try { _dir = Path.Combine(GenFilePaths.SaveDataFolderPath, "JawaBench"); } catch { } }
                return _dir == null ? null : Path.Combine(_dir, S.ProfileFileName);
            }
        }

        internal static S.Policy PolicyNow() { string w, d; return S.PolicyFor(Effective(out w, out d)); }

        internal static string Effective(out string why, out string declared)
        {
            lock (Gate)
            {
                double now = Clock.Elapsed.TotalSeconds;
                if (now - _readAt >= 2.0)
                {
                    _readAt = now;
                    try
                    {
                        string text = null, path = ProfilePath;
                        if (path != null && File.Exists(path)) text = File.ReadAllText(path);
                        var f = S.ProfileFile.Parse(text, DateTime.UtcNow);
                        string save = null;
                        try { save = JawaBenchTpsSampler.Life.SaveName; } catch { }
                        _effective = S.Effective(f, DateTime.UtcNow, string.IsNullOrEmpty(save) ? null : save, out _why);
                        _declared = !f.Present ? "none" : f.Error != null ? "invalid" : (f.Profile ?? "none");
                        if (path == null) _why += " (profile directory not resolved yet)";
                    }
                    catch (Exception e) { _effective = S.Campaign; _why = "profile unreadable (" + e.GetType().Name + "): campaign"; _declared = "unreadable"; }
                    CurrentPolicy = S.PolicyFor(_effective);
                }
                why = _why; declared = _declared;
                return _effective;
            }
        }

        // ------------------------------------------------------------------ install (main thread, at registration)
        internal static void Install(string by)
        {
            lock (Gate)
            {
                if (_attempted) return;
                _attempted = true;
            }
            var sw = Stopwatch.StartNew();
            try
            {
                var h = new Harmony(HarmonyId);
                var pTask = new HarmonyMethod(typeof(JawaBenchCompanionSafety).GetMethod(nameof(GateTask), BindingFlags.Static | BindingFlags.NonPublic));
                var pObj = new HarmonyMethod(typeof(JawaBenchCompanionSafety).GetMethod(nameof(GateObject), BindingFlags.Static | BindingFlags.NonPublic));
                Type[] types;
                try { types = typeof(JawaBenchCompanionSafety).Assembly.GetTypes(); }
                catch (ReflectionTypeLoadException rtle) { types = rtle.Types.Where(t => t != null).ToArray(); }
                foreach (var t in types)
                {
                    MethodInfo[] ms;
                    try { ms = t.GetMethods(BindingFlags.Public | BindingFlags.Static | BindingFlags.Instance | BindingFlags.DeclaredOnly); }
                    catch { continue; }
                    foreach (var m in ms)
                    {
                        ToolAttribute attr;
                        try { attr = m.GetCustomAttribute<ToolAttribute>(inherit: false); } catch { continue; }
                        if (attr == null || attr.Name == S.HandshakeTool) continue;   // the handshake is always allowed
                        lock (Gate) ToolOf[m] = attr.Name;
                        try
                        {
                            if (m.ReturnType == typeof(Task<object>)) h.Patch(m, prefix: pTask);
                            else if (m.ReturnType == typeof(object)) h.Patch(m, prefix: pObj);
                            else { Unguarded.Add(attr.Name + " (return type " + m.ReturnType.Name + ")"); continue; }
                            Guarded++;
                        }
                        catch (Exception e) { Unguarded.Add(attr.Name + " (" + e.GetType().Name + ": " + e.Message + ")"); }
                    }
                }
                GateStatus = Unguarded.Count == 0 ? "complete" : Guarded > 0 ? "partial" : "failed";
                GateDetail = Guarded + " tools gated, " + Unguarded.Count + " unguarded, by " + by;
            }
            catch (Exception e) { GateStatus = "failed"; GateDetail = e.GetType().Name + ": " + e.Message; }
            InstallMs = sw.Elapsed.TotalMilliseconds;
            string why, declared;
            string eff = Effective(out why, out declared);
            try
            {
                Log.Message("[JawaBench] profile gate " + GateStatus + " (" + GateDetail + ", " + InstallMs.ToString("F0") + " ms); compile " +
                            CompileProfile + ", runtime profile " + eff + " (" + why + ")");
            }
            catch { }
        }

        /// <summary>Null = run the tool. Otherwise the refusal text. Fail CLOSED on any internal error.</summary>
        private static string Check(MethodBase m)
        {
            try
            {
                string tool;
                lock (Gate) ToolOf.TryGetValue(m, out tool);
                if (tool == null) tool = "(unmapped " + m?.Name + ")";
                string why, declared;
                string eff = Effective(out why, out declared);
                if (S.Allowed(tool, eff)) return null;
                Interlocked.Increment(ref Refusals);
                LastRefusal = tool;
                return S.RefusalText(tool, why);
            }
            catch (Exception e)
            {
                Interlocked.Increment(ref GateErrors);
                return "REFUSED: the companion's profile gate could not decide (" + e.GetType().Name + ": " + e.Message + "); failing closed.";
            }
        }

        private static object Refusal(string text)
        {
            string why, declared;
            string eff;
            try { eff = Effective(out why, out declared); } catch { eff = S.Campaign; }
            return new { success = false, refused = true, error = text, message = text, effectiveProfile = eff, compileProfile = CompileProfile };
        }

        private static bool GateTask(MethodBase __originalMethod, ref Task<object> __result)
        {
            string r = Check(__originalMethod);
            if (r == null) return true;
            __result = Task.FromResult(Refusal(r));
            return false;
        }

        private static bool GateObject(MethodBase __originalMethod, ref object __result)
        {
            string r = Check(__originalMethod);
            if (r == null) return true;
            __result = Refusal(r);
            return false;
        }

        // ------------------------------------------------------------------ reserved expect* arguments (binder thread)
        /// <summary>Null = fine. Called from the binder hook with the RAW argument dictionary. Reads only references and
        /// a copied map-id list; anything it cannot read refuses ("could not verify"), never passes.</summary>
        internal static string CheckReserved(IReadOnlyDictionary<string, object> args)
        {
            if (args == null) return null;
            int? want = null, wantMap = null, wantCur = null;
            foreach (var k in S.ReservedArgs)
            {
                object v = null;
                foreach (var kv in args) if (string.Equals(kv.Key, k, StringComparison.OrdinalIgnoreCase)) { v = kv.Value; break; }
                if (v == null) continue;
                var err = S.ParseExpect(v, out int n);
                if (err != null) return "REFUSED: reserved argument " + k + " is " + err;
                if (k == "expectGameEpoch") want = n; else if (k == "expectMapId") wantMap = n; else wantCur = n;
            }
            if (!want.HasValue && !wantMap.HasValue && !wantCur.HasValue) return null;
            try
            {
                var game = Current.Game;
                int ep = Epochs.For(game);
                var r = S.CheckExpect(want, ep);
                if (r != null) return r;
                if (wantMap.HasValue || wantCur.HasValue)
                {
                    var ids = new List<int>();
                    int cur = -1;
                    if (game != null)
                    {
                        var maps = game.Maps?.ToArray();
                        if (maps != null) foreach (var m in maps) if (m != null) ids.Add(m.uniqueID);
                        cur = game.CurrentMap?.uniqueID ?? -1;
                    }
                    return S.CheckMaps(wantMap, wantCur, ids, cur);
                }
                return null;
            }
            catch (Exception e) { return "REFUSED: could not verify the expected game/map (" + e.GetType().Name + ": " + e.Message + ")"; }
        }

        // ------------------------------------------------------------------ identity (cached once)
        private static string _fileSha, _fileShaWhy;

        internal static string CompanionFileSha(out string why)
        {
            if (_fileSha == null && _fileShaWhy == null)
            {
                try
                {
                    string loc = typeof(JawaBenchCompanionSafety).Assembly.Location;
                    if (string.IsNullOrEmpty(loc)) _fileShaWhy = "assembly has no Location (loaded from bytes): the loaded bytes cannot be hashed from disk";
                    else using (var sha = SHA256.Create()) _fileSha = BitConverter.ToString(sha.ComputeHash(File.ReadAllBytes(loc))).Replace("-", "").ToLowerInvariant();
                }
                catch (Exception e) { _fileShaWhy = e.GetType().Name + ": " + e.Message; }
            }
            why = _fileShaWhy;
            return _fileSha;
        }
    }

    public sealed partial class JawaBenchTerrainTools
    {
        [Tool(
            "jawa/companion_handshake",
            Description =
                "WHAT IS ACTUALLY LOADED (schema companion_handshake/1, always allowed in every profile): the companion's " +
                "commit sha, version, MVID and on-disk SHA-256; compile profile (gm | standard) and runtime profile " +
                "(effective campaign | test, the reason, the profile file path) with its policy and declared recorder budget; " +
                "the profile gate's install status; every recorder " +
                "hook's install status and coverage; RimBridgeServer and Harmony versions; the game epoch, save, tick and map " +
                "ids (pass expectGameEpoch / expectMapId / expectCurrentMapId on any later call to refuse a stale target). " +
                "Read-only. The game block is filled on the main thread with a 5 s limit and says so if it could not be.",
            ResultDescription = "The companion_handshake/1 object: see design/RimMandrake/companion_handshake.md.")]
        public static async Task<object> CompanionHandshake(IRimBridgeContext ctx, CancellationToken cancellationToken)
        {
            var asm = typeof(JawaBenchCompanionSafety).Assembly;
            string info = null, sha = null;
            try
            {
                info = asm.GetCustomAttribute<AssemblyInformationalVersionAttribute>()?.InformationalVersion;
                int p = info == null ? -1 : info.IndexOf('+');
                sha = p >= 0 ? info.Substring(p + 1) : null;
            }
            catch { }
            string fileWhy;
            string fileSha = JawaBenchCompanionSafety.CompanionFileSha(out fileWhy);
            string why, declared;
            string eff = JawaBenchCompanionSafety.Effective(out why, out declared);

            object rbs = null;
            try
            {
                var a = AppDomain.CurrentDomain.GetAssemblies().FirstOrDefault(x => x.GetName().Name == "RimBridgeServer");
                rbs = a == null ? (object)new { loaded = false } : new
                {
                    loaded = true, version = a.GetName().Version?.ToString(),
                    informationalVersion = a.GetCustomAttribute<AssemblyInformationalVersionAttribute>()?.InformationalVersion,
                    path = SafeLocation(a)
                };
            }
            catch (Exception e) { rbs = new { loaded = (bool?)null, error = e.GetType().Name + ": " + e.Message }; }
            object harmony = null;
            try { var ha = typeof(Harmony).Assembly; harmony = new { version = ha.GetName().Version?.ToString(), path = SafeLocation(ha) }; }
            catch (Exception e) { harmony = new { error = e.GetType().Name + ": " + e.Message }; }

            object game;
            try
            {
                var t = ctx.MainThread.InvokeAsync<object>(() => GameBlock(), cancellationToken);
                var done = await Task.WhenAny(t, Task.Delay(5000, cancellationToken)).ConfigureAwait(false);
                game = done == t ? await t.ConfigureAwait(false) : new { available = false, why = "the main thread did not answer within 5 s" };
            }
            catch (Exception e) { game = new { available = false, why = e.GetType().Name + ": " + e.Message }; }

            var hooks = new Dictionary<string, object>
            {
                ["tps"] = new { installStatus = JawaBenchTpsSampler.InstallStatus, detail = JawaBenchTpsSampler.InstallDetail,
                                runtimeError = JawaBenchTpsSampler.RuntimeError, coverage = JawaBenchTpsSampler.HookCoverage(JawaBenchTpsSampler.Guards) },
                ["attribution"] = new { installStatus = JawaBenchTpsProfiler.InstallStatus, detail = JawaBenchTpsProfiler.InstallDetail,
                                        runtimeError = JawaBenchTpsProfiler.RuntimeError, coverage = JawaBenchTpsSampler.HookCoverage(JawaBenchTpsProfiler.Guards) },
                ["awareness"] = new { installStatus = JawaBenchAwareness.InstallStatus, detail = JawaBenchAwareness.InstallDetail,
                                      generationHook = JawaBenchAwareness.GenerationHook, faults = JawaBenchAwareness.Rec.Faults,
                                      lastFault = JawaBenchAwareness.Rec.LastFault, foreignThreadCalls = JawaBenchAwareness.ForeignThreadCalls },
                ["argGuard"] = new { installed = JawaBenchArgGuard.Installed, error = JawaBenchArgGuard.InstallError,
                                     staleRefusals = JawaBenchArgGuard.StaleRefusals },
                ["wildSpawner"] = new { patch = JawaBenchAwareness.WildPatch, blocked = JawaBenchAwareness.WildBlocked,
                                        lastRelease = JawaBenchAwareness.Wild.LastRelease },
            };
            var gate = new
            {
                status = JawaBenchCompanionSafety.GateStatus, detail = JawaBenchCompanionSafety.GateDetail,
                guarded = JawaBenchCompanionSafety.Guarded, unguarded = JawaBenchCompanionSafety.Unguarded.ToList(),
                installMs = Math.Round(JawaBenchCompanionSafety.InstallMs, 1), refusals = JawaBenchCompanionSafety.Refusals,
                lastRefusal = JawaBenchCompanionSafety.LastRefusal, gateErrors = JawaBenchCompanionSafety.GateErrors,
                campaignDenied = S.CampaignDenied.Count
            };
            var pol = S.PolicyFor(eff);
            double uptime = -1, awMs = 0;
            try { uptime = (DateTime.Now - Process.GetCurrentProcess().StartTime).TotalSeconds; } catch { }
            try { double f = Stopwatch.Frequency; foreach (var m in JawaBenchAwareness.Meters.Values) awMs += m.TotalMs(f); } catch { awMs = double.NaN; }
            double awShare;
            string awVerdict = S.BudgetVerdict(awMs / 1000.0, uptime, pol, out awShare);
            var policy = new
            {
                name = pol.Name, recorderBudgetShare = pol.RecorderBudgetShare, tpsSampler = pol.TpsSampler, tpsAttribution = pol.TpsAttribution,
                awarenessCheapHooks = pol.AwarenessCheapHooks, awarenessGenerationHook = pol.AwarenessGenerationHook,
                wildSpawnerBlock = pol.WildSpawnerBlock, deniedFamilies = pol.DenyCampaignFamilies ? S.FamilyReasons : null,
                budget = new
                {
                    verdict = "unmeasured",
                    note = "the recorders' real cost is the C0-C5 restart protocol (RECORDER_OVERHEAD_MEASURE_SIX_CONFIGS_DEEP); the partial " +
                           "figure below is awareness HOOK BODIES ONLY over process uptime (no Harmony dispatch, no TPS hooks) and is not a verdict",
                    awarenessBodiesMs = Math.Round(awMs, 1), uptimeS = Math.Round(uptime, 0),
                    awarenessBodiesShare = double.IsNaN(awShare) ? (double?)null : Math.Round(awShare, 5), awarenessBodiesVerdict = awVerdict
                }
            };
            return S.ComposeHandshake(new S.HandshakeInput
            {
                Utc = DateTime.UtcNow.ToString("o"),
                CompanionAssembly = asm.GetName().Name, CompanionVersion = info, CompanionSha = sha,
                CompanionMvid = SafeMvid(asm), CompanionFileSha256 = fileSha ?? ("unavailable: " + fileWhy), CompanionPath = SafeLocation(asm),
                CompileProfile = JawaBenchCompanionSafety.CompileProfile, RuntimeProfile = declared, EffectiveProfile = eff,
                ProfileWhy = why, ProfileFile = JawaBenchCompanionSafety.ProfilePath,
                Policy = policy, Gate = gate, Hooks = hooks, RimBridgeServer = rbs, Harmony = harmony, Game = game,
            });
        }

        private static object GameBlock()
        {
            var g = Current.Game;
            int ep = JawaBenchCompanionSafety.Epochs.For(g);
            var ids = new List<int>();
            if (g?.Maps != null) foreach (var m in g.Maps) if (m != null) ids.Add(m.uniqueID);
            string save = null;
            try { save = JawaBenchTpsSampler.Life.SaveName; } catch { }
            return new
            {
                available = true, epoch = ep, programState = Current.ProgramState.ToString(), save = string.IsNullOrEmpty(save) ? null : save,
                ticksGame = g != null && Find.TickManager != null ? Find.TickManager.TicksGame : -1,
                mapIds = ids, currentMapId = g?.CurrentMap?.uniqueID ?? -1,
                saveNote = "save is the name the TPS lifecycle saw loaded (null for a new game, or when the sampler is off)"
            };
        }

        private static string SafeLocation(Assembly a) { try { var l = a.Location; return string.IsNullOrEmpty(l) ? null : l; } catch { return null; } }
        private static string SafeMvid(Assembly a) { try { return a.ManifestModule.ModuleVersionId.ToString(); } catch { return null; } }
    }
}
