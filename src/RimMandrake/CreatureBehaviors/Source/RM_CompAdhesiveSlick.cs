using System;
using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.CreatureBehaviors
{
    /// <summary>See RM_CompProperties_AdhesiveSlick for the mechanic, why it
    /// is new C#, and the "commandable" CompFlickable convention (same
    /// gating idiom as RM_CompDryFieldEmitter.IsActive /
    /// CompDWCharger — GetComp&lt;CompFlickable&gt;, act only while
    /// SwitchIsOn if one is present).</summary>
    public class RM_CompAdhesiveSlick : ThingComp
    {
        public RM_CompProperties_AdhesiveSlick Props => (RM_CompProperties_AdhesiveSlick)props;

        public override void CompTick()
        {
            base.CompTick();

            if (!RM_CreatureBehaviorsSettings.adhesiveSlickEnabled)
            {
                return;
            }

            if (!parent.Spawned || parent.Map == null)
            {
                return;
            }

            if (!parent.IsHashIntervalTick(Math.Max(1, Props.checkIntervalTicks)))
            {
                return;
            }

            if (!IsActive())
            {
                return;
            }

            if (Props.slickHediff == null)
            {
                return;
            }

            List<Pawn> caught = FindPawnsInRange();
            for (int i = 0; i < caught.Count; i++)
            {
                ApplySlick(caught[i]);
            }
        }

        private bool IsActive()
        {
            CompFlickable flick = parent.GetComp<CompFlickable>();
            if (flick != null && !flick.SwitchIsOn)
            {
                return false; // the player's own toggle — "commandable" means it can be commanded OFF
            }

            return true;
        }

        private List<Pawn> FindPawnsInRange()
        {
            List<Pawn> result = new List<Pawn>();
            IReadOnlyList<Pawn> pawns = parent.Map.mapPawns.AllPawnsSpawned;
            float radiusSq = Props.radiusCells * Props.radiusCells;

            for (int i = 0; i < pawns.Count; i++)
            {
                Pawn candidate = pawns[i];
                if (candidate == null || candidate.Dead || candidate.health == null)
                {
                    continue;
                }

                if (Props.radiusCells <= 0f)
                {
                    if (candidate.Position != parent.Position)
                    {
                        continue;
                    }
                }
                else if ((candidate.Position - parent.Position).LengthHorizontalSquared > radiusSq)
                {
                    continue;
                }

                result.Add(candidate);
            }

            return result;
        }

        private void ApplySlick(Pawn pawn)
        {
            float mult = UnityEngine.Mathf.Max(0f, RM_CreatureBehaviorsSettings.adhesiveSlickSeverityMultiplier);
            float amount = Props.severityPerScan * mult;
            if (amount <= 0f)
            {
                return;
            }

            Hediff existing = pawn.health.hediffSet.GetFirstHediffOfDef(Props.slickHediff);
            if (existing != null)
            {
                existing.Severity += amount;
                return;
            }

            Hediff hediff = HediffMaker.MakeHediff(Props.slickHediff, pawn);
            hediff.Severity = amount;
            pawn.health.AddHediff(hediff);
        }
    }
}
