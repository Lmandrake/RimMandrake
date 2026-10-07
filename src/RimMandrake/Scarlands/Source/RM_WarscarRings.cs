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
        // true on the two world-placed rings (dead/live); false on the player-installable salvaged ring.
        public bool wild;
        public RM_CompProperties_WarscarRing() { compClass = typeof(RM_CompWarscarRing); }
    }

    public class RM_CompWarscarRing : RM_CompAerosolScreen
    {
        public const float WakeRange = RM_RingKernel.WakeRange;
        private bool wakeCached;

        // Part 7: condition rolled at generation, saved, revealed by the evaluate job.
        private int cond = -1;
        private bool evaluated;

        public RingCondition Condition => RM_RingKernel.Effective(cond);
        public bool Evaluated => evaluated;
        public void SetCondition(RingCondition c, bool isEvaluated) { cond = (int)c; evaluated = isEvaluated; }
        public void Evaluate() { evaluated = true; }
        public static string ConditionLabel(RingCondition c) { return c == RingCondition.Dead ? "dead" : c == RingCondition.Failing ? "failing" : "working"; }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref cond, "ringCond", -1);
            Scribe_Values.Look(ref evaluated, "ringEvaluated", false);
        }

        private void RollIfNeeded()
        {
            if (cond >= 0) return;
            // Dead def: always dead. Live def: 70% working, 30% failing. The first ring of a map is forced Working by the genstep.
            cond = RingProps.dead ? (int)RingCondition.Dead : RM_RingKernel.RollLive(Rand.Value);
        }

        public RM_CompProperties_WarscarRing RingProps => (RM_CompProperties_WarscarRing)props;

        public bool Woken => wakeCached;

        public override bool IsScreenLive
        {
            get
            {
                return RM_RingKernel.IsScreenLive(RingProps.dead, !RingProps.dead && base.IsScreenLive, Condition,
                    RM_WarscarSettings.shipWakesLine, wakeCached, parent.Spawned);
            }
        }

        public override void PostSpawnSetup(bool respawningAfterLoad)
        {
            base.PostSpawnSetup(respawningAfterLoad);
            RollIfNeeded();
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
            for (int i = 0; i < engines.Count; i++)
                if (engines[i].Spawned && RM_RingKernel.EngineWakes(engines[i].Position.x, engines[i].Position.z, parent.Position.x, parent.Position.z)) return true;
            return false;
        }

        public override string CompInspectStringExtra()
        {
            string cs = evaluated ? "condition: " + ConditionLabel(Condition) : "condition: unassessed (evaluation needs Crafting 6)";
            if (RingProps.dead && !IsScreenLive)
                return "Projector ring (" + cs + "), no hum" + (RM_WarscarSettings.shipWakesLine ? "; a landed gravship's engine would wake it" : "");
            if (RingProps.dead) return "Projector ring (" + cs + "), woken by the ship's engine; it will go dark when the ship lifts. " + base.CompInspectStringExtra();
            if (Condition == RingCondition.Failing) return "Projector ring (" + cs + "): the dome stutters and does not hold." + (RingProps.wild ? "" : " Needs repair.");
            return "Projector ring (" + cs + "): humming. " + base.CompInspectStringExtra();
        }

        public override IEnumerable<Gizmo> CompGetGizmosExtra()
        {
            foreach (Gizmo g in base.CompGetGizmosExtra()) yield return g;
            if (!parent.Spawned) yield break;
            if (RingProps.wild && RM_RingKernel.CanEvaluate(evaluated))
                yield return Toggle(RM_RingDesignations.Evaluate, "Evaluate ring", "Have someone with Crafting 6 work out this ring's true condition.");
            if (RM_WarscarSettings.ringSalvageEnabled && RM_RingKernel.CanSalvage(evaluated, RingProps.wild))
                yield return Toggle(RM_RingDesignations.Salvage,
                    Condition == RingCondition.Dead ? "Strip ring" : "Uninstall ring",
                    Condition == RingCondition.Dead ? "Break the dead ring down for steel, components and perhaps a projector core."
                        : "Take the ring up and haul it home. A working ring ends its dome here when it comes out.");
            if (RM_WarscarSettings.ringSalvageEnabled && !RingProps.dead && RM_RingKernel.CanRepair(RingProps.wild, Condition))
                yield return Toggle(RM_RingDesignations.Repair, "Repair ring", "Needs 2 industrial components and Crafting 8.");
        }

        private Command_Action Toggle(DesignationDef def, string label, string desc)
        {
            DesignationManager dm = parent.Map.designationManager;
            bool on = dm.DesignationOn(parent, def) != null;
            return new Command_Action
            {
                defaultLabel = on ? "Cancel: " + label : label,
                defaultDesc = desc,
                icon = ContentFinder<Texture2D>.Get("UI/Designators/Deconstruct", false),
                action = delegate
                {
                    Designation d = dm.DesignationOn(parent, def);
                    if (d != null) dm.RemoveDesignation(d); else dm.AddDesignation(new Designation(parent, def));
                }
            };
        }

        // Salvage of a wild ring (called by the job when work completes).
        // Dead: strip for steel, components, and a core by chance (projectorCoreChance).
        // Working/Failing: becomes the minified salvaged ring carrying the same condition.
        public void DoSalvage(Pawn by)
        {
            Map map = parent.Map;
            IntVec3 pos = parent.Position;
            RingCondition c = Condition;
            parent.Destroy(DestroyMode.Vanish);
            if (RM_RingKernel.Salvage(c) == SalvageResult.Strip)
            {
                Drop(ThingDefOf.Steel, Rand.RangeInclusive(30, 60), pos, map);
                Drop(ThingDefOf.ComponentIndustrial, Rand.RangeInclusive(1, 3), pos, map);
                if (Rand.Chance(RM_WarscarSettings.projectorCoreChance))
                {
                    ThingDef core = DefDatabase<ThingDef>.GetNamedSilentFail("RM_ProjectorCore");
                    if (core != null) Drop(core, 1, pos, map);
                }
                return;
            }
            ThingDef salvaged = DefDatabase<ThingDef>.GetNamedSilentFail("RM_WarscarProjector_Salvaged");
            if (salvaged == null) return;
            Thing ring = ThingMaker.MakeThing(salvaged);
            RM_CompWarscarRing rc = ring.TryGetComp<RM_CompWarscarRing>();
            if (rc != null) rc.SetCondition(RM_RingKernel.SalvagedCondition(c), true);
            MinifiedThing mini = MinifyUtility.MakeMinified(ring);
            GenPlace.TryPlaceThing(mini, pos, map, ThingPlaceMode.Near);
        }

        public static void Drop(ThingDef def, int n, IntVec3 pos, Map map)
        {
            Thing t = ThingMaker.MakeThing(def);
            t.stackCount = n;
            GenPlace.TryPlaceThing(t, pos, map, ThingPlaceMode.Near);
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
                ThingDef def = (n == 0 || Rand.Chance(RM_RingKernel.LiveSpawnChance)) ? live : dead;
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
                    Thing ring = GenSpawn.Spawn(ThingMaker.MakeThing(def), c, map);
                    if (RM_RingKernel.FirstLiveForcedWorking(n, def == live)) ring.TryGetComp<RM_CompWarscarRing>()?.SetCondition(RingCondition.Working, false);
                    placed.Add(c);
                    break;
                }
            }
        }
    }
}
