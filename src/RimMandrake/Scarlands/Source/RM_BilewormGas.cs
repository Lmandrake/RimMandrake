using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Scarlands
{
    // BILEWORM_CORPSE_ROT_1. The bileworm's description promises it: "murder on the dead. Anything it passes near
    // rots in minutes into a black, reeking fluid, which the bileworm then happily drinks." The donor did this with
    // two VEF comps that were dropped at the port (WARSCAR_SHEET_DONOR_PORT_1); this is ours.
    //   - every corpse within rotRadius rots rotTicksPerTick times faster than its own clock, frozen or not (it is
    //     the gas doing it, not the air);
    //   - a corpse that reaches Rotting within drinkRadius dissolves into corpse bile (filth, the readable sign) and
    //     the worm drinks it: food need up by its body size times nutritionPerBodySize;
    //   - a colonist's corpse dissolving says so in a message, so nobody vanishes without a sign;
    //   - a colonist within stenchRadius gets the stench memory (renewed, never stacked).
    // All numbers PROVISIONAL. Settings: bilewormGasEnabled (off = an ordinary slug).

    public class RM_CompProperties_BilewormGas : CompProperties
    {
        public float rotRadius = 6f;
        public float drinkRadius = 1.9f;
        public float stenchRadius = 10f;
        public float rotTicksPerTick = 40f;
        public float nutritionPerBodySize = 0.5f;
        public int intervalTicks = 250;
        public ThingDef bileFilth;
        public ThoughtDef stenchThought;

        public RM_CompProperties_BilewormGas()
        {
            compClass = typeof(RM_CompBilewormGas);
        }
    }

    /// <summary>Pure arithmetic, so the rules can be read and checked without a map.</summary>
    public static class RM_BilewormMath
    {
        /// <summary>Rot progress the gas adds over <paramref name="ticks"/>: independent of temperature.</summary>
        public static float RotAdded(int ticks, float rotTicksPerTick)
        {
            return ticks <= 0 || rotTicksPerTick <= 0f ? 0f : ticks * rotTicksPerTick;
        }

        /// <summary>A corpse dissolves once it is rotting (or past it) and close enough to drink.</summary>
        public static bool Dissolves(float rotProgress, int ticksToRotStart, float distSq, float drinkRadius)
        {
            return rotProgress >= ticksToRotStart && distSq <= drinkRadius * drinkRadius;
        }

        public static float Nutrition(float corpseBodySize, float perBodySize)
        {
            return Mathf.Max(0f, corpseBodySize) * Mathf.Max(0f, perBodySize);
        }
    }

    public class RM_CompBilewormGas : ThingComp
    {
        private RM_CompProperties_BilewormGas Props => (RM_CompProperties_BilewormGas)props;

        public override void CompTickInterval(int delta)
        {
            base.CompTickInterval(delta);
            if (!RM_WarscarSettings.bilewormGasEnabled || !parent.IsHashIntervalTick(Props.intervalTicks, delta))
            {
                return;
            }
            Pawn worm = parent as Pawn;
            if (worm == null || !worm.Spawned || worm.Dead)
            {
                return;
            }
            Map map = worm.Map;
            IntVec3 at = worm.Position;
            float rotSq = Props.rotRadius * Props.rotRadius;
            List<Thing> corpses = map.listerThings.ThingsInGroup(ThingRequestGroup.Corpse);
            List<Corpse> dissolve = null;
            for (int i = 0; i < corpses.Count; i++)
            {
                if (!(corpses[i] is Corpse corpse) || !corpse.Spawned)
                {
                    continue;
                }
                float distSq = (corpse.Position - at).LengthHorizontalSquared;
                if (distSq > rotSq)
                {
                    continue;
                }
                CompRottable rot = corpse.TryGetComp<CompRottable>();
                if (rot == null || !rot.Active)
                {
                    continue;
                }
                if (rot.Stage == RotStage.Fresh)
                {
                    rot.RotProgress = Mathf.Min(rot.PropsRot.TicksToRotStart,
                        rot.RotProgress + RM_BilewormMath.RotAdded(Props.intervalTicks, Props.rotTicksPerTick));
                }
                if (RM_BilewormMath.Dissolves(rot.RotProgress, rot.PropsRot.TicksToRotStart, distSq, Props.drinkRadius))
                {
                    (dissolve ?? (dissolve = new List<Corpse>())).Add(corpse);
                }
            }
            if (dissolve != null)
            {
                for (int i = 0; i < dissolve.Count; i++)
                {
                    Drink(worm, dissolve[i]);
                }
            }
            Stench(worm);
        }

        private void Drink(Pawn worm, Corpse corpse)
        {
            Pawn dead = corpse.InnerPawn;
            IntVec3 cell = corpse.Position;
            Map map = corpse.Map;
            float size = dead?.BodySize ?? 1f;
            if (dead != null && dead.RaceProps.Humanlike && dead.Faction == Faction.OfPlayer)
            {
                Messages.Message("A bileworm has dissolved " + dead.LabelShort + "'s body into corpse bile and is drinking it.",
                    new TargetInfo(cell, map), MessageTypeDefOf.NegativeEvent);
            }
            corpse.Destroy(DestroyMode.Vanish);
            if (Props.bileFilth != null)
            {
                int count = Mathf.Clamp(Mathf.RoundToInt(size * 3f), 1, 6);
                for (int i = 0; i < count; i++)
                {
                    FilthMaker.TryMakeFilth(cell, map, Props.bileFilth);
                }
            }
            if (worm.needs?.food != null)
            {
                worm.needs.food.CurLevel += RM_BilewormMath.Nutrition(size, Props.nutritionPerBodySize);
            }
        }

        private void Stench(Pawn worm)
        {
            if (Props.stenchThought == null)
            {
                return;
            }
            IReadOnlyList<Pawn> colonists = worm.Map.mapPawns.FreeColonistsSpawned;
            float sq = Props.stenchRadius * Props.stenchRadius;
            for (int i = 0; i < colonists.Count; i++)
            {
                Pawn p = colonists[i];
                if (p.needs?.mood == null || (p.Position - worm.Position).LengthHorizontalSquared > sq)
                {
                    continue;
                }
                Thought_Memory had = p.needs.mood.thoughts.memories.GetFirstMemoryOfDef(Props.stenchThought);
                if (had != null)
                {
                    had.Renew();
                }
                else
                {
                    p.needs.mood.thoughts.memories.TryGainMemory(Props.stenchThought);
                }
            }
        }
    }
}
