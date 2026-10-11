using System.Collections.Generic;
using System.Text;
using HarmonyLib;
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
        // A "rest" panel belongs to no set: reading it gives research points to the current project (the amount is
        // a setting) and every Nth rest panel read across the game reveals a sealed crate or a buried chassis.
        // It is read by the same transcribe job and gate as the set panels; its analysisID is never satisfied.
        public bool restPanel;
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
            // A rest panel's points go to the current project; with none chosen they would be lost, so say so.
            if (Props.restPanel && Find.ResearchManager.GetProject() == null)
                return "Choose a research project first (the reading feeds it).";
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
            Map map = parent.Spawned ? parent.Map : null;
            IntVec3 pos = parent.Position;
            if (Props.restPanel) RM_OldTongue.ReadRestPanel(pawn, parent);
            else base.OnAnalyzed(pawn);
            if (map != null)
            {
                map.mapDrawer.MapMeshDirty(pos, MapMeshFlagDefOf.Things);
                RM_OldTongue.DropTranscription(pawn, parent.def, pos, map);
            }
        }

        public override string CompInspectStringExtra()
        {
            StringBuilder sb = new StringBuilder();
            string baseStr = base.CompInspectStringExtra();
            if (!baseStr.NullOrEmpty()) sb.Append(baseStr);
            if (Props.restPanel)
            {
                if (sb.Length > 0) sb.Append("\n");
                sb.Append(read ? "Transcribed." : "Not part of a set: reading it feeds the current research project.");
                return sb.ToString();
            }
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
                        if (o != this && !o.read && o.AnalysisID == AnalysisID && o.parent.Spawned && o.parent.Map == parent.Map)
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

        public const string TranscriptionDef = "RM_OldTongueTranscription";

        // Rest panel read: points to the current project, then the every-Nth find.
        public static void ReadRestPanel(Pawn pawn, Thing panel)
        {
            ResearchProjectDef proj = Find.ResearchManager.GetProject();
            float pts = RM_WarscarSettings.oldTongueRestPoints;
            if (proj != null && pts > 0f && !proj.IsFinished)
                Find.ResearchManager.AddProgress(proj, pts, pawn);
            int every = RM_WarscarSettings.oldTongueFindEvery;
            int n = RM_OldTongueGame.Get() != null ? ++RM_OldTongueGame.Get().restPanelsRead : 0;
            string who = pawn != null ? pawn.LabelShortCap : "Someone";
            string head = who + " transcribed a rest panel" + (proj != null && pts > 0f ? " (+" + pts.ToString("0") + " research to " + proj.LabelCap + ")" : "");
            Thing found = null;
            if (every > 0 && n > 0 && n % every == 0 && panel.Spawned) found = RevealFind(panel.Map, panel.Position);
            if (found != null)
                Find.LetterStack.ReceiveLetter("Old tongue: a marked place",
                    head + ". The panel names a place nearby, and there it is: " + found.LabelNoCount + ".",
                    LetterDefOf.PositiveEvent, new LookTargets(found));
            else
                Messages.Message(head + ".", new LookTargets(panel), MessageTypeDefOf.PositiveEvent);
        }

        // Half the time a sealed crate (the loosened panels' cache def), half a buried chassis dug clear (slagged or
        // posed, unclaimed). Spawned on a free standable cell near the panel.
        public static Thing RevealFind(Map map, IntVec3 near)
        {
            ThingDef def;
            if (Rand.Chance(0.5f)) def = RM_GenStep_LoosenedPanels.DefaultCacheDef();
            else def = DefDatabase<ThingDef>.GetNamedSilentFail(Rand.Chance(0.5f) ? "RM_KneelingChassis_Posed" : "RM_KneelingChassis_Slagged");
            if (def == null) def = RM_GenStep_LoosenedPanels.DefaultCacheDef();
            if (def == null) return null;
            IntVec3 cell;
            if (!CellFinder.TryFindRandomCellNear(near, map, 8,
                    c => c.Standable(map) && c.GetEdifice(map) == null && c.GetFirstItem(map) == null && !c.Fogged(map)
                         && GenAdj.OccupiedRect(c, Rot4.North, def.size).InBounds(map), out cell))
                return null;
            return GenSpawn.Spawn(ThingMaker.MakeThing(def), cell, map);
        }

        // Every read leaves a copy at the reader's feet; the campaign layer makes it an antiquity.
        public static void DropTranscription(Pawn pawn, ThingDef panelDef, IntVec3 panelPos, Map map)
        {
            if (!RM_WarscarSettings.oldTongueTranscriptions) return;
            ThingDef d = DefDatabase<ThingDef>.GetNamedSilentFail(TranscriptionDef);
            if (d == null) return;
            Thing t = ThingMaker.MakeThing(d);
            IntVec3 at = pawn != null && pawn.Spawned && pawn.Map == map ? pawn.Position : panelPos;
            GenPlace.TryPlaceThing(t, at, map, ThingPlaceMode.Near);
        }

        // Unread panels of an unfinished set, on every map, for the research tooltip.
        public static string UnreadLine(ResearchProjectDef proj)
        {
            if (proj == null || proj.requiredAnalyzed.NullOrEmpty() || proj.AnalyzedThingsRequirementsMet) return null;
            List<string> where = new List<string>();
            for (int i = 0; i < CompInscribedPanel.All.Count; i++)
            {
                CompInscribedPanel c = CompInscribedPanel.All[i];
                if (c.read || !c.parent.Spawned || !proj.requiredAnalyzed.Contains(c.parent.def)) continue;
                Map m = c.parent.Map;
                where.Add((m.Parent != null ? m.Parent.LabelCap.ToString() : "map") + " (" + c.parent.Position.x + "," + c.parent.Position.z + ")");
            }
            if (where.Count == 0) return "Unread panels: none found on any map you hold.";
            return "Unread panels: " + string.Join(", ", where.ToArray());
        }
    }

    // Game-wide count of rest panels read, so "every Nth" spans maps.
    public class RM_OldTongueGame : GameComponent
    {
        public int restPanelsRead;
        public RM_OldTongueGame(Game game) { }
        public static RM_OldTongueGame Get() { return Current.Game != null ? Current.Game.GetComponent<RM_OldTongueGame>() : null; }
        public override void ExposeData() { Scribe_Values.Look(ref restPanelsRead, "restPanelsRead", 0); }
    }

    // The research tooltip lists where the unread panels of a needed set stand. GetTip caches the description
    // (cachedDescription), so the live line is appended after it on every call, never baked into the cache.
    [HarmonyPatch(typeof(ResearchProjectDef), nameof(ResearchProjectDef.GetTip))]
    public static class RM_OldTonguePatches_ResearchTip
    {
        public static void Postfix(ResearchProjectDef __instance, ref string __result)
        {
            if (__instance == null || !__instance.defName.StartsWith("RM_OldTongue_")) return;
            string line = RM_OldTongue.UnreadLine(__instance);
            if (!line.NullOrEmpty()) __result += "\n\n" + line;
        }
    }

    // A buy-side price premium. The engine has no XML lever for it (TraderKindDef.PriceTypeFor only reads stock
    // generators when the player BUYS -- see RUT_HuttCartel_EggMarket.xml), so: an item carrying this extension
    // sells for factor x its price to a trader of a listed faction. Factions are named by defName strings so a
    // campaign-layer patch can list its own factions without this mod depending on them.
    public class RM_FactionBuyPremium : DefModExtension
    {
        public List<string> factions = new List<string>();
        public float factor = 1.5f;   // PROVISIONAL
    }

    [HarmonyPatch(typeof(Tradeable), nameof(Tradeable.GetPriceFor), new[] { typeof(TradeAction) })]
    public static class RM_OldTonguePatches_BuyPremium
    {
        public static void Postfix(Tradeable __instance, TradeAction action, ref float __result)
        {
            if (action != TradeAction.PlayerSells || __instance == null || __instance.IsCurrency) return;
            if (!RM_WarscarSettings.oldTongueTradePremium) return;
            ThingDef def = __instance.ThingDef;
            RM_FactionBuyPremium ext = def != null ? def.GetModExtension<RM_FactionBuyPremium>() : null;
            if (ext == null || ext.factions.NullOrEmpty()) return;
            if (!TradeSession.Active || TradeSession.giftMode || TradeSession.trader == null) return;
            Faction f = TradeSession.trader.Faction;
            if (f == null || f.def == null || !ext.factions.Contains(f.def.defName)) return;
            __result *= ext.factor;
        }
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
            ThingDef rest = DefDatabase<ThingDef>.GetNamedSilentFail("RM_InscribedPanel_Rest");
            int restTarget = rest != null ? Mathf.RoundToInt(RM_WarscarSettings.oldTongueRestPanelsPerMap) : 0;
            if (kinds.Count == 0 && restTarget <= 0) return;
            List<IntVec3> cells = new List<IntVec3>();
            List<Thing> walls = map.listerThings.ThingsOfDef(wallDef);
            for (int i = 0; i < walls.Count; i++)
                foreach (IntVec3 c in GenAdj.CellsAdjacentCardinal(walls[i]))
                    if (c.InBounds(map) && c.Standable(map) && c.GetEdifice(map) == null && c.GetFirstItem(map) == null && !cells.Contains(c)) cells.Add(c);
            cells.Shuffle();
            int target = kinds.Count > 0 ? Mathf.RoundToInt(RM_WarscarSettings.oldTonguePanelsPerMap) : 0;
            int placed = 0, restPlaced = 0, ci = 0;
            for (; ci < cells.Count && placed < target; ci++)
            {
                // WARSCAR_TUNING_SEMANTICS_1: a per-CELL roll until the quota fills (see the setting's comment).
                if (!Rand.Chance(RM_WarscarSettings.oldTongueRevealChance)) continue;
                ThingDef kind = kinds[placed % kinds.Count];
                GenSpawn.Spawn(ThingMaker.MakeThing(kind), cells[ci], map);
                placed++;
            }
            // Rest panels take the next wall-side cells, after the set panels have theirs.
            for (; ci < cells.Count && restPlaced < restTarget; ci++)
            {
                if (!Rand.Chance(RM_WarscarSettings.oldTongueRevealChance)) continue;
                GenSpawn.Spawn(ThingMaker.MakeThing(rest), cells[ci], map);
                restPlaced++;
            }
        }
    }
}
