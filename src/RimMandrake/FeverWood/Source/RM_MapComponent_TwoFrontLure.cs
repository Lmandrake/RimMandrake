using System.Collections.Generic;
using System.Linq;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI.Group;

namespace RimMandrake.FeverWood
{
    // FEVERWOOD_TWO_FRONT_LURE_1. Owner ruling (fever_wood_deep_and_mud_
    // 2026-09-23.md §5/§6l, verbatim): "using one before they come also
    // increases the likelihood that one or both comes... Shouldn't both
    // come precisely at the same time. One comes, there's tension, then
    // maybe the other arrives too." This map component IS that gamble:
    // while any RM_LureStake on this map carries live bait, it rolls an
    // MTB chance each in-game hour to launch the first raid wave; a
    // successful first wave then separately rolls whether a SECOND wave
    // follows, scheduled a randomized delay later so the two can never
    // land on the same tick.
    //
    // "If only one arrives... it finishes the bait and they look around"
    // needs no code of its own: LordJob_AssaultColony's own combat AI
    // keeps advancing once nothing closer is left alive, so a raid that
    // kills the bait simply continues on toward the colony by itself.
    //
    // Ants (RM_FactionDef_KurrethSwarm, this mod) are always available.
    // The second front (RSW_Shokk_FeraliskBrood, the canon Wyyyschokk under
    // this world's "Feralisk" name) lives in the RSW-tier Shokk mod per
    // Q11a and is looked up by defName only — absent that mod, the second
    // front simply never fires ("ants only"), the same graceful-
    // degradation posture as every other MayRequire-gated class here.
    public class RM_MapComponent_TwoFrontLure : MapComponent
    {
        private const int CheckIntervalTicks = 2500; // 1 in-game hour
        private const float TicksPerDay = 60000f;
        private const string AntFactionDefName = "RM_FactionDef_KurrethSwarm";
        private const string FeraliskFactionDefName = "RSW_Shokk_FeraliskBrood";

        private readonly List<RM_CompLureStake> activeLures = new List<RM_CompLureStake>();

        private int pendingSecondWaveTick = -1;
        private string pendingSecondWaveFactionDefName;
        private IntVec3 pendingSecondWaveOrigin;

        private static readonly Dictionary<FactionDef, Faction> HiddenFactionCache = new Dictionary<FactionDef, Faction>();

        public RM_MapComponent_TwoFrontLure(Map map) : base(map)
        {
        }

        public void Notify_LureStaked(RM_CompLureStake comp)
        {
            if (comp != null && !activeLures.Contains(comp))
            {
                activeLures.Add(comp);
            }
        }

        public void Notify_LureCleared(RM_CompLureStake comp)
        {
            activeLures.Remove(comp);
        }

        public override void MapComponentTick()
        {
            base.MapComponentTick();
            if (!RM_FeverWoodSettings.twoFrontLureEnabled)
            {
                return;
            }
            if (Find.TickManager.TicksGame % CheckIntervalTicks != 0)
            {
                return;
            }

            activeLures.RemoveAll(c => c?.parent == null || !c.parent.Spawned || !c.HasLiveBait);

            TickPendingSecondWave();

            if (activeLures.Count == 0)
            {
                return;
            }

            float mtbDays = Mathf.Max(0.05f, RM_FeverWoodSettings.twoFrontLureRaidMtbHours / 24f);
            if (!Rand.MTBEventOccurs(mtbDays, TicksPerDay, CheckIntervalTicks))
            {
                return;
            }

            RM_CompLureStake origin = activeLures.RandomElement();
            LaunchFirstWave(origin.parent.Position);
        }

        private void TickPendingSecondWave()
        {
            if (pendingSecondWaveTick < 0 || Find.TickManager.TicksGame < pendingSecondWaveTick)
            {
                return;
            }
            string factionDefName = pendingSecondWaveFactionDefName;
            IntVec3 origin = pendingSecondWaveOrigin;
            pendingSecondWaveTick = -1;
            pendingSecondWaveFactionDefName = null;

            FactionDef def = DefDatabase<FactionDef>.GetNamedSilentFail(factionDefName);
            if (def != null)
            {
                SpawnRaidWave(def, origin, isSecondWave: true);
            }
        }

        private void LaunchFirstWave(IntVec3 originCell)
        {
            bool antsFirst = Rand.Bool;
            FactionDef firstDef = DefDatabase<FactionDef>.GetNamedSilentFail(
                antsFirst ? AntFactionDefName : FeraliskFactionDefName);
            string secondDefName = antsFirst ? FeraliskFactionDefName : AntFactionDefName;

            if (firstDef == null)
            {
                // The randomly-picked front isn't loaded this session (e.g.
                // Shokk/SWAC absent) — fall back to the one that IS,
                // instead of silently doing nothing this hour.
                firstDef = DefDatabase<FactionDef>.GetNamedSilentFail(AntFactionDefName);
                secondDefName = FeraliskFactionDefName;
            }
            if (firstDef == null)
            {
                return;
            }

            if (!SpawnRaidWave(firstDef, originCell, isSecondWave: false))
            {
                return;
            }

            // "if only one arrives... maybe the other arrives too" — always
            // a separately-scheduled later tick, never the same one.
            if (Rand.Chance(Mathf.Clamp01(RM_FeverWoodSettings.twoFrontLureSecondWaveChance)))
            {
                float minHours = Mathf.Min(RM_FeverWoodSettings.twoFrontLureSecondWaveMinHours, RM_FeverWoodSettings.twoFrontLureSecondWaveMaxHours);
                float maxHours = Mathf.Max(RM_FeverWoodSettings.twoFrontLureSecondWaveMinHours, RM_FeverWoodSettings.twoFrontLureSecondWaveMaxHours);
                IntRange delayTicks = new IntRange(Mathf.RoundToInt(minHours * 2500f), Mathf.Max(Mathf.RoundToInt(maxHours * 2500f), Mathf.RoundToInt(minHours * 2500f) + 500));
                pendingSecondWaveTick = Find.TickManager.TicksGame + delayTicks.RandomInRange;
                pendingSecondWaveFactionDefName = secondDefName;
                pendingSecondWaveOrigin = originCell;
            }
        }

        private bool SpawnRaidWave(FactionDef factionDef, IntVec3 origin, bool isSecondWave)
        {
            Faction faction = GetOrCreateFaction(factionDef);
            if (faction == null)
            {
                return false;
            }

            float points = Mathf.Max(80f, StorytellerUtility.DefaultThreatPointsNow(map) * 0.6f);
            PawnGroupMakerParms parms = new PawnGroupMakerParms
            {
                groupKind = PawnGroupKindDefOf.Combat,
                tile = map.Tile,
                faction = faction,
                points = points,
            };
            List<Pawn> pawns = PawnGroupMakerUtility.GeneratePawns(parms, warnOnZeroResults: false).ToList();
            if (pawns.Count == 0)
            {
                // No usable pawnGroupMaker for this faction on this mod set
                // (e.g. the donor species isn't loaded) — degrade
                // gracefully rather than spawning an empty raid.
                return false;
            }

            // "From opposite directions": the second wave enters from the
            // edge FACING AWAY from the first wave's origin, so the two
            // fronts genuinely converge instead of filing in side by side.
            IntVec3 focusDelta = isSecondWave ? (map.Center - origin) : (origin - map.Center);
            Rot4 edgeDir = Rot4.FromAngleFlat(focusDelta.AngleFlat);
            if (!CellFinder.TryFindRandomEdgeCellWith(c => c.Walkable(map) && !c.Fogged(map), map, edgeDir, CellFinder.EdgeRoadChance_Hostile, out IntVec3 spawnCenter)
                && !CellFinder.TryFindRandomEdgeCellWith(c => c.Walkable(map), map, CellFinder.EdgeRoadChance_Hostile, out spawnCenter))
            {
                return false;
            }
            Rot4 spawnRot = Rot4.FromAngleFlat((map.Center - spawnCenter).AngleFlat);

            foreach (Pawn p in pawns)
            {
                IntVec3 cell = CellFinder.RandomClosewalkCellNear(spawnCenter, map, 6);
                GenSpawn.Spawn(p, cell, map, spawnRot);
            }

            LordMaker.MakeNewLord(faction,
                new LordJob_AssaultColony(faction, canKidnap: false, canTimeoutOrFlee: false, canSteal: false),
                map, pawns);

            Messages.Message(
                isSecondWave
                    ? "A second column has arrived — the Fever Wood's other front has joined the fight."
                    : "Something has taken the bait — raiders are converging on the staked lure.",
                new TargetInfo(spawnCenter, map), MessageTypeDefOf.ThreatBig);
            return true;
        }

        private static Faction GetOrCreateFaction(FactionDef def)
        {
            if (def == null)
            {
                return null;
            }
            if (HiddenFactionCache.TryGetValue(def, out Faction cached)
                && cached != null && Find.FactionManager.AllFactionsListForReading.Contains(cached))
            {
                return cached;
            }
            Faction existing = Find.FactionManager.AllFactionsListForReading.FirstOrDefault(f => f.def == def);
            if (existing != null)
            {
                HiddenFactionCache[def] = existing;
                return existing;
            }
            Faction created = FactionGenerator.NewGeneratedFaction(new FactionGeneratorParms(def));
            Find.FactionManager.Add(created);
            HiddenFactionCache[def] = created;
            return created;
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref pendingSecondWaveTick, "pendingSecondWaveTick", -1);
            Scribe_Values.Look(ref pendingSecondWaveFactionDefName, "pendingSecondWaveFactionDefName");
            Scribe_Values.Look(ref pendingSecondWaveOrigin, "pendingSecondWaveOrigin");
            // activeLures is deliberately NOT scribed — every RM_CompLureStake
            // re-announces itself via Notify_LureStaked on its own
            // PostSpawnSetup(respawningAfterLoad: true), rebuilding this
            // list from real map state rather than a second, driftable copy.
        }
    }
}
