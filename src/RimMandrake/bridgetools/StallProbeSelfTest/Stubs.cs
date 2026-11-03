// Stubs.cs - the smallest Verse / Verse.AI / HarmonyLib surface JawaBenchStallProbe.cs reads, shaped like RimWorld 1.6
// (TickList.thingLists / tickType private fields reached by AccessTools.FieldRefAccess, Pawn.jobs.curJob.def.defName,
// Pawn.jobs.curDriver, Current.Game.tickManager.TicksGame, Find.TickManager). FieldRefAccess resolves the field by NAME
// and throws on any other name, as Harmony does, so a renamed field in the probe goes red here too.
// Test hooks: Thing.def is virtual (a thing may act when the probe reads it), Pawn.jobs may throw.
using System;
using System.Collections.Generic;

namespace HarmonyLib
{
    public static class AccessTools
    {
        public delegate ref F FieldRef<in T, F>(T instance);

        public static FieldRef<T, F> FieldRefAccess<T, F>(string fieldName)
        {
            if (typeof(T) == typeof(Verse.TickList))
            {
                if (fieldName == "thingLists" && typeof(F) == typeof(List<List<Verse.Thing>>))
                    return (FieldRef<T, F>)(Delegate)new FieldRef<Verse.TickList, List<List<Verse.Thing>>>(l => ref l.thingLists);
                if (fieldName == "tickType" && typeof(F) == typeof(Verse.TickerType))
                    return (FieldRef<T, F>)(Delegate)new FieldRef<Verse.TickList, Verse.TickerType>(l => ref l.tickType);
            }
            throw new MissingFieldException(typeof(T).Name, fieldName);
        }
    }
}

namespace Verse
{
    public enum TickerType { Never, Normal, Rare, Long }

    public class Def { public string defName; }
    public class ThingDef : Def { }
    public class JobDef : Def { }

    public struct IntVec3 { public int x, y, z; public IntVec3(int x, int y, int z) { this.x = x; this.y = y; this.z = z; } }

    public class Thing
    {
        private ThingDef _def;
        public virtual ThingDef def { get => _def; set => _def = value; }
        public string ThingID = "Thing0";
        public IntVec3 Position;
    }

    public class Pawn : Thing
    {
        private Verse.AI.Pawn_JobTracker _jobs;
        public bool JobsThrow;
        public Verse.AI.Pawn_JobTracker jobs
        {
            get { if (JobsThrow) throw new InvalidOperationException("jobs torn"); return _jobs; }
            set => _jobs = value;
        }
    }

    public class TickList
    {
        public List<List<Thing>> thingLists;   // private in the game; FieldRefAccess reaches it by name
        public TickerType tickType;

        public TickList(TickerType t)
        {
            tickType = t;
            int n = t == TickerType.Rare ? 250 : t == TickerType.Long ? 2000 : 1;
            thingLists = new List<List<Thing>>();
            for (int i = 0; i < n; i++) thingLists.Add(new List<Thing>());
        }
    }

    public class TickManager { public int TicksGame { get; set; } }
    public class Game { public TickManager tickManager = new TickManager(); }
    public static class Current { public static Game Game; }
    public static class Find { public static TickManager TickManager => Current.Game.tickManager; }
}

namespace Verse.AI
{
    public class JobDriver { }
    public class Job { public JobDef def; }
    public class Pawn_JobTracker { public Job curJob; public JobDriver curDriver; }
}

namespace JawaBench.BridgeTools
{
    // the members of production classes the probe touches; those classes need Verse whole, so they are stubbed here
    internal static class JawaBenchTpsProfiler { internal static bool Installed; }
    internal static class JawaBenchStallDump { internal static Func<string> Probe; }
    internal static class JawaBenchHookGuard { internal struct Scope { internal int I0; } }
}
