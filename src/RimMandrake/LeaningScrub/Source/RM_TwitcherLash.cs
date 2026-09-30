using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.LeaningScrub
{
    // ════════════════════════════════════════════════════════════════════
    // LEANINGSCRUB_MECHANICS_BUILD_1 part 9 — the twitcher lash.
    //
    // "A twitcher stand strikes once at whatever comes close - one whip-crack
    // of a cane, fast as a snake - and then spends an hour drooping, visibly
    // spent, earning the next one."
    //
    // Plants only TickLong (Plant.TickLong, ~2000 ticks), far too slow for a
    // strike, so the DRIVER is a MapComponent: every LashInterval ticks it
    // walks the map's spawned pawns and looks at the plant in each pawn's cell
    // and its eight neighbours. The comp on the plant carries only data —
    // its tuning (props) and its Scribed ready-tick — plus the inspect line,
    // which comps may do on a plant because they need no ticking at all.
    //
    // Driving from pawns, not plants, keeps the cost at 9 cell reads per pawn
    // per interval no matter how many stands a map holds.
    // ════════════════════════════════════════════════════════════════════
    public class RM_CompProperties_Lash : CompProperties
    {
        public DamageDef damageDef;
        public float damageAmount = 8f;
        public float armorPenetration = 0.1f;
        public int recoveryTicks = GenDate.TicksPerHour;
        public float minGrowth = 0.5f;

        public RM_CompProperties_Lash()
        {
            compClass = typeof(RM_CompLash);
        }

        public override IEnumerable<string> ConfigErrors(ThingDef parentDef)
        {
            foreach (string e in base.ConfigErrors(parentDef))
            {
                yield return e;
            }
            if (damageDef == null)
            {
                yield return "RM_CompProperties_Lash has no damageDef.";
            }
        }
    }

    public class RM_CompLash : ThingComp
    {
        private int readyTick = -1;

        public RM_CompProperties_Lash Props => (RM_CompProperties_Lash)props;

        public bool Poised => Find.TickManager.TicksGame >= readyTick;

        private float Growth => parent is Plant plant ? plant.Growth : 1f;

        public bool TryStrike(Pawn victim)
        {
            if (!Poised || Growth < Props.minGrowth || Props.damageDef == null)
            {
                return false;
            }
            float amount = Props.damageAmount * RM_LeaningScrubSettings.twitcherLashDamageFactor;
            DamageInfo dinfo = new DamageInfo(Props.damageDef, amount, Props.armorPenetration,
                (victim.Position - parent.Position).AngleFlat, parent);
            int recovery = Mathf.RoundToInt(Props.recoveryTicks * RM_LeaningScrubSettings.twitcherLashRecoveryFactor);
            readyTick = Find.TickManager.TicksGame + Mathf.Max(60, recovery);
            victim.TakeDamage(dinfo);
            return true;
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref readyTick, "rmLashReadyTick", -1);
        }

        public override string CompInspectStringExtra()
        {
            if (!RM_WindCalendar.On(RM_LeaningScrubSettings.twitcherLashEnabled) || Growth < Props.minGrowth)
            {
                return null;
            }
            if (Poised)
            {
                return "Poised to strike.";
            }
            return "Spent, drooping: strikes again in " + (readyTick - Find.TickManager.TicksGame).ToStringTicksToPeriod() + ".";
        }
    }

    public class RM_MapComponent_TwitcherLash : MapComponent
    {
        private const int LashInterval = 30;

        private readonly List<Pawn> tmpPawns = new List<Pawn>();

        public RM_MapComponent_TwitcherLash(Map map) : base(map)
        {
        }

        public override void MapComponentTick()
        {
            if (Find.TickManager.TicksGame % LashInterval != 0 || !RM_WindCalendar.On(RM_LeaningScrubSettings.twitcherLashEnabled))
            {
                return;
            }
            // Copy: a strike can kill or down a pawn and change the live list.
            tmpPawns.Clear();
            tmpPawns.AddRange(map.mapPawns.AllPawnsSpawned);
            for (int i = 0; i < tmpPawns.Count; i++)
            {
                Pawn p = tmpPawns[i];
                if (!p.Spawned || p.Dead || p.Downed || p.Flying)
                {
                    continue;
                }
                TryLashAt(p);
            }
            tmpPawns.Clear();
        }

        private void TryLashAt(Pawn victim)
        {
            IntVec3 root = victim.Position;
            for (int i = 0; i < 9; i++)
            {
                IntVec3 c = root + GenAdj.AdjacentCellsAndInside[i];
                if (!c.InBounds(map))
                {
                    continue;
                }
                Plant plant = c.GetPlant(map);
                if (plant == null)
                {
                    continue;
                }
                RM_CompLash lash = plant.GetComp<RM_CompLash>();
                if (lash != null && lash.TryStrike(victim))
                {
                    return; // one lash per pawn per interval is plenty
                }
            }
        }
    }
}
