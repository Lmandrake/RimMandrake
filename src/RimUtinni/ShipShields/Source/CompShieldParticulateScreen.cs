using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.Utinni.ShipShields
{
    // Particulate/light-kinetic field (shd:particulate-screen). Finished this
    // session: alongside the filth sweep (v1), this now also repels small
    // wild animals and negates the one concrete vanilla mechanism that
    // matches "vapor, bio contamination... damage completely" -- airborne
    // Toxic Fallout exposure (HarmonyPatches.cs). Wind/ash/sand/smoke/rain
    // are NOT modeled as direct HP damage anywhere in vanilla RimWorld (they
    // only affect accuracy/move speed/mood), so there is no damage source
    // for those to negate; see the item file for the precise accounting.
    public class CompShieldParticulateScreen : ThingComp
    {
        private static readonly List<CompShieldParticulateScreen> ActiveScreens = new List<CompShieldParticulateScreen>();

        public CompProperties_ShieldParticulateScreen Props => (CompProperties_ShieldParticulateScreen)props;

        private CompShieldModuleSwitch ModuleSwitch => parent.GetComp<CompShieldModuleSwitch>();
        private CompPowerTrader PowerTrader => parent.GetComp<CompPowerTrader>();

        private bool IsLive =>
            parent.Spawned
            && (ModuleSwitch == null || ModuleSwitch.CurrentMode == ShieldFieldMode.Particulate)
            && (PowerTrader == null || PowerTrader.PowerOn);

        public override void PostSpawnSetup(bool respawningAfterLoad)
        {
            base.PostSpawnSetup(respawningAfterLoad);
            if (!ActiveScreens.Contains(this))
            {
                ActiveScreens.Add(this);
            }
        }

        public override void PostDeSpawn(Map map, DestroyMode mode = DestroyMode.Vanish)
        {
            ActiveScreens.Remove(this);
            base.PostDeSpawn(map, mode);
        }

        // Read by HarmonyPatches.cs's toxic-fallout prefixes. Cheap: a colony
        // carries at most a handful of these generators, never a per-tick
        // hot path over the whole map.
        public static bool IsPositionProtected(IntVec3 c, Map map)
        {
            if (!ShipShieldsSettings.particulateWeatherDamageNegationEnabled)
            {
                return false;
            }

            for (int i = 0; i < ActiveScreens.Count; i++)
            {
                CompShieldParticulateScreen screen = ActiveScreens[i];
                if (screen?.parent == null || screen.parent.Map != map || !screen.IsLive)
                {
                    continue;
                }

                if (c.DistanceTo(screen.parent.Position) <= screen.Props.radius)
                {
                    return true;
                }
            }

            return false;
        }

        public override void CompTick()
        {
            if (!parent.IsHashIntervalTick(Props.intervalTicks))
            {
                return;
            }

            if (!IsLive)
            {
                return;
            }

            Map map = parent.Map;
            if (map == null)
            {
                return;
            }

            if (ShipShieldsSettings.particulateScreenEnabled)
            {
                SweepFilth(map);
            }

            if (ShipShieldsSettings.particulateAnimalRepulsionEnabled)
            {
                RepelSmallAnimals(map);
            }
        }

        private void SweepFilth(Map map)
        {
            foreach (IntVec3 cell in GenRadial.RadialCellsAround(parent.Position, Props.radius, true))
            {
                if (!cell.InBounds(map))
                {
                    continue;
                }

                List<Thing> things = map.thingGrid.ThingsListAtFast(cell);
                for (int i = things.Count - 1; i >= 0; i--)
                {
                    if (things[i] is Filth filth && !filth.Destroyed)
                    {
                        filth.Destroy();
                    }
                }
            }
        }

        // shd:particulate-screen: "repels small animals". A real vanilla
        // Flee job (FleeUtility.FleeJob -> CellFinderLoose.GetFleeDest),
        // aimed away from this building as the "danger" -- the same
        // mechanism wildlife already uses to run from fire or a predator,
        // not a teleport or an invented mechanic.
        private void RepelSmallAnimals(Map map)
        {
            IReadOnlyList<Pawn> pawns = map.mapPawns.AllPawnsSpawned;
            for (int i = 0; i < pawns.Count; i++)
            {
                Pawn animal = pawns[i];
                if (!IsRepellableSmallAnimal(animal))
                {
                    continue;
                }

                if (animal.Position.DistanceTo(parent.Position) > Props.radius)
                {
                    continue;
                }

                if (animal.CurJob != null && animal.CurJob.def == JobDefOf.Flee && animal.CurJob.targetB.Thing == parent)
                {
                    continue;
                }

                Job fleeJob = FleeUtility.FleeJob(animal, parent, Props.smallAnimalFleeDistance);
                if (fleeJob != null)
                {
                    animal.jobs.StartJob(fleeJob, JobCondition.InterruptForced);
                }
            }
        }

        private bool IsRepellableSmallAnimal(Pawn p)
        {
            return p.Spawned
                && p.RaceProps != null
                && p.RaceProps.Animal
                && p.Faction != Faction.OfPlayer
                && !p.Downed
                && !p.Dead
                && p.BodySize <= Props.smallAnimalMaxBodySize;
        }
    }
}
