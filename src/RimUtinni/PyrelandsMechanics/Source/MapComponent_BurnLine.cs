using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Utinni.PyrelandsMechanics
{
    /// <summary>
    /// PYRELANDS_MECHANICS_1, mechanisms 1 and 2 — "the burn-line as a persistent
    /// migrating map presence + where-is-the-burn intelligence"
    /// (design/Jawa/worldbuilding/biomes/the_pyrelands.md, "Owed").
    ///
    /// WHAT IT IS. RimWorld instantiates one of every non-abstract MapComponent
    /// for every map (Map.FillComponents), so this needs no def and no Harmony
    /// patch; it costs one cheap biome check per map per interval on every other
    /// map in the game.
    ///
    /// THREE JOBS:
    ///
    /// 1. MEASURE. Every BurnWatchIntervalTicks it recounts the map's free-standing
    ///    fires (Fire.parent == null: a pawn burning is not a burn-line) and keeps
    ///    the count and the centroid. Everything else in this kit asks this
    ///    component rather than sweeping the thing list again — the fire-hawk's
    ///    job-giver, both incident workers.
    ///
    /// 2. KEEP THE BURN ALIVE. Sheet §5, ruled: "The burn exists somewhere on the
    ///    biome, always; only its address changes." If a Pyrelands map goes
    ///    StandingBurnQuietTicks with no fire at all, this lights ONE smoulder in
    ///    open grass, far from anything the player built. It is the biome, not an
    ///    attack: see TryReseedStandingBurn for the four gates it has to pass.
    ///
    /// 3. ATTRIBUTE. Sheet §5/§8, ruled: "The Tribes farm the fire on their
    ///    schedule, and an unplanned burn is an act of war." Attribution is exact,
    ///    not inferred: Fire.instigator is a real saved field (Verse/Fire.cs,
    ///    `public Thing instigator`, written by FireUtility.TryStartFireIn and
    ///    carried through Fire.TrySpread to every child fire). A fire whose
    ///    instigator belongs to the player accrues arson debt; a lightning fire
    ///    has a null instigator and accrues none. That is the whole of
    ///    "unplanned-burn detection" — and it deliberately catches the player's
    ///    OWN tamed fire-hawk and tamed furnace-beast, because under the reversed
    ///    ban 5 those animals are the player's responsibility (owner, 2026-09-10).
    /// </summary>
    public class MapComponent_BurnLine : MapComponent
    {
        private float arsonDebt;
        private int ticksSinceAnyFire;
        private int lastReseedAttemptTick = -99999;

        // Unsaved: re-measured on the next interval after a load.
        private int fireCount;
        private IntVec3 burnCenter = IntVec3.Invalid;
        private bool? isPyrelandsCached;

        public MapComponent_BurnLine(Map map) : base(map)
        {
        }

        /// <summary>The kit's single entry point. Null-safe for callers that may
        /// run against a map that has not finished construction.</summary>
        public static MapComponent_BurnLine For(Map map)
        {
            return map?.GetComponent<MapComponent_BurnLine>();
        }

        /// <summary>Is this map one of the standing-burn biomes? Cached: a map's
        /// biome does not change.</summary>
        public bool IsPyrelandsMap
        {
            get
            {
                if (!isPyrelandsCached.HasValue)
                {
                    isPyrelandsCached = false;
                    BiomeDef biome = map?.Biome;
                    if (biome != null)
                    {
                        for (int i = 0; i < PyrelandsTuning.PyrelandsBiomeDefNames.Length; i++)
                        {
                            if (biome.defName == PyrelandsTuning.PyrelandsBiomeDefNames[i])
                            {
                                isPyrelandsCached = true;
                                break;
                            }
                        }
                    }
                }
                return isPyrelandsCached.Value;
            }
        }

        /// <summary>Free-standing fires counted at the last measurement.</summary>
        public int FireCount => fireCount;

        /// <summary>Centroid of the burn, or IntVec3.Invalid when nothing is
        /// burning. Where a harvest party walks to.</summary>
        public IntVec3 BurnCenter => burnCenter;

        public bool AnyBurn => fireCount > 0 && burnCenter.IsValid;

        /// <summary>Accumulated player-attributed burning. The fire-raid incident's
        /// gate; reset by the raid it causes.</summary>
        public float ArsonDebt => arsonDebt;

        public void ClearArsonDebt() => arsonDebt = 0f;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref arsonDebt, "arsonDebt", 0f);
            Scribe_Values.Look(ref ticksSinceAnyFire, "ticksSinceAnyFire", 0);
            Scribe_Values.Look(ref lastReseedAttemptTick, "lastReseedAttemptTick", -99999);
        }

        public override void MapComponentTick()
        {
            base.MapComponentTick();

            // Cheapest possible early-out for the other ~dozen biomes a campaign
            // map list carries.
            if (!IsPyrelandsMap)
            {
                return;
            }
            // Spread across maps by uniqueID so two Pyrelands maps do not measure
            // on the same tick. Map is not a Thing, so Thing.IsHashIntervalTick is
            // not available here; this is the same idea written out.
            if ((Find.TickManager.TicksGame + map.uniqueID) % PyrelandsTuning.BurnWatchIntervalTicks != 0)
            {
                return;
            }

            Measure();
            AccrueArsonDebt();
            KeepTheBurnAlive();
        }

        private void Measure()
        {
            List<Thing> fires = map.listerThings.ThingsOfDef(ThingDefOf.Fire);
            int count = 0;
            int sumX = 0;
            int sumZ = 0;
            for (int i = 0; i < fires.Count; i++)
            {
                // A fire attached to a burning pawn or a burning wall is not part
                // of the burn-line; only free-standing ground fire is.
                if (fires[i] is Fire { parent: null } fire && fire.Spawned)
                {
                    count++;
                    sumX += fire.Position.x;
                    sumZ += fire.Position.z;
                }
            }

            fireCount = count;
            burnCenter = count > 0
                ? new IntVec3(sumX / count, 0, sumZ / count)
                : IntVec3.Invalid;
        }

        private void AccrueArsonDebt()
        {
            int playerAttributed = 0;
            List<Thing> fires = map.listerThings.ThingsOfDef(ThingDefOf.Fire);
            for (int i = 0; i < fires.Count; i++)
            {
                if (fires[i] is Fire { parent: null } fire && IsPlayerAttributed(fire))
                {
                    playerAttributed++;
                }
            }

            if (playerAttributed > 0)
            {
                arsonDebt = Mathf.Min(
                    PyrelandsTuning.ArsonDebtCap,
                    arsonDebt + playerAttributed * PyrelandsTuning.ArsonDebtPerPlayerFirePerCheck);
            }
            else if (arsonDebt > 0f)
            {
                arsonDebt = Mathf.Max(0f, arsonDebt - PyrelandsTuning.ArsonDebtDecayPerCheck);
            }
        }

        /// <summary>
        /// A fire counts against the colony when the thing that lit it is the
        /// colony's. Fire.instigator is carried forward into every fire the
        /// original spreads to (Fire.TrySpread passes its own instigator along),
        /// so a colonist's one careless spark owns the whole burn it becomes —
        /// which is exactly what the sheet means by "an unplanned burn".
        /// </summary>
        private static bool IsPlayerAttributed(Fire fire)
        {
            Thing instigator = fire.instigator;
            if (instigator == null)
            {
                // Lightning, the storm loop, a raider's torch — not the colony's.
                return false;
            }
            return instigator.Faction != null && instigator.Faction.IsPlayer;
        }

        private void KeepTheBurnAlive()
        {
            if (!PyrelandsMechanicsSettings.standingBurnReseedEnabled)
            {
                return;
            }
            if (fireCount > 0)
            {
                ticksSinceAnyFire = 0;
                return;
            }

            ticksSinceAnyFire += PyrelandsTuning.BurnWatchIntervalTicks;
            if (ticksSinceAnyFire < PyrelandsTuning.StandingBurnQuietTicks)
            {
                return;
            }
            if (Find.TickManager.TicksGame - lastReseedAttemptTick < PyrelandsTuning.StandingBurnRetryTicks)
            {
                return;
            }

            lastReseedAttemptTick = Find.TickManager.TicksGame;
            if (TryReseedStandingBurn())
            {
                ticksSinceAnyFire = 0;
            }
        }

        /// <summary>
        /// Light the burn's next address. Four gates, all of them about keeping
        /// this the BIOME rather than an unannounced attack:
        ///   - the cell has to be able to take a fire at all (vanilla's own
        ///     ChanceToStartFireIn, so terrain flammability and fire bulwarks are
        ///     respected without re-deriving them);
        ///   - unroofed — the standing burn walks the open grass;
        ///   - outside the player's home area;
        ///   - StandingBurnMinDistFromColony from anything the player built.
        /// No letter: the burn being somewhere is the normal state of this biome,
        /// and a letter every two days would be noise. The smoulder is lit with a
        /// null instigator, so it accrues no arson debt — the biome is not the
        /// colony's fault.
        /// </summary>
        private bool TryReseedStandingBurn()
        {
            if (!CellFinderLoose.TryGetRandomCellWith(IsLawfulSeedCell, map,
                    PyrelandsTuning.StandingBurnSeedTries, out IntVec3 cell))
            {
                return false;
            }

            return FireUtility.TryStartFireIn(cell, map, PyrelandsTuning.SmoulderFireSize, null);
        }

        private bool IsLawfulSeedCell(IntVec3 c)
        {
            if (!c.InBounds(map) || c.Fogged(map) || c.Roofed(map))
            {
                return false;
            }
            if (FireUtility.ChanceToStartFireIn(c, map) <= 0f)
            {
                return false;
            }
            if (map.areaManager.Home[c])
            {
                return false;
            }
            return FarFromAnythingTheColonyBuilt(c);
        }

        private bool FarFromAnythingTheColonyBuilt(IntVec3 c)
        {
            float minDistSq = PyrelandsTuning.StandingBurnMinDistFromColony
                            * PyrelandsTuning.StandingBurnMinDistFromColony;

            List<Building> buildings = map.listerBuildings.allBuildingsColonist;
            for (int i = 0; i < buildings.Count; i++)
            {
                if ((buildings[i].Position - c).LengthHorizontalSquared < minDistSq)
                {
                    return false;
                }
            }
            return true;
        }
    }
}
