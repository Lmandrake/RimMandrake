using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // A single weighted boon entry. Ban #1 (miasma sheet §6.1, "no gene
    // machine") is structural here, not a runtime check: there is no
    // GeneDef field on this class, so a boon can only ever be a HediffDef.
    public class RM_ForgeOnSurvivalOption
    {
        public HediffDef hediff;
        public float weight = 1f;
    }

    //   <HediffDef>
    //     <defName>Plague</defName> <!-- patched onto vanilla/campaign disease defs -->
    //     ...
    //     <comps>
    //       <li Class="RimMandrake.EnvironmentalHazards.HediffCompProperties_ForgeOnSurvival">
    //         <onlyInBiomes><li>RUT_Miasma</li></onlyInBiomes>
    //         <minPeakSeverity>0.6</minPeakSeverity>
    //         <noBoonWeight>55</noBoonWeight>
    //         <boonOptions>
    //           <li><hediff>RUT_HardenedImmunity_Plague</hediff><weight>30</weight></li>
    //           <li><hediff>RUT_FeverForged_Toughskin</hediff><weight>14</weight></li>
    //         </boonOptions>
    //       </li>
    //     </comps>
    //   </HediffDef>
    public class HediffCompProperties_ForgeOnSurvival : HediffCompProperties
    {
        // Spec M5: "fires only when the pawn's map biome matches (the
        // Miasma, uniquely, per the sheet)." Empty/null = fires wherever
        // this comp is patched on — a content-authoring bug, not something
        // this class should silently default away, hence flagged.
        public List<BiomeDef> onlyInBiomes;

        // A brush with the disease doesn't forge; surviving a real fight
        // with it does (spec M5's own INVENTED starting value).
        public float minPeakSeverity = 0.6f;

        public float noBoonWeight = 55f;
        public List<RM_ForgeOnSurvivalOption> boonOptions;

        public HediffCompProperties_ForgeOnSurvival()
        {
            compClass = typeof(RM_HediffComp_ForgeOnSurvival);
        }

        public override IEnumerable<string> ConfigErrors(HediffDef parentDef)
        {
            foreach (string err in base.ConfigErrors(parentDef))
            {
                yield return err;
            }

            if (onlyInBiomes.NullOrEmpty())
            {
                yield return "HediffCompProperties_ForgeOnSurvival has no onlyInBiomes; it would fire in every biome this hediff def can occur in, not just the Miasma.";
            }

            if (boonOptions.NullOrEmpty())
            {
                yield return "HediffCompProperties_ForgeOnSurvival has no boonOptions; every roll will land on noBoonWeight (nothing).";
            }
        }
    }

    // MIASMA_MECHANICS_1 M5 spike (miasma_kit_spec.md). Crib confirmed
    // against the live 1.6 decompile: Verse/HediffComp_RecoveryThought.cs
    // (CompPostPostRemoved, gated on !Pawn.Dead) is exactly this shape.
    //
    // That crib closes the spec's own named ❓ ("verify how removal reason
    // is distinguishable at the comp seam"): it is NOT distinguishable.
    // Read directly —
    //   Verse/Hediff.cs:608          PostRemoved() takes no reason
    //   Verse/HediffWithComps.cs:197 override calls comps[i].CompPostPostRemoved()
    //   Verse/HediffComp.cs:48       CompPostPostRemoved() takes no reason
    // — no removal call site anywhere in the decompile passes a recovery/
    // amputation/death distinction through this seam. The seam fires
    // identically for a natural cure, a body-part loss, or a debug removal.
    // So the spec's own worst-case fallback is not a fallback, it is the
    // only route: gate on ImmunityHandler directly.
    //   Verse/HediffComp_Immunizable.cs:44   FullyImmune => Immunity >= 1f
    //   Verse/Hediff.cs:177                  ShouldRemove => Severity <= 0f
    // Once a vanilla-Immunizable disease reaches full immunity its
    // SeverityChangePerDay goes negative (HediffComp_Immunizable.cs:115-118)
    // and severity decays to the ShouldRemove threshold on its own — so
    // "recovered" and "GetImmunity(def) >= 1f at removal time" are the same
    // event for every disease this comp can be patched onto. Amputation
    // removes the hediff (with the body part) at whatever immunity level it
    // was at, almost never 1f; a straight kill never reaches PostRemoved at
    // all with pawn.Dead false. The gate is real, not a guess.
    public class RM_HediffComp_ForgeOnSurvival : HediffComp
    {
        private float peakSeverity;

        public HediffCompProperties_ForgeOnSurvival Props => (HediffCompProperties_ForgeOnSurvival)props;

        public override void CompPostTick(ref float severityAdjustment)
        {
            base.CompPostTick(ref severityAdjustment);
            if (parent.Severity > peakSeverity)
            {
                peakSeverity = parent.Severity;
            }
        }

        public override void CompPostPostRemoved()
        {
            base.CompPostPostRemoved();

            Pawn pawn = base.Pawn;
            HediffCompProperties_ForgeOnSurvival props = Props;
            if (pawn == null || pawn.Dead || pawn.Map == null || props == null)
            {
                return; // death/despawn removals never forge
            }

            if (peakSeverity < props.minPeakSeverity)
            {
                return; // a brush with it doesn't forge (spec M5)
            }

            if (pawn.health == null || pawn.health.immunity == null
                || pawn.health.immunity.GetImmunity(parent.def) < 1f)
            {
                return; // not a recovery-by-immunity removal
            }

            if (!props.onlyInBiomes.NullOrEmpty()
                && (pawn.Map.Biome == null || !props.onlyInBiomes.Contains(pawn.Map.Biome)))
            {
                return;
            }

            RollBoon(pawn, props);
        }

        private void RollBoon(Pawn pawn, HediffCompProperties_ForgeOnSurvival props)
        {
            if (props.boonOptions.NullOrEmpty())
            {
                return;
            }

            float totalWeight = props.noBoonWeight;
            for (int i = 0; i < props.boonOptions.Count; i++)
            {
                totalWeight += props.boonOptions[i].weight;
            }

            if (totalWeight <= 0f)
            {
                return;
            }

            float roll = Rand.Range(0f, totalWeight);
            if (roll < props.noBoonWeight)
            {
                return; // silent — the table stays illegible, per spec M5
            }

            roll -= props.noBoonWeight;
            for (int i = 0; i < props.boonOptions.Count; i++)
            {
                RM_ForgeOnSurvivalOption option = props.boonOptions[i];
                if (roll < option.weight)
                {
                    if (option.hediff != null)
                    {
                        pawn.health.AddHediff(option.hediff);
                        if (PawnUtility.ShouldSendNotificationAbout(pawn))
                        {
                            Find.LetterStack.ReceiveLetter(
                                "RM_MiasmaBoonLetterLabel".Translate(),
                                "RM_MiasmaBoonLetterText".Translate(pawn.Named("PAWN")).AdjustedFor(pawn).CapitalizeFirst(),
                                LetterDefOf.PositiveEvent, pawn);
                        }
                    }
                    return;
                }
                roll -= option.weight;
            }
        }
    }
}
