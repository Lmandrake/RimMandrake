using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.Utinni.ScavengerEvents
{
    /// <summary>
    /// RUT_SCAVENGEREVENTS_BUILD_1, mechanism 5 of 8 (item's "desert fauna";
    /// mechanism reference: infrastructure/state/items/
    /// RUT_SCAVENGEREVENTS_BUILD_1.md). Genuinely hostile: spawns
    /// max(2, round(colonistCount/3)) Spelopedes AND, separately, the same
    /// count of Megaspiders (so a 6-colonist base sees 2+2=4 insects, not 2
    /// total split between kinds -- confirmed from the donor's two identical-
    /// bound loops, not the class name's singular "count"). Each is forced
    /// into permanent manhunter state with food set near-zero for immediate
    /// aggression, and the game is nudged back to normal speed so the player
    /// doesn't miss it while fast-forwarding. Ported behavior-not-bugs from
    /// MoreIncidents.MOIncidentWorker_Insect -- added a null-guard per insect
    /// kind (the donor only checks that NEITHER resolved, so a mod set where
    /// exactly one of Spelopede/Megaspider is missing would NRE in the
    /// original; not reproducing that).
    /// </summary>
    public class IncidentWorker_Insect : IncidentWorker
    {
        private const int MinCountPerKind = 2;
        private const float ColonistDivisor = 3f;
        private const float StarvingFoodLevel = 0.01f;
        private const int MinExitTicks = 90000;
        private const int MaxExitTicks = 130000;

        private static Faction OfInsectoid => Find.FactionManager.FirstFactionOfDef(FactionDefOf.Insect);

        protected override bool TryExecuteWorker(IncidentParms parms)
        {
            var map = (Map)parms.target;

            PawnKindDef spelopede = PawnKindDef.Named("Spelopede");
            PawnKindDef megaspider = PawnKindDef.Named("Megaspider");
            if (spelopede == null && megaspider == null)
            {
                Log.Error("RUT_SCAVENGEREVENTS_BUILD_1: can't spawn any insects");
                return false;
            }

            if (!RCellFinder.TryFindRandomPawnEntryCell(out IntVec3 entryCell, map, 0f, false))
                return false;

            Rot4 facing = Rot4.FromAngleFlat((map.Center - entryCell).AngleFlat);

            int colonistCount = map.mapPawns.AllPawns.FindAll(p => p.IsColonist).Count;
            int countPerKind = Mathf.Max(MinCountPerKind, Mathf.RoundToInt(colonistCount / ColonistDivisor));

            Faction faction = OfInsectoid;
            bool spawnedAny = false;
            spawnedAny |= SpawnInsects(spelopede, faction, countPerKind, entryCell, facing, map);
            spawnedAny |= SpawnInsects(megaspider, faction, countPerKind, entryCell, facing, map);

            if (!spawnedAny)
                return false;

            Find.LetterStack.ReceiveLetter(
                "RUT_Insects".Translate(),
                "RUT_InsectsDesc".Translate(),
                LetterDefOf.ThreatBig,
                new TargetInfo(entryCell, map));

            Find.TickManager.slower.SignalForceNormalSpeedShort();
            return true;
        }

        private static bool SpawnInsects(PawnKindDef kind, Faction faction, int count, IntVec3 cell, Rot4 facing, Map map)
        {
            if (kind == null)
                return false;

            for (int i = 0; i < count; i++)
            {
                Pawn insect = PawnGenerator.GeneratePawn(kind, faction);
                GenSpawn.Spawn(insect, cell, map, facing);

                insect.needs.food.CurLevel = StarvingFoodLevel;
                insect.mindState.mentalStateHandler.TryStartMentalState(MentalStateDefOf.ManhunterPermanent);
                insect.mindState.exitMapAfterTick = Find.TickManager.TicksGame + Rand.Range(MinExitTicks, MaxExitTicks);
            }

            return count > 0;
        }
    }
}
