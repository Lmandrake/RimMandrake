using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.LanternDeeps
{
    // ════════════════════════════════════════════════════════════════════
    // LANTERNDEEPS_ANSWERING_RITE_BUILD_1 — the engine under The Answering (Ohm's first settlement rite).
    // Spec: design/Jawa/worldbuilding/biomes/lanterndeeps_bedazzle_review_2026-10-01.md section 6 R1; register
    // design/Jawa/salvation_rites_2026-10-01.md B8. The rite itself (precept, pattern, behaviour, outcome, memory) is campaign data in
    // mandrake.rut.rites (Defs/RUT_Answering.xml); this file is the franchise-free engine it points at, the same split as the Joining
    // Water and the Nine Faults. It names no faith: the god is a string on RM_AnsweringExtension.
    //
    //   Target: a Shard-mind (or any def the filter's RM_AnsweringTargetExtension lists, the campaign adds the mindstone) with one of
    //   the colony's droids standing in its line of sight. NOT gated on darkness. Lit is fine.
    //   Outcome (numbers PROVISIONAL, all on the outcome def):
    //     Poor       the droid in sight stops (RM_AnsweringStalled) and must be carried out; it restarts out of the mind's sight.
    //     Fair       a settlement entry for the god (Ninefold, by reflection, soft dependency).
    //     Good       + a line in the droid's log it did not write (RM_AnsweredLogLine, shown on its health tab).
    //     Excellent  + the line names where the next mindstone lies on this map, and a vein is there.
    // Nothing happens without a sign: the stopped droid, the log line, the letter.
    // ════════════════════════════════════════════════════════════════════

    public class RM_AnsweringTargetExtension : DefModExtension
    {
        /// <summary>Things whose line of sight counts as "a mind's sight" (RM_ShardMind here; the campaign adds the mindstone).</summary>
        public List<ThingDef> mindDefs = new List<ThingDef>();
        /// <summary>How far from the mind the droid may stand and still be in its sight.</summary>
        public float sightRadius = 12f;
    }

    public class RM_AnsweringExtension : DefModExtension
    {
        /// <summary>A Ninefold God enum member name. Absent Ninefold: no entry, the rest still happens.</summary>
        public string god = "Ohm";
        public float fairDelta = 6f;
        public float goodDelta = 8f;
        public float excellentDelta = 10f;
        public HediffDef stallHediff;
        public HediffDef logHediff;
        /// <summary>defName of the vein an excellent Answering places (campaign: RUT_MindstoneVein), looked up at run time so the
        /// rite's XML needs no def from a mod it does not depend on. Empty or unresolved: the line only.</summary>
        public string nextVeinDef;
        public float nextVeinMinDistance = 15f;
        public float nextVeinMaxDistance = 45f;
        /// <summary>The line it did not write. {0} is replaced by where the next mindstone lies, when one is named.</summary>
        public List<string> logLines = new List<string>();
        public List<string> nextStoneLines = new List<string>();
    }

    public static class RM_AnsweringUtil
    {
        public static bool IsDroid(Pawn p)
        {
            return p != null && CompRM_ShardMind.IsDroid(p);
        }

        /// <summary>Colony droids that stand in sight of this mind.</summary>
        public static List<Pawn> DroidsInSight(Thing mind, float radius)
        {
            var list = new List<Pawn>();
            if (mind == null || !mind.Spawned) return list;
            Map map = mind.Map;
            foreach (Pawn p in map.mapPawns.SpawnedPawnsInFaction(Faction.OfPlayer))
            {
                if (!IsDroid(p) || p.Dead || p.Downed) continue;
                if (!p.Position.InHorDistOf(mind.Position, radius)) continue;
                if (!GenSight.LineOfSightToThing(p.Position, mind, map, true)) continue;
                list.Add(p);
            }
            return list;
        }

        public static bool AnyMindInSight(Pawn p, List<ThingDef> mindDefs, float radius)
        {
            if (p?.Map == null || mindDefs == null) return false;
            foreach (ThingDef d in mindDefs)
            {
                if (d == null) continue;
                foreach (Thing t in p.Map.listerThings.ThingsOfDef(d))
                {
                    if (p.Position.InHorDistOf(t.Position, radius) && GenSight.LineOfSightToThing(p.Position, t, p.Map, true)) return true;
                }
            }
            return false;
        }
    }

    public class RM_RitualObligationTargetWorker_AnsweringMind : RitualObligationTargetFilter
    {
        public RM_RitualObligationTargetWorker_AnsweringMind() { }
        public RM_RitualObligationTargetWorker_AnsweringMind(RitualObligationTargetFilterDef def) : base(def) { }

        private RM_AnsweringTargetExtension Ext => def.GetModExtension<RM_AnsweringTargetExtension>();

        public override IEnumerable<TargetInfo> GetTargets(RitualObligation obligation, Map map)
        {
            RM_AnsweringTargetExtension ext = Ext;
            if (ext == null || !LanternDeepsSettings.answeringRiteEnabled) yield break;
            foreach (ThingDef d in ext.mindDefs)
            {
                if (d == null) continue;
                foreach (Thing t in map.listerThings.ThingsOfDef(d))
                {
                    if (RM_AnsweringUtil.DroidsInSight(t, ext.sightRadius).Count > 0) yield return t;
                }
            }
        }

        protected override RitualTargetUseReport CanUseTargetInternal(TargetInfo target, RitualObligation obligation)
        {
            // plain false for everything else: a fail REASON would show a disabled ritual gizmo on every thing
            RM_AnsweringTargetExtension ext = Ext;
            if (ext == null || !LanternDeepsSettings.answeringRiteEnabled || !target.HasThing) return false;
            if (!ext.mindDefs.Contains(target.Thing.def)) return false;
            return RM_AnsweringUtil.DroidsInSight(target.Thing, ext.sightRadius).Count > 0;
        }

        public override IEnumerable<string> GetTargetInfos(RitualObligation obligation)
        {
            yield return "a mind's sight, with one of your droids standing in it";
        }
    }

    public class RM_RitualOutcomeEffectWorker_Answering : RitualOutcomeEffectWorker_FromQuality
    {
        public RM_RitualOutcomeEffectWorker_Answering() { }
        public RM_RitualOutcomeEffectWorker_Answering(RitualOutcomeEffectDef def) : base(def) { }

        protected override void ApplyExtraOutcome(Dictionary<Pawn, int> totalPresence, LordJob_Ritual jobRitual,
            RitualOutcomePossibility outcome, out string extraOutcomeDesc, ref LookTargets letterLookTargets)
        {
            extraOutcomeDesc = null;
            if (!LanternDeepsSettings.answeringRiteEnabled) return;
            RM_AnsweringExtension ext = def.GetModExtension<RM_AnsweringExtension>() ?? new RM_AnsweringExtension();
            Thing mind = jobRitual?.selectedTarget.Thing;
            Map map = mind?.Map ?? jobRitual?.Map;
            float radius = FilterSight(jobRitual);
            Pawn droid = mind == null ? null : RM_AnsweringUtil.DroidsInSight(mind, radius).OrderBy(p => p.Position.DistanceToSquared(mind.Position)).FirstOrDefault();
            if (droid == null)
            {
                extraOutcomeDesc = "No droid stood in the mind's sight when the terms were spoken. Nothing was answered.";
                return;
            }
            var tier = AnsweringKernel.TierOf(outcome.positivityIndex);
            var sb = new System.Text.StringBuilder();

            if (AnsweringKernel.StallsDroid(tier))
            {
                if (LanternDeepsSettings.answeringStallEnabled && ext.stallHediff != null)
                {
                    droid.health.AddHediff(ext.stallHediff);
                    sb.Append(droid.LabelShortCap).Append(" stopped, and has to be carried out of the mind's sight.");
                }
                else sb.Append(droid.LabelShortCap).Append(" stood through it and was not answered.");
                extraOutcomeDesc = sb.ToString();
                letterLookTargets = new LookTargets(droid);
                return;
            }

            float delta = AnsweringKernel.GodDelta(tier, ext.fairDelta, ext.goodDelta, ext.excellentDelta);
            if (delta > 0f) RM_AnsweringNinefold.ApplyDelta(ext.god, delta, "The Answering");
            sb.Append("The terms were agreed.");

            if (AnsweringKernel.WritesLogLine(tier) && ext.logHediff != null)
            {
                string where = null;
                if (AnsweringKernel.NamesNextStone(tier) && LanternDeepsSettings.answeringNextStoneEnabled)
                {
                    IntVec3 cell = PlaceNextVein(map, mind, ext);
                    if (cell.IsValid) where = Describe(cell, mind.Position);
                }
                List<string> table = where != null && ext.nextStoneLines.Count > 0 ? ext.nextStoneLines : ext.logLines;
                int i = AnsweringKernel.PickLine(table.Count, Find.TickManager.TicksGame ^ droid.thingIDNumber);
                if (i >= 0)
                {
                    string line = string.Format(table[i], where ?? "");
                    Hediff h = HediffMaker.MakeHediff(ext.logHediff, droid);
                    (h as Hediff_RM_LogLine)?.SetLine(line);
                    droid.health.AddHediff(h);
                    sb.Append(" ").Append(droid.LabelShortCap).Append("'s log holds a line it did not write: \"").Append(line).Append("\"");
                }
            }
            extraOutcomeDesc = sb.ToString();
            letterLookTargets = new LookTargets(droid);
        }

        private static float FilterSight(LordJob_Ritual job)
        {
            RitualObligationTargetFilterDef d = DefDatabase<RitualObligationTargetFilterDef>.AllDefsListForReading
                .FirstOrDefault(x => x.GetModExtension<RM_AnsweringTargetExtension>() != null);
            return d?.GetModExtension<RM_AnsweringTargetExtension>()?.sightRadius ?? 12f;
        }

        /// <summary>A natural rock face with open floor beside it, between min and max distance from the mind.</summary>
        public static IntVec3 PlaceNextVein(Map map, Thing from, RM_AnsweringExtension ext)
        {
            ThingDef vein = ext.nextVeinDef.NullOrEmpty() ? null : DefDatabase<ThingDef>.GetNamedSilentFail(ext.nextVeinDef);
            if (map == null || from == null || vein == null) return IntVec3.Invalid;
            Building rock = GenRadial.RadialCellsAround(from.Position, ext.nextVeinMaxDistance, false)
                .Where(c => c.InBounds(map) && c.DistanceTo(from.Position) >= ext.nextVeinMinDistance)
                .Select(c => c.GetEdifice(map))
                .Where(b => b != null && b.def.building != null && b.def.building.isNaturalRock && b.def != vein
                            && GenAdj.CellsAdjacentCardinal(b).Any(a => a.InBounds(map) && a.Standable(map)))
                .InRandomOrder().FirstOrDefault();
            if (rock == null) return IntVec3.Invalid;
            IntVec3 at = rock.Position;
            rock.Destroy(DestroyMode.Vanish);
            GenSpawn.Spawn(ThingMaker.MakeThing(vein), at, map);
            return at;
        }

        /// <summary>"north-east, about 30 paces" from the mind: a person-sized direction, no coordinates.</summary>
        public static string Describe(IntVec3 to, IntVec3 from)
        {
            IntVec3 d = to - from;
            string ns = d.z > 5 ? "north" : d.z < -5 ? "south" : "";
            string ew = d.x > 5 ? "east" : d.x < -5 ? "west" : "";
            string dir = ns + (ns != "" && ew != "" ? "-" : "") + ew;
            if (dir == "") dir = "close by";
            return dir + ", about " + Mathf.RoundToInt(to.DistanceTo(from) / 5f) * 5 + " paces";
        }
    }

    // A stopped droid: cannot move, so it is downed and can be carried; it restarts on its own once out of every mind's sight.
    public class Hediff_RM_AnsweringStalled : HediffWithComps
    {
        public override void Tick()
        {
            base.Tick();
            if (pawn.IsHashIntervalTick(250) && pawn.Spawned && !StillInSight()) pawn.health.RemoveHediff(this);
        }

        private bool StillInSight()
        {
            RitualObligationTargetFilterDef d = DefDatabase<RitualObligationTargetFilterDef>.AllDefsListForReading
                .FirstOrDefault(x => x.GetModExtension<RM_AnsweringTargetExtension>() != null);
            RM_AnsweringTargetExtension e = d?.GetModExtension<RM_AnsweringTargetExtension>();
            if (e == null) return false;
            return AnsweringKernel.StallHolds(RM_AnsweringUtil.AnyMindInSight(pawn, e.mindDefs, e.sightRadius));
        }

        public override void PostRemoved()
        {
            base.PostRemoved();
            if (pawn.Spawned) MoteMaker.ThrowText(pawn.DrawPos, pawn.Map, "restarts", 3f);
        }
    }

    // The line it did not write.
    public class Hediff_RM_LogLine : HediffWithComps
    {
        private string line;
        public void SetLine(string s) { line = s; }
        public override string LabelInBrackets => null;
        public override string TipStringExtra => line.NullOrEmpty() ? base.TipStringExtra : "\"" + line + "\"";
        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref line, "line");
        }
    }

    // Ninefold by reflection: a soft dependency, absent reads as a silent no-op (same idiom as Aftermath's NinefoldBandBridge).
    internal static class RM_AnsweringNinefold
    {
        private static bool resolved, warned;
        private static PropertyInfo instanceProp;
        private static MethodInfo applyDelta;
        private static System.Type godType;

        private static void Resolve()
        {
            if (resolved) return;
            resolved = true;
            System.Type n = AccessTools.TypeByName("RimMandrake.Ninefold.GameComponent_Ninefold");
            godType = AccessTools.TypeByName("RimMandrake.Ninefold.God");
            if (n == null || godType == null) return;
            instanceProp = AccessTools.Property(n, "Instance");
            applyDelta = AccessTools.Method(n, "ApplyDelta", new[] { godType, typeof(float), typeof(string) });
            if (instanceProp == null || applyDelta == null || !godType.IsEnum)
            {
                if (!warned) { warned = true; Log.Warning("[RM LanternDeeps] Ninefold found but ApplyDelta(God,float,string) changed shape; the Answering's god entry is OFF."); }
                applyDelta = null;
            }
        }

        public static void ApplyDelta(string god, float amount, string reason)
        {
            Resolve();
            if (applyDelta == null || god.NullOrEmpty()) return;
            object inst = instanceProp.GetValue(null);
            if (inst == null) return;
            object g;
            try { g = System.Enum.Parse(godType, god); }
            catch (System.ArgumentException) { return; }
            applyDelta.Invoke(inst, new object[] { g, amount, reason });
        }
    }
}
