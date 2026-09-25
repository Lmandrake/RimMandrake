using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Utinni.ShipShields
{
    // shd:no-hard-landing-gate's other half (design doc §6, ship_shields_
    // deep_design.md): "Escalating damage ticks instead of a refusal...
    // the hazard applies from tick one at full raw strength (no shield, no
    // bubble) -- the same consequence a shielded ship risks only if its
    // shield later fails." Read precisely: the ruling's OWN words are "full
    // raw strength from tick one" -- a FLAT per-application magnitude, not
    // a ramping one. Vanilla already delivers that flat magnitude
    // automatically to PAWNS the instant a map is hazardous, shielded or
    // not: HediffGiver_Hypothermia/HediffGiver_Heat/HediffGiver_Terrain
    // (all three live in the OrganicStandard HediffGiverSetDef every
    // organic pawn carries) already burn-tick and ignite pawns standing on
    // lava terrain and grow Heatstroke from ambient temperature -- confirmed
    // via rimsage source read (Verse/HediffGiver_Terrain.cs,
    // Defs/Core/HediffGiverSetDefs/HediffGiverSets.xml), not guessed. This
    // class does NOT re-implement any of that; doing so would just double
    // the pawn tick vanilla already runs for free.
    //
    // What vanilla does NOT already do is damage the ship's own STRUCTURES
    // for sitting unshielded in a hazard ("the environment... immediately
    // goes to work on the ship... its hull is thick and can take a lot of
    // damage in most situations"). Vanilla's own building-scale precedent
    // for this shape of effect is CompTemperatureDamaged (Verse/
    // CompTemperatureDamaged.cs): a Thing outside a safe range takes
    // DamageDefOf.Deterioration on an interval. This class is that same
    // idiom -- scoped to "a hazard this ship's own shields don't currently
    // cover" instead of a per-building temperature range, applied to a
    // handful of Things near the ship each interval rather than to a
    // single comp's own parent.
    //
    // "Escalating" is real, but it deliberately does NOT live in the
    // per-hit magnitude (the ruling's "full raw strength from tick one"
    // rules that reading out). It lives in two other places instead:
    //   1. The application RATE doubles once a hazard has been unshielded
    //      continuously past EscalationStepTicks -- total accrued damage
    //      over time escalates; any single hit does not.
    //   2. The advisory letter fires a second time, at a harsher LetterDef,
    //      the moment that same step is crossed -- still only a letter,
    //      never a block, matching "advise... but no more than that."
    //
    // Lava is the one carve-out the ruling names by name ("Landing on lava
    // should be the worst case causing immediate severe damage (don't do
    // that)") -- an immediate, ONE-TIME burst fired from OnGravshipLanded,
    // unconditional on shield state. The ruling frames lava as the
    // exception precisely BECAUSE no shield configuration makes it safe,
    // not as another row in the shielded/unshielded hazard table -- so this
    // is never gated the way the ongoing heat/particulate tracking is, and
    // it is never a per-tick add-on.
    //
    // MapComponent, not GameComponent: the hazard state this tracks (is
    // THIS MAP currently hot/dusty/cold, is THIS MAP's shield generator
    // powered and configured) is inherently per-map, and MapComponent is the real
    // vanilla per-map tracked-state primitive (every non-abstract subclass
    // with a (Map) constructor is auto-instantiated per map by
    // Map.FillComponents -- confirmed via rimsage, not assumed) rather than
    // a single Game-wide GameComponent juggling one record per map by hand.
    public class ShieldHazardExposureTracker : MapComponent
    {
        // Matches the mod's existing per-interval-check convention
        // (CompShieldGenerator.PredictiveSampleIntervalTicks, both field
        // comps' intervalTicks=250).
        private const int CheckIntervalTicks = 250;

        // Base cadence for the Thing-damage application once a hazard is
        // confirmed unshielded; halved (twice as frequent) past the
        // escalation step. Never changes the per-hit amount -- see header.
        private const int BaseDamageIntervalTicks = 2000;
        private const int EscalatedDamageIntervalTicks = 1000;
        private const float ThingDamagePerApplication = 4f;
        private const int ThingsHitPerApplication = 3;

        // ~6 in-game hours -- the same "roughly N hours" register the
        // predictive-failure alert (~1 hour, CompShieldGenerator.
        // PredictiveWarnWithinTicks) and shield-collapse-evacuate's
        // countdown framing already use, just a longer band because this is
        // "stayed too long," not "about to fail."
        private const int EscalationStepTicks = 15000;

        // Fallback scan radius around the map's grav engine, used only when
        // there is no RUT_ShieldGenerator on the map AND no connected
        // substructure to read a real footprint from -- the shipped
        // generator's own default bubble radius (RUT_ShieldGenerator.xml's
        // CompProperties_ShieldGenerator radius field), this mod's one
        // canonical "near the ship" scale.
        private const float FallbackShipRadius = 14.9f;

        // Immediate lava-landing burst (design doc §6's carve-out). A
        // one-time DoExplosion, never a per-tick system -- see class header.
        private const float LavaBurstRadius = 8f;
        private const int LavaBurstDamageAmount = 140;
        private const float LavaBurstChanceToStartFire = 0.5f;

        private int heatUnshieldedSinceTick = -1;
        private int particulateUnshieldedSinceTick = -1;
        private int coldUnshieldedSinceTick = -1;
        private bool heatEscalationLetterSent;
        private bool particulateEscalationLetterSent;
        private bool coldEscalationLetterSent;

        public ShieldHazardExposureTracker(Map map) : base(map)
        {
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref heatUnshieldedSinceTick, "heatUnshieldedSinceTick", -1);
            Scribe_Values.Look(ref particulateUnshieldedSinceTick, "particulateUnshieldedSinceTick", -1);
            Scribe_Values.Look(ref coldUnshieldedSinceTick, "coldUnshieldedSinceTick", -1);
            Scribe_Values.Look(ref heatEscalationLetterSent, "heatEscalationLetterSent", false);
            Scribe_Values.Look(ref particulateEscalationLetterSent, "particulateEscalationLetterSent", false);
            Scribe_Values.Look(ref coldEscalationLetterSent, "coldEscalationLetterSent", false);
        }

        // Called from HarmonyPatches.Patch_Scenario_PostGravshipLanded's
        // postfix, alongside ShieldLandingAdvisory.Evaluate -- the one-time
        // lava carve-out, independent of shield state (see class header).
        public static void OnGravshipLanded(Map map)
        {
            if (map == null || !ShipShieldsSettings.lavaLandingBurstEnabled)
            {
                return;
            }

            if (!ShieldHazardUtility.HasLavaAtLanding(map))
            {
                return;
            }

            int amount = Mathf.Max(1, Mathf.RoundToInt(LavaBurstDamageAmount * ShipShieldsSettings.lavaLandingBurstDamageMultiplier));
            GenExplosion.DoExplosion(
                center: map.Center,
                map: map,
                radius: LavaBurstRadius,
                damType: DamageDefOf.Flame,
                instigator: null,
                damAmount: amount,
                chanceToStartFire: LavaBurstChanceToStartFire);

            Find.LetterStack.ReceiveLetter(
                "Lava landing",
                "The hull took immediate, severe damage setting down on active lava. This is the one "
                    + "landing hazard no shield configuration makes safe.",
                LetterDefOf.ThreatBig,
                new TargetInfo(map.Center, map));
        }

        public override void MapComponentTick()
        {
            if (!ShipShieldsSettings.landingHazardExposureEnabled)
            {
                return;
            }

            if (Find.TickManager.TicksGame % CheckIntervalTicks != 0)
            {
                return;
            }

            bool heatHazard = ShieldHazardUtility.HasHeatHazard(map)
                && !ShieldHazardUtility.IsHazardShielded(map, ShieldFieldMode.Thermal);
            bool particulateHazard = ShieldHazardUtility.HasParticulateHazard(map)
                && !ShieldHazardUtility.IsHazardShielded(map, ShieldFieldMode.Particulate);
            bool coldHazard = ShieldHazardUtility.HasColdHazard(map)
                && !ShieldHazardUtility.IsHazardShielded(map, ShieldFieldMode.Cryo);

            TrackHazard(heatHazard, ref heatUnshieldedSinceTick, ref heatEscalationLetterSent, "thermal stress");
            TrackHazard(particulateHazard, ref particulateUnshieldedSinceTick, ref particulateEscalationLetterSent, "particulate fouling");
            TrackHazard(coldHazard, ref coldUnshieldedSinceTick, ref coldEscalationLetterSent, "cold-seize");
        }

        private void TrackHazard(bool active, ref int unshieldedSinceTick, ref bool escalationLetterSent, string hazardLabel)
        {
            int now = Find.TickManager.TicksGame;

            if (!active)
            {
                unshieldedSinceTick = -1;
                escalationLetterSent = false;
                return;
            }

            if (unshieldedSinceTick < 0)
            {
                unshieldedSinceTick = now;
            }

            int exposureTicks = now - unshieldedSinceTick;
            bool escalated = exposureTicks >= EscalationStepTicks;
            int interval = escalated ? EscalatedDamageIntervalTicks : BaseDamageIntervalTicks;

            if (escalated && !escalationLetterSent)
            {
                escalationLetterSent = true;
                Find.LetterStack.ReceiveLetter(
                    "Unshielded exposure worsening",
                    "The ship has sat unshielded against " + hazardLabel + " for a long stretch now. "
                        + "Structural damage is accelerating -- this is still advisory only, but leaving "
                        + "unshielded much longer will cost more hull.",
                    LetterDefOf.ThreatBig,
                    new TargetInfo(map.Center, map));
            }

            if (now % interval == 0)
            {
                ApplyThingDamageNearShip();
            }
        }

        // shd:no-hard-landing-gate: "its hull is thick and can take a lot
        // of damage in most situations" -- a small, random sample of
        // Things near the ship's own footprint, not a map-wide sweep.
        private void ApplyThingDamageNearShip()
        {
            List<IntVec3> candidateCells = new List<IntVec3>();
            List<Thing> generators = ShieldHazardUtility.Generators(map);

            if (generators.Count > 0)
            {
                foreach (Thing generator in generators)
                {
                    float radius = FallbackShipRadius;
                    CompShieldGenerator comp = (generator as ThingWithComps)?.GetComp<CompShieldGenerator>();
                    if (comp?.Props != null)
                    {
                        radius = comp.Props.radius;
                    }

                    candidateCells.AddRange(GenRadial.RadialCellsAround(generator.Position, radius, true));
                }
            }
            else
            {
                // No generator instance to read a real radius from -- use
                // the grav engine's own connected substructure (the ship's
                // real footprint) if one exists, else the fallback radius
                // around the map center. NoRegen: this runs in the
                // background every 1000-2000 ticks and must never trigger
                // the visual section-layer regen the gizmo-facing
                // AllConnectedSubstructure getter does.
                Building_GravEngine engine = GravshipUtility.GetPlayerGravEngine_NewTemp(map);
                if (engine != null && engine.AllConnectedSubstructureNoRegen.Count > 0)
                {
                    candidateCells.AddRange(engine.AllConnectedSubstructureNoRegen);
                }
                else
                {
                    IntVec3 anchor = engine != null ? engine.Position : map.Center;
                    candidateCells.AddRange(GenRadial.RadialCellsAround(anchor, FallbackShipRadius, true));
                }
            }

            if (candidateCells.Count == 0)
            {
                return;
            }

            int hits = 0;
            int attempts = 0;
            int maxAttempts = candidateCells.Count * 2;
            while (hits < ThingsHitPerApplication && attempts < maxAttempts)
            {
                attempts++;
                IntVec3 cell = candidateCells[Rand.Range(0, candidateCells.Count)];
                if (!cell.InBounds(map))
                {
                    continue;
                }

                Thing target = FindDamageableThingAt(cell);
                if (target == null)
                {
                    continue;
                }

                target.TakeDamage(new DamageInfo(DamageDefOf.Deterioration, ThingDamagePerApplication));
                hits++;
            }
        }

        private Thing FindDamageableThingAt(IntVec3 cell)
        {
            List<Thing> thingsAt = map.thingGrid.ThingsListAtFast(cell);
            for (int i = 0; i < thingsAt.Count; i++)
            {
                Thing thing = thingsAt[i];
                if (thing == null || thing.Destroyed)
                {
                    continue;
                }

                if (thing.def.category == ThingCategory.Building || thing.def.EverHaulable)
                {
                    return thing;
                }
            }

            return null;
        }
    }
}
