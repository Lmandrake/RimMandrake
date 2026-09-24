using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.EnvironmentalHazards
{
    // SUMP_WALKWAYS_1 — glasswalk's "rare slip-and-fall: a pawn moving fast or
    // hauling sometimes goes prone, no real damage, just indignity" (his
    // spec, question-card ruling 2026-09-24).
    //
    // Generic, not RUT_Glasswalk-specific — any TerrainDef tagged with
    // SlipperyTag opts in, the same HasTag idiom vanilla's own
    // TerrainDef.IsRoad/IsFloor/IsWater already use (Source/Verse/
    // TerrainDef.cs, HasTag(string)). RUT_Glasswalk.xml (Sump kit) carries
    // the tag; nothing else does yet, so this is a harmless no-op everywhere
    // else, same posture as every other mechanism in this assembly.
    //
    // MECHANISM CHECK FIRST (CLAUDE.md's own standing instruction — reuse
    // before reinvent): the engine has no "slip" concept at all (verified,
    // search_source over every .cs file for Slip/Stumble/prone returns
    // nothing), but it DOES have a real, already-used involuntary-halt
    // primitive with no damage attached: RimWorld/StunHandler.cs via
    // Pawn.stances.stunner.StunFor(ticks, instigator, addBattleLog: false,
    // showMote: false) — used live for EMP grenades, teleport landings and
    // melee stun weapons. addBattleLog:false means nothing is logged as an
    // attack; no Hediff, no damage, no new animation work. That IS "no real
    // damage, just indignity" with zero new mechanic invented.
    //
    // Eligibility ("fast-moving or hauling", his spec): hauling
    // (carryTracker.CarriedThing != null) OR the current job's
    // LocomotionUrgency is Jog or Sprint. A pawn ambling or walking
    // deliberately (Amble/Walk) never triggers it — the biome is
    // punishing haste, not merely crossing the floor.
    //
    // Scan cadence/snapshot pattern matches RUT_MapComponent_TheTenant's own
    // ScanExposure in this assembly: AllPawnsSpawned is copied to a List
    // before iterating, because a stun (or anything downstream of it) could
    // in principle mutate the live spawned-pawns list mid-loop.
    public class RM_MapComponent_GlasswalkSlip : MapComponent
    {
        // TerrainDef.tags carries this to opt a floor into the slip check —
        // RUT_Glasswalk.xml's own <tags> list.
        public const string SlipperyTag = "RM_SlipperyWalkway";

        // Vanilla's "normal" tick-rare-adjacent cadence. Frequent enough that
        // RM_EnvironmentalHazardsSettings.glasswalkSlipChancePerSweep can be a
        // small, legible number ("about a 1-in-X chance every second of
        // hurrying across it") rather than a chance so large it has to be
        // spent on a much coarser interval.
        private const int TickInterval = 60;

        // "rare harmless pratfalls" (his spec) — INVENTED: half a second to a
        // second of stagger, long enough to read as a stumble, short enough
        // that nothing is lost mid-haul. Flag for live tuning.
        private static readonly IntRange SlipStunTicks = new IntRange(30, 60);

        public RM_MapComponent_GlasswalkSlip(Map map)
            : base(map)
        {
        }

        public override void MapComponentTick()
        {
            base.MapComponentTick();

            if (!RM_EnvironmentalHazardsSettings.glasswalkSlipEnabled)
            {
                return;
            }

            if (Find.TickManager.TicksGame % TickInterval != 0)
            {
                return;
            }

            float chance = RM_EnvironmentalHazardsSettings.glasswalkSlipChancePerSweep;
            if (chance <= 0f)
            {
                return;
            }

            List<Pawn> pawns = new List<Pawn>(map.mapPawns.AllPawnsSpawned);
            for (int i = 0; i < pawns.Count; i++)
            {
                Pawn pawn = pawns[i];
                if (pawn == null || pawn.Dead || pawn.Downed || !pawn.Spawned)
                {
                    continue;
                }

                if (pawn.stances == null || pawn.stances.stunner == null || pawn.stances.stunner.Stunned)
                {
                    continue; // already staggering (from this or anything else) — do not stack
                }

                if (!IsEligible(pawn))
                {
                    continue;
                }

                TerrainDef terrain = pawn.Position.GetTerrain(map);
                if (terrain == null || !terrain.HasTag(SlipperyTag))
                {
                    continue;
                }

                if (!Rand.Chance(chance))
                {
                    continue;
                }

                pawn.stances.stunner.StunFor(SlipStunTicks.RandomInRange, null, addBattleLog: false, showMote: false);

                if (PawnUtility.ShouldSendNotificationAbout(pawn))
                {
                    Messages.Message("RM_GlasswalkSlip".Translate(pawn.LabelShortCap), new TargetInfo(pawn.Position, map), MessageTypeDefOf.NeutralEvent, historical: false);
                }
            }
        }

        private static bool IsEligible(Pawn pawn)
        {
            if (pawn.carryTracker != null && pawn.carryTracker.CarriedThing != null)
            {
                return true; // hauling
            }

            Job job = pawn.CurJob;
            if (job == null)
            {
                return false;
            }

            return job.locomotionUrgency == LocomotionUrgency.Jog || job.locomotionUrgency == LocomotionUrgency.Sprint;
        }
    }
}
