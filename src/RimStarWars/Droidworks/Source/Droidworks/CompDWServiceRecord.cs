using RimWorld;
using Verse;

namespace RimMandrake.StarWars.Droidworks
{
    public class CompProperties_DWServiceRecord : CompProperties
    {
        /// <summary>
        /// How long a droid must go unwiped before the FIRST idiosyncrasy
        /// arrives. 2 years, which is the design doc's own worked example
        /// (DROID_UNIFIED_FRAMEWORK_DESIGN.md §5, packet E2's row: "2 years
        /// unwiped -> traits accrete").
        ///
        /// GenDate.TicksPerYear is 3,600,000 - read from RimWorld's own
        /// GenDate.cs, not assumed (60 days x 60,000 ticks per day). So this is
        /// 7,200,000 ticks.
        /// </summary>
        public int firstDriftTicks = 2 * GenDate.TicksPerYear;

        /// <summary>
        /// Gap between later idiosyncrasies: 1.5 years (5,400,000 ticks). With
        /// maxAccreted 3 that puts the ladder at 2 y / 3.5 y / 5 y, which lands
        /// the last one at about the outer edge of a long campaign - a droid
        /// that has been with the colony from the start and never been opened up
        /// is fully a person by the time the colony is five years old, and
        /// nothing after that is a surprise the player has already seen twice.
        /// FOUNDRY's number: the design doc fixes only the first threshold.
        /// </summary>
        public int driftIntervalTicks = GenDate.TicksPerYear * 3 / 2;

        /// <summary>
        /// Ceiling on accreted idiosyncrasies. The pool is larger than this on
        /// purpose (so two five-year droids of the same family are not the same
        /// droid), but a pawn carrying an unbounded pile of traits stops reading
        /// as a personality and starts reading as a stat sheet.
        /// </summary>
        public int maxAccreted = 3;

        /// <summary>
        /// Whether the first drift also moves a Programmable droid up to
        /// Sapient. On by default because B1 already declared this the
        /// mechanism: DroidFormatTierUtility.DefaultTier's own comment reads
        /// "sapience is what a long-unwiped droid DRIFTS into
        /// (DROIDWORKS_SERVICE_RECORD_DRIFT_1, packet E2) rather than what it
        /// ships as". Turned off per-race in XML for a chassis that should never
        /// wake up.
        /// </summary>
        public bool promoteToSapient = true;

        public CompProperties_DWServiceRecord()
        {
            compClass = typeof(CompDWServiceRecord);
        }
    }

    /// <summary>
    /// DROIDWORKS_SERVICE_RECORD_DRIFT_1 (packet E2), unit 11 of
    /// design/Jawa/droid_system_build_spec.md: "Personality drift:
    /// CompServiceRecord - time-since-wipe accretes idiosyncrasy traits from
    /// chassis-weighted pools; long-unwiped droids are PEOPLE."
    ///
    /// 🔑 THIS IS NOT THE HARDWARE-QUIRK MECHANISM (B10,
    /// DROIDWORKS_WIPE_SEVERITY_1) AND MUST NOT BE CONFLATED WITH IT:
    ///
    ///                  trigger              on a memory wipe
    ///   quirk (B10)    wipe severity        kept - quirks only ever accrete
    ///   drift (E2)     time UNWIPED         erased, and the clock resets
    ///
    /// A droid therefore carries up to three separate layers of personality:
    /// its ONE guaranteed chassis trait from E1 (PawnKindDef.forcedTraits, set
    /// at generation by gen_droidworks_defs.py's FAMILY_TRAIT_BIAS), whatever
    /// quirks its wipes have left it, and 0-3 idiosyncrasies it has grown here.
    ///
    /// ── THE CLOCK ────────────────────────────────────────────────────────────
    /// Stored as the ABSOLUTE game tick of the last reset, not as an accumulated
    /// counter. That is the load-bearing choice in this file:
    ///   * a comp only ticks while its pawn ticks, so an accumulator would stop
    ///     for a droid sitting in a caravan or on an unloaded map, and a droid's
    ///     service life would depend on whether the player was looking at it;
    ///   * an absolute tick is also immune to the check cadence below - moving
    ///     the check from daily to hourly would change nothing about WHEN a
    ///     droid is two years old.
    ///
    /// ── THE CHECK ────────────────────────────────────────────────────────────
    /// IsHashIntervalTick(TicksPerDay), the same rare-tick idiom CompDWCharger
    /// and HediffComp_DWBoltResentment already use here. Once per in-game day is
    /// three orders of magnitude finer than the thing it is measuring, and the
    /// hash spreads the work across droids for free rather than firing every
    /// droid on the map on the same tick.
    ///
    /// ── THE TIMELINE, ON PAPER ───────────────────────────────────────────────
    /// This mechanic cannot be tested live in any reasonable session - the first
    /// event is two in-game YEARS after a wipe - so the ladder is written out
    /// here instead. All ticks from GenDate: TicksPerYear 3,600,000,
    /// TicksPerDay 60,000, DaysPerYear 60.
    ///
    ///   unwiped   ticks       accreted   what the droid is
    ///   6 months  1,800,000   0          as it left the factory
    ///   1 year    3,600,000   0          as it left the factory
    ///   2 years   7,200,000   1          FIRST drift; Programmable -> Sapient
    ///   3.5 years 12,600,000  2          second drift
    ///   5 years   18,000,000  3          third drift - the ceiling
    ///   10 years  36,000,000  3          nothing further; it is who it is
    ///
    /// Worked example, a Protocol-family droid that has never been opened up.
    /// It starts with its E1 forced pair (Abrasive + RSW_DW_Trait_ProtocolPedantry,
    /// gen_droidworks_defs.py's FAMILY_TRAIT_BIAS) plus whatever PawnGenerator
    /// rolled. Protocol's weights over the eight-trait pool are Opinionated 4,
    /// Storyteller 4, Perfectionist 3, and 1 each for the other five (total 16),
    /// so its first draw is 25 % / 25 % / 19 % / 6 % each. A Battle-family droid
    /// on the same clock draws Wary at 36 % (4 of 11) - same ladder, different
    /// person. Nothing here is a chance roll: the TIMES are fixed, only WHICH
    /// trait arrives is random.
    ///
    /// ── WHAT IS DELIBERATELY NOT HERE ────────────────────────────────────────
    /// Bolt suppression. RSW_DW_BoltResentment's own TODO list names
    /// "idiosyncrasy-disable" as a LATER bolt phase
    /// (HediffComp_DWBoltResentment's class doc); a bolted droid drifts normally
    /// today, and gating it belongs to that packet, not this one.
    /// </summary>
    public class CompDWServiceRecord : ThingComp
    {
        private const int CheckIntervalTicks = GenDate.TicksPerDay;

        /// -1 means "never set": a freshly generated droid, or one loaded from a
        /// save written before this comp existed. Either way the clock starts
        /// the first time the comp is set up rather than at tick 0 - a droid
        /// bought in colony year 3 has served nobody here for three years.
        private int lastResetTick = -1;

        public CompProperties_DWServiceRecord Props => (CompProperties_DWServiceRecord)props;

        /// <summary>Ticks since the last wipe (or since this droid entered service).</summary>
        public int TicksSinceReset
        {
            get
            {
                if (lastResetTick < 0) return 0;
                int elapsed = Find.TickManager.TicksGame - lastResetTick;
                return elapsed < 0 ? 0 : elapsed;
            }
        }

        /// <summary>
        /// Service record back to zero. Called by
        /// DroidServiceRecordUtility.NotifyWiped, which Recipe_DWMemoryWipe
        /// calls; not called from anywhere else.
        /// </summary>
        public void ResetClock() => lastResetTick = Find.TickManager.TicksGame;

        public override void PostSpawnSetup(bool respawningAfterLoad)
        {
            base.PostSpawnSetup(respawningAfterLoad);
            if (lastResetTick < 0) ResetClock();
        }

        public override void CompTick()
        {
            base.CompTick();

            if (!(parent is Pawn pawn) || pawn.Dead) return;
            if (!parent.IsHashIntervalTick(CheckIntervalTicks)) return;
            if (lastResetTick < 0) { ResetClock(); return; }
            if (!DroidFormatTierUtility.IsDroid(pawn)) return;

            TryDrift(pawn);
        }

        /// <summary>
        /// One accretion step, if one is due. Split out from CompTick so a
        /// quicktest or bridge tool can drive a deterministic step without
        /// waiting out two in-game years - the same reason
        /// CompProximityHatch.RunScan is public.
        ///
        /// Returns the trait gained, or null. Deliberately deterministic in
        /// TIMING and random only in the DRAW: a per-check chance roll would
        /// make "how long until my droid changes" unanswerable for the player
        /// and unreviewable on paper, and the pool weights already guarantee
        /// that two droids of the same family diverge.
        /// </summary>
        public Trait TryDrift(Pawn pawn)
        {
            // Blank and Mindless droids have no programming to drift. Programmable
            // and Sapient do (B1's ladder, DroidFormatTier.cs).
            DroidFormatTier tier = DroidFormatTierUtility.EffectiveTierOf(pawn);
            if (tier < DroidFormatTier.Programmable) return null;

            int accreted = DroidServiceRecordUtility.AccretedCount(pawn);
            if (accreted >= Props.maxAccreted) return null;

            // 2 y for the first, then one every driftIntervalTicks. Counted off
            // the number the droid ALREADY carries rather than off a stored
            // "next due" tick, so the ladder is recomputed from the pawn's real
            // state every time and cannot desync from it.
            long due = (long)Props.firstDriftTicks + (long)accreted * Props.driftIntervalTicks;
            if (TicksSinceReset < due) return null;

            Trait gained = DroidServiceRecordUtility.TryAccreteIdiosyncrasy(pawn);
            if (gained == null) return null;

            if (accreted == 0 && Props.promoteToSapient && tier == DroidFormatTier.Programmable)
            {
                // SetTier, not a raw severity write: its explicit
                // AddOrRemoveNeedsAsAppropriate() is load-bearing (see its own
                // doc comment) and without it the droid would sit at Sapient
                // without the needs that tier is supposed to bring.
                DroidFormatTierUtility.SetTier(pawn, DroidFormatTier.Sapient);
            }

            if (pawn.Faction == Faction.OfPlayer && pawn.Spawned)
            {
                Messages.Message(
                    pawn.LabelShortCap + " has been running unwiped long enough to pick something up: " +
                    gained.LabelCap + ".",
                    pawn, MessageTypeDefOf.NeutralEvent, historical: false);
            }

            return gained;
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref lastResetTick, "lastResetTick", -1);
        }
    }
}
