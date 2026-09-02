// JawaBenchLoadStallProbe.cs - interrogate a cold-load stall WHILE IT IS HAPPENING.
//
// COLD_LOAD_STALL_INTERMITTENT_1
// ==============================
// 4 of 5 launches on the known-good 592-mod list hang forever with Player.log silent
// after Performance Optimizer's "Finished transpiling N methods" line (which is a
// frame-paced coroutine's finish line, NOT a load-stage marker). The loading screen
// keeps rendering (CPU burns, frames tick), the bridge answers, and the load never
// reaches Playing. The stall window sits inside DoPlayLoad's third ExecuteWhenFinished
// delegate: StaticConstructorOnStartupUtility.CallAll -> FloatMenuMakerMap.Init ->
// GlobalTextureAtlasManager.BakeStaticAtlases -> GC/Resources.UnloadUnusedAssets.
// This tool reads LongEventHandler's private state so the stuck stage can be NAMED
// from outside instead of inferred from 19 minutes of silence.
//
// 🔑 DELIBERATELY NOT MainThread.InvokeAsync - THAT IS THE ENTIRE POINT
// =====================================================================
// During the stall the main thread is the patient: a marshalled call would join the
// hang and never return. Everything here is reflection over static fields and
// already-resolved delegate metadata - no Map, no Pawn, no Unity object is touched.
// The values are a RACY SNAPSHOT of state another thread is mutating; every read is
// individually guarded and reports its own failure as data.
//
// ⛔ NO jawa/ PREFIXES IN PROSE in descriptions other than an EXACT tool name -
// build.py scans for jawa/... literals and a partial mention becomes a phantom tool.

using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Threading;
using System.Threading.Tasks;
using RimBridgeServer.Sdk;

namespace JawaBench.BridgeTools
{
    public sealed partial class JawaBenchTerrainTools
    {
        [Tool(
            "jawa/load_stall_probe",
            Description =
                "READ ONLY, and the ONLY tool that is safe while the game is stuck loading: it " +
                "deliberately does NOT marshal to the main thread, because during a load stall " +
                "the main thread never services the queue and any normal tool call hangs with " +
                "it. Reads Verse.LongEventHandler's private state (current long event, queued " +
                "events, the post-load action list with each action's declaring type, the async " +
                "loader thread's liveness) plus StaticConstructorOnStartupUtility." +
                "coreStaticAssetsLoaded - TRUE means every [StaticConstructorOnStartup] ctor " +
                "completed and the stall is later (FloatMenuMakerMap.Init, atlas baking, or the " +
                "GC/asset-unload step); FALSE during a stall means a static ctor is the suspect. " +
                "Also lists this process's top-CPU native threads; call TWICE ~30s apart and " +
                "diff cpuSeconds to see which thread is spinning. ⚠️ Values are a racy snapshot " +
                "read off-thread while loading mutates them - a fieldError entry means that one " +
                "read failed, not that the tool is broken; call again.",
            ResultDescription =
                "success, programState, coreStaticAssetsLoaded, currentEvent{...fields, " +
                "eventActionMethod}, queuedEventCount, executingToExecuteWhenFinished, " +
                "toExecuteWhenFinished[] of {declaringType, method, assembly}, eventThread" +
                "{alive, state, managedId, stackTrace|stackTraceError}, topThreads[] of " +
                "{id, cpuSeconds, state, waitReason}, fieldErrors[].")]
        public static async Task<object> LoadStallProbe(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken)
        {
            cancellationToken.ThrowIfCancellationRequested();

            var fieldErrors = new List<string>();
            const BindingFlags PrivStatic = BindingFlags.NonPublic | BindingFlags.Public | BindingFlags.Static;

            object Grab(string name, Func<object> read)
            {
                try { return read(); }
                catch (Exception ex)
                {
                    fieldErrors.Add(name + ": " + ex.GetType().Name + ": " + ex.Message);
                    return null;
                }
            }

            string DescribeDelegate(Delegate d)
            {
                if (d == null) return null;
                var m = d.Method;
                return (m.DeclaringType?.FullName ?? "?") + "." + m.Name +
                       " [" + (m.DeclaringType?.Assembly?.GetName().Name ?? "?") + "]";
            }

            var lehType = typeof(Verse.LongEventHandler);

            // --- programState: a static enum read, safe off-thread ---
            var programState = Grab("programState", () => Verse.Current.ProgramState.ToString());

            // --- the decisive bit: did CallAll() finish? ---
            var coreStaticAssetsLoaded = Grab("coreStaticAssetsLoaded",
                () => (object)Verse.StaticConstructorOnStartupUtility.coreStaticAssetsLoaded);

            // --- currentEvent: reflect every instance field generically ---
            object currentEvent = Grab("currentEvent", () =>
            {
                var fi = lehType.GetField("currentEvent", PrivStatic);
                if (fi == null) { fieldErrors.Add("currentEvent: field not found on this engine build"); return (object)"UNMEASURED (field not found)"; }
                var ce = fi.GetValue(null);
                if (ce == null) return (object)"null (no long event running)";
                var fields = new Dictionary<string, object>();
                foreach (var f in ce.GetType().GetFields(BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.Public))
                {
                    object v;
                    try { v = f.GetValue(ce); }
                    catch (Exception ex) { fields[f.Name] = "unreadable: " + ex.GetType().Name; continue; }
                    if (v == null) fields[f.Name] = null;
                    else if (v is Delegate del) fields[f.Name] = DescribeDelegate(del);
                    else if (v is string || v.GetType().IsPrimitive || v.GetType().IsEnum) fields[f.Name] = v.ToString();
                    else fields[f.Name] = "<" + v.GetType().Name + ">";
                }
                return (object)fields;
            });

            var queuedEventCount = Grab("eventQueue", () =>
            {
                var q = lehType.GetField("eventQueue", PrivStatic)?.GetValue(null) as ICollection;
                return (object)(q?.Count ?? -1);
            });

            var executingWhenFinished = Grab("executingToExecuteWhenFinished", () =>
            {
                var fi = lehType.GetField("executingToExecuteWhenFinished", PrivStatic);
                if (fi == null) { fieldErrors.Add("executingToExecuteWhenFinished: field not found on this engine build"); return (object)"UNMEASURED (field not found)"; }
                return fi.GetValue(null);
            });

            // --- the post-load action list: each pending delegate's identity ---
            object whenFinished = Grab("toExecuteWhenFinished", () =>
            {
                var raw = lehType.GetField("toExecuteWhenFinished", PrivStatic)?.GetValue(null) as IEnumerable;
                if (raw == null) return (object)"field not found";
                var rows = new List<object>();
                // snapshot defensively - the list can be mutated under us
                foreach (var item in raw.Cast<object>().ToList())
                {
                    var d = item as Delegate;
                    rows.Add(new
                    {
                        declaringType = d?.Method?.DeclaringType?.FullName,
                        method = d?.Method?.Name,
                        assembly = d?.Method?.DeclaringType?.Assembly?.GetName().Name
                    });
                }
                return (object)rows;
            });

            // --- the async loader thread ---
            object eventThread = Grab("eventThread", () =>
            {
                var fi = lehType.GetField("eventThread", PrivStatic);
                if (fi == null) { fieldErrors.Add("eventThread: field not found on this engine build"); return (object)"UNMEASURED (field not found)"; }
                var t = fi.GetValue(null) as Thread;
                if (t == null) return (object)"null (no async event thread)";
                string stack = null, stackErr = null;
                try
                {
#pragma warning disable CS0618 // deliberate: best-effort diagnostic on a possibly-stuck thread
                    var st = new System.Diagnostics.StackTrace(t, false);
#pragma warning restore CS0618
                    stack = st.ToString();
                }
                catch (Exception ex) { stackErr = ex.GetType().Name + ": " + ex.Message; }
                return (object)new
                {
                    alive = t.IsAlive,
                    state = t.ThreadState.ToString(),
                    managedId = t.ManagedThreadId,
                    name = t.Name,
                    stackTrace = stack,
                    stackTraceError = stackErr
                };
            });

            // --- native thread CPU: diff two probes to find the spinner ---
            object topThreads = Grab("topThreads", () =>
            {
                var rows = new List<object>();
                foreach (System.Diagnostics.ProcessThread pt in System.Diagnostics.Process.GetCurrentProcess().Threads)
                {
                    try
                    {
                        rows.Add(new
                        {
                            id = pt.Id,
                            cpuSeconds = Math.Round(pt.TotalProcessorTime.TotalSeconds, 1),
                            state = pt.ThreadState.ToString(),
                            waitReason = pt.ThreadState == System.Diagnostics.ThreadState.Wait
                                ? pt.WaitReason.ToString() : null
                        });
                    }
                    catch { /* threads die between enumeration and read; skip silently is fine here */ }
                }
                return (object)rows
                    .OrderByDescending(r => (double)r.GetType().GetProperty("cpuSeconds").GetValue(r))
                    .Take(8).ToList();
            });

            return await Task.FromResult<object>(new
            {
                success = true,
                programState,
                coreStaticAssetsLoaded,
                currentEvent,
                queuedEventCount,
                executingToExecuteWhenFinished = executingWhenFinished,
                toExecuteWhenFinished = whenFinished,
                eventThread,
                topThreads,
                fieldErrors,
                utcNow = DateTime.UtcNow.ToString("o")
            }).ConfigureAwait(false);
        }
    }
}
