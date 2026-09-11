using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // ALPHA_MECHANICS_KIT_1 item 5's pair (alpha_family_source_review.md
    // §4.5): "a generic GameCondition_ArmLatentHazard — 'add hediff X to
    // every animal on the map periodically,' data-driven on the hediff def."
    //
    // The condition itself does no damage. It arms a population with a
    // latent hediff whose own comps carry the payload — which is what makes
    // it compose with DeathActionProperties_ScaledExplosion (exploding fauna)
    // or HediffComp_PeriodicAreaAttack (a map-wide walking hazard) without
    // either knowing about this class.
    //
    //   <GameConditionDef>
    //     <defName>RM_ExampleExplodingFauna</defName>
    //     <conditionClass>RimMandrake.EnvironmentalHazards.GameCondition_ArmLatentHazard</conditionClass>
    //     ...
    //     <modExtensions>
    //       <li Class="RimMandrake.EnvironmentalHazards.ArmLatentHazardExtension">
    //         <hediffToApply>RM_ExampleVolatileBlood</hediffToApply>
    //         <intervalTicks>6000</intervalTicks>
    //         <targets>Animals</targets>
    //       </li>
    //     </modExtensions>
    //   </GameConditionDef>
    public class GameCondition_ArmLatentHazard : GameCondition
    {
        private int ticksUntilSweep;

        private ArmLatentHazardExtension ExtensionInt
        {
            get { return def != null ? def.GetModExtension<ArmLatentHazardExtension>() : null; }
        }

        public override void Init()
        {
            base.Init();

            ArmLatentHazardExtension ext = ExtensionInt;
            if (ext == null)
            {
                Log.WarningOnce(
                    "[RM EnvironmentalHazards] GameConditionDef " + (def != null ? def.defName : "(null)")
                    + " uses GameCondition_ArmLatentHazard but carries no ArmLatentHazardExtension; it will arm nothing.",
                    def != null ? def.shortHash ^ 0x5A14 : 0x5A14);
                return;
            }

            ticksUntilSweep = ext.armImmediately ? 1 : ext.intervalTicks;
        }

        public override void GameConditionTick()
        {
            base.GameConditionTick();

            ArmLatentHazardExtension ext = ExtensionInt;
            if (ext == null || ext.hediffToApply == null)
            {
                return;
            }

            if (--ticksUntilSweep > 0)
            {
                return;
            }

            ticksUntilSweep = ext.intervalTicks;

            List<Map> maps = AffectedMaps;
            for (int i = 0; i < maps.Count; i++)
            {
                Sweep(maps[i], ext);
            }
        }

        // Public so a quicktest can force one deterministic sweep.
        public void Sweep(Map map, ArmLatentHazardExtension ext)
        {
            if (map == null || ext == null || ext.hediffToApply == null)
            {
                return;
            }

            List<Pawn> pawns = new List<Pawn>(map.mapPawns.AllPawnsSpawned);

            for (int i = 0; i < pawns.Count; i++)
            {
                Pawn pawn = pawns[i];

                if (!Eligible(pawn, ext))
                {
                    continue;
                }

                // Already armed — never stack a second copy. The donor's own
                // gate, and the thing that keeps this cheap on a big map.
                if (pawn.health.hediffSet.HasHediff(ext.hediffToApply))
                {
                    continue;
                }

                if (ext.chancePerPawn < 1f && !Rand.Chance(ext.chancePerPawn))
                {
                    continue;
                }

                Hediff hediff = pawn.health.AddHediff(ext.hediffToApply);
                if (hediff != null && ext.initialSeverity > 0f)
                {
                    hediff.Severity = ext.initialSeverity;
                }
            }
        }

        private static bool Eligible(Pawn pawn, ArmLatentHazardExtension ext)
        {
            if (!HazardTargeting.Affects(pawn, ext.affects, ext.immuneThingDefs, ext.immunePawnKinds))
            {
                return false;
            }

            if (pawn.health == null || pawn.health.hediffSet == null)
            {
                return false;
            }

            switch (ext.targets)
            {
                case LatentHazardTargets.Animals:
                    return pawn.RaceProps != null && pawn.RaceProps.Animal;
                case LatentHazardTargets.Humanlikes:
                    return pawn.RaceProps != null && pawn.RaceProps.Humanlike;
                case LatentHazardTargets.NonPlayerFactionOnly:
                    return pawn.Faction != Faction.OfPlayer;
                default:
                    return true;
            }
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref ticksUntilSweep, "ticksUntilSweep", 0);
        }
    }
}
