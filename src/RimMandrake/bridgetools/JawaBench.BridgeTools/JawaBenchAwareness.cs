// JawaBenchAwareness.cs - map awareness, the Verse half: Harmony hooks that FEED JawaBenchAwarenessCore.
//
// Items: INCIDENT_JOURNAL_BUILD_CALLED_IS_NOT_FIRED (incident journal), PAWN_ORIGIN_BUILD_SAY_ORIGIN_UNKNOWN (origin
// recorder), THING_LOOKUP_BUILD_OWNER_IS_NOT_PAINTER (wild-spawner block). Doc: design/RimMandrake/map_awareness.md.
//
// EVERY ENGINE MEMBER BELOW WAS READ OUT OF DECOMPILED 1.6 VIA RimSage ON 2026-10-10, NOT GUESSED:
//   RimWorld/IncidentWorker.cs     public bool TryExecute(IncidentParms) - non-virtual; returns TRUE WITHOUT the
//                                  worker when def.requireColonistsPresent and the target map has no free colonists
//   RimWorld/Storyteller.cs        TryFire(fi) calls fi.def.Worker.TryExecute(fi.parms): the queued FiringIncident's
//                                  parms OBJECT reaches TryExecute, so a token keyed on it survives the schedule
//   Verse/PawnGenerator.cs:140     public static Pawn GeneratePawn(PawnGenerationRequest)
//   Verse/Pawn.cs:2616             public override void SpawnSetup(Map map, bool respawningAfterLoad)
//   Verse/MapGenerator.cs:289      public static void GenerateContentsIntoMap(IEnumerable<GenStepWithParams>, Map, int, bool)
//   RimWorld/WildAnimalSpawner.cs  WildAnimalSpawnerTick() (called from Map.cs:968; the ONLY ongoing replenish path) and
//                                  public bool SpawnRandomWildAnimalAt(IntVec3, bool, PawnKindDef) (mapgen uses it too)
//   RimWorld/CompSpawnerPawn.cs    private bool TrySpawnPawn(out Pawn)   (hives and other pawn spawners)
//   RimWorld/CompHatcher.cs        public void Hatch()
//   Verse/Hediff_Pregnant.cs       public static void DoBirthSpawn(Pawn mother, Pawn father)
//   RimWorld/UniqueIDsManager.cs   private int nextThingID - read in the GeneratePawn prefix: a result id at or above it
//                                  was allocated inside the call (new), below it is a reused world pawn
//   Installed 0Harmony is 2.4.1.0 (assembly version read from the dll, 2026-10-10); it carries __runOriginal and
//   __exception injection names. A void finalizer OBSERVES an exception and lets it propagate unchanged.
//
// LAWS (each is enforced by a hook below; the pure rules are unit-tested in bridgetools/AwarenessSelfTest):
//   * Contained: every hook body is try/catch -> Rec.Fault; a recorder never breaks the game and never swallows the
//     game's own exception (finalizers are void).
//   * Skip-safe: prefix pushes, FINALIZER pops by token (idempotent); a prefix skipped by another mod leaves an
//     invalid token and the pop does nothing. A postfix is never taken as proof the original ran: __runOriginal is.
//   * Game-scoped: Rec.EpochFor(Current.Game) on every hook; rows of an old game are dropped and counted.
//   * Bounded: everything lives in the core's capped stores; evictions are reported by jawa/awareness.
//   * Installed at bridge registration (JawaBenchTpsTools' constructor, the same path the TPS record starts on), so
//     the first map's generation can be seen without a bridge call. UNVERIFIED live: acceptance A4 of
//     MAP_AWARENESS_PROVE_ON_A_QUIET_MAP.
//   * EXCEPT the hottest hook, PawnGenerator.GeneratePawn (AWARENESS_GENPAWN_TAME_ARM_BEFORE_USE): it is installed
//     LAZILY, from the main thread, by the first `jawa/awareness action=arm` (or at registration only when
//     awareness_settings.json sets "install.generation-early": true). World generation and the first map therefore
//     pay nothing for it by default, and without it the first map's pawns read "origin unknown" - the trade is
//     stated in jawa/awareness `generationHook`. Registration happens at the main menu AFTER the cold load, so no
//     awareness hook can slow the cold load itself (TPS sampler header: RimBridgeStartup.OnRuntimeReady).
//   * Threads: these hooks ACCEPT foreign threads by design (thread-static scopes, locked stores) and count them
//     (foreignThreadCalls), unlike the TPS hooks, which reject them.
//   * Disk rows only while ARMED (TTL) and only through the TPS record's ordered bounded writer (kind "awareness").

using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Reflection;
using System.Runtime.CompilerServices;
using System.Text;
using HarmonyLib;
using RimWorld;
using Verse;
using A = JawaBench.BridgeTools.JawaBenchAwarenessCore;
using W = JawaBench.BridgeTools.JawaBenchTpsWriter;

namespace JawaBench.BridgeTools
{
    internal static class JawaBenchAwareness
    {
        internal static readonly A.Recorder Rec = new A.Recorder();
        internal static A.Switches Sw = new A.Switches();
        internal static readonly A.Arm DiskArm = new A.Arm();
        internal static readonly Dictionary<string, A.Meter> Meters = new Dictionary<string, A.Meter>();
        internal static string InstallStatus = "not installed", InstallDetail, StartedBy, SettingsPath;
        internal static DateTime InstalledUtc;
        internal static long DiskRows, DiskDropped;
        private static readonly object Gate = new object();
        private static bool _attempted;
        private static Harmony _harmony;
        private static readonly ConditionalWeakTable<IncidentParms, A.Ctx> Scheduled = new ConditionalWeakTable<IncidentParms, A.Ctx>();
        private static readonly Dictionary<long, A.IncidentRec> Open = new Dictionary<long, A.IncidentRec>();
        private static AccessTools.FieldRef<UniqueIDsManager, int> _nextThingId;

        // wild-spawner block (quiet-world profile): game-scoped + dead-man TTL (BRIDGE_TARGETS_HARDEN_STALE_AFTER_RELOAD).
        // A runner that dies leaves the block to EXPIRE; a load or new game releases it; the reason is kept.
        internal static readonly JawaBenchSafetyCore.QuietBlock Wild = new JawaBenchSafetyCore.QuietBlock();
        internal static bool WildBlocked => Wild.On;
        internal static long WildSkipped;
        internal static string WildPatch = "not patched";

        // GeneratePawn: lazy unless install.generation-early
        internal static string GenerationHook = "not installed (lazy: installs on the first jawa/awareness arm)";
        internal static long ForeignThreadCalls;
        private static void NoteThread() { try { if (!UnityData.IsInMainThread) System.Threading.Interlocked.Increment(ref ForeignThreadCalls); } catch { } }

        static JawaBenchAwareness()
        {
            foreach (var id in A.MetricIds) Meters[id] = new A.Meter();
        }

        internal static A.Meter M(string id) => Meters[id];
        private static long Now() => Stopwatch.GetTimestamp();
        private static void Cost(string id, long t0) { try { Meters[id].Add(Stopwatch.GetTimestamp() - t0); } catch { } }
        // Scope hooks (prefix ... finalizer around the original): charge only the three hook bodies, never the wrapped
        // original. Measured live 2026-10-10: charging prefix-start..finalizer-end put TryExecute and GeneratePawn
        // themselves into aware.incident-journal (mean 438 ms) and aware.origin-generation (mean 43 ms).
        private static void CostTicks(string id, long ticks) { try { Meters[id].Add(ticks); } catch { } }
        private static int Epoch() { try { return Rec.EpochFor(Current.Game); } catch { return Rec.Epoch; } }
        private static int Tick() { try { return Find.TickManager != null ? Find.TickManager.TicksGame : -1; } catch { return -1; } }

        // ------------------------------------------------------------------ install
        internal static void Install(string by)
        {
            lock (Gate)
            {
                if (_attempted) return;
                _attempted = true;
                StartedBy = by;
                InstalledUtc = DateTime.UtcNow;
                try { LoadSwitches(); } catch (Exception e) { Sw = new A.Switches { Note = "settings read failed: " + e.GetType().Name }; }
                try { _nextThingId = AccessTools.FieldRefAccess<UniqueIDsManager, int>("nextThingID"); } catch { _nextThingId = null; }
                if (!JawaBenchCompanionSafety.PolicyNow().AwarenessCheapHooks)
                {
                    InstallStatus = "disabled"; InstallDetail = "the " + JawaBenchCompanionSafety.PolicyNow().Name + " profile policy keeps awareness off";
                    return;
                }
                try { _harmony = new Harmony("mandrake.jawabench.awareness"); }
                catch (Exception e) { InstallStatus = "failed"; InstallDetail = "Harmony ctor: " + e.Message; return; }
                var self = typeof(JawaBenchAwareness);
                HarmonyMethod H(string n) => n == null ? null : new HarmonyMethod(self.GetMethod(n, BindingFlags.Static | BindingFlags.NonPublic));
                var plan = new List<KeyValuePair<JawaBenchTpsInstall.Target, string[]>>();
                void Add(string name, Func<object> resolve, string pre, string post, string fin) =>
                    plan.Add(new KeyValuePair<JawaBenchTpsInstall.Target, string[]>(new JawaBenchTpsInstall.Target(name, false, resolve), new[] { pre, post, fin }));
                Add("IncidentWorker.TryExecute", () => AccessTools.Method(typeof(IncidentWorker), "TryExecute", new[] { typeof(IncidentParms) }),
                    nameof(IncPre), nameof(IncPost), nameof(IncFin));
                // the profile's POLICY decides (JawaBenchSafetyCore.Policies), the settings option only asks: campaign never
                // installs GeneratePawn early, whatever the file says
                var pol = JawaBenchCompanionSafety.PolicyNow();
                bool genEarly = Sw.Option(A.OptGenerationEarly) && pol.AwarenessGenerationHook;
                if (Sw.Option(A.OptGenerationEarly) && !genEarly) GenerationHook = "not installed: install.generation-early is ignored in the " + pol.Name + " profile";
                if (genEarly)
                    Add("PawnGenerator.GeneratePawn", () => AccessTools.Method(typeof(PawnGenerator), "GeneratePawn", new[] { typeof(PawnGenerationRequest) }),
                        nameof(GenPre), nameof(GenPost), nameof(GenFin));
                Add("Pawn.SpawnSetup", () => AccessTools.DeclaredMethod(typeof(Pawn), "SpawnSetup", new[] { typeof(Map), typeof(bool) }),
                    null, nameof(SpawnPost), null);
                Add("MapGenerator.GenerateContentsIntoMap", () => AccessTools.Method(typeof(MapGenerator), "GenerateContentsIntoMap"),
                    nameof(MapgenPre), null, nameof(CtxFin));
                Add("WildAnimalSpawner.SpawnRandomWildAnimalAt", () => AccessTools.Method(typeof(WildAnimalSpawner), "SpawnRandomWildAnimalAt"),
                    nameof(WildPre), null, nameof(CtxFin));
                Add("CompSpawnerPawn.TrySpawnPawn", () => AccessTools.Method(typeof(CompSpawnerPawn), "TrySpawnPawn"),
                    nameof(SpawnerPre), null, nameof(CtxFin));
                Add("CompHatcher.Hatch", () => AccessTools.Method(typeof(CompHatcher), "Hatch"), nameof(HatchPre), null, nameof(CtxFin));
                Add("Hediff_Pregnant.DoBirthSpawn", () => AccessTools.Method(typeof(Hediff_Pregnant), "DoBirthSpawn"), nameof(BirthPre), null, nameof(CtxFin));
                var map = new Dictionary<string, string[]>();
                foreach (var kv in plan) map[kv.Key.Name] = kv.Value;
                string detail;
                InstallStatus = JawaBenchTpsInstall.Run(plan.ConvertAll(kv => kv.Key),
                    (name, m) => { var hs = map[name]; _harmony.Patch((MethodBase)m, prefix: H(hs[0]), postfix: H(hs[1]), finalizer: H(hs[2])); },
                    () => _harmony.UnpatchAll(_harmony.Id), out detail);
                InstallDetail = detail;
                if (genEarly) GenerationHook = InstallStatus == "failed" ? "failed with the early install" : "installed early (install.generation-early) by " + by;
                if (InstallStatus != "failed") Rec.InstallSeq = Rec.NextSeq();
                try { Log.Message("[JawaBench] map awareness: " + InstallStatus + " by " + by + " (" + detail + "); switches " + Sw.Note); } catch { }
            }
        }

        internal static void EnsureInstalled() { if (!_attempted) Install("tool-call"); }

        /// <summary>Install the GeneratePawn hook now (lazy path). MAIN THREAD ONLY: patching a method another thread may
        /// be running is not attempted. Returns null on success or when already installed, else why not.</summary>
        internal static string EnsureGenerationHook(string by)
        {
            lock (Gate)
            {
                if (GenerationHook.StartsWith("installed")) return null;
                try
                {
                    if (!UnityData.IsInMainThread) return "not on the main thread";
                    var pol = JawaBenchCompanionSafety.PolicyNow();
                    if (!pol.AwarenessGenerationHook) return "refused: the " + pol.Name + " profile keeps the GeneratePawn hook off (it costs play speed)";
                    EnsureInstalled();
                    if (_harmony == null) return GenerationHook = "failed: no Harmony instance (" + InstallDetail + ")";
                    var m = AccessTools.Method(typeof(PawnGenerator), "GeneratePawn", new[] { typeof(PawnGenerationRequest) });
                    if (m == null) return GenerationHook = "failed: PawnGenerator.GeneratePawn(PawnGenerationRequest) not found";
                    var self = typeof(JawaBenchAwareness);
                    HarmonyMethod H(string n) => new HarmonyMethod(self.GetMethod(n, BindingFlags.Static | BindingFlags.NonPublic));
                    _harmony.Patch(m, prefix: H(nameof(GenPre)), postfix: H(nameof(GenPost)), finalizer: H(nameof(GenFin)));
                    GenerationHook = "installed lazily by " + by + " at " + DateTime.UtcNow.ToString("o");
                    return null;
                }
                catch (Exception e) { return GenerationHook = "failed: " + e.GetType().Name + ": " + e.Message; }
            }
        }

        private static void LoadSwitches()
        {
            var dir = Path.Combine(Path.Combine(GenFilePaths.SaveDataFolderPath, "JawaBench"), "tps");
            SettingsPath = Path.Combine(dir, "awareness_settings.json");
            if (!File.Exists(SettingsPath))
            {
                Directory.CreateDirectory(dir);
                var sb = new StringBuilder("{");
                for (int i = 0; i < A.MetricIds.Length; i++) sb.Append(i == 0 ? "" : ", ").Append(A.J(A.MetricIds[i])).Append(": true");
                File.WriteAllText(SettingsPath, sb.Append("}\n").ToString());
            }
            Sw = A.Switches.Parse(File.ReadAllText(SettingsPath));
        }

        // ------------------------------------------------------------------ bridge contexts (called by tools)
        /// <summary>Open a `bridge:<tool>` context INSIDE the tool's main-thread lambda (the server-thread dispatch is
        /// another thread and an earlier time: a push there would not be on this stack).</summary>
        internal static A.Token BridgeBegin(string tool)
        {
            try
            {
                EnsureInstalled();
                if (!Sw.On(A.MContext)) return new A.Token();
                return A.Scope.Push("bridge", tool, Epoch());
            }
            catch (Exception e) { Rec.Fault(e); return new A.Token(); }
        }

        internal static void BridgeEnd(A.Token t) { try { A.Scope.Pop(t); } catch (Exception e) { Rec.Fault(e); } }

        /// <summary>A bridge tool that QUEUES an incident hands its context to the parms object; TryExecute adopts it
        /// when the queue fires the incident later (Storyteller.TryFire passes the same parms object).</summary>
        internal static void AttachToScheduled(IncidentParms parms)
        {
            try
            {
                var c = A.Scope.Current(Epoch());
                if (parms != null && c != null) { Scheduled.Remove(parms); Scheduled.Add(parms, c); }
            }
            catch (Exception e) { Rec.Fault(e); }
        }

        // ------------------------------------------------------------------ incident journal
        internal sealed class IncState { internal A.Token Adopted, Mine; internal A.IncidentRec Rec; internal long T0, Pre, Post; }

        private static void IncPre(IncidentWorker __instance, IncidentParms parms, out IncState __state)
        {
            __state = null;
            long t0 = Now();
            try
            {
                if (!Sw.On(A.MIncident) && !Sw.On(A.MContext)) return;
                NoteThread();
                int ep = Epoch();
                var st = new IncState { T0 = t0 };
                __state = st;      // FIRST: anything pushed below is popped by IncFin even if a later line throws
                if (parms != null && A.Scope.Current(ep) == null && Scheduled.TryGetValue(parms, out var tok))
                    st.Adopted = A.Scope.Adopt(tok, ep);
                string def = __instance?.def?.defName ?? "?";
                if (Sw.On(A.MContext)) st.Mine = A.Scope.Push("incident", def, ep);
                if (Sw.On(A.MIncident))
                {
                    var cur = A.Scope.Current(ep);
                    var r = new A.IncidentRec
                    {
                        Epoch = ep, Tick = Tick(), Def = def, Chain = cur?.Chain, CtxId = st.Mine.Valid ? st.Mine.Mine.Id : 0,
                        Target = parms?.target is Map m ? "map:" + m.uniqueID : parms?.target != null ? parms.target.GetType().Name : null,
                        Faction = parms?.faction?.def?.defName, Forced = parms?.forced ?? false, Points = parms?.points ?? -1f,
                        Strategy = parms?.raidStrategy?.defName, Arrival = parms?.raidArrivalMode?.defName,
                        Quest = parms?.quest != null ? "quest:" + parms.quest.id : null,
                    };
                    // the ONE branch established without instrumenting the worker (decompiled 1.6 IncidentWorker.TryExecute)
                    if (parms?.target is Map tm && __instance?.def != null && __instance.def.requireColonistsPresent
                        && tm.mapPawns.FreeColonistsSpawnedCount == 0)
                    {
                        r.WorkerEntered = "false";
                        r.WorkerEnteredWhy = "requireColonistsPresent and no free colonist on the target map: TryExecute returns true without the worker";
                    }
                    st.Rec = Rec.AddIncident(r);
                    if (st.Rec != null && st.Mine.Valid) lock (Open) Open[st.Mine.Mine.Id] = st.Rec;
                }
            }
            catch (Exception e) { Rec.Fault(e); }
            finally { if (__state != null) __state.Pre = Now() - t0; }
        }

        private static void IncPost(bool __result, bool __runOriginal, IncState __state)
        {
            long p0 = Now();
            try
            {
                var r = __state?.Rec;
                if (r == null) return;
                r.OuterBodyRan = __runOriginal ? "true" : "false";
                r.Returned = __result ? "true" : "false";
                if (!__runOriginal) { r.WorkerEntered = "unknown"; r.WorkerEnteredWhy = "the original was skipped by another prefix; whatever ran instead is not observed"; }
            }
            catch (Exception e) { Rec.Fault(e); }
            finally { if (__state != null) __state.Post = Now() - p0; }
        }

        private static void IncFin(Exception __exception, IncState __state)
        {
            long f0 = Now();
            try
            {
                if (__state == null) return;
                var r = __state.Rec;
                if (r != null && __exception != null) { r.Returned = "exception"; r.Exception = __exception.GetType().Name + ": " + A.Clip(__exception.Message, 200); }
                if (__state.Mine.Valid) lock (Open) Open.Remove(__state.Mine.Mine.Id);
                A.Scope.Pop(__state.Mine);
                A.Scope.Pop(__state.Adopted);
                if (r != null) DiskRow("incident", IncidentFields(r));
                CostTicks(A.MIncident, __state.Pre + __state.Post + (Now() - f0));
            }
            catch (Exception e) { Rec.Fault(e); }
        }

        private static void BumpOpen(bool spawned)
        {
            var c = A.Scope.Current(Rec.Epoch);
            if (c == null) return;
            lock (Open)
            {
                if (Open.Count == 0) return;
                for (var x = c; x != null; x = x.Parent)
                    if (x.Kind == "incident" && Open.TryGetValue(x.Id, out var r)) { if (spawned) r.PawnsSpawnedDuring++; else r.PawnsGeneratedDuring++; }
            }
        }

        // ------------------------------------------------------------------ generation tag
        internal sealed class GenState { internal long T0, Pre, Post; internal int NextId = -1; internal A.Ctx Ctx; internal int Epoch; }

        private static void GenPre(out GenState __state)
        {
            __state = null;
            long t0 = Now();
            try
            {
                if (!Sw.On(A.MGeneration) || !JawaBenchCompanionSafety.CurrentPolicy.AwarenessGenerationHook) return;
                NoteThread();
                int ep = Epoch();
                var c = A.Scope.Current(ep);
                if (c == null) { lock (Rec.Gate) Rec.UntaggedGenerations++; Cost(A.MGeneration, t0); return; }
                var st = new GenState { T0 = t0, Ctx = c, Epoch = ep };
                try { if (_nextThingId != null && Find.UniqueIDsManager != null) st.NextId = _nextThingId(Find.UniqueIDsManager); } catch { }
                __state = st;
            }
            catch (Exception e) { Rec.Fault(e); }
            finally { if (__state != null) __state.Pre = Now() - t0; }
        }

        private static void GenPost(Pawn __result, bool __runOriginal, GenState __state)
        {
            long p0 = Now();
            try
            {
                if (__state == null || __result == null) return;
                string reuse = !__runOriginal || __state.NextId < 0 ? "unknown" : (__result.thingIDNumber >= __state.NextId ? "new" : "reused");
                Rec.AddGeneration(new A.GenObs
                {
                    Epoch = __state.Epoch, Tick = Tick(), PawnId = __result.thingIDNumber, Kind = __result.kindDef?.defName,
                    Chain = __state.Ctx.Chain, RootKind = __state.Ctx.Root.Kind, Cause = __state.Ctx.Short, CtxId = __state.Ctx.Id,
                    Reuse = reuse, Thread = UnityData.IsInMainThread ? "main" : "worker:" + System.Threading.Thread.CurrentThread.ManagedThreadId
                });
                BumpOpen(false);
            }
            catch (Exception e) { Rec.Fault(e); }
            finally { if (__state != null) __state.Post = Now() - p0; }
        }

        private static void GenFin(GenState __state) { if (__state != null) CostTicks(A.MGeneration, __state.Pre + __state.Post); }

        // ------------------------------------------------------------------ spawn observation
        private static void SpawnPost(Pawn __instance, Map map, bool respawningAfterLoad, bool __runOriginal)
        {
            long t0 = Now();
            try
            {
                if (!Sw.On(A.MSpawn) || __instance == null) return;
                NoteThread();
                int ep = Epoch();
                int mapId = map != null ? map.uniqueID : -1;
                if (respawningAfterLoad) { Rec.NoteLoadRespawn(ep, __instance.thingIDNumber, mapId); return; }
                var c = A.Scope.Current(ep);
                var pos = __instance.Position;
                var s = Rec.AddSpawn(ep, Tick(), mapId, __instance.thingIDNumber, __instance.kindDef?.defName, __instance.def?.defName,
                                     __instance.Faction?.def?.defName, pos.x, pos.z, c?.Chain, __runOriginal);
                BumpOpen(true);
                if (s != null) DiskRow("arrival", SpawnFields(s, __instance.ThingID));
            }
            catch (Exception e) { Rec.Fault(e); }
            finally { Cost(A.MSpawn, t0); }
        }

        // ------------------------------------------------------------------ context scopes for non-incident sources
        private static A.Token Ctx(string kind, string label)
        {
            try { return Sw.On(A.MContext) ? A.Scope.Push(kind, label, Epoch()) : new A.Token(); }
            catch (Exception e) { Rec.Fault(e); return new A.Token(); }
        }

        private static void MapgenPre(Map map, out A.Token __state) => __state = Ctx("mapgen", map?.Parent?.def?.defName ?? "map");
        private static void WildPre(out A.Token __state) => __state = Ctx("wild-spawner", "SpawnRandomWildAnimalAt");
        private static void SpawnerPre(ThingComp __instance, out A.Token __state) => __state = Ctx("spawner", __instance?.parent?.def?.defName ?? "CompSpawnerPawn");
        private static void HatchPre(ThingComp __instance, out A.Token __state) => __state = Ctx("hatch", __instance?.parent?.def?.defName ?? "CompHatcher");
        private static void BirthPre(Pawn mother, out A.Token __state) => __state = Ctx("birth", mother?.kindDef?.defName ?? "mother");
        private static void CtxFin(A.Token __state) { try { A.Scope.Pop(__state); } catch (Exception e) { Rec.Fault(e); } }

        // ------------------------------------------------------------------ wild-spawner block
        internal static string EnsureWildPatch()
        {
            lock (Gate)
            {
                if (WildPatch == "patched") return null;
                try
                {
                    EnsureInstalled();
                    var m = AccessTools.Method(typeof(WildAnimalSpawner), "WildAnimalSpawnerTick");
                    if (m == null) return WildPatch = "WildAnimalSpawner.WildAnimalSpawnerTick not found";
                    (_harmony ?? new Harmony("mandrake.jawabench.awareness")).Patch(m,
                        prefix: new HarmonyMethod(typeof(JawaBenchAwareness).GetMethod(nameof(WildTickPre), BindingFlags.Static | BindingFlags.NonPublic)));
                    WildPatch = "patched";
                    return null;
                }
                catch (Exception e) { return WildPatch = "patch failed: " + e.GetType().Name + ": " + e.Message; }
            }
        }

        /// <summary>Blocks only while the block is ACTIVE for THIS game and unexpired (QuietBlock releases itself on a
        /// new game/load, on no game, and at TTL expiry - the dead-man for a runner that was killed). Contained: any
        /// failure here lets the spawner run (the game's normal behaviour), never throws into the map tick.</summary>
        private static bool WildTickPre()
        {
            try
            {
                if (!Wild.On || !Sw.On(A.MWild)) return true;
                if (!JawaBenchCompanionSafety.CurrentPolicy.WildSpawnerBlock) { Wild.Release("campaign-profile"); return true; }
                if (!Wild.Active(Current.Game, JawaBenchTpsWatchdog.Now)) return true;
                System.Threading.Interlocked.Increment(ref WildSkipped);
                return false;
            }
            catch (Exception e) { try { Rec.Fault(e); } catch { } return true; }
        }

        // ------------------------------------------------------------------ disk rows (armed, through the TPS writer)
        private static void DiskRow(string what, string fields)
        {
            try
            {
                if (!Sw.On(A.MDisk) || !DiskArm.Armed(DateTime.UtcNow)) return;
                if (!W.Running) { DiskDropped++; return; }
                long seq = W.Enqueue("awareness", "\"what\":" + A.J(what) + "," + fields);
                if (seq < 0) DiskDropped++; else DiskRows++;
            }
            catch { DiskDropped++; }
        }

        internal static string IncidentFields(A.IncidentRec r)
        {
            return "\"aseq\":" + A.I(r.Seq) + ",\"epoch\":" + r.Epoch + ",\"tick\":" + r.Tick + ",\"def\":" + A.J(r.Def) +
                   ",\"target\":" + A.J(r.Target) + ",\"faction\":" + A.J(r.Faction) + ",\"forced\":" + (r.Forced ? "true" : "false") +
                   ",\"strategy\":" + A.J(r.Strategy) + ",\"arrival\":" + A.J(r.Arrival) + ",\"quest\":" + A.J(r.Quest) +
                   ",\"called\":true,\"outerBodyRan\":" + A.J(r.OuterBodyRan) + ",\"returned\":" + A.J(r.Returned) +
                   ",\"exception\":" + A.J(r.Exception) + ",\"workerEntered\":" + A.J(r.WorkerEntered) +
                   ",\"pawnsGenerated\":" + r.PawnsGeneratedDuring + ",\"pawnsSpawned\":" + r.PawnsSpawnedDuring +
                   ",\"chain\":" + A.J(r.Chain) + ",\"statement\":" + A.J(A.IncidentStatement(r));
        }

        internal static string SpawnFields(A.SpawnObs s, string thingId)
        {
            return "\"aseq\":" + A.I(s.Seq) + ",\"epoch\":" + s.Epoch + ",\"tick\":" + s.Tick + ",\"map\":" + s.MapId +
                   ",\"id\":" + A.J(thingId) + ",\"pawnKind\":" + A.J(s.Kind) + ",\"faction\":" + A.J(s.Faction) +
                   ",\"x\":" + s.X + ",\"z\":" + s.Z + ",\"classification\":" + A.J(s.Classification) +
                   ",\"generation\":" + A.J(s.Gen?.Chain) + ",\"reuse\":" + A.J(s.Gen?.Reuse) + ",\"spawnChain\":" + A.J(s.SpawnChain) +
                   ",\"statement\":" + A.J(A.Statement(s));
        }
    }
}
