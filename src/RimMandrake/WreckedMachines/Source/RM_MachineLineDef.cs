// One row of the machine-line table (DESIGN.md, the table of ancient machines): a donor machine, its three levels of our own, the
// two restoration projects, and the cost and work of each repair step. The XML lives in Defs/MachineLines. RM_MachineLines is the
// one registry every other part reads (the repair comp, the work givers, the settings, the process lists and the proof type).
using System.Collections.Generic;
using PipeSystem;
using RimWorld;
using Verse;

namespace RimMandrake.WreckedMachines
{
    public class RM_MachineLineDef : Def
    {
        /// <summary>The line's key: the Mod Settings switch, WreckedMachineGrade.line, and every proof line name it.</summary>
        public string key;
        public ThingDef original, wrecked, kludged, refurbished;
        /// <summary>Wrecked to Kludged needs firstProject; Kludged to Refurbished needs secondProject.</summary>
        public ResearchProjectDef firstProject, secondProject;
        /// <summary>ProcessDef names the Kludged level keeps, read by name at startup (a name that does not exist is left out).</summary>
        public List<string> kludgedProcesses = new List<string>();
        /// <summary>When above 0 and kludgedProcesses names none that exist: the Kludged level keeps the donor's first N processes.</summary>
        public int kludgedProcessCount;
        public List<ThingDefCountClass> kludgeCost = new List<ThingDefCountClass>();
        public List<ThingDefCountClass> refurbishCost = new List<ThingDefCountClass>();
        public float kludgeWork = 1000f, refurbishWork = 1000f;
        public bool kludgedMovable = true, refurbishedMovable = true;

        [Unsaved(false)] public List<ProcessDef> kludgedProcessDefs = new List<ProcessDef>();

        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string e in base.ConfigErrors()) yield return e;
            if (key.NullOrEmpty()) yield return "RM_MachineLineDef " + defName + " has no key";
            if (wrecked == null || kludged == null || refurbished == null) yield return "RM_MachineLineDef " + defName + " lacks a level def";
        }
    }

    /// <summary>The registry of machine lines. Static and lazy: the defs are loaded before any caller (static constructors, gizmos).</summary>
    public static class RM_MachineLines
    {
        public const string AncientComponent = "RM_WM_AncientComponent";

        private static List<RM_MachineLineDef> all;
        private static Dictionary<string, RM_MachineLineDef> byKey;
        private static Dictionary<ThingDef, KeyValuePair<RM_MachineLineDef, int>> byDef;
        private static Dictionary<ResearchProjectDef, float> baseResearch;
        private static Dictionary<ResearchProjectDef, RM_MachineLineDef> byProject;

        public static List<RM_MachineLineDef> All
        {
            get { Build(); return all; }
        }

        private static void Build()
        {
            if (all != null) return;
            all = new List<RM_MachineLineDef>();
            byKey = new Dictionary<string, RM_MachineLineDef>();
            byDef = new Dictionary<ThingDef, KeyValuePair<RM_MachineLineDef, int>>();
            baseResearch = new Dictionary<ResearchProjectDef, float>();
            byProject = new Dictionary<ResearchProjectDef, RM_MachineLineDef>();
            foreach (RM_MachineLineDef l in DefDatabase<RM_MachineLineDef>.AllDefsListForReading)
            {
                if (l.key.NullOrEmpty() || byKey.ContainsKey(l.key)) continue;
                all.Add(l);
                byKey[l.key] = l;
                Index(l.wrecked, l, RM_WreckedMachinesKernel.Wrecked);
                Index(l.kludged, l, RM_WreckedMachinesKernel.Kludged);
                Index(l.refurbished, l, RM_WreckedMachinesKernel.Refurbished);
                Index(l.original, l, RM_WreckedMachinesKernel.Original);
                l.kludgedProcessDefs = new List<ProcessDef>();
                if (l.kludgedProcesses != null)
                    foreach (string n in l.kludgedProcesses)
                    {
                        ProcessDef p = DefDatabase<ProcessDef>.GetNamedSilentFail(n);
                        if (p != null && !l.kludgedProcessDefs.Contains(p)) l.kludgedProcessDefs.Add(p);
                    }
                foreach (ResearchProjectDef p in new[] { l.firstProject, l.secondProject })
                {
                    if (p != null && !baseResearch.ContainsKey(p)) baseResearch[p] = p.baseCost;
                    if (p != null && !byProject.ContainsKey(p)) byProject[p] = l;
                }
            }
        }

        private static void Index(ThingDef d, RM_MachineLineDef l, int level)
        {
            if (d != null && !byDef.ContainsKey(d)) byDef[d] = new KeyValuePair<RM_MachineLineDef, int>(l, level);
        }

        public static RM_MachineLineDef ByKey(string key)
        {
            Build();
            return key != null && byKey.TryGetValue(key, out RM_MachineLineDef l) ? l : null;
        }

        /// <summary>The line a def belongs to and its level (Wrecked..Original), or null and -1.</summary>
        public static RM_MachineLineDef LineOf(ThingDef def, out int level)
        {
            Build();
            if (def != null && byDef.TryGetValue(def, out var kv))
            {
                level = kv.Value;
                return kv.Key;
            }
            level = -1;
            return null;
        }

        /// <summary>The line's Mod Settings switch; a key missing from the dictionary is on (the shipped value).</summary>
        public static bool IsOn(RM_MachineLineDef line)
        {
            if (line == null) return false;
            var d = WreckedMachinesSettings.machineLines;
            return d == null || !d.TryGetValue(line.key, out bool on) || on;
        }

        /// <summary>The project is one of a line's two and that line is switched off (the research tab hides it).</summary>
        public static bool ProjectOfOffLine(ResearchProjectDef p)
        {
            Build();
            return p != null && byProject.TryGetValue(p, out RM_MachineLineDef l) && !IsOn(l);
        }

        /// <summary>At least one line is switched off.</summary>
        public static bool AnyOff()
        {
            Build();
            foreach (RM_MachineLineDef l in all)
                if (!IsOn(l)) return true;
            return false;
        }

        public static ThingDef DefAt(RM_MachineLineDef line, int level)
        {
            if (line == null) return null;
            switch (level)
            {
                case RM_WreckedMachinesKernel.Wrecked: return line.wrecked;
                case RM_WreckedMachinesKernel.Kludged: return line.kludged;
                case RM_WreckedMachinesKernel.Refurbished: return line.refurbished;
                case RM_WreckedMachinesKernel.Original: return line.original;
                default: return null;
            }
        }

        /// <summary>Step 1 leads Wrecked to Kludged, step 2 Kludged to Refurbished. The step from a level is level + 1.</summary>
        public static ResearchProjectDef ProjectFor(RM_MachineLineDef line, int step)
        {
            if (line == null) return null;
            return step == 1 ? line.firstProject : step == 2 ? line.secondProject : null;
        }

        /// <summary>The materials of a step after the material slider. The ancient component is never scaled (it is the scarce part).</summary>
        public static List<ThingDefCountClass> StepCost(RM_MachineLineDef line, int step)
        {
            var cost = new List<ThingDefCountClass>();
            if (line == null) return cost;
            List<ThingDefCountClass> raw = step == 1 ? line.kludgeCost : step == 2 ? line.refurbishCost : null;
            if (raw == null) return cost;
            foreach (ThingDefCountClass e in raw)
            {
                if (e == null || e.thingDef == null) continue;
                int n = e.thingDef.defName == AncientComponent
                    ? e.count
                    : RM_WreckedMachinesKernel.ScaledCount(e.count, WreckedMachinesSettings.materialCostFactor);
                cost.Add(new ThingDefCountClass(e.thingDef, n));
            }
            return cost;
        }

        /// <summary>The work of a step (no slider scales work).</summary>
        public static float StepWork(RM_MachineLineDef line, int step)
        {
            if (line == null) return 0f;
            return step == 1 ? line.kludgeWork : step == 2 ? line.refurbishWork : 0f;
        }

        /// <summary>The step needs the ancient component (an entry of it in the step's cost).</summary>
        public static bool NeedsComponent(RM_MachineLineDef line, int step)
        {
            foreach (ThingDefCountClass e in StepCost(line, step))
                if (e.thingDef.defName == AncientComponent && e.count > 0) return true;
            return false;
        }

        /// <summary>A machine of this level may be uninstalled and carried. Kludged and Refurbished follow the row; Wrecked and Original
        /// follow their def (minifiable or not).</summary>
        public static bool Movable(RM_MachineLineDef line, int level)
        {
            ThingDef d = DefAt(line, level);
            if (d == null || !d.Minifiable) return false;
            if (level == RM_WreckedMachinesKernel.Kludged) return line.kludgedMovable;
            if (level == RM_WreckedMachinesKernel.Refurbished) return line.refurbishedMovable;
            return true;
        }

        /// <summary>The research slider on every line project, from the base cost captured at first read.</summary>
        public static void ApplyResearchCost()
        {
            Build();
            foreach (var kv in baseResearch)
                kv.Key.baseCost = RM_WreckedMachinesKernel.ScaledResearch(kv.Value, WreckedMachinesSettings.researchCostFactor);
        }
    }
}
