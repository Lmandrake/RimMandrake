using System.Collections.Generic;
using System.Linq;
using RimMandrake.CreatureBehaviors;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Cauldron
{
    // RHOSSAK_MIGRATE_ROOTS_TAKE_HOLD — owner by card 2026-10-19: "Make them animals and make them bind."
    // The rhossak and the galled rhossak are ordinary animals (AnimalThingBase, the vanilla Animal think tree: no
    // Gauranlen tree, no dryad think tree, nothing that walks them off the map). This comp is the binding, read off the
    // description the owner approved on the Cauldron sheet (Cauldron_Rename.xml, 2026-10-09):
    //   * BIND  — each one binds to the nearest grove tree (props.groveTrees) on its map and stays near it. The "stays
    //             near" is NOT new code: it is our RM_CompHomeTether (CreatureBehaviors), whose home this comp points at
    //             the bound tree. Tree gone -> rebinds to the next nearest; none on the map -> unbound, a plain wild
    //             animal. The inspect pane always says which (no animal changes behaviour without a readable sign).
    //   * SPROUT — "Where a rhossak lies down to rest, the ground around it sprouts": a resting seed-bearer sometimes
    //             sets a seedling of one of the biome's own wild plants on an empty cell beside it.
    //   * ROOT  — "three of them standing together long enough can root a whole new grove": three seed-bearers within
    //             groupRadius of each other, clear of every grove tree by groveSpacing, for rootHours of awake time together
    //             (sleeping together holds the count, being apart resets it), root a young grove tree beside them and all
    //             three bind to it.
    // The galled rhossak binds but "carries no seed at all" (seedBearing=false): it never sprouts or roots.
    // Each part is a Mod Settings toggle (RM_CauldronSettings.rhossak*). The comp must come AFTER RM_CompHomeTether in
    // the def's comps, so its spawn-time bind overrides the tether's spawn-cell home.
    public class RM_CompProperties_RhossakGrove : CompProperties
    {
        public List<ThingDef> groveTrees = new List<ThingDef>();
        public bool seedBearing = true;
        public int checkIntervalTicks = 250;
        public int groupSize = 3;
        public float groupRadius = 4f;
        public float rootHours = 24f;
        public float groveSpacing = 6f;          // well inside the tether (10): the 6-10 cell ring around a bound tree is where kin can root
        public float rootCooldownDays = 10f;
        public float rootGrowth = 0.15f;
        public float sproutMtbHours = 3f;
        public float sproutRadius = 2f;

        public RM_CompProperties_RhossakGrove()
        {
            compClass = typeof(RM_CompRhossakGrove);
        }

        public override IEnumerable<string> ConfigErrors(ThingDef parentDef)
        {
            foreach (string e in base.ConfigErrors(parentDef)) yield return e;
            if (groveTrees.NullOrEmpty()) yield return "RM_CompProperties_RhossakGrove: groveTrees is empty (nothing to bind to)";
            else
                foreach (ThingDef d in groveTrees)
                    if (d == null || d.plant == null) yield return "RM_CompProperties_RhossakGrove: grove tree " + d + " is not a plant";
            if (parentDef.comps == null || !parentDef.comps.Any(c => c is RM_CompProperties_HomeTether))
                yield return "RM_CompProperties_RhossakGrove: " + parentDef.defName + " has no RM_CompProperties_HomeTether (binding cannot hold it near the tree)";
        }
    }

    public class RM_CompRhossakGrove : ThingComp
    {
        private Thing boundTree;
        private int togetherTicks;
        private int lastRootTick = -1;

        public RM_CompProperties_RhossakGrove Props => (RM_CompProperties_RhossakGrove)props;
        public Thing BoundTree => boundTree;
        public int TogetherTicks => togetherTicks;

        private Pawn Pawn => parent as Pawn;
        private RM_CompHomeTether Tether => parent.TryGetComp<RM_CompHomeTether>();

        public override void PostSpawnSetup(bool respawningAfterLoad)
        {
            base.PostSpawnSetup(respawningAfterLoad);
            if (!respawningAfterLoad) Check(0);
        }

        public override void CompTickInterval(int delta)
        {
            base.CompTickInterval(delta);
            int interval = Mathf.Max(1, Props.checkIntervalTicks);
            if (!parent.Spawned || !parent.IsHashIntervalTick(interval, delta)) return;
            Check(interval);
        }

        private void Check(int interval)
        {
            Pawn pawn = Pawn;
            if (pawn == null || pawn.Dead || !pawn.Spawned) return;
            Bind();
            if (interval <= 0) return;
            Sprout(pawn, interval);
            Grove(pawn, interval);
        }

        // ------------------------------------------------------------------ bind
        private bool TreeValid(Thing t)
        {
            return t != null && t.Spawned && !t.Destroyed && t.Map == parent.Map;
        }

        private void Bind()
        {
            RM_CompHomeTether tether = Tether;
            if (!RM_CauldronSettings.rhossakBindEnabled)
            {
                boundTree = null;
                if (tether != null && tether.Home.IsValid) tether.SetHome(IntVec3.Invalid);   // off: a plain wild animal
                return;
            }
            if (TreeValid(boundTree))
            {
                if (tether != null && tether.Home != boundTree.Position) tether.SetHome(boundTree.Position);
                return;
            }
            BindTo(NearestGroveTree(parent.Map, parent.Position));
        }

        public void BindTo(Thing tree)
        {
            boundTree = tree;
            Tether?.SetHome(tree != null ? tree.Position : IntVec3.Invalid);
        }

        private IEnumerable<Thing> GroveTreesOn(Map map)
        {
            foreach (ThingDef d in Props.groveTrees)
                if (d != null)
                    foreach (Thing t in map.listerThings.ThingsOfDef(d))
                        if (t.Spawned && !t.Destroyed) yield return t;
        }

        private Thing NearestGroveTree(Map map, IntVec3 from)
        {
            List<Thing> trees = GroveTreesOn(map).ToList();
            if (trees.Count == 0) return null;
            int[] xs = new int[trees.Count], zs = new int[trees.Count];
            bool[] ok = new bool[trees.Count];
            for (int i = 0; i < trees.Count; i++)
            {
                xs[i] = trees[i].Position.x;
                zs[i] = trees[i].Position.z;
                ok[i] = true;
            }
            int k = RM_RhossakKernel.NearestIndex(from.x, from.z, xs, zs, ok);
            return k < 0 ? null : trees[k];
        }

        // ------------------------------------------------------------------ sprout
        private void Sprout(Pawn pawn, int interval)
        {
            bool resting = !pawn.Awake() && !pawn.Downed;
            float chance = RM_RhossakKernel.ChancePerCheck(Props.sproutMtbHours, interval);
            if (!RM_RhossakKernel.ShouldSprout(RM_CauldronSettings.rhossakSproutEnabled, Props.seedBearing, resting, Rand.Value, chance))
                return;
            Map map = pawn.Map;
            List<ThingDef> pool = map.Biome.AllWildPlants
                .Where(d => d.plant != null && !d.plant.IsTree && map.Biome.CommonalityOfPlant(d) > 0f).ToList();
            if (pool.Count == 0) return;
            int cells = GenRadial.NumCellsInRadius(Mathf.Max(1f, Props.sproutRadius));
            for (int attempt = 0; attempt < 8; attempt++)
            {
                IntVec3 c = pawn.Position + GenRadial.RadialPattern[Rand.Range(1, cells)];
                if (!c.InBounds(map) || c.GetPlant(map) != null || c.GetEdifice(map) != null) continue;
                if (!pool.TryRandomElementByWeight(d => map.Biome.CommonalityOfPlant(d), out ThingDef def)) return;
                if (!def.CanEverPlantAt(c, map)) continue;
                Plant p = (Plant)ThingMaker.MakeThing(def);
                p.Growth = 0.05f;
                GenSpawn.Spawn(p, c, map);
                return;
            }
        }

        // ------------------------------------------------------------------ root a grove
        private void Grove(Pawn pawn, int interval)
        {
            if (!RM_CauldronSettings.rhossakGroveEnabled || !Props.seedBearing)
            {
                togetherTicks = 0;
                return;
            }
            Map map = pawn.Map;
            bool able = !pawn.Downed && !pawn.InMentalState;
            bool awake = able && pawn.Awake();
            // RHOSSAK A6 (2026-10-20): kin count asleep or awake, and sleeping together HOLDS the count instead of resetting
            // it (RM_RhossakKernel.StepTogetherHeld) — an animal sleeps every day, so "24 unbroken awake hours" was unreachable.
            List<Pawn> kin = able ? Kin(pawn) : new List<Pawn>();
            bool clear = able && !GroveTreesOn(map).Any(t => RM_RhossakKernel.Within(t.Position.x - pawn.Position.x,
                t.Position.z - pawn.Position.z, Props.groveSpacing));
            bool cooled = RM_RhossakKernel.CooledDown(Find.TickManager.TicksGame, lastRootTick, Props.rootCooldownDays);
            bool together = RM_RhossakKernel.Together(true, Props.seedBearing, awake, kin.Count, Props.groupSize, clear, cooled);
            bool held = able && !awake && RM_RhossakKernel.Together(true, Props.seedBearing, true, kin.Count, Props.groupSize, clear, cooled);
            togetherTicks = RM_RhossakKernel.StepTogetherHeld(togetherTicks, together, held, interval);
            if (RM_RhossakKernel.ShouldRoot(togetherTicks, Props.rootHours)) TryRoot(pawn, kin);
        }

        private List<Pawn> Kin(Pawn pawn)
        {
            var kin = new List<Pawn>();
            foreach (Thing t in GenRadial.RadialDistinctThingsAround(pawn.Position, pawn.Map, Props.groupRadius, true))
            {
                if (t is Pawn p && p != pawn && p.def == pawn.def && !p.Dead && !p.Downed && p.Faction == pawn.Faction
                    && !p.InMentalState)   // asleep or awake: a resting herd-mate is still standing with it (A6)
                    kin.Add(p);
            }
            return kin;
        }

        private void TryRoot(Pawn pawn, List<Pawn> kin)
        {
            togetherTicks = 0;
            Map map = pawn.Map;
            ThingDef def = boundTree != null && Props.groveTrees.Contains(boundTree.def) ? boundTree.def : Props.groveTrees.FirstOrDefault();
            if (def == null) return;
            if (!CellFinder.TryFindRandomCellNear(pawn.Position, map, 3,
                    c => c.GetPlant(map) == null && c.GetEdifice(map) == null && def.CanEverPlantAt(c, map), out IntVec3 cell))
                return;   // nowhere a tree can stand: they try again after another unbroken stretch
            Plant tree = (Plant)ThingMaker.MakeThing(def);
            tree.Growth = Mathf.Clamp01(Props.rootGrowth);
            GenSpawn.Spawn(tree, cell, map);
            int now = Find.TickManager.TicksGame;
            var trio = new List<Pawn> { pawn };
            trio.AddRange(kin.OrderBy(k => k.Position.DistanceToSquared(pawn.Position)).Take(Mathf.Max(0, Props.groupSize - 1)));
            foreach (Pawn p in trio)
            {
                RM_CompRhossakGrove g = p.TryGetComp<RM_CompRhossakGrove>();
                if (g == null) continue;
                g.lastRootTick = now;
                g.togetherTicks = 0;
                if (RM_CauldronSettings.rhossakBindEnabled) g.BindTo(tree);
            }
            if (map.IsPlayerHome)
                Messages.Message("Three " + pawn.def.label + " have rooted a new grove.", new LookTargets(tree), MessageTypeDefOf.NeutralEvent);
        }

        // ------------------------------------------------------------------ readout
        public override string CompInspectStringExtra()
        {
            bool valid = TreeValid(boundTree);
            return RM_RhossakKernel.BindLine(RM_CauldronSettings.rhossakBindEnabled, valid, valid ? boundTree.LabelNoCount : null);
        }

        // RHOSSAK A3 probe surface (read by jawa/comp_read, members="BindSettingSeen,InspectLine"): the setting as THIS
        // assembly's code sees it, and this comp's own pane line. The live A3 failure had the pane saying "Bound to" while
        // comp_read saw boundTree null and the bridge read the setting False — impossible for this code, so the row now
        // reads the comp's own line beside the pane to say which side is lying.
        public bool BindSettingSeen => RM_CauldronSettings.rhossakBindEnabled;
        public string InspectLine => CompInspectStringExtra();

        public override void PostExposeData()
        {
            base.PostExposeData();
            if (Scribe.mode == LoadSaveMode.Saving && boundTree != null && boundTree.Destroyed) boundTree = null;
            Scribe_References.Look(ref boundTree, "rmRhossakTree");
            Scribe_Values.Look(ref togetherTicks, "rmRhossakTogether", 0);
            Scribe_Values.Look(ref lastRootTick, "rmRhossakLastRoot", -1);
        }
    }
}
