using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.Pyrelands
{
    /// <summary>
    /// A colonist carrying the firefoam sprayer foams the fire in its way (bar firefoam_sprayer_reaches_the_fruit,
    /// RIMMANDRAKE_DESIGN_PYRE_SPRAYER_CARRIER_NEVER_FOAMS_ITS_PATH). Before this, RM_FE_FirefoamSprayer was a Verb_Shoot gun
    /// that nothing fired unless the player drafted the pawn and aimed it: in Pyrelands visits 3 and 4 a carrier ordered to
    /// harvest scorch-fruit inside a burning ring laid 0 Filth_FireFoam in 4 of 4 runs.
    ///
    /// Each tick, on any map where fire burns (a physical condition, no biome in it), each spawned player-faction humanlike
    /// holding the sprayer, undrafted, mobile and able, asks RM_FoamPathKernel.PickTarget for the first burning cell on its own
    /// cell, its path ahead or beside either, that the sprayer can hit; it then casts the sprayer there, as vanilla's idle
    /// colonist beats an adjacent fire on its own (JobDriver_Wait.CheckForAutoAttack). The cast is a stance, not a job: the
    /// carrier's job (the harvest) is kept, and the pather waits while the stance is busy (Pawn_PathFollower.PatherTick
    /// returns on FullBodyBusy), so the carrier stops, foams and walks on.
    ///
    /// Every tick, not an interval: a pawn walks a cell in about 13 ticks (MoveSpeed 4.6 cells/s at 60 ticks/s), and the
    /// cooldown ends on a tick of its own; an interval of N ticks lets the pather step into a fire cell up to N ticks before
    /// the next read. The cost is a few list reads per carrier on maps that hold fire; a map with no carrier pays one list
    /// count and one loop over its player pawns.
    /// </summary>
    public class MapComponent_RM_FoamPath : MapComponent
    {
        public const string SprayerDefName = "RM_FE_FirefoamSprayer";

        private static ThingDef sprayerDef;
        private static bool sprayerLooked;

        /// <summary>Casts started since the game launched, and the last one ("pawn → x,z @tick"); read by ProbeFoam.</summary>
        public static int CastsStarted;
        public static string LastCast = "none";

        // Scratch buffers of one TryFoam call, cleared at its start; per map component, so no state outlives a game.
        private readonly List<IntVec3> ahead = new List<IntVec3>();
        private readonly List<int> ax = new List<int>();
        private readonly List<int> az = new List<int>();

        public MapComponent_RM_FoamPath(Map map) : base(map) { }

        internal static ThingDef SprayerDef
        {
            get
            {
                if (!sprayerLooked)
                {
                    sprayerDef = DefDatabase<ThingDef>.GetNamedSilentFail(SprayerDefName);
                    sprayerLooked = true;
                }
                return sprayerDef;
            }
        }

        public override void MapComponentTick()
        {
            if (!RM_PyrelandsSettings.sprayerFoamsPathEnabled || SprayerDef == null) return;
            if (map.listerThings.ThingsOfDef(ThingDefOf.Fire).Count == 0) return;
            List<Pawn> pawns = map.mapPawns.SpawnedPawnsInFaction(Faction.OfPlayer);
            for (int i = 0; i < pawns.Count; i++)
            {
                Pawn p = pawns[i];
                if (p.equipment?.Primary?.def == SprayerDef) TryFoam(p);
            }
        }

        /// <summary>The sprayer's verb when the pawn holds the sprayer, else null.</summary>
        internal static Verb SprayerVerb(Pawn p)
        {
            if (p?.equipment?.Primary == null || p.equipment.Primary.def != SprayerDef) return null;
            return p.equipment.PrimaryEq?.PrimaryVerb;
        }

        /// <summary>True while the pawn is aiming the sprayer (Stance_Warmup on its verb). JobGiver_RM_StepAwayFromFire leaves
        /// such a pawn alone: a new job would end the current one, and ending a job cancels a warmup
        /// (Pawn_JobTracker.CleanupCurrentJob → CancelBusyStanceSoft), so the foam would never land.</summary>
        public static bool AimingSprayer(Pawn p)
        {
            Verb v = SprayerVerb(p);
            return v != null && p.stances?.curStance is Stance_Warmup w && w.verb == v;
        }

        private void TryFoam(Pawn p)
        {
            Verb verb = SprayerVerb(p);
            RM_FoamGate gate = RM_FoamPathKernel.Gate(true, verb != null,
                p.RaceProps.Humanlike && p.Faction == Faction.OfPlayer,
                p.Drafted,
                p.Downed || p.InMentalState || p.IsBurning(),
                !(p.stances.curStance is Stance_Mobile),
                verb != null && verb.Available() && verb.state != VerbState.Bursting);
            if (gate != RM_FoamGate.Foam) return;

            ahead.Clear();
            ax.Clear();
            az.Clear();
            Pawn_PathFollower pather = p.pather;
            if (pather != null && pather.Moving)
            {
                if (pather.nextCell.IsValid && pather.nextCell != p.Position) ahead.Add(pather.nextCell);
                if (pather.curPath != null && pather.curPath.Found && !pather.curPath.Finished)
                {
                    var peek = pather.curPath.PeekNextCells(RM_FoamPathKernel.LookAheadCells, 0);
                    ahead.AddRange(peek);
                }
            }
            foreach (IntVec3 c in ahead)
            {
                ax.Add(c.x);
                az.Add(c.z);
            }
            Map m = map;
            bool Burning(int x, int z)
            {
                var c = new IntVec3(x, 0, z);
                return c.InBounds(m) && c.ContainsStaticFire(m);
            }
            bool CanHit(int x, int z) => verb.CanHitTarget(new LocalTargetInfo(new IntVec3(x, 0, z)));
            if (!RM_FoamPathKernel.PickTarget(p.Position.x, p.Position.z, ax, az, Burning, CanHit, out int tx, out int tz)) return;
            var target = new IntVec3(tx, 0, tz);
            if (verb.TryStartCastOn(new LocalTargetInfo(target), surpriseAttack: false, canHitNonTargetPawns: false))
            {
                CastsStarted++;
                LastCast = p.LabelShort + " -> " + tx + "," + tz + " @" + Find.TickManager.TicksGame;
            }
        }

        /// <summary>static_call probe: "FOAMPATH enabled B | casts N | last S".</summary>
        public static string ProbeFoam()
        {
            return "FOAMPATH enabled " + RM_PyrelandsSettings.sprayerFoamsPathEnabled + " | casts " + CastsStarted
                + " | last " + LastCast + " | sprayerDef " + (SprayerDef != null);
        }
    }
}
