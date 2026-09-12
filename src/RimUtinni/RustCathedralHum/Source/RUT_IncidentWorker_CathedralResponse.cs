using System.Collections.Generic;
using System.Linq;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI.Group;

namespace RimMandrake.Utinni.RustCathedralHum
{
	// RUST_CATHEDRAL_MECHANICS_1 §5 -- the deep-drill response event.
	//
	// ⛔ BAN 6 IS ABSOLUTE and it constrains this FILE too, not just the letter:
	// "no text -- letter, def description, commentary line, art note -- ever
	// describes the response beyond 'massive mechanoid movement'." Everything
	// below is mechanism; the only player-readable strings this kit ships for
	// §5 are in the IncidentDef, and they describe nothing.
	//
	// ENGINE ROUTE (all re-read from source, none assumed):
	//
	//  * FIRING. No new storyteller plumbing at all. Vanilla's
	//    StorytellerComp_DeepDrillInfestation already sits on the storyteller
	//    base def (Defs/Core/Storyteller/Storytellers.xml), rolls MTB
	//    baseMtbDaysPerDrill=20 per USABLE drill (difficulty-scaled), and then
	//    picks by UsableIncidentsInCategory(DeepDrillInfestation) ->
	//    TryRandomElement. That selection is UNIFORM over every incident in the
	//    category whose worker says CanFireNow -- so simply existing in the
	//    category is the whole firing route.
	//
	//  * THE SPEC'S ❓, ANSWERED. "verify at build that category selection picks
	//    the RUT_ incident on Cathedral maps over vanilla infestation." It does
	//    NOT: with both usable it is a straight coin flip, because
	//    TryRandomElement is unweighted (baseChance is not consulted here).
	//    The spec's own named fallback is therefore taken -- vanilla's worker is
	//    gated off Cathedral maps (see the Harmony postfix at the bottom), which
	//    leaves this incident as the only candidate there and leaves every other
	//    map's infestations exactly as they were.
	//
	//  * THE FORCE. PawnGroupMakerUtility on faction 13 (vanilla Mechanoid,
	//    reskinned "the Forgotten/Forsaken Arsenal" in mandrake.rut.patches),
	//    which ships six Combat pawnGroupMakers -- no new pawn kinds, no roster
	//    of our own.
	//
	//  * CONVERGE-DESTROY-WITHDRAW. Vanilla LordJob_AssaultThings, which is
	//    exactly that shape already: LordToil_AssaultThings on the named things,
	//    with a Trigger_ThingsDamageTaken transition into
	//    LordToil_ExitMapAndDefendSelf. Trigger_ThingsDamageTaken returns true
	//    when every listed thing is gone (num2 == 0), so destroying the drill IS
	//    the withdrawal signal. Movement against the violation, never an assault
	//    on the colony -- the group never takes an AssaultColony lord, so ban 3
	//    is structurally honoured rather than merely intended.
	//
	//    ⚠️ DEVIATION from the spec's INVENTED "withdrawal 1 day after drill
	//    death": vanilla's trigger withdraws IMMEDIATELY on drill death. Adding
	//    a one-day hold would mean a custom LordJob, which the spec's own
	//    "Reuse: vanilla storyteller plumbing + ... lord" line argues against.
	//    Recorded, not silently dropped.
	//
	//    ⚠️ The spec also names RM_LordJob_DefendPerimeter as the Scarlands
	//    kit's contribution to reuse here. It DOES NOT EXIST -- src/RimUtinni/
	//    ScarlandsLadder ships About/ and Defs/ only, no Source/ and no
	//    assembly. LordJob_AssaultThings is the vanilla equivalent of what that
	//    line asked for, and is used instead of stubbing a placeholder.
	public class RUT_IncidentWorker_CathedralResponse : IncidentWorker
	{
		public const string TargetBiomeDefName = "RUT_RustCathedral";

		public const string LivePatternMetalDefName = "RUT_LivePatternMetal";

		// INVENTED parameters (kit spec §5's own "INVENTED parameters" line,
		// with the deviations named above):
		//   force size 2-3x current threat-scale points, capped.
		public const float MinPointsFactor = 2f;

		public const float MaxPointsFactor = 3f;

		public const float MaxPoints = 10000f;

		// Escalation coupling: "firing the event also floors the §1 band and
		// takes a large goodwill bite -- drilling the deep metal is the top of
		// the sacrilege ladder." §1 clamps composite to 100 and its worst band
		// starts at 80, so +100 irritation floors the band on any goodwill.
		// INVENTED: the -25 goodwill bite (the spec says "large", not a number).
		public const float ResponseIrritation = 100f;

		public const int ResponseGoodwill = -25;

		private static readonly List<Thing> tmpDrills = new List<Thing>();

		/// <summary>
		/// True when this map is the Cathedral -- the one gate every §5 hook
		/// shares, including the Harmony gate on vanilla's own worker.
		/// </summary>
		public static bool IsCathedralMap(Map map)
		{
			return map?.Biome != null && map.Biome.defName == TargetBiomeDefName;
		}

		/// <summary>
		/// Usable player deep drills on this map that are currently sitting over
		/// the §2 tier-4 deep resource. "Usable" is vanilla's own definition
		/// (DeepDrillInfestationIncidentUtility: player-owned, has
		/// CompCreatesInfestations, drilled within the last tick, off its own
		/// 7-day refire cooldown and not shadowed by a neighbour's).
		/// </summary>
		private static void GetQualifyingDrills(Map map, List<Thing> outDrills)
		{
			outDrills.Clear();
			tmpDrills.Clear();
			DeepDrillInfestationIncidentUtility.GetUsableDeepDrills(map, tmpDrills);
			for (int i = 0; i < tmpDrills.Count; i++)
			{
				Thing drill = tmpDrills[i];
				ThingDef resDef;
				int countPresent;
				IntVec3 cell;
				// Vanilla's own resolver, the same one CompDeepDrill uses to
				// decide what the next portion yields. Cross-mod by defName on
				// purpose: RUT_LivePatternMetal lives in
				// mandrake.rut.rustcathedralwalls, which this mod does not and
				// should not reference.
				if (!DeepDrillUtility.GetNextResource(drill.Position, map, out resDef, out countPresent, out cell))
				{
					continue;
				}
				if (resDef != null && resDef.defName == LivePatternMetalDefName)
				{
					outDrills.Add(drill);
				}
			}
			tmpDrills.Clear();
		}

		protected override bool CanFireNowSub(IncidentParms parms)
		{
			if (!base.CanFireNowSub(parms))
			{
				return false;
			}
			if (!RustCathedralHumSettings.DrillResponseActive)
			{
				return false;
			}
			if (Faction.OfMechanoids == null)
			{
				return false;
			}
			Map map = parms.target as Map;
			if (!IsCathedralMap(map))
			{
				return false;
			}
			List<Thing> drills = new List<Thing>();
			GetQualifyingDrills(map, drills);
			return drills.Count > 0;
		}

		protected override bool TryExecuteWorker(IncidentParms parms)
		{
			Map map = parms.target as Map;
			if (map == null)
			{
				return false;
			}

			List<Thing> drills = new List<Thing>();
			GetQualifyingDrills(map, drills);
			Thing drill;
			if (!drills.TryRandomElement(out drill))
			{
				return false;
			}

			IntVec3 entry;
			if (parms.spawnCenter.IsValid && parms.spawnCenter.InBounds(map))
			{
				entry = parms.spawnCenter;
			}
			else if (!RCellFinder.TryFindRandomPawnEntryCell(out entry, map, CellFinder.EdgeRoadChance_Hostile))
			{
				return false;
			}

			float points = Mathf.Min(
				Mathf.Max(parms.points, 0f) * Rand.Range(MinPointsFactor, MaxPointsFactor),
				MaxPoints);

			PawnGroupMakerParms groupParms = new PawnGroupMakerParms
			{
				groupKind = PawnGroupKindDefOf.Combat,
				tile = map.Tile,
				faction = Faction.OfMechanoids,
				points = points
			};
			List<Pawn> pawns = PawnGroupMakerUtility.GeneratePawns(groupParms).ToList();
			if (pawns.Count == 0)
			{
				return false;
			}

			for (int i = 0; i < pawns.Count; i++)
			{
				IntVec3 cell = CellFinder.RandomClosewalkCellNear(entry, map, 8);
				GenSpawn.Spawn(pawns[i], cell, map, Rot4.Random);
			}

			LordMaker.MakeNewLord(
				Faction.OfMechanoids,
				new LordJob_AssaultThings(Faction.OfMechanoids, new List<Thing> { drill }),
				map,
				pawns);

			// Vanilla's own per-drill cooldown, so the response cannot chain off
			// the same drill inside 7 days -- the same call
			// IncidentWorker_DeepDrillInfestation makes.
			drill.TryGetComp<CompCreatesInfestations>()?.Notify_CreatedInfestation();

			// Escalation coupling into §1.
			RM_MapComponent_BiomeAttitude.AddIrritation(map, ResponseIrritation);
			Faction.OfMechanoids.TryAffectGoodwillWith(
				Faction.OfPlayer,
				ResponseGoodwill,
				canSendMessage: false,
				canSendHostilityLetter: true);

			// No text args: ban 6 means the letter names nothing and describes
			// nothing, so there is nothing to substitute into it.
			SendStandardLetter(parms, new TargetInfo(entry, map));
			return true;
		}
	}

	// The spec's own named fallback, now confirmed necessary (see the ❓ note at
	// the top of this file). Vanilla's deep-drill infestation is refused on a
	// Cathedral map so the category's uniform pick can only land on the RUT_
	// response there. A postfix on the vanilla WORKER, not a workerClass swap on
	// the vanilla DEF: a def swap would stomp any other mod that replaced that
	// worker, and a postfix on the base type still covers a subclass.
	//
	// Every other map in the game is untouched: the gate is one biome-defName
	// comparison and falls straight through.
	[HarmonyPatch(typeof(IncidentWorker_DeepDrillInfestation), "CanFireNowSub")]
	public static class HarmonyPatch_CathedralResponse_GateVanillaInfestation
	{
		public static void Postfix(IncidentParms parms, ref bool __result)
		{
			if (!__result)
			{
				return;
			}
			if (!RustCathedralHumSettings.DrillResponseActive)
			{
				return;
			}
			if (RUT_IncidentWorker_CathedralResponse.IsCathedralMap(parms?.target as Map))
			{
				__result = false;
			}
		}
	}
}
