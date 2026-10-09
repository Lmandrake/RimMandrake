using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.DivingInteraction
{
    // ════════════════════════════════════════════════════════════════════
    // CHILL_HEATED_SUIT_1 — the heated dive suit's ONE clock (card ruling:
    // a battery charge gauge; the two-clock heat+air option and the
    // no-clock option were both declined).
    //
    // ODYSSEY RESEARCH (read via RimSage before writing anything here):
    // Odyssey's own vacuum-suit machinery — VacuumResistance (a flat
    // equippedStatOffsets stat, StatWorker_VacuumResistance), Room.Vacuum
    // (a per-room float the engine equalises toward 0 or 1 over time, no
    // depleting/rechargeable-gauge concept anywhere in it) and Insulation_
    // Cold (also a flat statBases/equippedStatOffsets value) — has NO
    // depleting-charge-with-recharge pattern anywhere in the decompiled
    // engine. The closest vanilla apparel-worn "stored float that drains
    // and refills" is CompShield, but its recharge is ambient/passive
    // (EnergyGainPerTick ticks up on its own whenever the shield is
    // Active) — it never draws power from anything, so it cannot satisfy
    // this item's hard requirement that recharging "must consume the
    // ship's power budget." CompMechCarrier/Building_MechCharger IS a
    // real draw-power-to-recharge pattern, but it is a whole JobDriver/
    // WorkGiver system built for MECH pawns recharging themselves — far
    // heavier than a worn apparel gauge needs.
    // ⇒ What Odyssey DOES give for free, and this suit uses outright:
    // Apparel_Vacsuit itself (ParentName below) — real shipped art
    // (Things/Pawn/Humanlike/Apparel/Vacsuit/Vacsuit), real armor/
    // insulation/EquipDelay/bodyPartGroups/layers, the "protective suit
    // that keeps the user safe in a hostile environment, restricts
    // movement" framing the owner already described unprompted. ⇒ What is
    // bespoke here: the charge/recharge gauge (this file), the charger
    // building (RM_HeatedSuitCharger.xml), and the StatPart that gates
    // the suit's real cold protection on that charge
    // (RM_StatPart_HeatedSuitCharge.cs).
    //
    // WHY Insulation_Cold IS OVERRIDDEN DOWN FROM THE INHERITED 90 (see
    // RM_ChillHeatedSuit.xml): that stat is vanilla's own ALWAYS-ON
    // apparel insulation (StatPart_GearStatOffset on ComfyTemperatureMin,
    // Defs/Core/Stats), applied regardless of this comp's charge state.
    // Left at 90 it would make an EMPTY suit still deliver ~-74C comfy
    // min — nowhere near "hypothermia sets in FAST" once the battery
    // dies. The suit's static material insulation is cut to a modest 20
    // (ordinary winter-coat territory) and ALL of the real -110C
    // protection is charge-gated through RM_StatPart_HeatedSuitCharge —
    // full charge counteracts the Chill's ambient outright, empty leaves
    // the wearer with only that modest static baseline, which is not
    // enough: HediffGiver_Hypothermia's own severity-per-interval formula
    // (Mathf.Abs(ambient - safeMin) * 6.45e-5, HealthTuning.cs) scales
    // with the deficit, and -110C against a ~-9C safe min there is a ~101C
    // deficit — the same order of magnitude as a fully naked pawn, i.e.
    // genuinely fast, but NOT instant: severity 1.0 (death) takes roughly
    // 130+ hypothermia intervals, several in-game hours, which is exactly
    // the "walk back to the airlock is the horror beat, not instant
    // death" window the ruling asked for. Nothing new was written to
    // produce that curve — it is vanilla's own hypothermia hediff, simply
    // no longer being held off by suit insulation.
    //
    // SCOPE: drains ONLY while worn, outdoors, on the Chill's own SEABED
    // pocket map (RM_ChillFireGate.IsChillSeabedMap) — every other map in
    // the game, including the Chill's surface/shore tile (same biome
    // defName, IsPocketMap false), leaves the charge untouched. Recharges
    // ONLY while indoors on that same map, within range of a powered
    // RM_HeatedSuitCharger — CHILL_THERMAL_ENGINE_1's own "extensive ship
    // heating is THE logistics problem" gets a second, permanent power
    // sink to plan around, not a free clock reset.
    // ════════════════════════════════════════════════════════════════════
    public class RM_CompProperties_HeatedSuitBattery : CompProperties
    {
        // 15,000 ticks = 6 in-game hours of continuous outdoor Chill-seabed
        // wear on a full charge — long enough for a real work session,
        // short enough that "bring the suit home to recharge" is a genuine
        // planning constraint rather than a formality.
        public int maxChargeTicks = 15000;

        // CompTickRare cadence (vanilla's own RareTickInterval).
        public int drainIntervalTicks = 250;

        // Recharges 3x faster than it drains while docked at a powered
        // charger — a full recharge from empty takes ~2 in-game hours,
        // deliberately faster than the drain so "come home and charge" is
        // a viable loop rather than a losing race.
        public float rechargeRateMultiplier = 3f;

        // How far from a powered RM_HeatedSuitCharger the wearer can stand
        // and still recharge — a small pocket-map "docking bay" radius,
        // not whole-map range.
        public float chargerSearchRadius = 3.9f;

        // CHILL_SUIT_SHELTER_RULE_1: the suit drains while the AIR AT THE WEARER is colder than this (vanilla
        // temperature, no second heat model), roof or no roof. PROVISIONAL.
        public float drainBelowTempC = 0f;

        public RM_CompProperties_HeatedSuitBattery()
        {
            compClass = typeof(RM_CompHeatedSuitBattery);
        }
    }

    public class RM_CompHeatedSuitBattery : ThingComp
    {
        private int chargeTicksRemaining;

        private static ThingDef chargerDefCached;
        private static bool chargerDefLookupDone;

        public RM_CompProperties_HeatedSuitBattery Props => (RM_CompProperties_HeatedSuitBattery)props;

        /// <summary>True while there is any charge left at all — the gate
        /// RM_StatPart_HeatedSuitCharge reads for "does this suit still
        /// counteract the cold." Mod Settings off (master or this
        /// mechanic specifically) degrades to "always charged," per
        /// MOD_OPTIONS_RETROFIT_1 — off never strands anyone on a dead
        /// battery.</summary>
        public bool IsCharged =>
            !RM_DivingSettings.masterEnabled || !RM_DivingSettings.chillHeatedSuitEnabled || chargeTicksRemaining > 0;

        public float ChargeFraction
        {
            get
            {
                int max = Props?.maxChargeTicks ?? 0;
                return max <= 0 ? 0f : Mathf.Clamp01((float)chargeTicksRemaining / max);
            }
        }

        public override void Initialize(CompProperties props)
        {
            base.Initialize(props);
            // Ships full — a freshly crafted or spawned suit is ready to
            // wear outside immediately, never a dead battery by default.
            chargeTicksRemaining = Props.maxChargeTicks;
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref chargeTicksRemaining, "chillSuitChargeTicks", Props?.maxChargeTicks ?? 0);
        }

        public override void CompTickRare()
        {
            base.CompTickRare();

            if (!RM_DivingSettings.masterEnabled || !RM_DivingSettings.chillHeatedSuitEnabled)
            {
                return; // degrade to "always full" per MOD_OPTIONS_RETROFIT_1 — off never strands anyone on a dead battery
            }
            if (!(parent is Apparel apparel) || apparel.Wearer == null || !apparel.Wearer.Spawned)
            {
                return;
            }

            Pawn wearer = apparel.Wearer;
            Map map = wearer.MapHeld;
            if (map == null || !RM_ChillFireGate.IsChillSeabedMap(map))
            {
                return; // every other map in the game, including the Chill's own SURFACE tile: neither drains nor recharges
            }

            bool cold = wearer.Position.GetTemperature(map) < Props.drainBelowTempC;
            if (cold)
            {
                if (chargeTicksRemaining > 0)
                {
                    chargeTicksRemaining = Mathf.Max(0, chargeTicksRemaining - Props.drainIntervalTicks);
                }
            }
            else if (chargeTicksRemaining < Props.maxChargeTicks && !wearer.Position.UsesOutdoorTemperature(map))
            {
                TryRechargeNearCharger(wearer, map);
            }
        }

        private void TryRechargeNearCharger(Pawn wearer, Map map)
        {
            Building charger = FindNearbyPoweredCharger(wearer, map);
            if (charger == null)
            {
                return;
            }
            int gain = Mathf.Max(1, Mathf.RoundToInt(Props.drainIntervalTicks * Props.rechargeRateMultiplier));
            chargeTicksRemaining = Mathf.Min(Props.maxChargeTicks, chargeTicksRemaining + gain);
        }

        private Building FindNearbyPoweredCharger(Pawn wearer, Map map)
        {
            ThingDef chargerDef = GetChargerDef();
            if (chargerDef == null)
            {
                return null; // charger def failed to load — never blocks the suit from being worn, just never recharges
            }

            List<Thing> chargers = map.listerThings.ThingsOfDef(chargerDef);
            for (int i = 0; i < chargers.Count; i++)
            {
                if (!(chargers[i] is Building charger) || !charger.Spawned)
                {
                    continue;
                }
                if (wearer.Position.DistanceTo(charger.Position) > Props.chargerSearchRadius)
                {
                    continue;
                }
                Room wr = wearer.Position.GetRoom(map);
                if (wr == null || charger.GetRoom() != wr)
                {
                    continue; // through a wall is not docked: same room only
                }
                CompPowerTrader power = charger.TryGetComp<CompPowerTrader>();
                if (power != null && power.PowerOn)
                {
                    return charger; // powered AND in range — an unpowered charger (ship can't afford it) never charges anything
                }
            }
            return null;
        }

        private static ThingDef GetChargerDef()
        {
            if (!chargerDefLookupDone)
            {
                chargerDefCached = DefDatabase<ThingDef>.GetNamedSilentFail("RM_HeatedSuitCharger");
                chargerDefLookupDone = true;
            }
            return chargerDefCached;
        }

        public override string CompInspectStringExtra()
        {
            string status = IsCharged
                ? "RM_HeatedSuitCharge".Translate(ChargeFraction.ToStringPercent())
                : "RM_HeatedSuitChargeDepleted".Translate();
            if (IsCharged && RM_DivingSettings.chillHeatedSuitEnabled && RM_DivingSettings.masterEnabled)
            {
                status += " (about " + Mathf.CeilToInt(chargeTicksRemaining / 2500f) + "h outdoors)"; // DI-4 time-left line
            }
            return status;
        }
    }
}
