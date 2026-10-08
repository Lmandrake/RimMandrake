using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Pyrelands
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

        // PYRELANDS_ULLAI_GIANT_BUILD_1: where the burn WAS. One burn-centre sample per hour while anything burns,
        // ten days kept. Ash terrain never reverts (AshLadder.xml), so terrain alone cannot say which black is
        // fresh; this record can. The ullai graze where it burned about two days ago.
        private List<int> burnHistTicks = new List<int>();
        private List<IntVec3> burnHistCells = new List<IntVec3>();
        public const int BurnHistoryIntervalTicks = 2500;
        public const int BurnHistoryKeepTicks = 600000;

        /// <summary>PYRELANDS_FIRE_CADENCE_1 — the biome's fire clock. Owned here
        /// rather than being its own MapComponent so the biome check, the tick
        /// gate and the save block are paid for once. See PyrelandsFireFront for
        /// why a clock and a reseed are two different mechanisms.</summary>
        private readonly PyrelandsFireFront fireFront;

        public MapComponent_BurnLine(Map map) : base(map)
        {
            fireFront = new PyrelandsFireFront(map);
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

        public bool AnyBurn => RM_BurnKernel.AnyBurn(fireCount, burnCenter.IsValid);

        private void RecordHistory()
        {
            if (!burnCenter.IsValid)
            {
                return;
            }
            RM_BurnKernel.RecordHistory(burnHistTicks, burnHistCells, Find.TickManager.TicksGame, burnCenter,
                BurnHistoryIntervalTicks, BurnHistoryKeepTicks);
        }

        /// <summary>Where the burn was about <paramref name="ticksAgo"/> ago: the newest sample at least that
        /// old, else the oldest sample kept (the freshest black we know of), else Invalid.</summary>
        public IntVec3 BurnCenterAgo(int ticksAgo)
        {
            int at = RM_BurnKernel.HistoryIndexAgo(burnHistTicks, Find.TickManager.TicksGame, ticksAgo);
            return at >= 0 ? burnHistCells[at] : IntVec3.Invalid;
        }

        /// <summary>Accumulated player-attributed burning. The fire-raid incident's
        /// gate; reset by the raid it causes.</summary>
        public float ArsonDebt => arsonDebt;

        public void ClearArsonDebt() => arsonDebt = 0f;

        /// <summary>DEEP_TRIBES_FIRE_RITE_1 — light the fire clock's line where a
        /// harvest party is standing, attributed to them. The fire front is
        /// private to this component so "where the biome may light" stays stated
        /// once; this is the one door through it.</summary>
        public int IgniteRiteFront(IntVec3 origin, Thing instigator)
        {
            return fireFront.IgniteAt(origin, instigator);
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref arsonDebt, "arsonDebt", 0f);
            Scribe_Values.Look(ref ticksSinceAnyFire, "ticksSinceAnyFire", 0);
            Scribe_Values.Look(ref lastReseedAttemptTick, "lastReseedAttemptTick", -99999);
            Scribe_Collections.Look(ref burnHistTicks, "burnHistTicks", LookMode.Value);
            Scribe_Collections.Look(ref burnHistCells, "burnHistCells", LookMode.Value);
            if (Scribe.mode == LoadSaveMode.PostLoadInit && (burnHistTicks == null || burnHistCells == null
                || burnHistTicks.Count != burnHistCells.Count))
            {
                burnHistTicks = new List<int>();
                burnHistCells = new List<IntVec3>();
            }
            fireFront.ExposeData();
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
            if (!RM_BurnKernel.MeasureDue(Find.TickManager.TicksGame, map.uniqueID, PyrelandsTuning.BurnWatchIntervalTicks))
            {
                return;
            }

            if (!RM_PyrelandsSettings.pyrelandsEnabled)
            {
                // Master switch off: nothing runs, but the fire clock must still be told it is off, or it keeps a stale
                // deadline and fires a front the instant the switch is turned back on (PyrelandsFireFront.Tick re-arms
                // to -1 when disabled).
                fireFront.Tick();
                return;
            }

            // MOD_OPTIONS_RETROFIT_1: burnLineEnabled and fireClockEnabled are
            // independent switches (§6a) — off on one leaves the other running.
            // fireFront.Tick() self-gates on fireClockEnabled (and re-arms its
            // own clock when the toggle flips), so it is always called here.
            if (RM_PyrelandsSettings.burnLineEnabled)
            {
                Measure();
                AccrueArsonDebt();
                KeepTheBurnAlive();
            }
            fireFront.Tick();
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
            burnCenter = RM_BurnKernel.Centroid(sumX, sumZ, count, out int cx, out int cz)
                ? new IntVec3(cx, 0, cz)
                : IntVec3.Invalid;
            RecordHistory();
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

            arsonDebt = RM_BurnKernel.ArsonStep(arsonDebt, playerAttributed, PyrelandsTuning.ArsonDebtPerPlayerFirePerCheck,
                PyrelandsTuning.ArsonDebtCap, PyrelandsTuning.ArsonDebtDecayPerCheck);
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
            // Lightning, the storm loop, a raider's torch — not the colony's.
            Thing instigator = fire.instigator;
            Faction faction = instigator?.Faction;
            return RM_BurnKernel.PlayerAttributed(instigator != null, faction != null, faction != null && faction.IsPlayer);
        }

        private void KeepTheBurnAlive()
        {
            // Gated by the caller (burnLineEnabled) — no inner check here.
            if (RM_BurnKernel.KeepAlive(fireCount, ref ticksSinceAnyFire, PyrelandsTuning.BurnWatchIntervalTicks,
                    PyrelandsTuning.StandingBurnQuietTicks, Find.TickManager.TicksGame, lastReseedAttemptTick,
                    PyrelandsTuning.StandingBurnRetryTicks) != RM_ReseedDecision.Reseed)
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
            if (!CellFinderLoose.TryGetRandomCellWith(IsLawfulBurnCell, map,
                    PyrelandsTuning.StandingBurnSeedTries, out IntVec3 cell))
            {
                return false;
            }

            return FireUtility.TryStartFireIn(cell, map, PyrelandsTuning.SmoulderFireSize, null);
        }

        /// <summary>Where the BIOME may light — as opposed to where a raider or a
        /// colonist may. Shared with PyrelandsFireFront so "the burn starts out in
        /// the grass, away from what you built" is stated once.</summary>
        internal bool IsLawfulBurnCell(IntVec3 c)
        {
            bool inBounds = c.InBounds(map);
            bool fogged = inBounds && c.Fogged(map);
            bool roofed = inBounds && !fogged && c.Roofed(map);
            float chance = inBounds && !fogged && !roofed ? FireUtility.ChanceToStartFireIn(c, map) : 0f;
            bool home = chance > 0f && map.areaManager.Home[c];
            bool far = chance > 0f && !home && FarFromAnythingTheColonyBuilt(c);
            return RM_BurnKernel.LawfulBurnCell(inBounds, fogged, roofed, chance, home, far);
        }

        private bool FarFromAnythingTheColonyBuilt(IntVec3 c)
        {
            List<Building> buildings = map.listerBuildings.allBuildingsColonist;
            for (int i = 0; i < buildings.Count; i++)
            {
                if (RM_BurnKernel.TooCloseToColony((buildings[i].Position - c).LengthHorizontalSquared, PyrelandsTuning.StandingBurnMinDistFromColony))
                {
                    return false;
                }
            }
            return true;
        }
    }
}
