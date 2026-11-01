using System.Collections.Generic;
using System.Linq;
using System.Text;
using RimMandrake.RustCathedral.Hum;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.RustCathedral
{
    /// <summary>RUSTCATHEDRAL_WORN_BIT_ARC_1: the orders on the borehulk, the fork, and what each branch does. World
    /// state lives in RM_WornBitGame, per-hulk state in RM_CompBorehulkDrill.</summary>
    public static class RM_WornBit
    {
        public const int MinUnbitConstruction = 8;
        public const string CampaignTag = "The Worn Bit";

        public static RM_Area_BorehulkDig DigArea(Map map)
        {
            if (map == null)
            {
                return null;
            }
            RM_Area_BorehulkDig area = map.areaManager.Get<RM_Area_BorehulkDig>();
            if (area == null)
            {
                area = new RM_Area_BorehulkDig(map.areaManager);
                map.areaManager.AllAreas.Add(area);
            }
            return area;
        }

        public static bool OnCathedralGround(Map map)
        {
            return RM_MapComponent_BiomeAttitude.GetBand(map) >= 0 && RM_MapComponent_BiomeAttitude.GetStanding(map) != null;
        }

        public static bool IsSacred(Thing t)
        {
            return t?.def != null && t.def.HasModExtension<RM_SacredCellExtension>();
        }

        // ---- the orders ----

        public static IEnumerable<FloatMenuOption> Options(RM_CompBorehulkDrill comp, Pawn pawn)
        {
            Pawn hulk = comp.parent as Pawn;
            if (hulk == null || !hulk.Spawned || hulk.Dead || pawn.Faction != Faction.OfPlayer || pawn.Map != hulk.Map)
            {
                yield break;
            }
            RM_BorehulkDrillState state = comp.State;
            if (state == RM_BorehulkDrillState.Worn && RM_RustCathedralSettings.wornBitEnabled)
            {
                string refusal = UnbitRefusal(comp, pawn);
                yield return refusal != null
                    ? new FloatMenuOption("Unbolt the drill head: " + refusal, null)
                    : new FloatMenuOption("Unbolt the drill head", delegate { Assign(pawn, RM_WornBitDefOf.RM_Job_UnbitBorehulk, hulk); });
            }
            else if (state == RM_BorehulkDrillState.Unbitted && RM_WornBitGame.Instance?.RestorationOpen == true)
            {
                string refusal = RestorationRefusal(comp, pawn);
                yield return refusal != null
                    ? new FloatMenuOption("Restore the borehulk: " + refusal, null)
                    : new FloatMenuOption("Restore the borehulk", delegate { Assign(pawn, RM_WornBitDefOf.RM_Job_RestoreBorehulk, hulk); });
            }
            else if (comp.Kept && RM_RustCathedralSettings.wornBitMaintenanceEnabled)
            {
                string refusal = ServiceRefusal(comp, pawn);
                yield return refusal != null
                    ? new FloatMenuOption("Service the borehulk: " + refusal, null)
                    : new FloatMenuOption("Service the borehulk", delegate { Assign(pawn, RM_WornBitDefOf.RM_Job_ServiceBorehulk, hulk); });
            }
        }

        private static void Assign(Pawn pawn, JobDef def, Pawn hulk)
        {
            Job job = JobMaker.MakeJob(def, hulk);
            job.playerForced = true;
            pawn.jobs.TryTakeOrderedJob(job, JobTag.Misc);
        }

        public static string UnbitRefusal(RM_CompBorehulkDrill comp, Pawn pawn)
        {
            if (RM_WornBitGame.Instance?.ArcRunning == true)
            {
                return "another drill head is already out";
            }
            if (!RM_WornBitKernel.CalmEnough(RM_MapComponent_BiomeAttitude.GetBand(comp.parent.Map)))
            {
                return "the hum is not calm enough";
            }
            if (pawn != null && (pawn.skills?.GetSkill(SkillDefOf.Construction)?.Level ?? 0) < MinUnbitConstruction)
            {
                return "needs Construction " + MinUnbitConstruction;
            }
            return null;
        }

        /// <summary>What the restoration still lacks, naming the first missing item; null when it can go ahead.
        /// pawn null reads the map only.</summary>
        public static string RestorationRefusal(RM_CompBorehulkDrill comp, Pawn pawn)
        {
            RM_BorehulkRestorationDef def = RM_WornBitDefOf.RM_BorehulkRestoration;
            if (pawn != null && (pawn.skills?.GetSkill(SkillDefOf.Crafting)?.Level ?? 0) < def.minCrafting)
            {
                return "needs Crafting " + def.minCrafting;
            }
            Map map = comp.parent.Map;
            var need = new List<int>();
            var have = new List<int>();
            foreach (ThingDefCountClass row in def.ingredients)
            {
                int done = comp.Delivered(row.thingDef);
                need.Add(row.count);
                have.Add(done + AvailableCount(map, row.thingDef));
            }
            int shortAt = RM_WornBitKernel.FirstShort(need, have);
            if (shortAt >= 0)
            {
                ThingDefCountClass row = def.ingredients[shortAt];
                return "missing " + row.thingDef.label + " (" + have[shortAt] + "/" + row.count + ", in a stockpile)";
            }
            return null;
        }

        public static string ServiceRefusal(RM_CompBorehulkDrill comp, Pawn pawn)
        {
            Map map = comp.parent.Map;
            int comps = RM_RustCathedralSettings.wornBitServiceComponents;
            int fuel = RM_RustCathedralSettings.wornBitServiceChemfuel;
            if (AvailableCount(map, ThingDefOf.ComponentIndustrial) < comps)
            {
                return "missing " + comps + " " + ThingDefOf.ComponentIndustrial.label;
            }
            if (AvailableCount(map, ThingDefOf.Chemfuel) < fuel)
            {
                return "missing " + fuel + " " + ThingDefOf.Chemfuel.label;
            }
            return null;
        }

        public static IEnumerable<Thing> Available(Map map, ThingDef def)
        {
            bool isHead = def == RM_WornBitDefOf.RM_RefurbishedDrillHead;
            return map.listerThings.ThingsOfDef(def).Where(t => t.Spawned && (isHead || t.IsInAnyStorage()));
        }

        public static int AvailableCount(Map map, ThingDef def)
        {
            return Available(map, def).Sum(t => t.stackCount);
        }

        // ---- stage 1 ----

        public static int WorkersAt(Pawn hulk, JobDef job)
        {
            int n = 0;
            foreach (Pawn p in hulk.Map.mapPawns.AllPawnsSpawned)
            {
                if (p.CurJobDef == job && p.CurJob.targetA.Thing == hulk && p.Position.InHorDistOf(hulk.Position, 2.9f))
                {
                    n++;
                }
            }
            return n;
        }

        /// <summary>One worker's tick of stage 1, the workers already counted. Returns the amount added.</summary>
        public static float UnbitTick(RM_CompBorehulkDrill comp, int workers, float speed)
        {
            Pawn hulk = (Pawn)comp.parent;
            float delta = RM_WornBitKernel.UnbitDelta(workers, speed, RM_MapComponent_BiomeAttitude.GetBand(hulk.Map), hulk.pather?.Moving == true);
            comp.unbitProgress += delta;
            if (comp.unbitProgress >= RM_RustCathedralSettings.wornBitUnbitWork)
            {
                FinishUnbit(comp);
            }
            return delta;
        }

        public static void FinishUnbit(RM_CompBorehulkDrill comp)
        {
            if (comp.State != RM_BorehulkDrillState.Worn)
            {
                return;
            }
            Pawn hulk = (Pawn)comp.parent;
            comp.SetState(RM_BorehulkDrillState.Unbitted);
            Thing head = ThingMaker.MakeThing(RM_WornBitDefOf.RM_WornDrillHead);
            GenPlace.TryPlaceThing(head, hulk.Position, hulk.Map, ThingPlaceMode.Near);
            Find.LetterStack.ReceiveLetter("The drill head is off",
                "The bolts are out and the boom swings free. The drill head lies on the plate where it fell, far too heavy for one back. Whoever refurbishes it will want paying.",
                LetterDefOf.NeutralEvent, new TargetInfo(head.Position, hulk.Map));
            RM_WornBitGame.Instance?.OfferQuest(hulk);
        }

        // ---- stage 4: the fork ----

        public static void OpenChoiceDialog(RM_CompBorehulkDrill comp)
        {
            if (Find.WindowStack.IsOpen<Dialog_NodeTree>())
            {
                return;
            }
            var node = new DiaNode("The refurbished head is on the boom and half the bolts are home. The old machine holds still under the hands. This is the point past which it matters who it answers to.");
            node.options.Add(new DiaOption("Keep it: it joins the colony and mines where you say.") { action = delegate { TakeChoice(comp, RM_WornBitChoice.Keep); }, resolveTree = true });
            node.options.Add(new DiaOption("Free it: finish the work and let it go.") { action = delegate { TakeChoice(comp, RM_WornBitChoice.Free); }, resolveTree = true });
            node.options.Add(new DiaOption("Leave it unfinished: what went in so far is lost.") { action = delegate { TakeChoice(comp, RM_WornBitChoice.LeaveUnfinished); }, resolveTree = true });
            Find.WindowStack.Add(new Dialog_NodeTree(node, delayInteractivity: true, radioMode: false, "The Worn Bit"));
        }

        public static void TakeChoice(RM_CompBorehulkDrill comp, RM_WornBitChoice choice)
        {
            if (choice != RM_WornBitChoice.LeaveUnfinished)
            {
                comp.choice = choice;
                return;
            }
            // The head stays fitted if it went in; everything else is gone, and the offer stays open.
            ThingDef head = RM_WornBitDefOf.RM_RefurbishedDrillHead;
            bool headIn = comp.Delivered(head) > 0;
            comp.delivered.Clear();
            if (headIn)
            {
                comp.Deliver(head, 1);
            }
            comp.restoreProgress = 0f;
            comp.choice = RM_WornBitChoice.None;
        }

        public static void FinishRestoration(RM_CompBorehulkDrill comp)
        {
            Pawn hulk = (Pawn)comp.parent;
            RM_WornBitChoice choice = comp.choice;
            comp.SetState(RM_BorehulkDrillState.Restored);
            comp.lastServiceTick = Find.TickManager.TicksGame;
            comp.lastSelfBoreTick = Find.TickManager.TicksGame;
            if (choice == RM_WornBitChoice.Keep)
            {
                hulk.SetFaction(Faction.OfPlayer);
                DigArea(hulk.Map);
                Find.LetterStack.ReceiveLetter("The borehulk answers to you",
                    "A refurbished drill head is fitted, and the borehulk waits for a dig area. It will want servicing, and it will not be forgiven.",
                    LetterDefOf.PositiveEvent, hulk);
            }
            else
            {
                hulk.SetFaction(null);
                Find.LetterStack.ReceiveLetter("The borehulk goes its way",
                    "A refurbished drill head is fitted, and the borehulk trundles off to bore plate of its own choosing. It takes no orders. It may answer a favour.",
                    LetterDefOf.PositiveEvent, hulk);
            }
            RM_WornBitGame.Instance?.OnRestored(hulk);
            if (RM_RustCathedralSettings.wornBitPoliticsEnabled)
            {
                ApplyPolitics(hulk, choice == RM_WornBitChoice.Keep);
                Announce(hulk, choice == RM_WornBitChoice.Keep);
            }
        }

        /// <summary>Goodwill and the hum, each delta a setting times the political multiplier. Goodwill only moves where a
        /// faction carries RM_NeutralDroidsExtension (the free tier has none); no hediff, no stat.</summary>
        public static void ApplyPolitics(Pawn hulk, bool keep)
        {
            float m = RM_RustCathedralSettings.wornBitPoliticalMultiplier;
            int goodwill = RM_WornBitKernel.Scaled(keep ? RM_RustCathedralSettings.wornBitKeepGoodwill : RM_RustCathedralSettings.wornBitFreeGoodwill, m);
            float irritation = RM_WornBitKernel.ScaledF(keep ? RM_RustCathedralSettings.wornBitKeepIrritation : RM_RustCathedralSettings.wornBitFreeIrritation, m);
            foreach (Faction f in Find.FactionManager.AllFactionsListForReading)
            {
                if (!f.IsPlayer && !f.defeated && f.def.HasModExtension<RM_NeutralDroidsExtension>())
                {
                    Faction.OfPlayer.TryAffectGoodwillWith(f, goodwill, canSendMessage: true, canSendHostilityLetter: true, RM_WornBitDefOf.RM_WornBitChoiceMade);
                }
            }
            RM_MapComponent_BiomeAttitude.AddIrritation(hulk.Map, irritation);
        }

        /// <summary>The seam the campaign patches (RimUtinni Rites, Patch_WornBitChoice): RM tier knows no gods. Called only with
        /// the politics toggle on, so the toggle silences the campaign's deltas too.</summary>
        public static void Announce(Pawn hulk, bool keep)
        {
            Log.Message("[" + CampaignTag + "] the choice: " + (keep ? "keep" : "free"));
        }

        // ---- what the player reads ----

        public static string InspectLines(RM_CompBorehulkDrill comp, string stateLine)
        {
            var sb = new StringBuilder(stateLine ?? "");
            void Line(string s)
            {
                if (sb.Length > 0)
                {
                    sb.Append('\n');
                }
                sb.Append(s);
            }
            Pawn hulk = comp.parent as Pawn;
            if (comp.State == RM_BorehulkDrillState.Worn && comp.unbitProgress > 0f)
            {
                Line("Bolts out: " + (comp.unbitProgress / RM_RustCathedralSettings.wornBitUnbitWork).ToStringPercent() + ".");
                if (hulk?.Spawned == true && !RM_WornBitKernel.CalmEnough(RM_MapComponent_BiomeAttitude.GetBand(hulk.Map)))
                {
                    Line("The hum has dropped. The work has stopped.");
                }
            }
            if (comp.State == RM_BorehulkDrillState.Unbitted && comp.restoreProgress > 0f)
            {
                Line("Restoration: " + (comp.restoreProgress / RM_RustCathedralSettings.wornBitRestoreWork).ToStringPercent() + ".");
            }
            if (comp.Kept)
            {
                if (RM_RustCathedralSettings.wornBitMaintenanceEnabled)
                {
                    Line("Service left: " + comp.MaintenanceLeft.ToStringPercent() + (comp.MayDigKept ? "." : ". It has stopped digging and stands idle."));
                }
                if (hulk?.Spawned == true)
                {
                    int sacred = RM_DigFinder.SacredCellsInArea(hulk.Map);
                    if (sacred > 0)
                    {
                        Line("Warning: the dig area holds " + sacred + " sacred cells. Mining one is sacrilege.");
                    }
                }
            }
            if (comp.FreedWild)
            {
                Line("It answers favours, not orders.");
            }
            if (!comp.favourLine.NullOrEmpty())
            {
                Line(comp.favourLine);
            }
            return sb.ToString();
        }

        public static IEnumerable<Gizmo> Gizmos(RM_CompBorehulkDrill comp)
        {
            if (!comp.Kept)
            {
                yield break;
            }
            yield return new Command_Action
            {
                defaultLabel = "Expand dig area",
                defaultDesc = "Mark cells for the borehulk to mine. It mines any rock inside, sacred cells too if you draw them in.",
                icon = ContentFinder<Texture2D>.Get("UI/Designators/Mine"),
                action = delegate { Find.DesignatorManager.Select(new RM_Designator_BorehulkDigExpand()); }
            };
            yield return new Command_Action
            {
                defaultLabel = "Clear dig area",
                defaultDesc = "Remove cells from the borehulk's dig area.",
                icon = ContentFinder<Texture2D>.Get("UI/Designators/Cancel"),
                action = delegate { Find.DesignatorManager.Select(new RM_Designator_BorehulkDigClear()); }
            };
            if (RM_RustCathedralSettings.wornBitMaintenanceEnabled)
            {
                yield return new RM_Gizmo_BorehulkService(comp);
            }
        }
    }

    /// <summary>The maintenance bar.</summary>
    public class RM_Gizmo_BorehulkService : Gizmo
    {
        private readonly RM_CompBorehulkDrill comp;

        public RM_Gizmo_BorehulkService(RM_CompBorehulkDrill comp)
        {
            this.comp = comp;
            Order = -100f;
        }

        public override float GetWidth(float maxWidth)
        {
            return 140f;
        }

        public override GizmoResult GizmoOnGUI(Vector2 topLeft, float maxWidth, GizmoRenderParms parms)
        {
            Rect rect = new Rect(topLeft.x, topLeft.y, GetWidth(maxWidth), 75f);
            Widgets.DrawWindowBackground(rect);
            Rect inner = rect.ContractedBy(6f);
            Widgets.Label(new Rect(inner.x, inner.y, inner.width, 24f), "Service");
            Widgets.FillableBar(new Rect(inner.x, inner.y + 26f, inner.width, 28f), comp.MaintenanceLeft);
            return new GizmoResult(GizmoState.Clear);
        }
    }
}
