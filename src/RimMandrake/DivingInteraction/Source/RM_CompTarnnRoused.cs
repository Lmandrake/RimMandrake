using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.DivingInteraction
{
    // ════════════════════════════════════════════════════════════════════
    // CHILL_GARDEN_DEFENSE_1 — what makes a woken Tarnn actually dangerous.
    //
    // RM_Tarnn's OWN base stats (RM_TheChillFloorLife.xml, unowned by this
    // item) are: MoveSpeed 0.3 (cannot meaningfully chase or reposition),
    // one melee tool at power 1 / cooldown 3.5s (~0.29 raw dps before armor
    // — negligible), combatPower 6. That is correct for what it was built to
    // be: sessile floor-life "scenery," never a fighter. But it means five
    // dormant Tarnn woken and set hostile would, on melee alone, be
    // essentially harmless — failing the ruling's own "shocking" and
    // "genuinely frightening" language. This comp is the sleeper-wake
    // BEHAVIOR item's actual job: it does not touch RM_Tarnn's identity,
    // art, roster membership or base stats, it gives a WOKEN Tarnn a
    // temporary combat capability that only exists while roused — the same
    // "conductive frost / ground current" theme the Iliss arc uses, just
    // sourced from the lattice's own crystal structure instead.
    //
    // roused is set ONLY by RM_MapComponent_ChillGardenDefense.FireTier2Wake
    // — never true by default, never true from ordinary map load. Once set
    // it is never cleared (Scribed), matching the ruling's "the tarnn that
    // fought are now just... fought" — a woken Tarnn that survives simply
    // remains an ordinary, if now dangerous-if-approached, piece of wildlife
    // forever; there is no re-dormancy and no repeat wave.
    //
    // OVERCOMABLE MATH (documented once here, not re-derived per number):
    //   Per zap: Rand.Range(ZapDamageMin, ZapDamageMax) ElectricalBurn,
    //   average 9, every CompTickRare (250 ticks ≈ 4.17s at 1x) — ≈2.16 dps
    //   per roused Tarnn. FireTier2Wake caps a single wake at 3-5 Tarnn
    //   (WakeCountRange), so worst case (5, all with a target in range)
    //   ≈10.8 combined dps, plus negligible melee. Compare: a vanilla early-
    //   game raid of 3-5 raiders with firearms typically runs 25-50+
    //   combined dps and can reposition/flank; this skirmish cannot chase
    //   (Tarnn MoveSpeed 0.3) and each Tarnn's own HP is low (baseHealthScale
    //   0.7 on a small Snake body — a handful of hits from any real weapon
    //   downs one), so a prepared squad can end the fight in well under a
    //   minute of real combat, capping total exposure at roughly 100-250
    //   damage spread across however many colonists engage — bruising,
    //   plausibly needing medical attention, never a wipe for anyone with
    //   more than starting-tier gear. If this reads as too soft or too hard
    //   after a real playtest, ZapDamageMin/Max and WakeCountRange
    //   (RM_MapComponent_ChillGardenDefense.cs) are the two knobs to retune
    //   — erring toward this current (weaker) reading was the explicit
    //   calibration ruling ("if unsure, err toward weaker").
    // ════════════════════════════════════════════════════════════════════
    public class RM_CompTarnnRoused : ThingComp
    {
        private const int ZapIntervalTicks = 250; // CompTickRare's own cadence — no separate hand-rolled timer needed
        private const float ZapRadius = 6f;
        private const float ZapDamageMin = 6f;
        private const float ZapDamageMax = 12f;

        private bool roused;

        public CompProperties_TarnnRoused Props => (CompProperties_TarnnRoused)props;

        /// <summary>
        /// Called exactly once, by RM_MapComponent_ChillGardenDefense at the
        /// moment this Tarnn is woken. Idempotent — calling it again (e.g. a
        /// later wake targeting an already-roused survivor) is harmless.
        /// </summary>
        public void Rouse()
        {
            roused = true;
        }

        public override void CompTickRare()
        {
            base.CompTickRare();
            if (!roused)
            {
                return;
            }
            if (!RM_DivingSettings.masterEnabled || !RM_DivingSettings.chillGardenDefenseEnabled)
            {
                return; // toggled off mid-fight — degrade to the base def's own (negligible) melee, never strand the player mid-incident with an unkillable turret
            }
            Pawn tarnn = parent as Pawn;
            if (tarnn == null || tarnn.Dead || !tarnn.Spawned || tarnn.Downed)
            {
                return;
            }

            Pawn target = FindNearestTarget(tarnn);
            if (target == null)
            {
                return;
            }

            float dmg = Rand.Range(ZapDamageMin, ZapDamageMax);
            target.TakeDamage(new DamageInfo(DamageDefOf.ElectricalBurn, dmg));

            Vector3 mid = Vector3.Lerp(tarnn.DrawPos, target.DrawPos, 0.5f);
            FleckMaker.ThrowLightningGlow(mid, tarnn.Map, 1f);
            FleckMaker.ThrowMicroSparks(target.DrawPos, tarnn.Map);
        }

        private Pawn FindNearestTarget(Pawn tarnn)
        {
            Map map = tarnn.Map;
            if (map == null)
            {
                return null;
            }
            Pawn nearest = null;
            float bestDist = ZapRadius;
            IReadOnlyList<Pawn> pawns = map.mapPawns.AllPawnsSpawned;
            for (int i = 0; i < pawns.Count; i++)
            {
                Pawn p = pawns[i];
                if (p == null || p.Dead || !p.Spawned || p == tarnn)
                {
                    continue;
                }
                if (!p.RaceProps.Humanlike && !p.RaceProps.IsMechanoid)
                {
                    continue; // never zaps other floor life — this is a defence against the offender, not friendly fire on the ecosystem
                }
                float d = p.Position.DistanceTo(tarnn.Position);
                if (d > bestDist)
                {
                    continue;
                }
                bestDist = d;
                nearest = p;
            }
            return nearest;
        }

        public override string CompInspectStringExtra()
        {
            return roused ? "RM_ChillGardenDefense_TarnnRoused".Translate() : null;
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref roused, "roused", false);
        }
    }

    public class CompProperties_TarnnRoused : CompProperties
    {
        public CompProperties_TarnnRoused()
        {
            compClass = typeof(RM_CompTarnnRoused);
        }
    }
}
