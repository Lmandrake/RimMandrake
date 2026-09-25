using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace RimMandrake.Utinni.PropaneLakeMechanics
{
	/// <summary>
	/// Row 6, "saturation heist" (§5, §9 row 6, owner ruling): "Give them better
	/// weapons... Strictly non-flammable, non-temperature-based, non-explosive.
	/// Vibro-weaponry." Read as: when the PLAYER'S OWN base is already
	/// saturated, an incoming raid that showed up with guns would deflagrate
	/// itself as readily as the colony, so this raid re-equips its own gunners
	/// with the ruled safe loadout before the letter goes out. Reuses every bit
	/// of vanilla IncidentWorker_RaidEnemy's faction/strategy/arrival machinery —
	/// only the gate (CanFireNowSub) and the post-spawn loadout swap
	/// (PostProcessSpawnedPawns) are new.
	/// </summary>
	public class IncidentWorker_SaturationHeistRaid : IncidentWorker_RaidEnemy
	{
		/// <summary>Matches the tracker's own 50% "coin-flip" band (§5) — below
		/// that, ranged combat is still viable and a gun-swapped raid would just
		/// be a strange downgrade for no reason.</summary>
		private const float MinSaturationPercentToFire = 50f;

		protected override bool CanFireNowSub(IncidentParms parms)
		{
			if (!base.CanFireNowSub(parms))
			{
				return false;
			}
			if (PropaneLakeMechanicsMod.Settings != null && !PropaneLakeMechanicsMod.Settings.saturationHeistRaidEnabled)
			{
				return false;
			}
			if (!(parms.target is Map map))
			{
				return false;
			}
			MapComponent_GasSaturationTracker tracker = map.GetComponent<MapComponent_GasSaturationTracker>();
			if (tracker == null)
			{
				return false;
			}
			if (tracker.AmbientSurge >= MinSaturationPercentToFire)
			{
				return true;
			}
			foreach (Pawn colonist in map.mapPawns.FreeColonistsSpawned)
			{
				if (tracker.SaturationPercentAt(colonist.Position) >= MinSaturationPercentToFire)
				{
					return true;
				}
			}
			return false;
		}

		private static IEnumerable<ThingDef> CandidateWeapons()
		{
			// Real Star Wars vibro/sonic content when the armoury is loaded
			// (mandrake.rsw.armoury — Absorbed_KotorWeapons); a vanilla
			// neolithic-melee fallback keeps the loadout real without it, so
			// this raid ships correctly whether or not that mod is active.
			string[] preferredDefNames = { "guy762_vblade", "guy762_vdubblade", "guy762_sonpistol" };
			foreach (string defName in preferredDefNames)
			{
				ThingDef def = DefDatabase<ThingDef>.GetNamedSilentFail(defName);
				if (def != null)
				{
					yield return def;
				}
			}
			string[] fallbackDefNames = { "MeleeWeapon_Spear", "MeleeWeapon_Knife", "MeleeWeapon_Club" };
			foreach (string defName in fallbackDefNames)
			{
				ThingDef def = DefDatabase<ThingDef>.GetNamedSilentFail(defName);
				if (def != null)
				{
					yield return def;
				}
			}
		}

		protected override void PostProcessSpawnedPawns(IncidentParms parms, List<Pawn> pawns)
		{
			base.PostProcessSpawnedPawns(parms, pawns);
			if (PropaneLakeMechanicsMod.Settings != null && !PropaneLakeMechanicsMod.Settings.saturationHeistRaidEnabled)
			{
				return;
			}
			List<ThingDef> candidates = CandidateWeapons().ToList();
			if (candidates.Count == 0)
			{
				return;
			}
			foreach (Pawn pawn in pawns)
			{
				ThingWithComps primary = pawn.equipment?.Primary;
				if (primary == null || !primary.def.IsRangedWeapon)
				{
					continue;
				}
				pawn.equipment.DestroyAllEquipment();
				ThingDef chosen = candidates.RandomElement();
				ThingWithComps replacement = (ThingWithComps)ThingMaker.MakeThing(chosen, GenStuff.DefaultStuffFor(chosen));
				pawn.equipment.AddEquipment(replacement);
			}
		}
	}
}
