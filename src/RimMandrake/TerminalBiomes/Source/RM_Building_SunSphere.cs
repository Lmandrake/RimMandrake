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
    public enum RM_SunSphereStage
    {
        Husk, // starved past grace; dark; needs reseeding
        Seeded, // has a seed, not yet culturing
        Culturing,
        Mature,
    }

    public class RM_Building_SunSphere : Building
    {
        private CompRefuelable seedComp; // one wild seed (RM_Pallu or RM_LampBladder) — consumed once
        private CompRefuelable foodComp; // ongoing feed: any raw floor food
        private CompGlower glowerComp;

        private RM_SunSphereStage stage = RM_SunSphereStage.Husk;
        private int cultureTicks;
        private int starvedTicks;

        private const int CultureTicksToMature = 6 * 60000; // a week-ish culture, "you watch your light grow, over days"
        private const float MatureRadius = 6f; // "sun-strength, radius ~6" (§3.1)

        public override void SpawnSetup(Map map, bool respawningAfterLoad)
        {
            base.SpawnSetup(map, respawningAfterLoad);
            // Two CompRefuelable siblings share no distinct subtype, so
            // they are told apart by comp ORDER: the seed comp is listed
            // first in the def, the food comp second. See RM_SunSphere.xml's
            // own comment for the order contract this relies on.
            var refuelables = new System.Collections.Generic.List<CompRefuelable>();
            foreach (ThingComp c in AllComps)
            {
                if (c is CompRefuelable rc) refuelables.Add(rc);
            }
            if (refuelables.Count >= 2)
            {
                seedComp = refuelables[0];
                foodComp = refuelables[1];
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

            if (stage == RM_SunSphereStage.Husk)
            {
                if (seedComp.HasFuel)
                {
                    stage = RM_SunSphereStage.Seeded;
                    cultureTicks = 0;
                    starvedTicks = 0;
                    seedComp.ConsumeFuel(seedComp.Fuel); // the wild seed is consumed once, on planting
                }
                RecomputeVisual();
                return;
            }

            bool fed = foodComp.HasFuel;
            int graceTicks = Mathf.RoundToInt(RM_TerminalBiomesSettings.twilightSunSphereGraceDays * 60000f);
            if (fed)
            {
                starvedTicks = 0;
                cultureTicks += delta;
                if (stage == RM_SunSphereStage.Seeded && cultureTicks > 0)
                {
                    stage = RM_SunSphereStage.Culturing;
                }
                if (cultureTicks >= CultureTicksToMature)
                {
                    cultureTicks = CultureTicksToMature;
                    stage = RM_SunSphereStage.Mature;
                }
            }
            else
            {
                starvedTicks += delta;
                if (graceTicks > 0 && starvedTicks >= graceTicks)
                {
                    // Dims to a seedable husk — NEVER explodes (RULED).
                    stage = RM_SunSphereStage.Husk;
                    cultureTicks = 0;
                    starvedTicks = 0;
                }
            }
            RecomputeVisual();
        }

        private void RecomputeVisual()
        {
            if (glowerComp == null)
            {
                return;
            }
            float factor;
            switch (stage)
            {
                case RM_SunSphereStage.Husk:
                    factor = 0f;
                    break;
                case RM_SunSphereStage.Seeded:
                    factor = 0.1f; // "seeded dark"
                    break;
                case RM_SunSphereStage.Culturing:
                    factor = Mathf.Lerp(0.15f, 0.7f, Mathf.Clamp01((float)cultureTicks / CultureTicksToMature)); // "culturing dim"
                    break;
                case RM_SunSphereStage.Mature:
                default:
                    factor = 1f; // "mature sun"
                    break;
            }
            float newRadius = Mathf.Max(0.05f, MatureRadius * factor);
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
