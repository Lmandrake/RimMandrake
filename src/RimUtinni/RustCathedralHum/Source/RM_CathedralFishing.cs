using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.Utinni.RustCathedralHum
{
	// RUST_CATHEDRAL_MECHANICS_1 §4 -- eel-fishing consequences.
	//
	// TWO mechanics, deliberately wired two different ways, because they are
	// two different KINDS of event:
	//
	//   1. THE LINE-IN TELL -- a STATE ("someone is fishing right now"), so it
	//      is read by the interval scan the kit spec itself prefers ("zero-
	//      Harmony route: RM_MapComponent_BiomeAttitude scans on its own
	//      interval for pawns executing the fish job on Cathedral water").
	//      Nothing structural made that awkward, so the Harmony fallback the
	//      spec offers is NOT taken. §1's own interval is 250 ticks against a
	//      7500-tick base fishing job, so a line going in is seen ~30x before
	//      the job completes -- "the moment a line goes in", with no toil hook.
	//
	//   2. THE PER-CATCH PRICE -- an INSTANT ("a fish just came out"), which an
	//      interval scan structurally cannot see: the catch is created and the
	//      job ends inside a single toil initAction. The one honest hook is
	//      vanilla's own WaterBodyTracker.Notify_Fished(cell, count), which
	//      JobDriver_Fish calls exactly once per successful non-rare catch and
	//      which carries both the map and the number taken. A small Harmony
	//      postfix, matching the precedent §2 and §3 already set in this kit.
	//      (The kit spec's "New C#: none beyond §1" line for §4 does not
	//      survive contact with that: it is recorded as a deviation, not as an
	//      oversight.)
	//
	// Both are gated in Mod Settings and both no-op instantly off a map whose
	// biome has an RM_BiomeAttitudeDef -- i.e. everywhere but the Cathedral.
	public static class RM_CathedralFishing
	{
		public const string CoolantEelDefName = "RUT_CoolantEel";

		// INVENTED parameters, from the kit spec §4's own "INVENTED parameters"
		// line, carried over verbatim: irritation +5 line-in, +2 per catch,
		// goodwill -1 per 3 catches within a day.
		public const float LineInIrritation = 5f;

		public const float PerCatchIrritation = 2f;

		public const int CatchesPerGoodwillTick = 3;

		public const int GoodwillPerTick = -1;

		// One charge per fishing job, not per interval: a pawn stands at the
		// water for 7500 ticks and would otherwise be billed ~30 times for one
		// line. Keyed by job loadID, so the SAME pawn starting a SECOND fishing
		// job is charged again -- which is the intent ("every time, before
		// anything else happens").
		//
		// Session-local on purpose, same trade §3's curiosity debounce makes and
		// for the same reason: persisting it would mean adding save fields to
		// §1's MapComponent from §4. The cost is bounded and small -- a fishing
		// job still running across a save/load is charged once more when the
		// scan next sees it. Flagged rather than hidden.
		private static readonly HashSet<int> chargedFishingJobs = new HashSet<int>();

		// Rolling per-day catch counter, per map, for the goodwill tick. Also
		// session-local, also deliberately: losing the partial count across a
		// save/load can at worst forgive up to two catches.
		private static readonly Dictionary<int, int> catchesTowardGoodwill = new Dictionary<int, int>();

		private static readonly Dictionary<int, int> goodwillWindowAnchorTick = new Dictionary<int, int>();

		/// <summary>
		/// The line-in tell. Called by RM_MapComponent_BiomeAttitude on its own
		/// check interval, on a map already known to have an attitude def.
		/// </summary>
		public static void ScanForFishing(Map map)
		{
			if (!RustCathedralHumSettings.FishingPricingActive)
			{
				return;
			}
			if (map == null)
			{
				return;
			}

			IReadOnlyList<Pawn> pawns = map.mapPawns.AllPawnsSpawned;
			for (int i = 0; i < pawns.Count; i++)
			{
				Pawn pawn = pawns[i];
				// Only the colony is watched, same rule §3's pricing uses: a
				// visitor or a raider dropping a line is not the player's
				// sacrilege.
				if (pawn?.Faction == null || !pawn.Faction.IsPlayer)
				{
					continue;
				}
				Job job = pawn.CurJob;
				if (job == null || job.def != JobDefOf.Fish)
				{
					continue;
				}
				if (!chargedFishingJobs.Add(job.loadID))
				{
					continue;
				}
				RM_MapComponent_BiomeAttitude.AddIrritation(map, LineInIrritation);
			}
		}

		/// <summary>
		/// The per-catch price. Called from the Notify_Fished postfix below.
		/// </summary>
		public static void NoteCatch(Map map, float amount)
		{
			if (!RustCathedralHumSettings.FishingPricingActive)
			{
				return;
			}
			if (map == null || amount <= 0f)
			{
				return;
			}
			// Vanilla's Notify_Fished takes a float (the stack count taken).
			// Round down, floored at one, so a catch always costs something.
			int count = Mathf.Max(1, Mathf.FloorToInt(amount));
			// Off a Cathedral-class map there is no attitude component state to
			// move, and GetBand returns -1. Cheapest possible gate, and it is
			// the same one the line-in scan rides.
			if (RM_MapComponent_BiomeAttitude.GetBand(map) < 0)
			{
				return;
			}

			RM_MapComponent_BiomeAttitude.AddIrritation(map, PerCatchIrritation * count);

			if (Faction.OfMechanoids == null)
			{
				return;
			}

			int mapId = map.uniqueID;
			int nowTick = Find.TickManager.TicksGame;
			int anchor;
			if (!goodwillWindowAnchorTick.TryGetValue(mapId, out anchor) || nowTick - anchor >= GenDate.TicksPerDay)
			{
				goodwillWindowAnchorTick[mapId] = nowTick;
				catchesTowardGoodwill[mapId] = 0;
			}

			int running;
			catchesTowardGoodwill.TryGetValue(mapId, out running);
			running += count;

			// "-1 per 3 catches within a day": pay out whole ticks and carry the
			// remainder, so three separate single-fish catches cost the same as
			// one stack of three.
			int ticks = running / CatchesPerGoodwillTick;
			catchesTowardGoodwill[mapId] = running % CatchesPerGoodwillTick;

			if (ticks <= 0)
			{
				return;
			}

			Faction.OfMechanoids.TryAffectGoodwillWith(
				Faction.OfPlayer,
				GoodwillPerTick * ticks,
				canSendMessage: false,
				canSendHostilityLetter: true);
		}
	}

	// The catch hook. WaterBodyTracker.Notify_Fished is called once per
	// successful, non-rare, non-negative fishing completion (JobDriver_Fish's
	// CompleteFishingToil), with the cell fished and the total stack count
	// taken -- i.e. exactly the event the spec prices, with no extra guessing
	// about which fish it was.
	//
	// Only the eel lives in Cathedral fresh water (the biome's fishTypes has a
	// single entry), so a catch on a Cathedral map IS an eel catch; the
	// component gate inside NoteCatch is what keeps every other map's fishing
	// completely untouched.
	// ⚠️ WaterBodyTracker.map is `private readonly`, so the map comes in through
	// Harmony's private-field injection (`___map`), not through __instance.
	// The second parameter is `float amount`, not an int count -- matched by
	// name and type or Harmony refuses the patch at startup.
	[HarmonyPatch(typeof(WaterBodyTracker), nameof(WaterBodyTracker.Notify_Fished))]
	public static class HarmonyPatch_CathedralFishing_Catch
	{
		public static void Postfix(Map ___map, float amount)
		{
			RM_CathedralFishing.NoteCatch(___map, amount);
		}
	}
}
