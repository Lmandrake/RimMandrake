// BLUEDESERT_GPT_ENRICHMENT_1 §1 — the blue-ice heat sink.
//
// Owner-picked by question card 2026-09-30 from the GPT enrichment consult
// (Transient/bedazzle_gpt_enrich_2026-09-30/bluedesert.md §3). Loading blue
// ice into a rack holds a room cold through a power failure: the rack draws
// no power, so it keeps working in a blackout, and it only melts ice while
// the room sits ABOVE its target, so a room held cold by powered coolers
// leaves the ice untouched. The blocks cloud from deep blue to white as the
// rack's cold store runs down, the rack groans, and the melt drips into
// sealed cans of distilled-grade meltwater.
//
// Engine seams (RimSage, decompiled 1.6, 2026-09-30):
//  - Building_Cooler.TickRare: energy = energyPerSecond * 4.1666665 per rare
//    tick, applied through GenTemperature.ControlTemperatureTempChange(cell,
//    map, energy, target), which returns 0 for an outdoor or null room and
//    clamps the change so the room never overshoots its target. This comp
//    reuses exactly that call; the rack has no hot side (melting ice absorbs
//    heat, it does not move it), so there is no PushHeat exhaust.
//  - CompTempControl is safe without a CompPowerTrader (its PowerTrader
//    getter is null-guarded in CompInspectStringExtra), so the vanilla
//    target-temperature gizmos come free.
//  - CompRefuelable with consumeFuelOnlyWhenUsed never burns fuel on its own;
//    this comp calls ConsumeFuel with the heat it actually absorbed.
//
// Heat capacity: coldPerBlock is the energy one block absorbs before it is
// spent (Cooler-scale units). The Mod Settings multiplier scales it.
//
// Gate: RM_BlueDesertSettings.masterEnabled && coldSinkEnabled. Off: the
// rack holds its ice and does nothing.

using System.Text;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.Sound;

namespace RimMandrake.BlueDesert
{
    public class CompProperties_ColdSink : CompProperties
    {
        /// <summary>Most cold the rack can give per second (negative, same
        /// units as CompProperties_TempControl.energyPerSecond; vanilla
        /// cooler -21, so the rack is a bit over half a cooler).</summary>
        public float energyPerSecond = -12f;

        /// <summary>Energy one blue-ice block absorbs before it is spent
        /// (500 = about one game hour of full draw per block).</summary>
        public float coldPerBlock = 500f;

        /// <summary>Blocks melted per can of meltwater produced.</summary>
        public float blocksPerCan = 5f;
        public int cansPerMelt = 3;
        public ThingDef meltwaterDef;

        /// <summary>Mean ticks between groans while the rack is working.</summary>
        public float groanMtbTicks = 5000f;
        public SoundDef groanSound;
        public SoundDef dripSound;

        /// <summary>Clarity tints applied to the rack's (greyscale) texture:
        /// full store, half store, nearly spent.</summary>
        public Color fullColor = new Color(0.45f, 0.65f, 1f);
        public Color cloudingColor = new Color(0.72f, 0.82f, 0.95f);
        public Color spentColor = new Color(0.95f, 0.96f, 0.98f);

        public CompProperties_ColdSink()
        {
            compClass = typeof(RM_CompColdSink);
        }
    }

    public class RM_CompColdSink : ThingComp
    {
        private float meltedBlocks;
        private bool workingNow;

        private CompRefuelable refuelable;
        private CompTempControl tempControl;

        public CompProperties_ColdSink Props => (CompProperties_ColdSink)props;

        public bool WorkingNow => workingNow;

        private static bool On =>
            RM_BlueDesertSettings.masterEnabled && RM_BlueDesertSettings.coldSinkEnabled;

        private float ColdPerBlock =>
            RM_BlueKernel.ColdPerBlock(Props.coldPerBlock, RM_BlueDesertSettings.coldSinkCapacityFactor);

        /// <summary>0 = deep blue (store full) .. 2 = white (spent).</summary>
        public int ClarityStage
        {
            get
            {
                return RM_BlueKernel.ClarityStage(refuelable != null, refuelable != null ? refuelable.FuelPercentOfMax : 0f);
            }
        }

        public override void PostSpawnSetup(bool respawningAfterLoad)
        {
            base.PostSpawnSetup(respawningAfterLoad);
            refuelable = parent.GetComp<CompRefuelable>();
            tempControl = parent.GetComp<CompTempControl>();
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref meltedBlocks, "rmMeltedBlocks", 0f);
        }

        public override void CompTickRare()
        {
            base.CompTickRare();
            int stageBefore = ClarityStage;
            workingNow = false;
            if (On && refuelable != null && refuelable.HasFuel && parent.Spawned)
            {
                Absorb();
            }
            if (ClarityStage != stageBefore && parent.Spawned)
            {
                parent.Map.mapDrawer.MapMeshDirty(parent.Position, MapMeshFlagDefOf.Things);
            }
        }

        private void Absorb()
        {
            Map map = parent.Map;
            IntVec3 cell = parent.Position;
            Room room = cell.GetRoom(map);
            if (room == null || room.UsesOutdoorTemperature)
            {
                return;
            }
            float target = tempControl != null ? tempControl.TargetTemperature : -5f;
            float energyLimit = Props.energyPerSecond * 4.1666665f;
            float tempChange = GenTemperature.ControlTemperatureTempChange(cell, map, energyLimit, target);
            // Never absorb more heat than the ice left in the rack holds.
            if (!RM_BlueKernel.Absorb(tempChange, room.CellCount, refuelable.Fuel, ColdPerBlock, out tempChange, out float blocks))
            {
                return;
            }
            room.Temperature += tempChange;
            refuelable.ConsumeFuel(blocks);
            workingNow = true;
            meltedBlocks += blocks;
            TryDripMeltwater(map);
            // Rare ticks are 250 game ticks apart, so the MTB is scaled.
            if (Props.groanSound != null && Rand.MTBEventOccurs(Props.groanMtbTicks, 1f, 250f))
            {
                Props.groanSound.PlayOneShot(new TargetInfo(cell, map));
            }
        }

        private void TryDripMeltwater(Map map)
        {
            if (Props.meltwaterDef == null || Props.blocksPerCan <= 0f)
            {
                return;
            }
            int drips = RM_BlueKernel.Drip(ref meltedBlocks, Props.blocksPerCan);
            for (int i = 0; i < drips; i++)
            {
                Thing can = ThingMaker.MakeThing(Props.meltwaterDef);
                can.stackCount = RM_BlueKernel.CansPerDrip(Props.cansPerMelt);
                GenPlace.TryPlaceThing(can, parent.Position, map, ThingPlaceMode.Near);
                Props.dripSound?.PlayOneShot(new TargetInfo(parent.Position, map));
            }
        }

        public Color ClarityColor
        {
            get
            {
                switch (ClarityStage)
                {
                    case 0: return Props.fullColor;
                    case 1: return Props.cloudingColor;
                    default: return Props.spentColor;
                }
            }
        }

        public override string CompInspectStringExtra()
        {
            if (refuelable == null)
            {
                return null;
            }
            StringBuilder sb = new StringBuilder();
            string clarity = ClarityStage == 0 ? "deep blue" : ClarityStage == 1 ? "clouding" : "white, nearly spent";
            sb.Append("Ice: " + clarity);
            float heldCold = refuelable.Fuel * ColdPerBlock;
            // Hours of full draw left: heldCold / (|energy| * 4.1666 per 250 ticks).
            float perHour = Mathf.Abs(Props.energyPerSecond) * 4.1666665f * (2500f / 250f);
            if (perHour > 0f)
            {
                sb.Append("\nCold held: " + (heldCold / perHour).ToString("0.#") + " h at full draw");
            }
            if (!On)
            {
                sb.Append("\nHeat sink disabled in Mod Settings.");
            }
            else if (workingNow)
            {
                sb.Append("\nMelting: the room is above its target.");
            }
            return sb.ToString();
        }
    }

    /// <summary>The rack itself: tints its one greyscale texture by how
    /// clouded the ice is (deep blue -> white), so the store's state reads
    /// from across the room without a stage texture per state.</summary>
    public class RM_Building_ColdSinkRack : Building
    {
        private Graphic[] clarityGraphics;

        public override Graphic Graphic
        {
            get
            {
                Graphic baseGraphic = base.Graphic;
                RM_CompColdSink sink = GetComp<RM_CompColdSink>();
                if (sink == null || baseGraphic == null)
                {
                    return baseGraphic;
                }
                if (clarityGraphics == null)
                {
                    clarityGraphics = new Graphic[3];
                }
                int stage = sink.ClarityStage;
                if (clarityGraphics[stage] == null)
                {
                    clarityGraphics[stage] = baseGraphic.GetColoredVersion(baseGraphic.Shader, sink.ClarityColor, sink.ClarityColor);
                }
                return clarityGraphics[stage];
            }
        }
    }
}
