using System;
using System.Collections.Generic;
using System.Linq;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.Sound;

namespace RimMandrake.Pyrelands
{
    // PYRELANDS_LIGHTNING_BREAKER_BUILD_1 (design/Jawa/worldbuilding/biomes/pyrelands_bedazzle_review_2026-10-01.md §5).
    // Owner, typed: "The Lightning breakers is a neat idea. They should be made of metal and sand in a recipe in the
    // forge. Only learnable here because of the frequent lightning and sandy soil. Desert sand works just fine too
    // once you know how".
    //
    // The engine (RimSage-read, decompiled 1.6): every short circuit goes through ShortCircuitUtility.DoShortCircuit
    // (Building culprit), which drains EVERY battery on the culprit's PowerNet into one explosion. A breaker is a
    // power-transmitting building; when the fault's section of the grid (walked cell by cell from the culprit,
    // stopping at armed breakers) holds fewer batteries than the whole net, every armed breaker on that boundary
    // trips: it stops transmitting (the net splits, like a switched-off power switch), spends tripCost glass sand
    // from its hopper, and only the faulted section's batteries discharge. The rest of the grid stays live.
    public class RM_LightningBreaker : Building
    {
        public bool tripped;
        public int trips;
        private Graphic trippedGraphic;

        public CompRefuelable Hopper => GetComp<CompRefuelable>();

        public bool Armed => RM_BreakerKernel.Armed(tripped, RM_PyrelandsSettings.lightningBreakerEnabled, Hopper != null,
            Hopper != null ? Hopper.Fuel : 0f, RM_PyrelandsSettings.breakerTripCost);

        public override bool TransmitsPowerNow => !tripped;

        public override Graphic Graphic
        {
            get
            {
                if (!tripped)
                {
                    return base.Graphic;
                }
                if (trippedGraphic == null)
                {
                    trippedGraphic = GraphicDatabase.Get(def.graphicData.graphicClass, def.graphicData.texPath + "_Off",
                        def.graphicData.shaderType.Shader, def.graphicData.drawSize, DrawColor, DrawColorTwo);
                }
                return trippedGraphic;
            }
        }

        public void Trip()
        {
            if (tripped)
            {
                return;
            }
            tripped = true;
            trips++;
            Hopper?.ConsumeFuel(RM_PyrelandsSettings.breakerTripCost);
            NotifyGrid();
            if (Spawned)
            {
                DefDatabase<SoundDef>.GetNamedSilentFail("Thunder_OnMap")?.PlayOneShot(new TargetInfo(Position, Map));
                FleckMaker.ThrowMicroSparks(DrawPos, Map);
                FleckMaker.ThrowLightningGlow(DrawPos, Map, 1.5f);
            }
        }

        public void Rearm()
        {
            if (!tripped)
            {
                return;
            }
            tripped = false;
            NotifyGrid();
            if (Spawned)
            {
                SoundDefOf.FlickSwitch.PlayOneShot(new TargetInfo(Position, Map));
            }
        }

        private void NotifyGrid()
        {
            if (Spawned)
            {
                Map.powerNetManager.Notfiy_TransmitterTransmitsPowerNowChanged(PowerComp);
                Map.mapDrawer.MapMeshDirty(Position, (ulong)MapMeshFlagDefOf.Buildings | (ulong)MapMeshFlagDefOf.Things);
            }
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref tripped, "tripped");
            Scribe_Values.Look(ref trips, "trips");
        }

        public override IEnumerable<Gizmo> GetGizmos()
        {
            foreach (Gizmo g in base.GetGizmos())
            {
                yield return g;
            }
            if (Faction == Faction.OfPlayer && tripped)
            {
                yield return new Command_Action
                {
                    defaultLabel = "Re-arm breaker",
                    defaultDesc = "Close the breaker again and reconnect the two sides of the grid. Fix whatever faulted first: it will trip again only if its hopper holds enough glass sand.",
                    icon = ContentFinder<Texture2D>.Get("UI/Commands/DesirePower"),
                    action = Rearm,
                };
            }
        }

        public override string GetInspectString()
        {
            string s = base.GetInspectString();
            string mine = tripped
                ? "TRIPPED: the grid is split here. Re-arm once the fault is fixed."
                : Armed ? "Armed: a short circuit on one side trips it and spares the other side's batteries."
                        : "Not armed: needs " + RM_PyrelandsSettings.breakerTripCost + " glass sand in its hopper (or breakers are off in Mod Settings).";
            if (trips > 0)
            {
                mine += "\nTripped " + trips + " time(s).";
            }
            return s.NullOrEmpty() ? mine : s + "\n" + mine;
        }
    }

    public class RM_BreakerTripReport
    {
        public List<RM_LightningBreaker> tripped = new List<RM_LightningBreaker>();
        public List<CompPowerBattery> lost = new List<CompPowerBattery>();
        public List<CompPowerBattery> protectedBatteries = new List<CompPowerBattery>();
    }

    public static class RM_LightningBreakerUtility
    {
        /// <summary>
        /// Walks the culprit's grid section: from its transmitter, through cardinally adjacent transmitters of the
        /// same net, never through an armed breaker (those are the boundary). Null when no armed breaker separates
        /// any battery from the fault (then vanilla runs untouched).
        /// </summary>
        public static RM_BreakerTripReport Plan(Building culprit)
        {
            CompPower start = culprit?.PowerComp;
            PowerNet net = start?.PowerNet;
            Map map = culprit?.Map;
            if (net == null || map == null || !RM_PyrelandsSettings.lightningBreakerEnabled)
            {
                return null;
            }
            if (!start.Props.transmitsPower && start.connectParent != null)
            {
                start = start.connectParent;
            }
            var inNet = new HashSet<CompPower>(net.transmitters);
            RM_BreakerKernel.Section(start, cur => AdjacentPower(cur, map), c => inNet.Contains(c),
                c => c.parent is RM_LightningBreaker br && br.Armed,
                out HashSet<CompPower> visited, out HashSet<CompPower> boundary);
            if (boundary.Count == 0)
            {
                return null;
            }
            var report = new RM_BreakerTripReport { tripped = boundary.Select(c => (RM_LightningBreaker)c.parent).ToList() };
            foreach (CompPowerBattery b in net.batteryComps)
            {
                bool inSection = RM_BreakerKernel.InSection(visited, (CompPower)b, b.connectParent != null, b.connectParent);
                (inSection ? report.lost : report.protectedBatteries).Add(b);
            }
            return RM_BreakerKernel.WorthTripping(report.tripped.Count, report.protectedBatteries.Count) ? report : null;
        }

        /// <summary>Every power comp on a cell edge-adjacent to the building (the node's neighbours in the net).</summary>
        private static IEnumerable<CompPower> AdjacentPower(CompPower cur, Map map)
        {
            foreach (IntVec3 cell in cur.parent.OccupiedRect())
            {
                for (int d = 0; d < 4; d++)
                {
                    IntVec3 n = cell + GenAdj.CardinalDirections[d];
                    if (!n.InBounds(map))
                    {
                        continue;
                    }
                    List<Thing> things = n.GetThingList(map);
                    for (int i = 0; i < things.Count; i++)
                    {
                        CompPower pc = (things[i] as ThingWithComps)?.GetComp<CompPower>();
                        if (pc != null)
                        {
                            yield return pc;
                        }
                    }
                }
            }
        }

        private static readonly Func<Building, bool> TryStartFireNear =
            AccessTools.MethodDelegate<Func<Building, bool>>(AccessTools.Method(typeof(ShortCircuitUtility), "TryStartFireNear"));

        /// <summary>The breaker's version of DoShortCircuit: trip the boundary, discharge only the faulted section.</summary>
        public static void Execute(Building culprit, RM_BreakerTripReport report)
        {
            Map map = culprit.Map;
            IntVec3 at = culprit.Position;
            string label = culprit.def == ThingDefOf.PowerConduit ? "an electrical conduit" : Find.ActiveLanguageWorker.WithIndefiniteArticlePostProcessed(culprit.Label);
            float lostEnergy = report.lost.Sum(b => b.StoredEnergy);
            float keptEnergy = report.protectedBatteries.Sum(b => b.StoredEnergy);
            foreach (RM_LightningBreaker br in report.tripped)
            {
                br.Trip();
            }
            bool fire = false;
            if (RM_BreakerKernel.LostCanBlast(report.lost.Select(b => b.StoredEnergy)))
            {
                foreach (CompPowerBattery b in report.lost)
                {
                    b.DrawPower(b.StoredEnergy);
                }
                float radius = RM_BreakerKernel.BlastRadius(lostEnergy);
                GenExplosion.DoExplosion(at, map, radius, DamageDefOf.Flame, null);
                if (RM_BreakerKernel.SecondBlast(radius))
                {
                    GenExplosion.DoExplosion(at, map, radius * 0.3f, DamageDefOf.Bomb, null);
                }
            }
            else
            {
                fire = TryStartFireNear != null && TryStartFireNear(culprit);
            }
            string text = "A short circuit in " + label + (fire ? " started a fire" : "") + ", and the lightning breaker"
                          + (report.tripped.Count > 1 ? "s" : "") + " tripped with a crack.\n\n"
                          + "Lost: " + lostEnergy.ToString("F0") + " Wd from " + report.lost.Count + " batter" + (report.lost.Count == 1 ? "y" : "ies")
                          + " on the faulted side.\nProtected: " + report.protectedBatteries.Count + " batter"
                          + (report.protectedBatteries.Count == 1 ? "y" : "ies") + " holding " + keptEnergy.ToString("F0")
                          + " Wd beyond the breaker, still powering that side.\n\nRe-arm the breaker once the fault is fixed.";
            Find.LetterStack.ReceiveLetter("Breaker tripped", text, LetterDefOf.NegativeEvent,
                new LookTargets(report.tripped.Cast<Thing>().Concat(new[] { (Thing)culprit })));
        }
    }

    [StaticConstructorOnStartup]
    public static class Patch_ShortCircuit_LightningBreaker
    {
        static Patch_ShortCircuit_LightningBreaker()
        {
            try
            {
                var h = new Harmony("mandrake.rm.pyrelands.lightningbreaker");
                h.Patch(AccessTools.Method(typeof(ShortCircuitUtility), nameof(ShortCircuitUtility.DoShortCircuit)),
                    prefix: new HarmonyMethod(typeof(Patch_ShortCircuit_LightningBreaker), nameof(Prefix)));
                h.Patch(AccessTools.PropertyGetter(typeof(ResearchProjectDef), nameof(ResearchProjectDef.CanStartNow)),
                    postfix: new HarmonyMethod(typeof(Patch_ShortCircuit_LightningBreaker), nameof(CanStartNowPostfix)));
                RM_LightningBreakerRecipeCost.Apply();
            }
            catch (Exception e)
            {
                Log.Error("[RimMandrake.Pyrelands] lightning breaker failed to patch: " + e);
            }
        }

        public static bool Prefix(Building culprit)
        {
            RM_BreakerTripReport report;
            try
            {
                report = RM_LightningBreakerUtility.Plan(culprit);
            }
            catch (Exception e)
            {
                Log.WarningOnce("[RimMandrake.Pyrelands] lightning breaker plan failed, vanilla short circuit runs: " + e.Message, 0x4C1B7EA);
                return true;
            }
            if (report == null)
            {
                return true;
            }
            RM_LightningBreakerUtility.Execute(culprit, report);
            return false;
        }

        /// <summary>A project carrying RM_PyrelandsOnlyResearch cannot be begun without a home on a Pyrelands map.</summary>
        public static void CanStartNowPostfix(ResearchProjectDef __instance, ref bool __result)
        {
            if (!__result || !RM_PyrelandsSettings.breakerPyrelandsOnly || __instance.ProgressReal > 0f
                || !__instance.HasModExtension<RM_PyrelandsOnlyResearch>())
            {
                return;
            }
            __result = RM_PyrelandsOnlyResearch.PlayerHoldsPyrelands();
        }
    }

    public class RM_PyrelandsOnlyResearch : DefModExtension
    {
        public static bool PlayerHoldsPyrelands()
        {
            List<Map> maps = Find.Maps;
            for (int i = 0; i < maps.Count; i++)
            {
                if (maps[i].IsPlayerHome && maps[i].Biome?.defName == "RM_Pyrelands")
                {
                    return true;
                }
            }
            return false;
        }
    }

    /// <summary>Mod Settings "recipe cost": scales the breaker core recipe's ingredient counts once at startup.</summary>
    public static class RM_LightningBreakerRecipeCost
    {
        public static void Apply()
        {
            RecipeDef r = DefDatabase<RecipeDef>.GetNamedSilentFail("RM_Make_LightningBreakerCore");
            if (r == null || Mathf.Approximately(RM_PyrelandsSettings.breakerRecipeCostFactor, 1f))
            {
                return;
            }
            foreach (IngredientCount ing in r.ingredients)
            {
                ing.SetBaseCount(Mathf.Max(1f, Mathf.Round(ing.GetBaseCount() * RM_PyrelandsSettings.breakerRecipeCostFactor)));
            }
        }
    }

    /// <summary>Dev proofs, called through jawa/static_call.</summary>
    public static class RM_LightningBreakerProof
    {
        /// <summary>
        /// Builds a two-section grid on the current map (battery A - conduit - breaker - conduit - battery B), charges
        /// both, forces a short circuit on A's conduit, and reports what tripped and what kept its charge.
        /// </summary>
        public static string ProofTrip(string unused)
        {
            Map map = Find.CurrentMap;
            ThingDef breakerDef = DefDatabase<ThingDef>.GetNamedSilentFail("RM_LightningBreaker");
            ThingDef battery = DefDatabase<ThingDef>.GetNamedSilentFail("Battery");
            if (map == null || breakerDef == null || battery == null)
            {
                return "UNMEASURED no map or no RM_LightningBreaker/Battery def";
            }
            IntVec3 origin = IntVec3.Invalid;
            foreach (IntVec3 c in GenRadial.RadialCellsAround(map.Center, 30f, true))
            {
                CellRect r = new CellRect(c.x, c.z, 9, 4);
                if (r.InBounds(map) && r.Cells.All(x => x.Standable(map) && x.GetFirstBuilding(map) == null && x.GetFirstItem(map) == null))
                {
                    origin = c;
                    break;
                }
            }
            if (!origin.IsValid)
            {
                return "UNMEASURED no clear 9x4 area near the map centre";
            }
            Thing Spawn(ThingDef d, int dx, int dz)
            {
                Thing t = ThingMaker.MakeThing(d, d.MadeFromStuff ? GenStuff.DefaultStuffFor(d) : null);
                t.SetFaction(Faction.OfPlayer);
                return GenSpawn.Spawn(t, origin + new IntVec3(dx, 0, dz), map);
            }
            Building batA = (Building)Spawn(battery, 0, 0);
            Building culprit = (Building)Spawn(ThingDefOf.PowerConduit, 1, 0);
            Spawn(ThingDefOf.PowerConduit, 2, 0);
            var breaker = (RM_LightningBreaker)Spawn(breakerDef, 3, 0);
            breaker.Hopper?.Refuel(30f);
            Spawn(ThingDefOf.PowerConduit, 4, 0);
            Spawn(ThingDefOf.PowerConduit, 5, 0);
            Building batB = (Building)Spawn(battery, 6, 0);
            map.powerNetManager.UpdatePowerNetsAndConnections_First();
            CompPowerBattery a = batA.GetComp<CompPowerBattery>(), b = batB.GetComp<CompPowerBattery>();
            a.SetStoredEnergyPct(1f);
            b.SetStoredEnergyPct(1f);
            bool oneNet = a.PowerNet == b.PowerNet;
            float fuelBefore = breaker.Hopper?.Fuel ?? -1f;
            ShortCircuitUtility.DoShortCircuit(culprit);
            map.powerNetManager.UpdatePowerNetsAndConnections_First();
            string result = string.Format("TRIP oneNetBefore={0} tripped={1} storedA={2:0} storedB={3:0} splitAfter={4} fuel={5:0}->{6:0}",
                oneNet, breaker.tripped, a.StoredEnergy, b.StoredEnergy, a.PowerNet != b.PowerNet, fuelBefore, breaker.Hopper?.Fuel ?? -1f);
            return result;
        }

        /// <summary>Reports whether a gated project can start now and whether the player holds a Pyrelands home.</summary>
        public static string ProofGate(string projectDefName)
        {
            ResearchProjectDef p = DefDatabase<ResearchProjectDef>.GetNamedSilentFail(projectDefName);
            if (p == null)
            {
                return "UNMEASURED no research project " + projectDefName;
            }
            return string.Format("GATE canStart={0} holdsPyrelands={1} gated={2} prereqsDone={3} finished={4}",
                p.CanStartNow, RM_PyrelandsOnlyResearch.PlayerHoldsPyrelands(), p.HasModExtension<RM_PyrelandsOnlyResearch>(),
                p.PrerequisitesCompleted, p.IsFinished);
        }
    }
}
