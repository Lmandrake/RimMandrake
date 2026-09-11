using System;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.GelatinousSlime
{
    public class HediffCompProperties_Slimification : HediffCompProperties
    {
        public HediffCompProperties_Slimification()
        {
            compClass = typeof(HediffComp_Slimification);
        }
    }

    // ════════════════════════════════════════════════════════════════════
    // THE LADDER (spec §3), THE CURE GEOGRAPHY (§4) AND DISSOLUTION.
    //
    // Everything that decides how fast a creature is being read lives here,
    // because the rate depends on WHERE the creature is and that is not
    // expressible in a vanilla HediffCompProperties_SeverityPerDay.
    //
    // 🔑 WHY THIS WORKS ON A CARAVAN, WITH NO HARMONY AND NO WORLD-PAWN LEG.
    // Verified before writing, not assumed — the spec priced a "world-pawn
    // hediff ticking is real C#" leg into SPIKE A and it turns out not to
    // exist:
    //   · Caravan.TickInterval calls CheckAnyNonWorldPawns() — every pawn in a
    //     caravan IS a world pawn (RimWorld/Planet/Caravan.cs:432).
    //   · WorldPawns.WorldPawnsTick() calls DoTick() on every live world pawn
    //     (RimWorld/Planet/WorldPawns.cs:73).
    //   · Pawn.TickInterval runs health.HealthTickInterval(delta) whether or
    //     not the pawn is spawned (Verse/Pawn.cs:2893).
    //   · WorldPawns.ShouldMothball() returns false for any caravan member
    //     (RimWorld/Planet/WorldPawns.cs:365), so a travelling colonist is
    //     never mothballed and never skips a tick.
    // So a caravan pawn's hediffs tick at full rate, and `Pawn.Tile` is the
    // world tile they are standing on. The drying-biome walk is free.
    //
    // 🔴 THE THREE LAWS (spec §3):
    //   1. Colonists ride the FULL ladder. Nothing here special-cases
    //      humanlikes out of any stage, dissolution included.
    //   2. NEVER HOSTILE — and enforced positively, not just by omission:
    //      at stage 3+ this comp ENDS any aggressive or panicked mental state
    //      each check. The library files entries; it does not recruit
    //      soldiers.
    //   3. Drying biomes reverse it (§4), by DryingBiomeExtension.
    //
    // ⚠️ EVERY NUMBER BELOW EXCEPT THE 7-DAY TOTAL IS [INVENTED] and the spec
    // says so. The 7-day total is RULED.
    // ════════════════════════════════════════════════════════════════════
    public class HediffComp_Slimification : HediffComp
    {
        // Vanilla's own severity cadence: HediffComp_SeverityModifierBase
        // checks every 200 ticks and scales by 200/60000. Matching it exactly
        // keeps this hediff calibrated against every vanilla one.
        private const int CheckIntervalTicks = 200;
        private const float PerDayToPerCheck = 200f / 60000f;

        // RULED: ~7 days from first touch to dissolution on the biome.
        private const float GrowthPerDayOnSlime = 1f / 7f;

        // [INVENTED, spec §5d] The injected clock: "the concentrated slime
        // converts in ~3 days, not 7". Set by the injectable, saved with the
        // hediff, and it does not decay away — dry country still cures it.
        private const float GrowthPerDayFastClock = 1f / 3f;

        // [INVENTED, spec §3] Stage 1 self-reverses off slime terrain; stages
        // 2-3 hold in ordinary country and need dry land or the antidote.
        private const float SelfRevertPerDay = 0.5f;
        private const float SelfRevertCeiling = 0.2f;

        // Stage thresholds, mirroring the HediffDef's own <stages>.
        private const float SlickedAt = 0.2f;
        private const float HalfAbsorbedAt = 0.5f;
        private const float ReturningAt = 0.9f;

        // Saved state.
        private bool fastClock;
        private int highestStageAnnounced = -1;

        public bool FastClock
        {
            get { return fastClock; }
        }

        public void StartFastClock()
        {
            fastClock = true;
        }

        public override void CompExposeData()
        {
            base.CompExposeData();
            Scribe_Values.Look(ref fastClock, "fastClock", false);
            Scribe_Values.Look(ref highestStageAnnounced, "highestStageAnnounced", -1);
        }

        public override string CompLabelInBracketsExtra
        {
            get { return fastClock ? "injected" : null; }
        }

        public override void CompPostTickInterval(ref float severityAdjustment, int delta)
        {
            Pawn pawn = Pawn;
            if (pawn == null || pawn.Dead)
            {
                return;
            }
            if (!pawn.IsHashIntervalTick(CheckIntervalTicks, delta))
            {
                return;
            }

            try
            {
                // Law 2, made positive. Done before anything else so it still
                // happens on the tick the pawn dissolves.
                if (parent.Severity >= HalfAbsorbedAt)
                {
                    EndAnyHostileMentalState(pawn);
                }

                if (parent.Severity >= 1f)
                {
                    Dissolve(pawn);
                    return;
                }

                severityAdjustment += SeverityChangePerDay(pawn) * PerDayToPerCheck;
                AnnounceIfStageRose(pawn);
            }
            catch (Exception e)
            {
                Log.WarningOnce("[RimMandrake.GelatinousSlime] slimification tick: " + e.Message, 0x51A11);
            }
        }

        // ────────────────────────────────────────────────────────────────
        // THE RATE. One method, three cases, in priority order.
        // ────────────────────────────────────────────────────────────────
        private float SeverityChangePerDay(Pawn pawn)
        {
            BiomeDef biome = SlimeUtility.BiomeOf(pawn);

            // §4 — dry country and brine leach the film, wherever the pawn is
            // and whatever clock it is on. This wins over everything.
            if (biome != null)
            {
                DryingBiomeExtension drying = biome.GetModExtension<DryingBiomeExtension>();
                if (drying != null)
                {
                    return -Mathf.Abs(drying.decayPerDay);
                }
            }

            // On the body: it is reading you.
            if (SlimeUtility.IsBeingRead(pawn))
            {
                return fastClock ? GrowthPerDayFastClock : GrowthPerDayOnSlime;
            }

            // The injected clock runs anywhere — the concentrated dose is
            // already inside the patient and does not need the ground. That
            // is the whole point of §5d's race: carrying the injectable home
            // to your people does not buy the patient time, only witnesses.
            if (fastClock)
            {
                return GrowthPerDayFastClock;
            }

            // Ordinary country, no dose: stage 1 wipes off, stages 2-3 hold.
            if (parent.Severity < SelfRevertCeiling)
            {
                return -SelfRevertPerDay;
            }
            return 0f;
        }

        // ────────────────────────────────────────────────────────────────
        // DISSOLUTION (spec §3 stage 4, spike D). No corpse, a smear and what
        // is left of the body's own material — and it must work in a bed,
        // because that is the gene machine's failure case (§5d).
        // ────────────────────────────────────────────────────────────────
        private void Dissolve(Pawn pawn)
        {
            Map map = pawn.MapHeld;
            IntVec3 pos = pawn.PositionHeld;
            bool wasColonist = pawn.Faction == Faction.OfPlayer;
            string name = pawn.LabelShortCap;
            float bodySize = (pawn.RaceProps != null) ? pawn.RaceProps.baseBodySize : 1f;

            // Vanilla's own in-tick kill pattern (Verse/HediffComp_KillAfterDays.cs).
            pawn.Kill(null, parent);

            // Pawn.Corpse is ParentHolder as Corpse (Verse/Pawn.cs:2138) and is
            // set once the corpse has spawned. No corpse means nothing to
            // remove, which is already the outcome we want.
            Corpse corpse = pawn.Corpse;
            if (corpse != null && !corpse.Destroyed)
            {
                if (map == null)
                {
                    map = corpse.MapHeld;
                    pos = corpse.PositionHeld;
                }
                corpse.Destroy();
            }

            if (map != null && pos.IsValid && pos.InBounds(map))
            {
                if (SlimeDefs.SlimeSmear != null)
                {
                    FilthMaker.TryMakeFilth(pos, map, SlimeDefs.SlimeSmear, 3);
                }
                if (SlimeDefs.RawSlime != null)
                {
                    int count = Mathf.Clamp(Mathf.RoundToInt(bodySize * 25f), 5, 120);
                    Thing slime = ThingMaker.MakeThing(SlimeDefs.RawSlime);
                    slime.stackCount = count;
                    GenPlace.TryPlaceThing(slime, pos, map, ThingPlaceMode.Near);
                }
            }

            if (wasColonist)
            {
                Find.LetterStack.ReceiveLetter(
                    "Returned to the flow",
                    name + " has finished being read. There is no body: only a smear on the "
                    + "floor and a quantity of the same slime that was, an hour ago, a "
                    + "person. The gelatinous body keeps what it files.",
                    LetterDefOf.NegativeEvent,
                    (map != null && pos.IsValid) ? new TargetInfo(pos, map) : TargetInfo.Invalid);
            }
            else if (SlimeSettings.flavorEntryRecorded && map != null && pos.IsValid)
            {
                // The ruled flavor hook (§10, round 2): the body acknowledges
                // what it just filed. A mod-settings toggle, on by default.
                MoteMaker.ThrowText(pos.ToVector3Shifted(), map, "Entry recorded", 3.5f);
            }
        }

        // ────────────────────────────────────────────────────────────────
        // LAW 2, POSITIVELY. A placid creature does not hunt and does not
        // panic; the stage is "half-absorbed", not "enraged".
        // ────────────────────────────────────────────────────────────────
        private static void EndAnyHostileMentalState(Pawn pawn)
        {
            MentalState state = (pawn.mindState != null && pawn.mindState.mentalStateHandler != null)
                ? pawn.mindState.mentalStateHandler.CurState
                : null;
            if (state == null)
            {
                return;
            }
            MentalStateDef def = state.def;
            if (def == null)
            {
                return;
            }
            if (def.IsAggro || def == MentalStateDefOf.PanicFlee)
            {
                state.RecoverFromState();
            }
        }

        // ────────────────────────────────────────────────────────────────
        // THE ALERT CASCADE (spec §3 law 1): "Humanlikes get the alert
        // cascade (stage 1 letter, stage 2 'spend the antidote or leave'
        // alert, stage 3 red alert with the clock)."
        //
        // The letters are here; the standing alerts are Alert_Slimification
        // (SlimeAlerts.cs), which is where a persistent red bar belongs.
        // highestStageAnnounced is saved, so nothing re-announces on reload or
        // when a severity wobbles across a boundary.
        // ────────────────────────────────────────────────────────────────
        private void AnnounceIfStageRose(Pawn pawn)
        {
            if (!pawn.RaceProps.Humanlike || pawn.Faction != Faction.OfPlayer)
            {
                return;
            }

            int stage = StageIndex(parent.Severity);
            if (stage <= highestStageAnnounced)
            {
                return;
            }
            highestStageAnnounced = stage;

            switch (stage)
            {
                case 0:
                    Find.LetterStack.ReceiveLetter(
                        "Touched by the slime",
                        pawn.LabelShortCap + " has picked up a sheen that will not wipe off. "
                        + "It is the gelatinous body beginning to read them. At this stage it "
                        + "comes off on its own once they are away from slime ground — after "
                        + "the next stage it does not.",
                        LetterDefOf.NeutralEvent, pawn);
                    break;
                case 1:
                    Find.LetterStack.ReceiveLetter(
                        "Slicked",
                        pawn.LabelShortCap + " has gone past the point where walking away is "
                        + "enough. From here it holds: spend a slime antidote, or take them "
                        + "somewhere dry — desert, arid shrubland, or out to sea — and let it "
                        + "leach off on the road.",
                        LetterDefOf.NegativeEvent, pawn);
                    break;
                case 2:
                    Find.LetterStack.ReceiveLetter(
                        "Half absorbed",
                        pawn.LabelShortCap + " is being taken. They have stopped feeling pain "
                        + "and stopped minding, which is not recovery. The antidote still "
                        + "works and will keep working right up until it does not.",
                        LetterDefOf.ThreatSmall, pawn);
                    break;
                case 3:
                    Find.LetterStack.ReceiveLetter(
                        "Returning to the flow",
                        pawn.LabelShortCap + " is hours from dissolution. The antidote works "
                        + "at any stage below the last. This is the last stage.",
                        LetterDefOf.ThreatBig, pawn);
                    break;
            }
        }

        internal static int StageIndex(float severity)
        {
            if (severity >= ReturningAt) return 3;
            if (severity >= HalfAbsorbedAt) return 2;
            if (severity >= SlickedAt) return 1;
            return 0;
        }
    }

    // ════════════════════════════════════════════════════════════════════
    // Shared questions with exactly one answer each, so the exposure
    // component, the hediff comp and the seeker cannot drift apart on them.
    // ════════════════════════════════════════════════════════════════════
    public static class SlimeUtility
    {
        // Where is this pawn, biome-wise? Works on a map, in a caravan, or as
        // any other world pawn. Null when there is genuinely no answer.
        public static BiomeDef BiomeOf(Pawn pawn)
        {
            Map map = pawn.MapHeld;
            if (map != null)
            {
                return map.Biome;
            }
            PlanetTile tile = pawn.Tile;
            if (tile.Valid)
            {
                Tile t = Find.WorldGrid[tile];
                if (t != null)
                {
                    return t.PrimaryBiome;
                }
            }
            return null;
        }

        // Is the body actively reading this creature right now?
        //
        // 🔑 TERRAIN TAG, NOT A defName LIST, NOT THE BIOME. Standing on the
        // slime is what counts — a colonist on a hardened shelf inside their
        // own base is still on it, a colonist on a constructed floor they laid
        // over it is not, and any mod's own tagged ground works. Off-map, the
        // biome is the only signal there is.
        public static bool IsBeingRead(Pawn pawn)
        {
            Map map = pawn.MapHeld;
            if (map != null)
            {
                IntVec3 pos = pawn.PositionHeld;
                if (!pos.IsValid || !pos.InBounds(map))
                {
                    return false;
                }
                TerrainDef terrain = pos.GetTerrain(map);
                return terrain != null && terrain.HasTag(SlimeDefs.SlimeTerrainTag);
            }
            return BiomeOf(pawn) == SlimeDefs.GelatinousSlime && SlimeDefs.GelatinousSlime != null;
        }

        // Spec §2 "resistant by identity" and §3 law 1's acquirable
        // resistance. Both routes, one question, so nothing can honour one and
        // forget the other.
        public static bool IsResistant(Pawn pawn)
        {
            if (pawn == null || pawn.RaceProps == null)
            {
                return true;
            }
            if (!pawn.RaceProps.IsFlesh)
            {
                return true;
            }
            if (pawn.def.HasModExtension<SlimeResistantExtension>())
            {
                return true;
            }
            if (ModsConfig.BiotechActive && pawn.genes != null)
            {
                GeneDef resist = DefDatabase<GeneDef>.GetNamedSilentFail("RM_Gene_SlimeResistance");
                if (resist != null && pawn.genes.HasActiveGene(resist))
                {
                    return true;
                }
            }
            return false;
        }

        public static HediffComp_Slimification GetSlimification(Pawn pawn)
        {
            if (pawn == null || pawn.health == null || SlimeDefs.Slimification == null)
            {
                return null;
            }
            Hediff h = pawn.health.hediffSet.GetFirstHediffOfDef(SlimeDefs.Slimification);
            HediffWithComps hwc = h as HediffWithComps;
            return (hwc != null) ? hwc.TryGetComp<HediffComp_Slimification>() : null;
        }
    }
}
