using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI.Group;

namespace RimMandrake.Utinni.PyrelandsMechanics
{
    /// <summary>
    /// DEEP_TRIBES_FIRE_RITE_1 — putting the rite party on the map.
    ///
    /// WHO. The Deep Tribes, read off PyrelandsFactions (vanilla FactionDef
    /// TribeCivil, reskinned by
    /// src/RimUtinni/UtinniPatches/Patches/DeepDesertTribes.xml). Not guessed
    /// here and not guessed there.
    ///
    /// ⚠️ WHY A FIXED COUNT AND NOT A POINTS BUDGET. The owner asked for "a small
    /// group", and PawnGroupMakerUtility.GeneratePawns takes threat points, not a
    /// headcount — the same 180 points that makes four tribals on one world makes
    /// one chieftain on another. So the kinds are drawn from the faction's own
    /// Peaceful group maker (the same list a visitor group would use, weights and
    /// all) and generated one at a time to a rolled count. Nothing about WHO shows
    /// up is invented; only HOW MANY.
    ///
    /// 🔑 NO INCIDENT DEF. The fire clock triggers this directly
    /// (PyrelandsFireFront.TryRunRite), because the thing that decides a rite
    /// happens is the burn schedule, not the storyteller. Routing it through an
    /// IncidentDef would put a second, unrelated clock in front of it.
    /// </summary>
    internal static class PyrelandsFireRite
    {
        /// <summary>
        /// Send the rite. Returns false — and changes nothing — for every reason a
        /// rite cannot happen, so the caller can fall through to the plain front:
        /// no Tribes in this world, the Tribes at war (then the thing that arrives
        /// is IncidentWorker_FireRaid, not this), nowhere to walk in from, or a
        /// group maker that produced nobody.
        /// </summary>
        internal static bool TrySend(Map map, IntVec3 riteOrigin)
        {
            if (map == null || !riteOrigin.IsValid)
            {
                return false;
            }

            Faction tribes = PyrelandsFactions.TribesOrNull();
            if (tribes == null || tribes.HostileTo(Faction.OfPlayer))
            {
                return false;
            }

            if (!RCellFinder.TryFindRandomPawnEntryCell(out IntVec3 entry, map, CellFinder.EdgeRoadChance_Neutral))
            {
                return false;
            }

            List<Pawn> party = GenerateParty(map, tribes);
            if (party.Count == 0)
            {
                return false;
            }

            for (int i = 0; i < party.Count; i++)
            {
                IntVec3 cell = CellFinder.RandomClosewalkCellNear(entry, map, PyrelandsTuning.FireRiteSpawnSpread);
                GenSpawn.Spawn(party[i], cell, map);
            }

            int harvestTicks = Mathf.Max(
                1,
                Mathf.RoundToInt(PyrelandsMechanicsSettings.fireRiteHarvestHours * 2500f));

            LordMaker.MakeNewLord(
                tribes,
                new LordJob_RUT_FireRite(riteOrigin, harvestTicks),
                map,
                party);

            // Gated behind the fire clock's own letter switch rather than a new
            // one: this IS that letter's event, arriving with people attached.
            if (PyrelandsMechanicsSettings.fireFrontLetterEnabled)
            {
                Find.LetterStack.ReceiveLetter(
                    "RUT_FireRiteLetterLabel".Translate(),
                    "RUT_FireRiteLetterText".Translate(tribes.Name),
                    LetterDefOf.NeutralEvent,
                    new LookTargets(party[0]),
                    tribes);
            }

            return true;
        }

        private static List<Pawn> GenerateParty(Map map, Faction tribes)
        {
            List<Pawn> party = new List<Pawn>();

            int min = PyrelandsMechanicsSettings.fireRiteGroupMin;
            int max = PyrelandsMechanicsSettings.fireRiteGroupMax;
            if (max < min)
            {
                max = min;
            }
            int count = Rand.RangeInclusive(min, max);

            for (int i = 0; i < count; i++)
            {
                PawnKindDef kind = PickHarvesterKind(tribes);
                if (kind == null)
                {
                    break;
                }

                Pawn pawn = PawnGenerator.GeneratePawn(new PawnGenerationRequest(
                    kind,
                    tribes,
                    PawnGenerationContext.NonPlayer,
                    map.Tile,
                    forceGenerateNewPawn: false,
                    allowDead: false,
                    allowDowned: false,
                    canGeneratePawnRelations: true,
                    mustBeCapableOfViolence: false,
                    colonistRelationChanceFactor: 0f));

                if (pawn != null)
                {
                    party.Add(pawn);
                }
            }

            return party;
        }

        /// <summary>
        /// One harvester, drawn from the Tribes' own Peaceful group maker so the
        /// party is made of the same people a visitor group would be. Children are
        /// excluded — pawnGroupDevelopmentStage is the field the group makers
        /// themselves use to say so — because this walks into a live burn.
        /// basicMemberKind is the fallback for a faction whose group makers were
        /// patched out from under us; null if even that is missing, and then no
        /// rite happens rather than a guessed pawn kind.
        /// </summary>
        private static PawnKindDef PickHarvesterKind(Faction tribes)
        {
            List<PawnGroupMaker> makers = tribes.def?.pawnGroupMakers;
            if (makers != null)
            {
                List<PawnGenOption> pool = new List<PawnGenOption>();
                for (int i = 0; i < makers.Count; i++)
                {
                    PawnGroupMaker maker = makers[i];
                    if (maker?.kindDef != PawnGroupKindDefOf.Peaceful || maker.options == null)
                    {
                        continue;
                    }
                    for (int j = 0; j < maker.options.Count; j++)
                    {
                        PawnGenOption option = maker.options[j];
                        if (option?.kind != null && option.selectionWeight > 0f && IsAdultKind(option.kind))
                        {
                            pool.Add(option);
                        }
                    }
                }

                if (pool.Count > 0
                    && pool.TryRandomElementByWeight(o => o.selectionWeight, out PawnGenOption chosen))
                {
                    return chosen.kind;
                }
            }

            return tribes.def?.basicMemberKind;
        }

        private static bool IsAdultKind(PawnKindDef kind)
        {
            return !kind.pawnGroupDevelopmentStage.HasValue
                || (kind.pawnGroupDevelopmentStage.Value & DevelopmentalStage.Adult) != 0;
        }
    }
}
