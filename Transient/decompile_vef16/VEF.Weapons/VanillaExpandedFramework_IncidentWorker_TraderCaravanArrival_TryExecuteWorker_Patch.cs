using System.Collections.Generic;
using System.Linq;
using RimWorld;
using RimWorld.Planet;
using Verse;

namespace VEF.Weapons;

public static class VanillaExpandedFramework_IncidentWorker_TraderCaravanArrival_TryExecuteWorker_Patch
{
	private static readonly HashSet<HistoryEventDef> factionImpacts = new HashSet<HistoryEventDef>();

	public static void DetectEmpireContraband(bool __result, IncidentParms parms)
	{
		//IL_000c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0012: Expected O, but got Unknown
		if (!__result)
		{
			return;
		}
		Map val = (Map)parms.target;
		Faction faction = parms.faction;
		if (val == null || faction == null)
		{
			return;
		}
		List<Pawn> list = val.PlayerPawnsForStoryteller.ToList();
		factionImpacts.Clear();
		foreach (Pawn item in list)
		{
			Pawn_EquipmentTracker equipment = item.equipment;
			object obj;
			if (equipment == null)
			{
				obj = null;
			}
			else
			{
				ThingWithComps primary = equipment.Primary;
				obj = ((primary != null) ? primary.GetComp<CompUniqueWeapon>() : null);
			}
			CompUniqueWeapon val2 = (CompUniqueWeapon)obj;
			if (val2 == null)
			{
				continue;
			}
			foreach (WeaponTraitDef item2 in val2.TraitsListForReading)
			{
				WeaponTraitDefExtension modExtension = ((Def)item2).GetModExtension<WeaponTraitDefExtension>();
				if (modExtension == null || GenList.NullOrEmpty<FactionRelationImpacts>((IList<FactionRelationImpacts>)modExtension.factionRelationImpacts))
				{
					continue;
				}
				foreach (FactionRelationImpacts factionRelationImpact in modExtension.factionRelationImpacts)
				{
					if (factionRelationImpact.factionDef == faction.def && factionRelationImpact.eventDef != null && factionRelationImpact.impact != 0 && factionImpacts.Add(factionRelationImpact.eventDef))
					{
						Faction.OfPlayer.TryAffectGoodwillWith(faction, factionRelationImpact.impact, true, true, factionRelationImpact.eventDef, (GlobalTargetInfo?)null);
					}
				}
			}
		}
		factionImpacts.Clear();
	}
}
