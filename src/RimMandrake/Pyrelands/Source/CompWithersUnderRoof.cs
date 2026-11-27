using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Pyrelands
{
    // Open-sky grass withers under a roof, visibly, at its own pace, and leaves dead grass (bar roofed_grass_declines_visibly,
    // owner 2026-11-26: "the grass just suddenly all dies at the same time ... it doesn't turn into dead grass, just... barren
    // nothing"). The rule is Kernel/RM_RoofWitherKernel.cs (T_ROOF_WITHER_OFFLINE drives it offline): each plant has its own death
    // time from its id and cell, loses hit points evenly up to it, and looks wilting, then withered (RM_RoofWitherLook).
    //
    // Never kill inside the plant's own tick: vanilla Plant.TickLong ticks the comps (base.TickLong) and then reads base.Map
    // (PlantUtility.GrowthSeasonNow, decompiled Plant.cs:832) with no Destroyed check, so 0.1.0's lethal TakeDamage here was
    // "Exception ticking RM_FE_Plant_EmberGrass". The lethal step goes to MapComponent_RM_RoofWither, which kills the plant on the
    // map's own tick and spawns Props.remainsDef (dead grass) on its cell.

    public class CompProperties_WithersUnderRoof : CompProperties
    {
        /// <summary>Roofed ticks at the middle of a patch's death window (RM_RoofWitherKernel.SpreadLo..SpreadHi of this).</summary>
        public int witherTicks = 60000;

        /// <summary>What a dead plant leaves on its cell: a dead-grass def (RM_DeadGrass).</summary>
        public ThingDef remainsDef;

        public CompProperties_WithersUnderRoof()
        {
            compClass = typeof(CompWithersUnderRoof);
        }

        public override IEnumerable<string> ConfigErrors(ThingDef parentDef)
        {
            foreach (string e in base.ConfigErrors(parentDef))
            {
                yield return e;
            }
            if (remainsDef == null)
            {
                yield return "CompProperties_WithersUnderRoof on " + parentDef.defName + " names no remainsDef: a roofed death would leave nothing";
            }
        }
    }

    public class CompWithersUnderRoof : ThingComp
    {
        private int roofedTicks;
        private int damageDealt;
        private int lookStage;
        private bool queued;

        public CompProperties_WithersUnderRoof Props => (CompProperties_WithersUnderRoof)props;

        /// <summary>The look the plant's graphic reads (RM_RoofWitherKernel.StageFresh .. StageWithered).</summary>
        public int LookStage => PyrelandsMechanicsGate.On ? lookStage : RM_RoofWitherKernel.StageFresh;

        public int RoofedTicks => roofedTicks;

        private bool Roofed => parent.Spawned && parent.Map != null && parent.Position.Roofed(parent.Map);

        public override void PostSpawnSetup(bool respawningAfterLoad)
        {
            base.PostSpawnSetup(respawningAfterLoad);
            lookStage = ReadStage();
        }

        private int ReadStage()
        {
            if (!parent.Spawned)
            {
                return RM_RoofWitherKernel.StageFresh;
            }
            int d = RM_RoofWitherKernel.DeathTicks(parent.thingIDNumber, parent.Position.x, parent.Position.z, Props.witherTicks);
            int s = RM_RoofWitherKernel.Stage(roofedTicks, d, true);
            return s == RM_RoofWitherKernel.StageDead ? RM_RoofWitherKernel.StageWithered : s;
        }

        public override void CompTickLong()
        {
            if (queued || !parent.Spawned)
            {
                return;
            }
            Map map = parent.Map;
            IntVec3 c = parent.Position;
            RM_RoofWitherKernel.Step s = RM_RoofWitherKernel.Advance(ref roofedTicks, ref damageDealt, parent.thingIDNumber, c.x, c.z,
                parent.MaxHitPoints, parent.HitPoints, Props.witherTicks, PyrelandsMechanicsGate.On, Roofed);
            if (s.Lethal)
            {
                queued = true;
                MapComponent_RM_RoofWither q = map.GetComponent<MapComponent_RM_RoofWither>();
                if (q != null)
                {
                    q.Queue(parent as Plant, Props.remainsDef);
                }
                return;
            }
            if (s.Damage > 0)
            {
                parent.TakeDamage(new DamageInfo(DamageDefOf.Rotting, s.Damage));
            }
            if (s.Stage != lookStage && s.Stage != RM_RoofWitherKernel.StageDead)
            {
                lookStage = s.Stage;
                map.mapDrawer.MapMeshDirty(c, MapMeshFlagDefOf.Things);
            }
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref roofedTicks, "rmRoofedTicks", 0);
            Scribe_Values.Look(ref damageDealt, "rmRoofDamage", 0);
        }

        public override string CompInspectStringExtra()
        {
            if (!PyrelandsMechanicsGate.On)
            {
                return null;
            }
            if (lookStage == RM_RoofWitherKernel.StageWithered)
            {
                return "RM_WitheredUnderRoof".Translate().Resolve();
            }
            if (lookStage == RM_RoofWitherKernel.StageWilting || Roofed)
            {
                return "RM_WithersUnderRoof".Translate().Resolve();
            }
            return null;
        }
    }

    /// <summary>Kills the plants a roof has finished, on the map's tick (never inside the plant's own), and leaves their remains.
    /// Not saved: a queued plant that outlives a save is still lethal at its next long tick and queues again.</summary>
    public class MapComponent_RM_RoofWither : MapComponent
    {
        private readonly List<Plant> plants = new List<Plant>();
        private readonly List<ThingDef> remains = new List<ThingDef>();

        public MapComponent_RM_RoofWither(Map map) : base(map)
        {
        }

        public void Queue(Plant plant, ThingDef remainsDef)
        {
            if (plant == null)
            {
                return;
            }
            plants.Add(plant);
            remains.Add(remainsDef);
        }

        public override void MapComponentTick()
        {
            if (plants.Count == 0)
            {
                return;
            }
            for (int i = 0; i < plants.Count; i++)
            {
                KillAndLeaveRemains(plants[i], remains[i], map);
            }
            plants.Clear();
            remains.Clear();
        }

        public static void KillAndLeaveRemains(Plant plant, ThingDef remainsDef, Map map)
        {
            if (plant == null || plant.Destroyed || !plant.Spawned || plant.Map != map)
            {
                return;
            }
            IntVec3 cell = plant.Position;
            float growth = plant.Growth;
            plant.Kill(null);
            if (remainsDef == null || !cell.InBounds(map))
            {
                return;
            }
            Thing left = GenSpawn.Spawn(remainsDef, cell, map);
            if (left is Plant dead)
            {
                dead.Growth = growth;
            }
        }
    }

    /// <summary>Dead grass: a dead plant (no growth, no dying, cuttable) that crumbles on its own clock wherever it lies, roofed or
    /// not (vanilla deterioration is zero under a roof in a closed room: StatPart_EnvironmentalEffects). Each one's end is spread
    /// like the deaths (RM_RoofWitherKernel.Crumble), so a patch does not vanish on one long tick either.</summary>
    public class RM_DeadGrassExtension : DefModExtension
    {
        public int crumbleTicks = 120000;
    }

    public class RM_DeadGrass : DeadPlant
    {
        private int crumbleAge;
        private int crumbleDealt;

        private int CrumbleTicks => def.GetModExtension<RM_DeadGrassExtension>()?.crumbleTicks ?? 120000;

        public override void TickLong()
        {
            base.TickLong();
            if (Destroyed || !Spawned)
            {
                return;
            }
            // After base.TickLong() has returned: a kill here is a kill at the end of the plant's own tick, as vanilla's dying
            // damage at the end of Plant.TickLong is.
            RM_RoofWitherKernel.Step s = RM_RoofWitherKernel.Crumble(ref crumbleAge, ref crumbleDealt, thingIDNumber, Position.x,
                Position.z, MaxHitPoints, HitPoints, CrumbleTicks);
            if (s.Lethal)
            {
                Kill(null);
                return;
            }
            if (s.Damage > 0)
            {
                TakeDamage(new DamageInfo(DamageDefOf.Deterioration, s.Damage));
            }
        }

        public override string GetInspectString()
        {
            int left = RM_RoofWitherKernel.CrumbleTicksLeft(crumbleAge, thingIDNumber, Position.x, Position.z, CrumbleTicks);
            return "DeteriorateInDuration".Translate(left.ToStringTicksToPeriod()).Resolve();
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref crumbleAge, "rmCrumbleAge", 0);
            Scribe_Values.Look(ref crumbleDealt, "rmCrumbleDealt", 0);
        }
    }

    /// <summary>The wilting and withered look: the plant's own graphic, tinted (GetColoredVersion, as ExplosiveGrowth's hue shift
    /// does; only Graphic_Single and Graphic_Random support it, anything else stays untinted). No new art.</summary>
    public static class RM_RoofWitherLook
    {
        // Invented colours (our own rule), to be judged live by sc_roofed_grass_declines: a drying yellow, then a dead brown.
        private static readonly Color Wilting = new Color(0.92f, 0.84f, 0.58f);
        private static readonly Color Withered = new Color(0.70f, 0.58f, 0.42f);

        private static readonly Dictionary<(Graphic, int), Graphic> cache = new Dictionary<(Graphic, int), Graphic>();

        public static Graphic Apply(Plant plant, Graphic g)
        {
            if (g == null || plant == null)
            {
                return g;
            }
            CompWithersUnderRoof comp = plant.TryGetComp<CompWithersUnderRoof>();
            if (comp == null)
            {
                return g;
            }
            int stage = comp.LookStage;
            if (stage != RM_RoofWitherKernel.StageWilting && stage != RM_RoofWitherKernel.StageWithered)
            {
                return g;
            }
            if (!(g is Graphic_Random) && !(g is Graphic_Single))
            {
                return g;
            }
            var key = (g, stage);
            if (!cache.TryGetValue(key, out Graphic tinted))
            {
                Color tint = stage == RM_RoofWitherKernel.StageWilting ? Wilting : Withered;
                tinted = g.GetColoredVersion(g.Shader, g.color * tint, g.colorTwo * tint);
                cache[key] = tinted;
            }
            return tinted;
        }
    }

    /// <summary>Ember grass's thing class: vanilla Plant, its graphic through RM_RoofWitherLook.</summary>
    public class RM_Plant_WithersUnderRoof : Plant
    {
        public override Graphic Graphic => RM_RoofWitherLook.Apply(this, base.Graphic);
    }
}
