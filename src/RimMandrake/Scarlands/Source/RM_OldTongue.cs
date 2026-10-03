using System.Collections.Generic;
using System.Text;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Scarlands
{
    // WARSCAR_OLD_TONGUE_1. Inscribed panels are stock analyzables (CompAnalyzableUnlockResearch): the panel
    // def carries an analysisID and analysisRequiredRange = the set size, and the research project lists the
    // panel DEF in requiredAnalyzed -- so a set of 3 is ONE def read 3 times (offline reading of
    // ResearchProjectDef.AnalyzedThingsCompleted: counts defs whose analysis is Satisfied). Our additions:
    // an Intellectual gate, one-read-per-panel, a chalk mark on a read panel, and a sibling-location line.

    public class CompProperties_InscribedPanel : CompProperties_CompAnalyzableUnlockResearch
    {
        public string chalkTexPath;
        public CompProperties_InscribedPanel() { compClass = typeof(CompInscribedPanel); }
    }

    public class CompInscribedPanel : CompAnalyzableUnlockResearch
    {
        public bool read;
        public new CompProperties_InscribedPanel Props { get { return (CompProperties_InscribedPanel)props; } }
        public static readonly List<CompInscribedPanel> All = new List<CompInscribedPanel>();

        public override void PostSpawnSetup(bool respawningAfterLoad)
        {
            base.PostSpawnSetup(respawningAfterLoad);
            if (!All.Contains(this)) All.Add(this);
        }
        public override void PostDeSpawn(Map map, DestroyMode mode = DestroyMode.Vanish)
        {
            base.PostDeSpawn(map, mode);
            All.Remove(this);
        }
        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref read, "panelRead", false);
        }

        public override AcceptanceReport CanInteract(Pawn activateBy = null, bool checkOptionalItems = true)
        {
            if (read) return "Already transcribed.";
            AcceptanceReport r = base.CanInteract(activateBy, checkOptionalItems);
            if (!r.Accepted) return r;
            int gate = RM_WarscarSettings.oldTongueSkillGate;
            if (activateBy != null && gate > 0)
            {
                SkillRecord s = activateBy.skills != null ? activateBy.skills.GetSkill(SkillDefOf.Intellectual) : null;
                if (s == null || s.TotallyDisabled || s.Level < gate)
                    return "Needs Intellectual " + gate + " (has " + (s == null ? 0 : s.Level) + ")";
            }
            return true;
        }

        public override void OnAnalyzed(Pawn pawn)
        {
            read = true;
            base.OnAnalyzed(pawn);
            if (parent.Spawned) parent.Map.mapDrawer.MapMeshDirty(parent.Position, MapMeshFlagDefOf.Things);
        }

        public override string CompInspectStringExtra()
        {
            StringBuilder sb = new StringBuilder();
            string baseStr = base.CompInspectStringExtra();
            if (!baseStr.NullOrEmpty()) sb.Append(baseStr);
            AnalysisDetails d;
            if (Find.AnalysisManager.TryGetAnalysisProgress(AnalysisID, out d) && d != null)
            {
                if (sb.Length > 0) sb.Append("\n");
                sb.Append("Set read: " + d.timesDone + "/" + d.required);
                if (!d.Satisfied)
                {
                    List<string> where = new List<string>();
                    for (int i = 0; i < All.Count; i++)
                    {
                        CompInscribedPanel o = All[i];
                        if (o != this && !o.read && o.AnalysisID == AnalysisID && o.parent.Spawned)
                            where.Add("(" + o.parent.Position.x + "," + o.parent.Position.z + ")");
                    }
                    if (where.Count > 0) sb.Append("; other unread: " + string.Join(" ", where.ToArray()));
                }
            }
            return sb.ToString();
        }
    }

    // Draws the chalk mark over a read panel.
    public class Building_InscribedPanel : Building
    {
        private Graphic chalk;
        public override void Print(SectionLayer layer)
        {
            base.Print(layer);
            CompInscribedPanel c = GetComp<CompInscribedPanel>();
            if (c == null || !c.read || c.Props.chalkTexPath.NullOrEmpty()) return;
            if (chalk == null) chalk = GraphicDatabase.Get<Graphic_Single>(c.Props.chalkTexPath, ShaderDatabase.Cutout, Vector2.one, Color.white);
            chalk.Print(layer, this, 0.1f);
        }
    }

    // Unlock flags for the unbuilt consumers (hospice cradle, projector screen, pool phase reader). Each reads
    // the research project, which is the single source of truth: Read = panels transcribed, Unlocked = researched.
    public static class RM_OldTongue
    {
        public const string Hospice = "RM_OldTongue_Hospice";
        public const string Projector = "RM_OldTongue_Projector";
        public const string Pool = "RM_OldTongue_Pool";

        public static bool Unlocked(string projectDefName)
        {
            ResearchProjectDef p = DefDatabase<ResearchProjectDef>.GetNamedSilentFail(projectDefName);
            return p != null && p.IsFinished;
        }
        public static bool Read(string projectDefName)
        {
            ResearchProjectDef p = DefDatabase<ResearchProjectDef>.GetNamedSilentFail(projectDefName);
            return p != null && p.AnalyzedThingsRequirementsMet;
        }
        public static bool HospiceUnlocked { get { return Unlocked(Hospice); } }
        public static bool ProjectorCalibrated { get { return Unlocked(Projector); } }
        public static bool PoolPhaseReaderUnlocked { get { return Unlocked(Pool); } }
    }

    // Places panels on the floor against ancient fortified walls. Kinds whose set is already complete are skipped.
    public class GenStep_InscribedPanels : GenStep
    {
        public override int SeedPart { get { return 84921907; } }
        private static readonly string[] Kinds = { "RM_InscribedPanel_Hospice", "RM_InscribedPanel_Projector", "RM_InscribedPanel_Pool" };

        public override void Generate(Map map, GenStepParams parms)
        {
            if (!RM_WarscarSettings.oldTongueEnabled) return;
            ThingDef wallDef = DefDatabase<ThingDef>.GetNamedSilentFail("AncientFortifiedWall");
            if (wallDef == null) return;
            List<ThingDef> kinds = new List<ThingDef>();
            for (int i = 0; i < Kinds.Length; i++)
            {
                ThingDef d = DefDatabase<ThingDef>.GetNamedSilentFail(Kinds[i]);
                if (d == null) continue;
                CompProperties_InscribedPanel p = d.GetCompProperties<CompProperties_InscribedPanel>();
                AnalysisDetails det;
                if (p != null && Find.AnalysisManager != null && Find.AnalysisManager.TryGetAnalysisProgress(p.analysisID, out det) && det != null && det.Satisfied) continue;
                kinds.Add(d);
            }
            if (kinds.Count == 0) return;
            List<IntVec3> cells = new List<IntVec3>();
            List<Thing> walls = map.listerThings.ThingsOfDef(wallDef);
            for (int i = 0; i < walls.Count; i++)
                foreach (IntVec3 c in GenAdj.CellsAdjacentCardinal(walls[i]))
                    if (c.InBounds(map) && c.Standable(map) && c.GetEdifice(map) == null && c.GetFirstItem(map) == null && !cells.Contains(c)) cells.Add(c);
            cells.Shuffle();
            int target = Mathf.RoundToInt(RM_WarscarSettings.oldTonguePanelsPerMap);
            int placed = 0;
            for (int i = 0; i < cells.Count && placed < target; i++)
            {
                if (!Rand.Chance(RM_WarscarSettings.oldTongueRevealChance)) continue;
                ThingDef kind = kinds[placed % kinds.Count];
                GenSpawn.Spawn(ThingMaker.MakeThing(kind), cells[i], map);
                placed++;
            }
        }
    }
}
