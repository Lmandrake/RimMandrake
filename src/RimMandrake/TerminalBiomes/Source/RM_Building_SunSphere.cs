using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.TerminalBiomes
{
    // TWILIGHT_LIGHT_ECONOMY_1 §3.1/§3.3. The independence arc's centrepiece:
    // "culturing the ollumin", fed on any raw floor food, never explodes,
    // dims to a seedable husk when starved past grace, growth IS brightness
    // (radius steps with culture stage). Pattern lifted from
    // src/RimMandrake/LuminousPigment/Source/Building_GlowTank.cs (a seed
    // CompRefuelable gates growth; a second CompRefuelable is the ongoing
    // feed) — same two-comp shape, no plant grower here since the sphere
    // itself is the organism, not a bed for one.
    public class RM_Building_SunSphere : Building
    {
        private CompRefuelable seedComp; // one wild seed (RM_PalluCatch or RM_LampBladder) — consumed once
        private CompRefuelable foodComp; // ongoing feed: any raw floor food
        private CompGlower glowerComp;

        private RM_SunSphereStage stage = RM_SunSphereStage.Husk;
        private int cultureTicks;
        private int starvedTicks;


        public override void SpawnSetup(Map map, bool respawningAfterLoad)
        {
            base.SpawnSetup(map, respawningAfterLoad);
            // Two CompRefuelable siblings share no distinct subtype, so
            // they cannot be told apart by C# type. RM_SunSphere.xml lists
            // the seed comp first and the food comp second, but a future
            // def reorder must not silently swap "seed" and "feed"
            // semantics -- identify each by what it actually ACCEPTS
            // (the food comp's fuelFilter allows raw floor food; the seed
            // comp's does not) rather than trusting list order alone.
            var refuelables = new System.Collections.Generic.List<CompRefuelable>();
            foreach (ThingComp c in AllComps)
            {
                if (c is CompRefuelable rc) refuelables.Add(rc);
            }
            if (refuelables.Count >= 2)
            {
                bool firstIsFood = refuelables[0].Props.fuelFilter?.Allows(ThingDefOf.RawPotatoes) == true;
                bool secondIsFood = refuelables[1].Props.fuelFilter?.Allows(ThingDefOf.RawPotatoes) == true;
                if (firstIsFood != secondIsFood)
                {
                    foodComp = firstIsFood ? refuelables[0] : refuelables[1];
                    seedComp = firstIsFood ? refuelables[1] : refuelables[0];
                }
                else
                {
                    Log.Error("RM_Building_SunSphere on " + ThingID + ": could not tell the seed and food CompRefuelable apart by fuelFilter (both or neither accept raw food) -- falling back to def order (seed first, food second). Check RM_SunSphere.xml's <comps> block.");
                    seedComp = refuelables[0];
                    foodComp = refuelables[1];
                }
            }
            glowerComp = GetComp<CompGlower>();
            RecomputeVisual();
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref stage, "rmSunSphereStage", RM_SunSphereStage.Husk);
            Scribe_Values.Look(ref cultureTicks, "rmSunSphereCultureTicks", 0);
            Scribe_Values.Look(ref starvedTicks, "rmSunSphereStarvedTicks", 0);
        }

        protected override void Tick()
        {
            base.Tick();
            if (!RM_TerminalBiomesSettings.SunSphereActive)
            {
                return; // mod/biome all-off must degrade this feature too
            }
            if (!this.IsHashIntervalTick(60))
            {
                return;
            }
            TickCulture(60);
        }

        private void TickCulture(int delta)
        {
            if (seedComp == null || foodComp == null)
            {
                return;
            }

            int graceTicks = Mathf.RoundToInt(RM_TerminalBiomesSettings.twilightSunSphereGraceDays * 60000f);
            if (RM_SunSphereKernel.Step(ref stage, ref cultureTicks, ref starvedTicks, seedComp.HasFuel, foodComp.HasFuel, graceTicks, delta))
            {
                seedComp.ConsumeFuel(seedComp.Fuel); // the wild seed is consumed once, on planting
            }
            RecomputeVisual();
        }

        private void RecomputeVisual()
        {
            if (glowerComp == null)
            {
                return;
            }
            float factor = RM_SunSphereKernel.Factor(stage, cultureTicks);
            float newRadius = RM_SunSphereKernel.Radius(factor);
            if (!Mathf.Approximately(newRadius, glowerComp.GlowRadius))
            {
                glowerComp.GlowRadius = newRadius;
                if (Spawned)
                {
                    glowerComp.ForceRegister(Map);
                }
            }
        }

        // §3.1: "grows crops without any well" — a plant grower placed near
        // a mature sphere sees this radius as its light, through the
        // vanilla glow grid; no separate hook is needed for that half.
        public override string GetInspectString()
        {
            string baseString = base.GetInspectString();
            string stageLine;
            switch (stage)
            {
                case RM_SunSphereStage.Husk:
                    stageLine = "RM_SunSphere_Husk".Translate();
                    break;
                case RM_SunSphereStage.Seeded:
                    stageLine = "RM_SunSphere_Seeded".Translate();
                    break;
                case RM_SunSphereStage.Culturing:
                    stageLine = "RM_SunSphere_Culturing".Translate();
                    break;
                default:
                    stageLine = "RM_SunSphere_Mature".Translate();
                    break;
            }
            return baseString.NullOrEmpty() ? stageLine : baseString + "\n" + stageLine;
        }
    }
}
