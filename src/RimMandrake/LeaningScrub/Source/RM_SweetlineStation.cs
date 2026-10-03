using System.Collections.Generic;
using System.Text;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.LeaningScrub
{
    // ════════════════════════════════════════════════════════════════════
    // LEANINGSCRUB_GPT_ENRICHMENT_1 part 3 — named sweetline trees.
    //
    // "Each sweetline tree gets a generated name, a small history panel, a
    // snagged-wool timer."  Built here, on one comp:
    //   name     generated once at first spawn from the comp's namer
    //            RulePackDef, unique among sweetline trees on the map, Scribed;
    //            shown as the tree's label.
    //   history  a short Scribed list of dated entries (named, wool shed,
    //            struck) behind a "History" gizmo — the small panel.
    //   wool     a Scribed timer: every woolIntervalDays a mature tree sheds
    //            woolCount of woolThing beside its trunk.
    // Plants only TickLong, so the timer rides CompTickLong (never CompTick)
    // and the engine's own Long cadence is the only throttle.
    //
    // part 4 (LEANINGSCRUB_SWEETLINE_VISITORS_1): abstract live visits, see TryVisit.
    // NOT here, each a filed follow-up: the resident guardian that harm wakes (the guardian
    // creature is not designed yet).
    // ════════════════════════════════════════════════════════════════════
    public class RM_CompProperties_SweetlineStation : CompProperties
    {
        public RulePackDef namer;
        public ThingDef woolThing;
        public int woolCount = 5;
        public float woolIntervalDays = 5f;
        public int maxHistory = 12;
        // LEANINGSCRUB_SWEETLINE_VISITORS_1: road-folk who camp under the tree and pilgrims who leave tokens.
        public ThingDef tokenThing;
        public float pilgrimChance = 0.6f;
        public int maxTokensNear = 3;

        public RM_CompProperties_SweetlineStation()
        {
            compClass = typeof(RM_CompSweetlineStation);
        }

        public override IEnumerable<string> ConfigErrors(ThingDef parentDef)
        {
            foreach (string e in base.ConfigErrors(parentDef))
            {
                yield return e;
            }
            if (namer == null)
            {
                yield return "RM_CompProperties_SweetlineStation has no namer.";
            }
            if (woolThing == null)
            {
                yield return "RM_CompProperties_SweetlineStation has no woolThing.";
            }
        }
    }

    public class RM_CompSweetlineStation : ThingComp
    {
        private string treeName;
        private int nextWoolTick = -1;
        private int lastStruckTick = -999999;
        private List<string> history = new List<string>();
        private int nextVisitTick = -1;
        private int campCount;
        private int pilgrimCount;

        public RM_CompProperties_SweetlineStation Props => (RM_CompProperties_SweetlineStation)props;

        public string TreeName => treeName;

        private static bool Enabled => RM_WindCalendar.On(RM_LeaningScrubSettings.sweetlineStationsEnabled);

        private static bool VisitorsOn => Enabled && RM_LeaningScrubSettings.sweetlineVisitorsEnabled;

        private static int VisitIntervalTicks =>
            (int)(Mathf.Max(1f, RM_LeaningScrubSettings.sweetlineVisitIntervalDays) * GenDate.TicksPerDay);

        private bool everMature;

        // Owner 2026-10-03 (LEANINGSCRUB_SWEETLINE_GUARDIAN_1 ruling, "a harvested tree keeps
        // shedding"): a harvest resets growth to 0.05, so a tree that has once matured counts
        // as grown for shedding, visits and the inspect line.
        private bool Mature
        {
            get
            {
                if (!everMature && parent is Plant plant && plant.LifeStage == PlantLifeStage.Mature)
                {
                    everMature = true;
                }
                return everMature;
            }
        }

        public override void PostSpawnSetup(bool respawningAfterLoad)
        {
            base.PostSpawnSetup(respawningAfterLoad);
            if (treeName == null && Props.namer != null)
            {
                treeName = NameGenerator.GenerateName(Props.namer, n => !NameTakenOnMap(n));
                AddHistory("named " + treeName + ".");
            }
            if (nextWoolTick < 0)
            {
                // Stagger first sheds so a map's trees never shed in unison.
                nextWoolTick = Find.TickManager.TicksGame
                    + Rand.Range(0, (int)(Props.woolIntervalDays * GenDate.TicksPerDay));
            }
        }

        private bool NameTakenOnMap(string candidate)
        {
            Map map = parent.Map;
            if (map == null)
            {
                return false;
            }
            foreach (Thing t in map.listerThings.ThingsOfDef(parent.def))
            {
                if (t != parent && t.TryGetComp<RM_CompSweetlineStation>()?.TreeName == candidate)
                {
                    return true;
                }
            }
            return false;
        }

        public override void CompTickLong()
        {
            base.CompTickLong();
            TryVisit();
            if (!Enabled || !parent.Spawned || Props.woolThing == null)
            {
                return;
            }
            int now = Find.TickManager.TicksGame;
            if (now < nextWoolTick)
            {
                return;
            }
            nextWoolTick = now + (int)(Props.woolIntervalDays * GenDate.TicksPerDay);
            if (!Mature)
            {
                return;
            }
            Thing wool = ThingMaker.MakeThing(Props.woolThing);
            wool.stackCount = Props.woolCount;
            if (GenPlace.TryPlaceThing(wool, parent.Position, parent.Map, ThingPlaceMode.Near))
            {
                AddHistory("shed " + Props.woolCount + " " + Props.woolThing.label + " snagged from passing giants.");
            }
        }

        // A visit is abstract: no pawns walk in. Road-folk (generic, unnamed) camp a night under the
        // tree (cold ash left beside the trunk) or pilgrims leave a token. Either lands in History.
        private void TryVisit()
        {
            if (!VisitorsOn || !parent.Spawned || !Mature || !parent.Map.IsPlayerHome)
            {
                return;
            }
            int now = Find.TickManager.TicksGame;
            if (nextVisitTick < 0)
            {
                nextVisitTick = now + (int)(VisitIntervalTicks * Rand.Range(0.5f, 1.5f));
                return;
            }
            if (now < nextVisitTick)
            {
                return;
            }
            nextVisitTick = now + (int)(VisitIntervalTicks * Rand.Range(0.5f, 1.5f));
            Map map = parent.Map;
            if (Rand.Chance(Props.pilgrimChance))
            {
                pilgrimCount++;
                int near = 0;
                if (Props.tokenThing != null)
                {
                    foreach (Thing t in GenRadial.RadialDistinctThingsAround(parent.Position, map, 5f, true))
                    {
                        if (t.def == Props.tokenThing)
                        {
                            near += t.stackCount;
                        }
                    }
                }
                if (Props.tokenThing != null && near < Props.maxTokensNear)
                {
                    Thing token = ThingMaker.MakeThing(Props.tokenThing);
                    token.stackCount = 1;
                    GenPlace.TryPlaceThing(token, parent.Position, map, ThingPlaceMode.Near);
                    AddHistory("a pilgrim stopped here and left a token at the trunk.");
                }
                else
                {
                    AddHistory("a pilgrim stopped here; the trunk already holds all the tokens it can.");
                }
            }
            else
            {
                campCount++;
                ThingDef ash = DefDatabase<ThingDef>.GetNamedSilentFail("Filth_Ash");
                if (ash != null)
                {
                    FilthMaker.TryMakeFilth(parent.Position + GenRadial.RadialPattern[Rand.Range(1, 9)], map, ash);
                }
                AddHistory("a road-party camped a night under it.");
            }
        }

        public override void PostPostApplyDamage(DamageInfo dinfo, float totalDamageDealt)
        {
            base.PostPostApplyDamage(dinfo, totalDamageDealt);
            if (!Enabled || totalDamageDealt <= 0f)
            {
                return;
            }
            int now = Find.TickManager.TicksGame;
            // One entry per day at most: a tree being chopped is one event.
            if (now - lastStruckTick < GenDate.TicksPerDay)
            {
                return;
            }
            lastStruckTick = now;
            string by = dinfo.Instigator != null ? dinfo.Instigator.LabelShort : dinfo.Def.label;
            AddHistory("struck by " + by + ".");
        }

        /// <summary>SHRUBLAND_TREE_GUARDIAN_1: the bark-warden roost writes its events here.</summary>
        public void Remember(string text)
        {
            if (Enabled)
            {
                AddHistory(text);
            }
        }

        private void AddHistory(string text)
        {
            Map m = parent.MapHeld;
            UnityEngine.Vector2 loc = m != null ? Find.WorldGrid.LongLatOf(m.Tile) : UnityEngine.Vector2.zero;
            string date = GenDate.DateFullStringAt(GenDate.TickGameToAbs(Find.TickManager.TicksGame), loc);
            history.Add(date + ": " + text);
            while (history.Count > Props.maxHistory)
            {
                history.RemoveAt(0);
            }
        }

        public override string TransformLabel(string label)
        {
            if (!Enabled || treeName.NullOrEmpty())
            {
                return label;
            }
            return treeName + " (" + label + ")";
        }

        public override string CompInspectStringExtra()
        {
            if (!Enabled || !Mature || Props.woolThing == null)
            {
                return null;
            }
            string visits = VisitorsOn && (campCount + pilgrimCount) > 0
                ? "Visitors remembered: " + campCount + " camps, " + pilgrimCount + " pilgrims.\n"
                : "";
            int left = nextWoolTick - Find.TickManager.TicksGame;
            if (left <= 0)
            {
                return visits + "Snagged " + Props.woolThing.label + " ready to shed.";
            }
            return visits + "Snagged " + Props.woolThing.label + " sheds in " + left.ToStringTicksToPeriod() + ".";
        }

        public override IEnumerable<Gizmo> CompGetGizmosExtra()
        {
            foreach (Gizmo g in base.CompGetGizmosExtra())
            {
                yield return g;
            }
            if (!Enabled || treeName.NullOrEmpty())
            {
                yield break;
            }
            yield return new Command_Action
            {
                defaultLabel = "History",
                defaultDesc = "What is remembered of " + treeName + ".",
                icon = TexCommand.Install,
                action = () =>
                {
                    StringBuilder sb = new StringBuilder();
                    sb.AppendLine(treeName);
                    sb.AppendLine();
                    if (history.Count == 0)
                    {
                        sb.AppendLine("Nothing remembered yet.");
                    }
                    for (int i = history.Count - 1; i >= 0; i--)
                    {
                        sb.AppendLine(history[i]);
                    }
                    Find.WindowStack.Add(new Dialog_MessageBox(sb.ToString().TrimEnd()));
                },
            };
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref treeName, "rmSweetlineName");
            Scribe_Values.Look(ref nextWoolTick, "rmSweetlineNextWool", -1);
            Scribe_Values.Look(ref nextVisitTick, "rmSweetlineNextVisit", -1);
            Scribe_Values.Look(ref campCount, "rmSweetlineCamps", 0);
            Scribe_Values.Look(ref pilgrimCount, "rmSweetlinePilgrims", 0);
            Scribe_Values.Look(ref lastStruckTick, "rmSweetlineLastStruck", -999999);
            Scribe_Values.Look(ref everMature, "rmSweetlineEverMature", false);
            Scribe_Collections.Look(ref history, "rmSweetlineHistory", LookMode.Value);
            if (Scribe.mode == LoadSaveMode.PostLoadInit && history == null)
            {
                history = new List<string>();
            }
        }
    }
}
