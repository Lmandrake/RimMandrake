using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Scarlands
{
    // WARSCAR_AEROSOL_SCREEN_1 parts 6 and 8: the old-line projector rings.
    //  * RM_WarscarProjector_Live hums on its own (needsPower=false) and is the analysable ring that unlocks
    //    RM_AerosolScreenResearch. Analysis never consumes it (CompAnalyzable.OnAnalyzed only destroys the parent
    //    when destroyedOnAnalyzed is true; the defs set it false).
    //  * RM_WarscarProjector_Dead is silent until a landed gravship's GravEngine is within WakeRange cells
    //    (spec 8, gated by shipWakesLine); the live dome and the analysable state follow the ship and end when it lifts.

    public class RM_CompProperties_WarscarRing : RM_CompProperties_AerosolScreen
    {
        public bool dead;
        public RM_CompProperties_WarscarRing() { compClass = typeof(RM_CompWarscarRing); }
    }

    public class RM_CompWarscarRing : RM_CompAerosolScreen
    {
        public const float WakeRange = 40f;
        private bool wakeCached;

        public RM_CompProperties_WarscarRing RingProps => (RM_CompProperties_WarscarRing)props;

        public bool Woken => wakeCached;

        public override bool IsScreenLive
        {
            get
            {
                if (!RingProps.dead) return base.IsScreenLive;
                return RM_WarscarSettings.shipWakesLine && wakeCached && parent.Spawned;
            }
        }

        public override void PostSpawnSetup(bool respawningAfterLoad)
        {
            base.PostSpawnSetup(respawningAfterLoad);
            if (RingProps.dead) wakeCached = ComputeWake();
        }

        public override void CompTickRare()
        {
            base.CompTickRare();
            if (RingProps.dead) wakeCached = ComputeWake();
        }

        private bool ComputeWake()
        {
            if (!RM_WarscarSettings.shipWakesLine || !parent.Spawned) return false;
            Map map = parent.Map;
            ThingDef engine = ThingDefOf.GravEngine;
            if (engine == null) return false;
            List<Thing> engines = map.listerThings.ThingsOfDef(engine);
            float r2 = WakeRange * WakeRange;
            for (int i = 0; i < engines.Count; i++)
                if (engines[i].Spawned && engines[i].Position.DistanceToSquared(parent.Position) <= r2) return true;
            return false;
        }

        public override string CompInspectStringExtra()
        {
            if (RingProps.dead && !IsScreenLive)
                return "Projector ring: dead, no hum" + (RM_WarscarSettings.shipWakesLine ? " (a landed gravship's engine would wake it)" : "");
            if (RingProps.dead) return "Projector ring: woken by the ship's engine; it will go dark when the ship lifts. " + base.CompInspectStringExtra();
            return "Projector ring: humming. " + base.CompInspectStringExtra();
        }
    }

    // Analysis only while the ring is humming, so a dead ring cannot be studied until the ship wakes it.
    // Dead and live ring defs share one analysisID, so progress is one pool.
    public class RM_CompProperties_RingAnalyzable : CompProperties_CompAnalyzableUnlockResearch
    {
        public RM_CompProperties_RingAnalyzable() { compClass = typeof(RM_CompRingAnalyzable); }
    }

    public class RM_CompRingAnalyzable : CompAnalyzableUnlockResearch
    {
        public override AcceptanceReport CanInteract(Pawn activateBy = null, bool checkOptionalItems = true)
        {
            RM_CompAerosolScreen screen = parent.GetComp<RM_CompAerosolScreen>();
            if (screen != null && !screen.IsScreenLive) return "The ring is dead; nothing to read.";
            return base.CanInteract(activateBy, checkOptionalItems);
        }
    }

    // Rings along the outer edge of the Odyssey ruins (centroid and farthest wall of AncientFortifiedWall,
    // else the map centre). Count comes from hummingRingsPerMap (0-3): the first is always live, the rest 40%.
    public class GenStep_WarscarRings : GenStep
    {
        public override int SeedPart { get { return 84921913; } }

        public override void Generate(Map map, GenStepParams parms)
        {
            int count = Mathf.Clamp(RM_WarscarSettings.hummingRingsPerMap, 0, 3);
            if (count == 0) return;
            ThingDef live = DefDatabase<ThingDef>.GetNamedSilentFail("RM_WarscarProjector_Live");
            ThingDef dead = DefDatabase<ThingDef>.GetNamedSilentFail("RM_WarscarProjector_Dead");
            if (live == null || dead == null) return;

            Vector3 centre = map.Center.ToVector3Shifted();
            float outer = 20f;
            ThingDef wallDef = DefDatabase<ThingDef>.GetNamedSilentFail("AncientFortifiedWall");
            if (wallDef != null)
            {
                List<Thing> walls = map.listerThings.ThingsOfDef(wallDef);
                if (walls.Count >= 6)
                {
                    float sx = 0f, sz = 0f;
                    for (int i = 0; i < walls.Count; i++) { sx += walls[i].Position.x; sz += walls[i].Position.z; }
                    centre = new Vector3(sx / walls.Count + 0.5f, 0f, sz / walls.Count + 0.5f);
                    outer = 0f;
                    for (int i = 0; i < walls.Count; i++)
                        outer = Mathf.Max(outer, Mathf.Sqrt((walls[i].Position.x - centre.x) * (walls[i].Position.x - centre.x) + (walls[i].Position.z - centre.z) * (walls[i].Position.z - centre.z)));
                }
            }

            List<IntVec3> placed = new List<IntVec3>();
            for (int n = 0; n < count; n++)
            {
                ThingDef def = (n == 0 || Rand.Chance(0.4f)) ? live : dead;
                for (int attempt = 0; attempt < 200; attempt++)
                {
                    float a = Rand.Range(0f, 360f) * Mathf.Deg2Rad;
                    float d = outer + Rand.Range(2f, 6f);
                    IntVec3 c = new IntVec3(Mathf.RoundToInt(centre.x + d * Mathf.Cos(a)), 0, Mathf.RoundToInt(centre.z + d * Mathf.Sin(a)));
                    if (!c.InBounds(map)) continue;
                    bool near = false;
                    for (int i = 0; i < placed.Count; i++) if (placed[i].DistanceTo(c) < 15f) near = true;
                    if (near) continue;
                    CellRect rect = GenAdj.OccupiedRect(c, Rot4.North, def.size);
                    bool ok = rect.InBounds(map);
                    if (ok)
                        foreach (IntVec3 cell in rect)
                            if (!cell.Standable(map) || cell.GetEdifice(map) != null || cell.GetFirstItem(map) != null) { ok = false; break; }
                    if (!ok) continue;
                    GenSpawn.Spawn(ThingMaker.MakeThing(def), c, map);
                    placed.Add(c);
                    break;
                }
            }
        }
    }
}
