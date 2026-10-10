using RimWorld;
using Verse;
using RimMandrake.Shared;

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
    // Ocean water (spec §2.5, DESIGN_PASS LP-2 / GLOW_TANK_LIQUID_FEED_1):
    // with FlowWorks loaded and tankNeedsWater on, the tank drinks salt or
    // boiling water from a FlowWorks liquid tank on its net (an adjacent
    // tank, or one on a hose run touching it) through FlowWorksWaterBridge.
    // It keeps a small reserve (RM_GlowTankWater); dry, the crop's growth
    // pauses (Patch_Plant_GrowthRate_GlowTank) and the inspect string says
    // so. Nothing dies of thirst. Without FlowWorks: power + seed alone.
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
        private int waterReserveTicks;
        private string lastWaterDrawn;
        // The culture is established once the first sow has taken (the seed unit is consumed then); a blackout clears it.
        private bool established;
        /// <summary>GLOW_TANK_SEED_LIVE_SOW_1: an established culture glows on its own (Patch_CompRefuelable_GlowTankLit).</summary>
        public bool Established => established;

        private static int TicksPerUnit => RM_GlowTankWater.TicksPerUnit(LuminousPigmentSettings.tankWaterUnitsPerDay);

        private static bool WaterGateActive =>
            RM_GlowTankWater.GateActive(LuminousPigmentSettings.tankNeedsWater, FlowWorksWaterBridge.Present);

        /// <summary>True while the water gate applies and the reserve is empty: growth is paused.</summary>
        public bool Parched => RM_GlowTankWater.Parched(WaterGateActive, TicksPerUnit, waterReserveTicks);

        public override void SpawnSetup(Map map, bool respawningAfterLoad)
        {
            base.SpawnSetup(map, respawningAfterLoad);
            seedComp = GetComp<CompRefuelable>();
            powerComp = GetComp<CompPowerTrader>();
            LightLedger.Tag(GetComp<CompGlower>(), "deepfire");   // DEEPFIRE_WORLD_LIGHT_1: its glow is deepfire light
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref unpoweredTicks, "rmGlowTankUnpoweredTicks", 0);
            Scribe_Values.Look(ref waterReserveTicks, "rmGlowTankWaterReserveTicks", 0);
            Scribe_Values.Look(ref lastWaterDrawn, "rmGlowTankLastWater");
            Scribe_Values.Look(ref established, "rmGlowTankEstablished", false);
        }

        public new bool CanAcceptSowNow()
        {
            if (!established && (seedComp == null || !seedComp.HasFuel)) return false;
            return base.CanAcceptSowNow();
        }

        public override string GetInspectString()
        {
            string text = base.GetInspectString();
            if (!established && seedComp != null && !seedComp.HasFuel)
            {
                text = Append(text, "Needs a seed culture: haul one unit of fresh crowncarpet here.");
            }
            if (LuminousPigmentSettings.tankNeedsWater && TicksPerUnit > 0)
            {
                text = Append(text, WaterLine());
            }
            return text;
        }

        private static string Append(string text, string line)
        {
            return string.IsNullOrEmpty(text) ? line : text + "\n" + line;
        }

        private string WaterLine()
        {
            if (!FlowWorksWaterBridge.Present)
            {
                return "Ocean water: not needed (FlowWorks not loaded).";
            }
            if (Parched)
            {
                return "Dry: growth paused. Pipe salt or boiling water to it from a FlowWorks liquid tank (adjacent, or on a hose run).";
            }
            string kind = lastWaterDrawn == RM_GlowTankWater.BoilingWater ? " (boiling water)"
                : lastWaterDrawn == RM_GlowTankWater.SaltWater ? " (salt water)" : "";
            return "Ocean water: " + (waterReserveTicks / 2500f).ToString("0.0") + " h in reserve" + kind + ".";
        }

        /// <summary>LP-2: drink while running, top up from the net at the refill mark.</summary>
        private void TickWater()
        {
            if (!WaterGateActive) return;
            int perUnit = TicksPerUnit;
            if (perUnit <= 0) return;
            if (powerComp == null || powerComp.PowerOn)
            {
                waterReserveTicks = RM_GlowTankWater.Drain(waterReserveTicks, GenTicks.TickRareInterval);
            }
            if (RM_GlowTankWater.WantsDraw(waterReserveTicks, perUnit))
            {
                string drawn = FlowWorksWaterBridge.TryDrawOceanUnit(this);
                if (drawn != null)
                {
                    waterReserveTicks = RM_GlowTankWater.Refill(waterReserveTicks, perUnit);
                    lastWaterDrawn = drawn;
                }
            }
        }

        /// <summary>First successful sow: a plant stands in the tank, so the seed unit is spent and the culture lives on its own.</summary>
        private void TryEstablish()
        {
            if (established || seedComp == null || !seedComp.HasFuel) return;
            foreach (IntVec3 cell in this.OccupiedRect())
            {
                if (cell.GetPlant(Map) != null)
                {
                    established = true;           // set first: the RanOutOfFuel signal re-reads the glow
                    seedComp.ConsumeFuel(seedComp.Fuel);
                    GetComp<CompGlower>()?.UpdateLit(Map);
                    return;
                }
            }
        }

        public override void TickRare()
        {
            base.TickRare();
            TickWater();
            TryEstablish();

            if (powerComp == null) return;
            if (powerComp.PowerOn)
            {
                unpoweredTicks = 0;
                return;
            }

            unpoweredTicks += GenTicks.TickRareInterval;
            int graceTicks = (int)(LuminousPigmentSettings.tankPowerGraceHours * 2500f); // 2500 ticks/hour
            if (graceTicks <= 0) return; // grace disabled by settings (0h) never kills.
            if (unpoweredTicks < graceTicks) return;

            // Blackout past the grace window: the culture and any crop die.
            unpoweredTicks = 0;
            established = false;
            if (seedComp != null && seedComp.HasFuel)
            {
                seedComp.ConsumeFuel(seedComp.Fuel);
            }
            GetComp<CompGlower>()?.UpdateLit(Map);
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
