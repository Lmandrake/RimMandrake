using System.Collections.Generic;
using System.Linq;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.Noise;

namespace RimMandrake.Stillsand
{
    // ════════════════════════════════════════════════════════════════════
    // STILLSAND_DUNE_GALE_1 §10 — the dust devil. A fair-weather event, distinct from
    // the gale: one brief spinning column that wanders the flat, lifts light items,
    // scatters a stockpile, scours a little sand off whatever it crosses (a buried
    // cache shows for a moment), and spooks animals. It never damages anything and
    // leaves no Thing behind: it fades and destroys itself, or leaves over the edge.
    // Movement borrows vanilla Tornado's Perlin-steered walk at a slower pace.
    // ════════════════════════════════════════════════════════════════════
    public class RM_DustDevilExtension : DefModExtension
    {
        public IntRange durationTicks = new IntRange(900, 2400);
        public float cellsPerTick = 0.018f;
        public float scourRadius = 2.4f;
        public int effectIntervalTicks = 30;
        public float liftChance = 0.35f;
        /// <summary>Items of at most this mass per unit (kg) can be lifted.</summary>
        public float liftMaxMass = 2f;
        public IntRange liftCells = new IntRange(2, 5);
        public float scourDepthPerPass = 0.08f;
        public float spookRadius = 6f;
    }

    public class RM_DustDevil : ThingWithComps
    {
        private Vector2 realPosition;
        private float direction;
        private int spawnTick;
        private int ticksLeft = -1;
        private int fadeTicks = -1;

        private const int FadeTicks = 90;
        private static ModuleBase directionNoise;

        private RM_DustDevilExtension Ext => def.GetModExtension<RM_DustDevilExtension>() ?? DefaultExt;
        private static readonly RM_DustDevilExtension DefaultExt = new RM_DustDevilExtension();

        public override Vector3 DrawPos => new Vector3(realPosition.x, def.Altitude, realPosition.y);

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref realPosition, "realPosition");
            Scribe_Values.Look(ref direction, "direction");
            Scribe_Values.Look(ref spawnTick, "spawnTick");
            Scribe_Values.Look(ref ticksLeft, "ticksLeft", -1);
            Scribe_Values.Look(ref fadeTicks, "fadeTicks", -1);
        }

        public override void SpawnSetup(Map map, bool respawningAfterLoad)
        {
            base.SpawnSetup(map, respawningAfterLoad);
            if (!respawningAfterLoad)
            {
                Vector3 v = Position.ToVector3Shifted();
                realPosition = new Vector2(v.x, v.z);
                direction = Rand.Range(0f, 360f);
                spawnTick = Find.TickManager.TicksGame;
                ticksLeft = Ext.durationTicks.RandomInRange;
            }
        }

        protected override void Tick()
        {
            if (!Spawned)
            {
                return;
            }
            if (fadeTicks >= 0)
            {
                fadeTicks--;
                if (fadeTicks <= 0)
                {
                    Destroy();
                }
                return;
            }
            RM_DustDevilExtension ext = Ext;
            directionNoise ??= new Perlin(0.002, 2.0, 0.5, 4, 774411, QualityMode.Medium);
            direction += (float)directionNoise.GetValue(Find.TickManager.TicksAbs, thingIDNumber % 500 * 1000f, 0.0) * 1.1f;
            realPosition = realPosition.Moved(direction, ext.cellsPerTick);
            IntVec3 cell = new Vector3(realPosition.x, 0f, realPosition.y).ToIntVec3();
            if (!cell.InBounds(Map))
            {
                fadeTicks = FadeTicks; // left over the edge
                return;
            }
            Position = cell;
            if (this.IsHashIntervalTick(5))
            {
                Vector3 at = DrawPos + Vector3Utility.RandomHorizontalOffset(0.8f);
                FleckMaker.ThrowDustPuffThick(at, Map, Rand.Range(0.8f, 1.6f), new Color(0.84f, 0.7f, 0.46f, 0.7f));
            }
            if (this.IsHashIntervalTick(Mathf.Max(1, ext.effectIntervalTicks)))
            {
                Scour(ext);
            }
            if (--ticksLeft <= 0)
            {
                fadeTicks = FadeTicks;
            }
        }

        protected override void DrawAt(Vector3 drawLoc, bool flip = false)
        {
            // A small sway so the column reads as spinning, not sliding.
            float t = (Find.TickManager.TicksGame + thingIDNumber * 37) / 18f;
            drawLoc.x += Mathf.Sin(t) * 0.12f;
            base.DrawAt(drawLoc, flip);
        }

        private void Scour(RM_DustDevilExtension ext)
        {
            Map map = Map;
            List<Thing> lift = null;
            foreach (IntVec3 c in GenRadial.RadialCellsAround(Position, ext.scourRadius, true))
            {
                if (!c.InBounds(map) || c.Roofed(map))
                {
                    continue;
                }
                if (map.sandGrid != null && ext.scourDepthPerPass > 0f)
                {
                    float d = map.sandGrid.GetDepth(c);
                    if (d > 0f)
                    {
                        map.sandGrid.SetDepth(c, Mathf.Max(0f, d - ext.scourDepthPerPass));
                    }
                }
                List<Thing> things = c.GetThingList(map);
                for (int i = 0; i < things.Count; i++)
                {
                    Thing t = things[i];
                    if (t.def.category == ThingCategory.Item && t.def.EverHaulable
                        && t.GetStatValue(StatDefOf.Mass) <= ext.liftMaxMass && Rand.Chance(ext.liftChance))
                    {
                        (lift ??= new List<Thing>()).Add(t);
                    }
                }
            }
            if (lift != null)
            {
                foreach (Thing t in lift)
                {
                    if (!t.Spawned)
                    {
                        continue;
                    }
                    IntVec3 dest = t.Position + (Rand.InsideUnitCircle * ext.liftCells.RandomInRange).ToVector3().ToIntVec3();
                    if (!dest.InBounds(map) || !dest.Standable(map))
                    {
                        continue;
                    }
                    // SS-4: never lose the item. Lift it, try the landing spot, then the devil's cell; if both
                    // refuse, put it back exactly where it was (that cell was vacated a line ago, so it fits).
                    IntVec3 origin = t.Position;
                    t.DeSpawn();
                    if (!GenPlace.TryPlaceThing(t, dest, map, ThingPlaceMode.Near)
                        && !GenPlace.TryPlaceThing(t, Position, map, ThingPlaceMode.Near))
                    {
                        GenSpawn.Spawn(t, origin, map);
                    }
                }
            }
            foreach (Pawn p in map.mapPawns.AllPawnsSpawned)
            {
                if (p.IsAnimal && !p.Downed && p.Position.InHorDistOf(Position, ext.spookRadius)
                    && FleeUtility.ShouldAnimalFleeDanger(p) && p.CurJobDef != JobDefOf.Flee)
                {
                    p.mindState?.StartFleeingBecauseOfPawnAction(this);
                }
            }
        }
    }

    public class RM_IncidentWorker_DustDevil : IncidentWorker
    {
        public override float BaseChanceThisGame => base.BaseChanceThisGame * RM_DuneGaleSettings.dustDevilFrequency;

        protected override bool CanFireNowSub(IncidentParms parms)
        {
            if (!RM_DuneGaleSettings.dustDevilsEnabled || !(parms.target is Map map))
            {
                return false;
            }
            RM_DuneGaleIncidentExtension gate = def.GetModExtension<RM_DuneGaleIncidentExtension>();
            if (gate != null && !gate.Allows(map))
            {
                return false;
            }
            // Fair weather only: never in a gale or any weather that carries sand.
            if (map.weatherManager.SandRate > 0.001f || map.gameConditionManager.ActiveConditions.Any(c => c is RM_GameCondition_DuneGale))
            {
                return false;
            }
            return TryFindCell(map, out _);
        }

        private static bool TryFindCell(Map map, out IntVec3 cell)
        {
            return CellFinder.TryFindRandomCellNear(map.Center, map, Mathf.Min(map.Size.x, map.Size.z) / 2 - 10,
                c => c.Standable(map) && !c.Roofed(map) && !c.Fogged(map) && c.GetEdifice(map) == null, out cell);
        }

        protected override bool TryExecuteWorker(IncidentParms parms)
        {
            Map map = (Map)parms.target;
            if (!TryFindCell(map, out IntVec3 cell) || def.DustDevilDef() == null)
            {
                return false;
            }
            Thing devil = GenSpawn.Spawn(def.DustDevilDef(), cell, map);
            Messages.Message("A hiss rises off the flat: a dust devil.", devil, MessageTypeDefOf.NeutralEvent);
            return true;
        }
    }

    public class RM_DustDevilIncidentExtension : DefModExtension
    {
        public ThingDef dustDevil;
    }

    internal static class RM_DustDevilDefUtil
    {
        public static ThingDef DustDevilDef(this IncidentDef def)
        {
            return def.GetModExtension<RM_DustDevilIncidentExtension>()?.dustDevil;
        }
    }
}
