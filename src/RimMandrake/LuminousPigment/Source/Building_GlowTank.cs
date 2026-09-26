using RimWorld;
using Verse;

namespace RimMandrake.LuminousPigment
{
    // Spec §2.5. Building_PlantGrower + a seeding gate: the tank refuses to
    // grow anything until it holds one unit of fresh crowncarpet in its
    // CompRefuelable "seed culture" (fuelCapacity 1, consumeFuelOnlyWhenUsed
    // -- the seed is consumed once, on the first successful sow, not drained
    // per tick). A power outage longer than tankPowerGraceHours (Mod
    // Settings) kills the crop AND the seed culture -- a blackout costs a
    // mat, not just a crop (ruling).
    //
    // The FlowWorks ocean-water requirement is NOT implemented here (see
    // About.xml / the def's own header) -- the tank runs on power + seed
    // alone in this build.
    // IPlantToGrowSettable re-declared deliberately: Building_PlantGrower's
    // own CanAcceptSowNow() is a plain (non-virtual) implicit interface
    // implementation, RimSage-verified (RimWorld/Building_PlantGrower.cs:115,
    // no `virtual`). WorkGiver_GrowerSow calls it through an
    // IPlantToGrowSettable reference, so a plain C# override cannot reach
    // it -- re-listing the interface here plus a `new` method of the same
    // name rebinds the interface dispatch slot for THIS type, which is the
    // standard fix for hiding a non-virtual base member behind an interface.
    public class Building_GlowTank : Building_PlantGrower, IPlantToGrowSettable
    {
        private CompRefuelable seedComp;
        private CompPowerTrader powerComp;
        private int unpoweredTicks;

        public override void SpawnSetup(Map map, bool respawningAfterLoad)
        {
            base.SpawnSetup(map, respawningAfterLoad);
            seedComp = GetComp<CompRefuelable>();
            powerComp = GetComp<CompPowerTrader>();
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref unpoweredTicks, "rmGlowTankUnpoweredTicks", 0);
        }

        public new bool CanAcceptSowNow()
        {
            if (seedComp == null || !seedComp.HasFuel) return false;
            return base.CanAcceptSowNow();
        }

        public override string GetInspectString()
        {
            string baseString = base.GetInspectString();
            if (seedComp != null && !seedComp.HasFuel)
            {
                string note = "Needs a seed culture: haul one unit of fresh crowncarpet here.";
                return string.IsNullOrEmpty(baseString) ? note : baseString + "\n" + note;
            }
            return baseString;
        }

        protected override void Tick()
        {
            base.Tick();

            if (powerComp == null) return;
            if (powerComp.PowerOn)
            {
                unpoweredTicks = 0;
                return;
            }

            unpoweredTicks++;
            int graceTicks = (int)(LuminousPigmentSettings.tankPowerGraceHours * 2500f); // 2500 ticks/hour
            if (graceTicks <= 0) return; // grace disabled by settings (0h) never kills.
            if (unpoweredTicks < graceTicks) return;

            // Blackout past the grace window: the culture and any crop die.
            unpoweredTicks = 0;
            if (seedComp != null && seedComp.HasFuel)
            {
                seedComp.ConsumeFuel(seedComp.Fuel);
            }
            foreach (IntVec3 cell in this.OccupiedRect())
            {
                Plant plant = cell.GetPlant(Map);
                if (plant != null && plant.def.defName == "RM_CrowncarpetCultured")
                {
                    plant.Destroy(DestroyMode.Vanish);
                }
            }
        }
    }
}
