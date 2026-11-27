// The repair on the machine (DESIGN.md "The repair on the machine"): one RM_RepairRecord per machine, the repair and cancel
// gizmos, the inspect text, the give-back of delivered materials (cancel, uninstall, destruction) and the swap to the next level.
// Every rule lives in the kernel (Kernel/RM_WreckedMachinesRepair.cs); this file only reads the game and calls it.
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.WreckedMachines
{
    /// <summary>The XML puts this on every Wrecked and Kludged level def, with no fields.</summary>
    public class CompProperties_WreckedMachine : CompProperties
    {
        public CompProperties_WreckedMachine()
        {
            compClass = typeof(CompWreckedMachine);
        }
    }

    [StaticConstructorOnStartup]
    internal static class RM_RepairTex
    {
        // Both paths are base-game textures (read in RimWorld.TexCommand and Building_GeneAssembler).
        public static readonly Texture2D Repair = ContentFinder<Texture2D>.Get("UI/Commands/Install");
        public static readonly Texture2D Cancel = ContentFinder<Texture2D>.Get("UI/Designators/Cancel");
    }

    /// <summary>The in-memory log of level changes since the game started, read by the proof type (SignalLog).</summary>
    public static class RM_LevelLog
    {
        public static readonly List<string> Lines = new List<string>();

        public static void Add(Thing t, int from, int to)
        {
            int tick = Find.TickManager != null ? Find.TickManager.TicksGame : 0;
            Lines.Add("SIGNAL " + t.ThingID + " | from " + RM_WreckedMachinesRepair.LevelName(from) + " | to "
                + RM_WreckedMachinesRepair.LevelName(to) + " | tick " + tick.ToString(CultureInfo.InvariantCulture));
            if (Lines.Count > 500) Lines.RemoveAt(0);
        }
    }

    public class CompWreckedMachine : ThingComp
    {
        public const string LevelChangedSignal = "RM_WM_LevelChanged";

        public RM_RepairRecord rec = new RM_RepairRecord();

        public RM_MachineLineDef Line => RM_MachineLines.LineOf(parent.def, out _);

        public int Level
        {
            get
            {
                RM_MachineLines.LineOf(parent.def, out int l);
                return l;
            }
        }

        public bool Active => RM_WreckedMachinesRepair.Active(rec);

        /// <summary>The def the open repair leads to (null with no repair under way).</summary>
        public ThingDef TargetDef => Active ? RM_MachineLines.DefAt(Line, rec.target) : null;

        public static bool GroundOk(Thing t, ThingDef next)
        {
            if (next == null || t == null || !t.Spawned) return false;
            return GenConstruct.CanBuildOnTerrain(next, t.Position, t.Map, t.Rotation, t);
        }

        /// <summary>The site of the open repair is ok: the line is on, the machine stands, and its ground is the next level's.</summary>
        public bool SiteOk()
        {
            return RM_MachineLines.IsOn(Line) && parent.Spawned && GroundOk(parent, TargetDef);
        }

        public static bool ProjectDone(ResearchProjectDef p)
        {
            return WreckedMachinesSettings.skipRestorationResearch || p == null || p.IsFinished;
        }

        /// <summary>The colony holds the scarce parts the step needs: enough unforbidden Ancient Components lie on the map.</summary>
        public bool ComponentAtHand(int step)
        {
            if (!parent.Spawned) return false;
            int need = 0;
            ThingDef comp = null;
            foreach (ThingDefCountClass e in RM_MachineLines.StepCost(Line, step))
                if (e.thingDef.defName == RM_MachineLines.AncientComponent)
                {
                    need += e.count;
                    comp = e.thingDef;
                }
            if (comp == null) return true;
            int have = 0;
            foreach (Thing t in parent.Map.listerThings.ThingsOfDef(comp))
                if (!t.IsForbidden(Faction.OfPlayer)) have += t.stackCount;
            return have >= need;
        }

        public int Blocks(out ResearchProjectDef project, out ThingDef next)
        {
            RM_MachineLineDef line = Line;
            int level = Level;
            int step = level + 1;
            project = RM_MachineLines.ProjectFor(line, step);
            next = level >= RM_WreckedMachinesKernel.Wrecked && level < RM_WreckedMachinesKernel.Refurbished
                ? RM_MachineLines.DefAt(line, step) : null;
            bool needs = RM_MachineLines.NeedsComponent(line, step);
            return RM_WreckedMachinesRepair.OrderBlocks(level, RM_MachineLines.IsOn(line), parent.Spawned, rec, ProjectDone(project),
                GroundOk(parent, next), needs, needs && ComponentAtHand(step));
        }

        /// <summary>One sentence per block, in the words the validator reads ("research", "floor", "component").</summary>
        public static string Reasons(int blocks, ResearchProjectDef project, ThingDef next)
        {
            var s = new List<string>();
            if ((blocks & RM_WreckedMachinesRepair.Research) != 0)
                s.Add("Needs the research project " + (project != null ? project.LabelCap.ToString() : "?") + ".");
            if ((blocks & RM_WreckedMachinesRepair.Ground) != 0)
            {
                string g = next?.terrainAffordanceNeeded?.label;
                if (g.NullOrEmpty()) g = "factory floor";
                s.Add(g.ToLower().Contains("floor")
                    ? "The machine must stand on " + g + " under every cell."
                    : "The machine must stand on a floor that holds " + g + " under every cell.");
            }
            if ((blocks & RM_WreckedMachinesRepair.Component) != 0)
                s.Add("Needs an Ancient Component lying unforbidden on the map.");
            return string.Join(" ", s);
        }

        public bool GiveOrder()
        {
            int blocks = Blocks(out _, out _);
            int step = Level + 1;
            List<ThingDefCountClass> cost = RM_MachineLines.StepCost(Line, step);
            return RM_WreckedMachinesRepair.Order(Level, blocks, rec, cost.Select(c => c.thingDef.defName).ToList(),
                cost.Select(c => c.count).ToList(), RM_MachineLines.StepWork(Line, step));
        }

        public void CancelOrder()
        {
            List<KeyValuePair<string, int>> back = RM_WreckedMachinesRepair.Cancel(rec);
            if (parent.Spawned) GiveBack(back, parent.Position, parent.Map);
        }

        public static void GiveBack(List<KeyValuePair<string, int>> back, IntVec3 at, Map map)
        {
            if (back == null || map == null) return;
            foreach (var kv in back)
            {
                ThingDef d = DefDatabase<ThingDef>.GetNamedSilentFail(kv.Key);
                if (d == null)
                {
                    Log.Warning("[WreckedMachines] cannot give back " + kv.Value + " of unknown def " + kv.Key);
                    continue;
                }
                int left = kv.Value;
                while (left > 0)
                {
                    int n = Mathf.Min(left, Mathf.Max(1, d.stackLimit));
                    Thing t = ThingMaker.MakeThing(d, d.MadeFromStuff ? GenStuff.DefaultStuffFor(d) : null);
                    t.stackCount = n;
                    GenPlace.TryPlaceThing(t, at, map, ThingPlaceMode.Near);
                    left -= n;
                }
            }
        }

        /// <summary>Put `count` of `def` into the repair; returns how many the record took.</summary>
        public int Deliver(ThingDef def, int count)
        {
            return RM_WreckedMachinesRepair.Deliver(rec, def.defName, count, SiteOk());
        }

        /// <summary>Add work. When the work completes the machine is swapped; the new thing is returned (else null).</summary>
        public Thing DoWork(float amount)
        {
            RM_LevelChange ch = RM_WreckedMachinesRepair.Work(Level, rec, amount, SiteOk());
            return ch.changed ? Swap(ch.from, ch.to) : null;
        }

        /// <summary>Swap this machine for the def of level `to`: same cells, facing, faction, health share and thing id number. The
        /// record is already empty (the kernel cleared it), so the despawn gives nothing back.</summary>
        public Thing Swap(int from, int to)
        {
            ThingDef next = RM_MachineLines.DefAt(Line, to);
            if (next == null || !parent.Spawned) return null;
            Map map = parent.Map;
            IntVec3 pos = parent.Position;
            Rot4 rot = parent.Rotation;
            Faction faction = parent.Faction;
            float hp = parent.def.useHitPoints && parent.MaxHitPoints > 0 ? (float)parent.HitPoints / parent.MaxHitPoints : 1f;
            int id = parent.thingIDNumber;
            ThingDef stuff = parent.Stuff;
            bool selected = Find.Selector != null && Find.Selector.IsSelected(parent);
            rec = new RM_RepairRecord();
            parent.Destroy(DestroyMode.Vanish);

            Thing t = ThingMaker.MakeThing(next, next.MadeFromStuff ? (stuff ?? GenStuff.DefaultStuffFor(next)) : null);
            t.thingIDNumber = id;                       // before anything keys a dictionary on it (its hash is the id)
            if (faction != null) t.SetFaction(faction);
            GenSpawn.Spawn(t, pos, map, rot, WipeMode.VanishOrMoveAside);   // moves items aside, wipes none
            if (t.def.useHitPoints)
                t.HitPoints = Mathf.Clamp(Mathf.RoundToInt(hp * t.MaxHitPoints), 1, t.MaxHitPoints);
            if (selected) Find.Selector.Select(t, playSound: false, forceDesignatorDeselect: false);
            Find.SignalManager.SendSignal(new Signal(LevelChangedSignal, new NamedArgument(t, "SUBJECT"),
                new NamedArgument(RM_WreckedMachinesRepair.LevelName(from), "FROM"),
                new NamedArgument(RM_WreckedMachinesRepair.LevelName(to), "TO")));
            RM_LevelLog.Add(t, from, to);
            return t;
        }

        public override void PostDeSpawn(Map map, DestroyMode mode = DestroyMode.Vanish)
        {
            base.PostDeSpawn(map, mode);
            // Uninstall (MakeMinified despawns), every destroy mode and any other despawn: delivered materials come back.
            if (Active) GiveBack(RM_WreckedMachinesRepair.Cancel(rec), parent.Position, map);
        }

        public override IEnumerable<Gizmo> CompGetGizmosExtra()
        {
            foreach (Gizmo g in base.CompGetGizmosExtra()) yield return g;
            if (parent.Faction != null && parent.Faction != Faction.OfPlayer) yield break;
            int blocks = Blocks(out ResearchProjectDef project, out ThingDef next);
            if (RM_WreckedMachinesRepair.OrderOffered(blocks))
            {
                string to = RM_WreckedMachinesRepair.LevelName(Level + 1);
                var c = new Command_Action
                {
                    defaultLabel = "Repair to " + to,
                    defaultDesc = "Order a repair of this machine to the " + to + " level. Colonists carry the materials in ("
                        + CostText(RM_MachineLines.StepCost(Line, Level + 1)) + ") and then work on it where it stands.",
                    icon = RM_RepairTex.Repair,
                    action = () => GiveOrder()
                };
                if (!RM_WreckedMachinesRepair.OrderAvailable(blocks)) c.Disable(Reasons(blocks, project, next));
                yield return c;
            }
            if (Active)
                yield return new Command_Action
                {
                    defaultLabel = "Cancel repair",
                    defaultDesc = "Cancel the repair. Every delivered material comes back beside the machine; the work done is lost.",
                    icon = RM_RepairTex.Cancel,
                    action = CancelOrder
                };
        }

        private static string CostText(List<ThingDefCountClass> cost)
        {
            if (cost.Count == 0) return "none";
            return string.Join(", ", cost.Select(c => c.count + " " + c.thingDef.label));
        }

        public override string CompInspectStringExtra()
        {
            var lines = new List<string> { "Level: " + RM_WreckedMachinesRepair.LevelName(Level) };
            if (Active)
            {
                var parts = new List<string>();
                for (int i = 0; i < rec.defs.Length; i++)
                {
                    ThingDef d = DefDatabase<ThingDef>.GetNamedSilentFail(rec.defs[i]);
                    parts.Add((d != null ? d.LabelCap.ToString() : rec.defs[i]) + " " + rec.delivered[i] + " of " + rec.need[i]);
                }
                lines.Add("Repair to " + RM_WreckedMachinesRepair.LevelName(rec.target) + ": delivered "
                    + (parts.Count > 0 ? string.Join(", ", parts) : "nothing needed"));
                lines.Add("Repair work: " + Mathf.FloorToInt(rec.workDone) + " of " + Mathf.CeilToInt(rec.workTotal));
                if (!RM_MachineLines.IsOn(Line)) lines.Add("The repair waits: this machine line is off in Mod Settings.");
                else if (parent.Spawned && !GroundOk(parent, TargetDef)) lines.Add("The repair waits: the ground is wrong for the next level.");
            }
            return string.Join("\n", lines);
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            string text = Scribe.mode == LoadSaveMode.Saving ? RM_WreckedMachinesRepair.Save(rec) : "";
            Scribe_Values.Look(ref text, "rmRepair", "");
            if (Scribe.mode == LoadSaveMode.LoadingVars)
            {
                rec = RM_WreckedMachinesRepair.Load(text, out bool ok) ?? new RM_RepairRecord();
                if (!ok) Log.Error("[WreckedMachines] the saved repair of " + parent.ThingID + " did not read back; the order is dropped: " + text);
            }
        }
    }
}
