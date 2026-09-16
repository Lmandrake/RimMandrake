using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Utinni.PyrelandsMechanics
{
    /// <summary>
    /// PYRELANDS_FIRE_CADENCE_1 — the biome clock.
    ///
    /// 🔑 OWNER, 2026-09-14, verbatim: "the fires should come every few days, not
    /// a rare event." That is a CADENCE, and it is a different mechanism from
    /// MapComponent_BurnLine's standing-burn reseed, which this class does not
    /// replace:
    ///
    ///   - the RESEED is a floor. It only ever fires when the map has been
    ///     completely fireless for two days, and it lights ONE smoulder. Its job
    ///     is "the burn exists somewhere, always".
    ///   - the FRONT (here) is the clock. Every 2-4 days, whatever else is
    ///     burning, a line of grass goes up and walks. Its job is "the grass
    ///     burns on a schedule you can plan around".
    ///
    /// A map with a healthy standing burn never triggers the reseed at all, and
    /// under the old code that map saw nothing happen for weeks — which is
    /// exactly the "rare event" the owner ruled against.
    ///
    /// 🔴 IT LIGHTS A LINE, NOT A POINT. One smoulder in dry grass usually dies
    /// to vanilla's own fire maths before it becomes anything. A front is
    /// FireFrontWidthCells ignitions on one bearing, so the thing that walks off
    /// downwind is a burn-line rather than a candle. Every cell still goes
    /// through vanilla's FireUtility.ChanceToStartFireIn, so terrain
    /// flammability, firebreaks (RM_FE_FirebreakLine) and the existing fire
    /// chain are all respected without re-deriving any of them — this is how it
    /// "burns THROUGH quickgrass" rather than around it.
    ///
    /// 🔑 NULL INSTIGATOR, deliberately. MapComponent_BurnLine.IsPlayerAttributed
    /// reads Fire.instigator, so a front lit by the biome accrues no arson debt
    /// and provokes no Tribe raid. The biome is not the colony's fault.
    ///
    /// Owned and ticked by MapComponent_BurnLine (one biome check, one tick gate,
    /// one ExposeData for the whole kit) rather than being a second MapComponent:
    /// RimWorld instantiates every MapComponent on every map in the save, and one
    /// that early-outs is still one more virtual call per map per tick.
    /// </summary>
    public class PyrelandsFireFront
    {
        private readonly Map map;

        /// <summary>Absolute game tick the next front is due. -1 means "not
        /// scheduled yet" — set on the first tick after a load or a map gen, so
        /// a fresh map does not burn on tick one.</summary>
        private int nextFrontTick = -1;

        public PyrelandsFireFront(Map map)
        {
            this.map = map;
        }

        public void ExposeData()
        {
            Scribe_Values.Look(ref nextFrontTick, "fireFrontNextTick", -1);
        }

        /// <summary>Called from MapComponent_BurnLine's already-gated tick: this
        /// only ever runs on a Pyrelands map, on the watch interval.</summary>
        public void Tick()
        {
            if (!PyrelandsMechanicsSettings.fireFrontEnabled)
            {
                // Off means off, but keep the clock honest: re-arm from now, so
                // switching the mechanism back on does not fire instantly with a
                // months-overdue timer.
                nextFrontTick = -1;
                return;
            }

            int now = Find.TickManager.TicksGame;
            if (nextFrontTick < 0)
            {
                Schedule(now);
                return;
            }
            if (now < nextFrontTick)
            {
                return;
            }

            Schedule(now);

            // DEEP_TRIBES_FIRE_RITE_1 — sometimes this scheduled burn is not the
            // biome's own, it is the Tribes'. The rite REPLACES the front rather
            // than adding to it: the party walks in and lights it themselves when
            // they arrive, so the clock has fired either way. Anything that stops
            // the rite being sendable (no Tribes in this world, at war, nowhere to
            // walk in from) falls straight through to the plain front below, which
            // is what "all-off degrades to the fire clock" means.
            if (TryRunRite())
            {
                return;
            }

            int lit = TryStartFront();
            if (lit > 0 && PyrelandsMechanicsSettings.fireFrontLetterEnabled)
            {
                Find.LetterStack.ReceiveLetter(
                    "RUT_FireFrontLetterLabel".Translate(),
                    "RUT_FireFrontLetterText".Translate(),
                    LetterDefOf.NegativeEvent,
                    new TargetInfo(lastOrigin, map));
            }
        }

        /// <summary>
        /// Re-arm the clock. The interval is randomized per front rather than
        /// fixed, so the player learns "every few days" and never learns a tick
        /// count to farm.
        /// </summary>
        private void Schedule(int now)
        {
            float minDays = PyrelandsMechanicsSettings.fireFrontMinDays;
            float maxDays = PyrelandsMechanicsSettings.fireFrontMaxDays;
            if (maxDays < minDays)
            {
                maxDays = minDays;
            }
            nextFrontTick = now + Mathf.RoundToInt(
                Rand.Range(minDays, maxDays) * GenDate.TicksPerDay);
        }

        private IntVec3 lastOrigin = IntVec3.Invalid;

        /// <summary>
        /// Light the front. Returns how many cells actually took, which is 0 on a
        /// map that is soaked, paved or entirely roofed — a legitimate outcome,
        /// not an error, and the clock has already been re-armed either way.
        /// </summary>
        private int TryStartFront()
        {
            if (!TryFindOrigin(out IntVec3 origin))
            {
                return 0;
            }
            lastOrigin = origin;
            return IgniteAt(origin, null);
        }

        /// <summary>
        /// DEEP_TRIBES_FIRE_RITE_1 — roll the rite, and send it if it rolls.
        /// Returns true only when a party is actually standing on the map with a
        /// Lord; every other outcome returns false so the caller lights the plain
        /// front instead and the clock never silently skips a beat.
        /// </summary>
        private bool TryRunRite()
        {
            if (!PyrelandsMechanicsSettings.fireRiteEnabled)
            {
                return false;
            }
            if (Rand.Value >= PyrelandsMechanicsSettings.fireRiteFraction)
            {
                return false;
            }
            if (!TryFindOrigin(out IntVec3 origin))
            {
                return false;
            }
            lastOrigin = origin;
            return PyrelandsFireRite.TrySend(map, origin);
        }

        /// <summary>
        /// Light a front on one bearing through <paramref name="origin"/>.
        ///
        /// 🔴 The instigator is the whole difference between the biome's front and
        /// the Tribes' rite. Null is the biome (no arson debt, nobody's fault);
        /// the lead harvester is the rite (still no arson debt — see
        /// MapComponent_BurnLine.IsPlayerAttributed, which only counts fires whose
        /// instigator belongs to the PLAYER — but every burn that follows now
        /// carries their name, because Fire.TrySpread hands the instigator down to
        /// every child fire).
        /// </summary>
        internal int IgniteAt(IntVec3 origin, Thing instigator)
        {
            if (!origin.IsValid)
            {
                return 0;
            }

            // A bearing for the LINE itself; the burn then walks off it in
            // whichever direction vanilla's own spread maths prefers.
            float angle = Rand.Range(0f, 360f);
            Vector3 step = Quaternion.AngleAxis(angle, Vector3.up) * Vector3.forward;

            int width = PyrelandsMechanicsSettings.fireFrontWidthCells;
            int half = width / 2;
            int lit = 0;

            for (int i = -half; i <= half; i++)
            {
                IntVec3 cell = origin + (step * i).ToIntVec3();
                if (!IsLawfulFrontCell(cell))
                {
                    continue;
                }
                if (FireUtility.TryStartFireIn(cell, map, PyrelandsTuning.FireFrontFireSize, instigator))
                {
                    lit++;
                }
            }

            return lit;
        }

        /// <summary>
        /// Where the front starts. Weighted toward ember-grass because ember-grass
        /// IS the biome's fuel ladder (src/RimMandrake/Pyrelands/Defs/
        /// ThingDefs_Plants/EmberGrass.xml) — a front that starts in the fuel is a
        /// front that goes somewhere.
        ///
        /// Two passes, not a weighted sum: sample for an ember-grass cell first,
        /// and only fall back to any lawful flammable cell if the map has none.
        /// Cheaper than scoring the whole map and it degrades to the reseed's own
        /// behaviour on a map where the plant never established.
        /// </summary>
        private bool TryFindOrigin(out IntVec3 origin)
        {
            ThingDef emberGrass = DefDatabase<ThingDef>.GetNamedSilentFail("RM_FE_Plant_EmberGrass");
            if (emberGrass != null)
            {
                List<Thing> grass = map.listerThings.ThingsOfDef(emberGrass);
                if (grass.Count > 0)
                {
                    for (int i = 0; i < PyrelandsTuning.FireFrontEmberGrassTries; i++)
                    {
                        IntVec3 c = grass[Rand.Range(0, grass.Count)].Position;
                        if (IsLawfulFrontCell(c))
                        {
                            origin = c;
                            return true;
                        }
                    }
                }
            }

            return CellFinderLoose.TryGetRandomCellWith(
                IsLawfulFrontCell, map, PyrelandsTuning.FireFrontSeedTries, out origin);
        }

        /// <summary>
        /// The same four gates the standing-burn reseed passes — this is the
        /// biome, not an attack. Shared with MapComponent_BurnLine so a change to
        /// "where the biome may light" only ever has to be made once.
        /// </summary>
        private bool IsLawfulFrontCell(IntVec3 c)
        {
            return MapComponent_BurnLine.For(map)?.IsLawfulBurnCell(c) ?? false;
        }
    }
}
