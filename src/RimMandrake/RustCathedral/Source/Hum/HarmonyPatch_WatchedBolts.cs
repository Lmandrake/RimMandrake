using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using Verse;

namespace RimMandrake.Utinni.RustCathedralHum
{
	// RUST_CATHEDRAL_MECHANICS_1 §3 -- "watched" pricing, plus the mod-option
	// gate on the shed spawner.
	//
	// WIRING STYLE: a Harmony postfix/prefix set, matching the precedent this
	// kit already set in §2 (src/RimUtinni/RustCathedralWalls/Source/
	// HarmonyPatch_GateLivePatternMetal.cs) rather than inventing a new one.
	// No new ThingComp is introduced -- the kit spec's "Reuse: vanilla
	// CompSpawner; no RC comp" line is honoured, and a comp would also be
	// visible on the info card, which ban 1 forbids: nothing the player can
	// read may say that carrying a curiosity or killing a bolt is noticed.
	//
	// All four hooks are scoped by defName and no-op instantly for every
	// other thing in the game.
	[StaticConstructorOnStartup]
	public static class RustCathedralHumHarmony
	{
		static RustCathedralHumHarmony()
		{
			new Harmony("mandrake.rut.rustcathedralhum").PatchAll();
		}
	}

	public static class RM_WatchedBolts
	{
		public const string LivingBoltDefName = "RUT_LivingBolt";

		public const string CuriosityDefName = "RUT_BoltShedCuriosity";

		// INVENTED parameters, from the kit spec §3's own "INVENTED
		// parameters" line: irritation +3 pickup / +15 kill.
		public const float PickupIrritation = 3f;

		public const float KillIrritation = 15f;

		// Charge a given curiosity at most once. Session-local on purpose:
		// persisting it would mean either a save-data field on a def whose
		// info card must stay silent, or editing §1's MapComponent ExposeData
		// from §3. The cost of the cheap version is bounded and small -- after
		// a save/load, re-picking-up a curiosity that was already charged can
		// charge it again. Flagged rather than hidden.
		private static readonly HashSet<int> chargedCuriosities = new HashSet<int>();

		public static void NotePickup(Pawn carrier, Thing item)
		{
			if (!RustCathedralHumSettings.BoltWatchedPricingActive)
			{
				return;
			}
			if (item?.def == null || item.def.defName != CuriosityDefName)
			{
				return;
			}
			// Only the colony is watched. A trader's hauler or a raider
			// walking off with one is not the player's sacrilege.
			if (carrier?.Faction == null || !carrier.Faction.IsPlayer)
			{
				return;
			}
			Map map = carrier.MapHeld;
			if (map == null)
			{
				return;
			}
			if (!chargedCuriosities.Add(item.thingIDNumber))
			{
				return;
			}
			RM_MapComponent_BiomeAttitude.AddIrritation(map, PickupIrritation);
		}

		public static void NoteKill(Pawn bolt, DamageInfo? dinfo)
		{
			if (!RustCathedralHumSettings.BoltWatchedPricingActive)
			{
				return;
			}
			if (bolt?.def == null || bolt.def.defName != LivingBoltDefName)
			{
				return;
			}
			Map map = bolt.MapHeld;
			if (map == null)
			{
				return;
			}
			// Same rule as pickup: priced only when the colony did it. A bolt
			// caught in a raider's crossfire is not charged to the player.
			Thing instigator = dinfo?.Instigator;
			Faction faction = instigator?.Faction;
			if (faction == null || !faction.IsPlayer)
			{
				return;
			}
			RM_MapComponent_BiomeAttitude.AddIrritation(map, KillIrritation);
		}
	}

	// Pickup, overload 1 of 2. Pawn_CarryTracker.TryStartCarry(Thing) --
	// both overloads are patched because vanilla haul toils use the
	// (Thing, int, bool) form while several direct pickups use the single-arg
	// form; patching one only would price half the routes.
	[HarmonyPatch(typeof(Pawn_CarryTracker), nameof(Pawn_CarryTracker.TryStartCarry), new[] { typeof(Thing) })]
	public static class HarmonyPatch_WatchedBolts_CarrySingle
	{
		public static void Postfix(Pawn_CarryTracker __instance, Thing item, bool __result)
		{
			if (__result)
			{
				RM_WatchedBolts.NotePickup(__instance?.pawn, item);
			}
		}
	}

	// Pickup, overload 2 of 2. Returns the count actually taken, so a zero
	// result means nothing was picked up.
	[HarmonyPatch(typeof(Pawn_CarryTracker), nameof(Pawn_CarryTracker.TryStartCarry), new[] { typeof(Thing), typeof(int), typeof(bool) })]
	public static class HarmonyPatch_WatchedBolts_CarryCount
	{
		public static void Postfix(Pawn_CarryTracker __instance, Thing item, int __result)
		{
			if (__result > 0)
			{
				RM_WatchedBolts.NotePickup(__instance?.pawn, item);
			}
		}
	}

	// Kill. A PREFIX, not a postfix, on purpose: by the time Kill returns the
	// pawn is despawned and its Map is gone, so the irritation would have
	// nowhere to land.
	[HarmonyPatch(typeof(Pawn), nameof(Pawn.Kill))]
	public static class HarmonyPatch_WatchedBolts_Kill
	{
		public static void Prefix(Pawn __instance, DamageInfo? dinfo)
		{
			RM_WatchedBolts.NoteKill(__instance, dinfo);
		}
	}

	// Mod option gate for the shed. Vanilla CompSpawner has no enable field,
	// so the only way to let Mod Settings switch the shed off without
	// replacing the comp (which the kit spec forbids) is to refuse the spawn
	// for this one race. Every other CompSpawner in the game falls straight
	// through.
	[HarmonyPatch(typeof(CompSpawner), nameof(CompSpawner.TryDoSpawn))]
	public static class HarmonyPatch_WatchedBolts_GateShed
	{
		public static bool Prefix(CompSpawner __instance, ref bool __result)
		{
			if (RustCathedralHumSettings.BoltShedActive)
			{
				return true;
			}
			if (__instance?.parent?.def == null || __instance.parent.def.defName != RM_WatchedBolts.LivingBoltDefName)
			{
				return true;
			}
			__result = false;
			return false;
		}
	}
}
