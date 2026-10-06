using System.Collections.Generic;
using System.Linq;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.Scarlands
{
    // WARSCAR_LOOSENED_PANEL_BUILD_1 (WARSCAR_SNAP_MARK_1 spec 6; warscar_bedazzle sitting). The mark's other pay:
    // a few panels per Warscar map are set into the ancient fortified walls in place of a wall segment, each with a
    // sealed crate decided behind it at generation. Always visible, own graphic. Only a pawn whose Warscar mark is
    // at DEEPENING or above (the mark's own stage threshold, read from RM_WarscarMark's stages) can work it loose;
    // anyone else is refused: "It won't give. Someone who knows this ground might." Worked loose, the panel comes
    // out and the crate it hid stands in the gap. Not destroyable, not deconstructible: the mark is the key.
    public class RM_Building_LoosenedPanel : Building
    {
        public const string Refusal = "It won't give. Someone who knows this ground might.";
        public ThingDef cacheDef;

        public static float DeepeningSeverity
        {
            get
            {
                HediffStage s = RM_WarscarMark.MarkDef?.stages?.FirstOrDefault(x => x.label != null && x.label.Contains("deepening"));
                return s != null ? s.minSeverity : 0.5f;
            }
        }

        public static bool CanWork(Pawn p)
        {
            Hediff h = p?.health?.hediffSet?.GetFirstHediffOfDef(RM_WarscarMark.MarkDef);
            return h != null && h.Severity >= DeepeningSeverity;
        }

        public override IEnumerable<FloatMenuOption> GetFloatMenuOptions(Pawn selPawn)
        {
            foreach (FloatMenuOption o in base.GetFloatMenuOptions(selPawn))
            {
                yield return o;
            }
            if (!RM_WarscarSettings.loosenedPanelsEnabled)
            {
                yield break;
            }
            if (!selPawn.CanReach(this, PathEndMode.Touch, Danger.Deadly))
            {
                yield return new FloatMenuOption("Work the panel loose (cannot reach)", null);
                yield break;
            }
            if (!CanWork(selPawn))
            {
                yield return new FloatMenuOption("Work the panel loose: " + Refusal, null);
                yield break;
            }
            yield return new FloatMenuOption("Work the panel loose", delegate
            {
                Job job = JobMaker.MakeJob(RM_LoosenedPanelDefOf.RM_WorkPanelLoose, this);
                selPawn.jobs.TryTakeOrderedJob(job, JobTag.Misc);
            });
        }

        /// <summary>The panel comes out; the crate it hid stands in the gap. Returns the crate (or null).</summary>
        public Thing Open(Pawn by)
        {
            Map map = Map;
            IntVec3 pos = Position;
            ThingDef cache = cacheDef ?? RM_GenStep_LoosenedPanels.DefaultCacheDef();
            Destroy(DestroyMode.Vanish);
            Thing crate = null;
            if (cache != null)
            {
                crate = GenSpawn.Spawn(ThingMaker.MakeThing(cache), pos, map);
            }
            Messages.Message((by != null ? by.LabelShortCap + " works the panel loose" : "The panel comes loose")
                + (crate != null ? ": a sealed crate was hidden behind it." : "."),
                new LookTargets(crate ?? (Thing)by), MessageTypeDefOf.PositiveEvent);
            return crate;
        }

        public override string GetInspectString()
        {
            string s = base.GetInspectString();
            string mine = "A wall panel loose in its frame; something is behind it. Only someone the Warscar has marked deeply knows how it gives.";
            return s.NullOrEmpty() ? mine : s + "\n" + mine;
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Defs.Look(ref cacheDef, "cacheDef");
        }
    }

    public class RM_JobDriver_WorkPanelLoose : JobDriver
    {
        private const int WorkTicks = 900; // INVENTED: a long, careful pull

        private RM_Building_LoosenedPanel Panel => (RM_Building_LoosenedPanel)job.targetA.Thing;

        public override bool TryMakePreToilReservations(bool errorOnFailed)
        {
            return pawn.Reserve(job.targetA, job, 1, -1, null, errorOnFailed);
        }

        protected override IEnumerable<Toil> MakeNewToils()
        {
            this.FailOnDespawnedOrNull(TargetIndex.A);
            this.FailOn(() => !RM_Building_LoosenedPanel.CanWork(pawn) || !RM_WarscarSettings.loosenedPanelsEnabled);
            yield return Toils_Goto.GotoThing(TargetIndex.A, PathEndMode.Touch);
            Toil work = Toils_General.Wait(WorkTicks, TargetIndex.A);
            work.WithProgressBarToilDelay(TargetIndex.A);
            work.FailOnCannotTouch(TargetIndex.A, PathEndMode.Touch);
            yield return work;
            yield return Toils_General.Do(() => Panel.Open(pawn));
        }
    }

    [DefOf]
    public static class RM_LoosenedPanelDefOf
    {
        public static JobDef RM_WorkPanelLoose;

        static RM_LoosenedPanelDefOf()
        {
            DefOfHelper.EnsureInitializedInCtor(typeof(RM_LoosenedPanelDefOf));
        }
    }

    // Replaces ancient fortified wall segments that stand between two open cells (so the panel faces somewhere
    // and has a "behind"), at least MinSpacing apart, with a loosened panel holding a sealed crate.
    public class RM_GenStep_LoosenedPanels : GenStep
    {
        private const int MinSpacing = 6;
        public override int SeedPart => 61873204;

        public static ThingDef DefaultCacheDef()
        {
            return DefDatabase<ThingDef>.GetNamedSilentFail("AncientSealedCrate") ?? DefDatabase<ThingDef>.GetNamedSilentFail("SealedCrate");
        }

        public static bool IsSlot(Thing wall, Map map)
        {
            IntVec3 c = wall.Position;
            foreach (IntVec3 d in new[] { IntVec3.North, IntVec3.East })
            {
                IntVec3 a = c + d, b = c - d;
                if (a.InBounds(map) && b.InBounds(map) && a.Standable(map) && b.Standable(map))
                {
                    return true;
                }
            }
            return false;
        }

        public override void Generate(Map map, GenStepParams parms)
        {
            Place(map, Mathf.RoundToInt(RM_WarscarSettings.loosenedPanelsPerMap));
        }

        public static int Place(Map map, int target)
        {
            if (!RM_WarscarSettings.loosenedPanelsEnabled || target <= 0)
            {
                return 0;
            }
            ThingDef wallDef = DefDatabase<ThingDef>.GetNamedSilentFail("AncientFortifiedWall");
            ThingDef panelDef = DefDatabase<ThingDef>.GetNamedSilentFail("RM_LoosenedPanel");
            ThingDef cache = DefaultCacheDef();
            if (wallDef == null || panelDef == null || cache == null)
            {
                return 0;
            }
            List<Thing> walls = map.listerThings.ThingsOfDef(wallDef).Where(w => IsSlot(w, map)).ToList();
            walls.Shuffle();
            var placed = new List<IntVec3>();
            foreach (Thing w in walls)
            {
                if (placed.Count >= target)
                {
                    break;
                }
                IntVec3 c = w.Position;
                if (placed.Any(p => p.InHorDistOf(c, MinSpacing)))
                {
                    continue;
                }
                Faction f = w.Faction;
                w.Destroy(DestroyMode.Vanish);
                var panel = (RM_Building_LoosenedPanel)ThingMaker.MakeThing(panelDef);
                panel.cacheDef = cache;
                GenSpawn.Spawn(panel, c, map);
                if (f != null)
                {
                    panel.SetFaction(f);
                }
                placed.Add(c);
            }
            return placed.Count;
        }
    }

    /// <summary>Proof hooks for the loosened_panel chain (static_call, args "current|severity").</summary>
    public static class RM_LoosenedPanelProof
    {
        /// <summary>Spawns a panel and a colonist whose mark is at `severity`, reads the gate, and opens the panel
        /// when the gate allows. "sev 0.30 deepening 0.50 canWork False opened False crate - refusal ..."</summary>
        /// jawa/static_call splits its args on '|' into PARAMETERS, so "current|0.3" needs two of them (LIVE
        /// 2026-10-06: the one-string signature was never callable and the script read an empty reply as a FAIL).
        public static string ProofWork(string mapArg, string sevArg)
        {
            Map map = Find.CurrentMap;
            float sev = sevArg != null && float.TryParse(sevArg, System.Globalization.NumberStyles.Float,
                System.Globalization.CultureInfo.InvariantCulture, out float v) ? v : 0.5f;
            ThingDef panelDef = DefDatabase<ThingDef>.GetNamedSilentFail("RM_LoosenedPanel");
            if (map == null || panelDef == null || RM_WarscarMark.MarkDef == null)
            {
                return "ERROR no map / RM_LoosenedPanel / RM_WarscarMark";
            }
            if (!CellFinder.TryFindRandomCellNear(map.Center, map, 25, c => c.Standable(map) && c.GetEdifice(map) == null
                    && c.GetFirstItem(map) == null && (c + IntVec3.East).Standable(map), out IntVec3 cell))
            {
                return "ERROR no cell";
            }
            var panel = (RM_Building_LoosenedPanel)GenSpawn.Spawn(ThingMaker.MakeThing(panelDef), cell, map);
            panel.cacheDef = RM_GenStep_LoosenedPanels.DefaultCacheDef();
            Pawn p = PawnGenerator.GeneratePawn(PawnKindDefOf.Colonist, Faction.OfPlayer);
            GenSpawn.Spawn(p, cell + IntVec3.East, map);
            if (sev > 0f)
            {
                Hediff h = HediffMaker.MakeHediff(RM_WarscarMark.MarkDef, p);
                h.Severity = sev;
                p.health.AddHediff(h);
            }
            bool can = RM_Building_LoosenedPanel.CanWork(p);
            string menu = string.Join(" / ", panel.GetFloatMenuOptions(p).Select(o => o.Label + (o.Disabled ? " [disabled]" : "")));
            Thing crate = can ? panel.Open(p) : null;
            string r = "sev " + sev.ToString("0.00") + " deepening " + RM_Building_LoosenedPanel.DeepeningSeverity.ToString("0.00")
                       + " canWork " + can + " opened " + (crate != null) + " crate " + (crate?.def.defName ?? "-")
                       + " menu " + menu;
            if (!panel.Destroyed)
            {
                panel.Destroy();
            }
            p.Destroy();
            return r;
        }

        /// <summary>Runs the genstep's placement on the current map: how many wall slots exist and how many panels it set.</summary>
        public static string ProofPlace(Map map)
        {
            map = map ?? Find.CurrentMap;
            ThingDef wallDef = DefDatabase<ThingDef>.GetNamedSilentFail("AncientFortifiedWall");
            int slots = wallDef == null ? 0 : map.listerThings.ThingsOfDef(wallDef).Count(w => RM_GenStep_LoosenedPanels.IsSlot(w, map));
            int placed = RM_GenStep_LoosenedPanels.Place(map, 2);
            return "slots " + slots + " placed " + placed;
        }
    }
}
