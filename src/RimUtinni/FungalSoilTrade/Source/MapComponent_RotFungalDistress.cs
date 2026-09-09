using System.Collections.Generic;
using System.Reflection;
using HarmonyLib;
using RimWorld;
using Verse;

namespace RimMandrake.Utinni.FungalSoilTrade
{
	// FUNGAL_SOIL_TRADE_1, "the price" half of the spec: digging tears the Rot's
	// connected fungal network (the_rot.md section 4, health-sharing - "the
	// connected biology defends itself and repairs itself collectively") and the
	// network sends its own hybrid fauna after the diggers.
	//
	// TRIGGER MECHANISM: one Harmony prefix on the exact vanilla method the
	// standard Mine job already calls when a mineable is fully mined out
	// (RimWorld/Mineable.cs: DestroyMined(Pawn pawn), read via
	// mcp__rimsage__read_csharp_symbol, not guessed) - so digging fungal soil
	// uses the ordinary Designator_Mine / WorkGiver_Miner / JobDriver_Mine chain
	// with no new job system, per the item's own instruction. Prefix (not
	// postfix): DestroyMined's own body calls base.Destroy() partway through,
	// after which the Mineable's Map is no longer valid to read (Thing.Map
	// returns null once mapIndexOrState is reset by DeSpawn) - confirmed by
	// reading Verse/Thing.cs's Map/DeSpawn via mcp__rimsage__read_file, not
	// guessed. (Position itself is just the positionInt field and stays
	// readable post-Destroy - vanilla's own TrySpawnYield relies on that - but
	// Map alone is reason enough that the cell and map must be captured before
	// the original method runs; capturing both together here is the simpler,
	// still-correct call.)
	//
	// HARMONY PARAMETER NAMES: DestroyMined's real signature is
	// `public void DestroyMined(Pawn pawn)` - one parameter, named "pawn",
	// confirmed via mcp__rimsage__read_csharp_symbol. The Prefix below binds
	// __instance via Harmony's special reserved name (not tied to any real
	// parameter name) and binds "pawn" by matching the real parameter's name
	// exactly - both bindings verified against the decompiled source, not
	// assumed.
	//
	// RESPONSE ROSTER: the six PawnKindDefs are AA_Agaripawn, AA_Agaripod,
	// AA_Wildpawn, AA_Wildpod, AA_Swarmling and AA_MycoidColossus - every one
	// confirmed LIVE on AB_MycoticJungle (the Rot) by two independent sources
	// already in this repo: src/RimUtinni/UtinniPatches/Patches/
	// BiomeCast_Ashkarr.xml's own animalCommonalities block for the biome, and
	// design/Jawa/fauna/animal_census.csv. None of the six is guessed. Relative
	// tier weights below (which threshold calls in which creature) are this
	// pass's own design judgement, not sourced from a doc - the_rot.md section 4
	// says hybrid defenders are "summoned through the mycelial network" but does
	// not rank them, so grading pawns/pods as the first responders, swarmlings as
	// the numbers, and the Mycoid Colossus as the rare heavy answer is this
	// implementation's call, open to the owner's revision.
	//
	// RESPONSE SHAPE: the summoned pawns are ownerless (faction: null) and forced
	// into MentalStateDefOf.ManhunterPermanent, the exact pattern vanilla's own
	// GenStep_ManhunterPack and IncidentWorker_AggressiveAnimals use (both read
	// via search_source) - a manhunter pack is already "hostile fauna attacks
	// whoever it can see," which is precisely what a distress-summoned defender
	// should do; no bespoke combat AI was written.
	[StaticConstructorOnStartup]
	public static class FungalSoilTradeMod
	{
		static FungalSoilTradeMod()
		{
			Harmony harmony = new Harmony("mandrake.rut.fungalsoiltrade");
			harmony.PatchAll(Assembly.GetExecutingAssembly());
			Log.Message("[RimMandrake.Utinni.FungalSoilTrade] loaded: digging RUT_MineableFungalGround "
					  + "on the Rot will build distress and can call in its fauna.");
		}
	}

	[HarmonyPatch(typeof(Mineable), nameof(Mineable.DestroyMined))]
	public static class Patch_Mineable_DestroyMined_FungalSoilDistress
	{
		[HarmonyPrefix]
		public static void Prefix(Mineable __instance, Pawn pawn)
		{
			if (__instance == null || __instance.def == null)
			{
				return;
			}
			if (__instance.def.defName != FungalSoilDefOf.MineableFungalGroundDefName)
			{
				return;
			}
			Map map = __instance.Map;
			if (map == null)
			{
				return;
			}
			IntVec3 cell = __instance.Position;
			map.GetComponent<MapComponent_RotFungalDistress>()?.Notify_SoilDug(cell, pawn);
		}
	}

	// Raw defName strings rather than a [DefOf] class on purpose: this assembly
	// must still load (and simply never trigger) on a mod list missing Alpha
	// Animals or Alpha Biomes, and [DefOf] would hard-error at startup on any
	// PawnKindDef DefDatabase lookup miss.
	public static class FungalSoilDefOf
	{
		public const string MineableFungalGroundDefName = "RUT_MineableFungalGround";
		public const string RotBiomeDefName = "AB_MycoticJungle";

		public const string AgaripawnDefName = "AA_Agaripawn";
		public const string AgaripodDefName = "AA_Agaripod";
		public const string WildpawnDefName = "AA_Wildpawn";
		public const string WildpodDefName = "AA_Wildpod";
		public const string SwarmlingDefName = "AA_Swarmling";
		public const string MycoidColossusDefName = "AA_MycoidColossus";
	}

	public class MapComponent_RotFungalDistress : MapComponent
	{
		// Tuning constants. All flat, data-free (no ModExtension/def wired to
		// them this pass) - an open follow-up if the owner wants these
		// per-difficulty tunable without a recompile.
		private const float DistressPerDig = 1f;
		private const float DistressDecayPerInterval = 0.15f;
		private const int DecayIntervalTicks = 2000; // ~1/30th of an in-game day

		private const float FirstResponseThreshold = 3f;   // ~3 knots dug: one pawn-tier first responder
		private const float SwarmThreshold = 6f;            // a swarmling cluster joins
		private const float HeavyThreshold = 9f;             // a pod-tier heavy hybrid joins
		private const float ColossusThreshold = 14f;        // sustained digging: the Colossus itself

		private const int PulseCooldownTicks = 2500; // ~1 in-game hour between distress pulses

		private float distress;
		private int lastPulseTick = -999999;
		private bool colossusSummonedThisEpisode;

		public MapComponent_RotFungalDistress(Map map) : base(map)
		{
		}

		public override void ExposeData()
		{
			base.ExposeData();
			Scribe_Values.Look(ref distress, "rutFungalDistress", 0f);
			Scribe_Values.Look(ref lastPulseTick, "rutFungalDistressLastPulseTick", -999999);
			Scribe_Values.Look(ref colossusSummonedThisEpisode, "rutFungalDistressColossusSummoned", false);
		}

		public override void MapComponentTick()
		{
			if (distress <= 0f)
			{
				return;
			}
			if (map.IsHashIntervalTick(DecayIntervalTicks))
			{
				distress -= DistressDecayPerInterval;
				if (distress < 0f)
				{
					distress = 0f;
				}
				if (distress <= 0f)
				{
					// A fresh "episode": stopping long enough to let the network
					// settle earns another shot at avoiding the Colossus.
					colossusSummonedThisEpisode = false;
				}
			}
		}

		public void Notify_SoilDug(IntVec3 cell, Pawn digger)
		{
			if (map?.Biome == null || map.Biome.defName != FungalSoilDefOf.RotBiomeDefName)
			{
				return;
			}
			distress += DistressPerDig;
			if (distress < FirstResponseThreshold)
			{
				return;
			}
			if (Find.TickManager.TicksGame - lastPulseTick < PulseCooldownTicks)
			{
				return;
			}
			lastPulseTick = Find.TickManager.TicksGame;
			FireDistressPulse(cell, digger);
		}

		private void FireDistressPulse(IntVec3 cell, Pawn digger)
		{
			List<PawnKindDef> response = ComposeResponse();
			if (response.Count == 0)
			{
				return;
			}

			int spawned = 0;
			foreach (PawnKindDef kind in response)
			{
				Pawn pawn = PawnGenerator.GeneratePawn(kind, faction: null, tile: map.Tile);
				if (pawn == null)
				{
					continue;
				}
				if (!CellFinder.TryFindRandomSpawnCellForPawnNear(cell, map, out IntVec3 spawnCell, 12))
				{
					spawnCell = cell;
				}
				GenSpawn.Spawn(pawn, spawnCell, map, Rot4.Random);
				pawn.mindState?.mentalStateHandler?.TryStartMentalState(MentalStateDefOf.ManhunterPermanent, forced: true, forceWake: true);
				spawned++;
			}

			if (spawned > 0)
			{
				// Plain strings, not TKey/.Translate(): this mod ships no
				// Languages/Keyed file, and an unresolved translation key would
				// print the raw key to the player rather than degrade quietly.
				Find.LetterStack.ReceiveLetter(
					(TaggedString)"Fungal distress",
					(TaggedString)"The mycelial mat convulses where it was torn. Something the network raised is coming for whoever is digging.",
					LetterDefOf.ThreatBig,
					new TargetInfo(cell, map));
			}
		}

		private List<PawnKindDef> ComposeResponse()
		{
			var result = new List<PawnKindDef>();

			PawnKindDef firstResponder = Rand.Bool
				? LookUp(FungalSoilDefOf.AgaripawnDefName)
				: LookUp(FungalSoilDefOf.WildpawnDefName);
			// If neither AA_Agaripawn nor AA_Wildpawn resolved (Alpha Animals
			// absent), firstResponder is null and AddIfFound is a no-op - the
			// swarm/heavy/colossus tiers below are each independently
			// guarded the same way, so a higher-distress response can still
			// fire even with this tier empty.
			AddIfFound(result, firstResponder);

			if (distress >= SwarmThreshold)
			{
				PawnKindDef swarmling = LookUp(FungalSoilDefOf.SwarmlingDefName);
				if (swarmling != null)
				{
					int count = Rand.RangeInclusive(3, 5);
					for (int i = 0; i < count; i++)
					{
						result.Add(swarmling);
					}
				}
			}

			if (distress >= HeavyThreshold)
			{
				PawnKindDef heavy = Rand.Bool
					? LookUp(FungalSoilDefOf.AgaripodDefName)
					: LookUp(FungalSoilDefOf.WildpodDefName);
				AddIfFound(result, heavy);
			}

			if (distress >= ColossusThreshold && !colossusSummonedThisEpisode)
			{
				PawnKindDef colossus = LookUp(FungalSoilDefOf.MycoidColossusDefName);
				if (colossus != null)
				{
					result.Add(colossus);
					colossusSummonedThisEpisode = true;
				}
			}

			return result;
		}

		private static void AddIfFound(List<PawnKindDef> list, PawnKindDef kind)
		{
			if (kind != null)
			{
				list.Add(kind);
			}
		}

		private static PawnKindDef LookUp(string defName)
		{
			return DefDatabase<PawnKindDef>.GetNamed(defName, errorOnFail: false);
		}
	}
}
