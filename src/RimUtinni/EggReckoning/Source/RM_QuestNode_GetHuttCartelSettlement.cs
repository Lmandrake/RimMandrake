using System.Collections.Generic;
using RimWorld;
using RimWorld.Planet;
using RimWorld.QuestGen;
using Verse;

namespace RimMandrake.Utinni.EggReckoning
{
	/// <summary>
	/// WEBWORK_EGG_RECKONING_QUEST_1. Copies
	/// RimMandrake.Utinni.WildsteamEggBounty.RM_QuestNode_GetWildsteamSettlement
	/// verbatim (same gap: vanilla's own QuestNode_GetNearbySettlement has no
	/// faction-filter field), swapped to RUT_Jawa_HuttCartel — "The Reckoning" is
	/// specifically the Cartel's own outlet, never a random nearby settlement's,
	/// since it is the Cartel that is owed the debt.
	///
	/// Find.FactionManager.FirstFactionOfDef / Find.WorldObjects.SettlementBases /
	/// TradeRequestComp / WorldGrid distance: same standard RimWorld.Planet API as
	/// that sibling node, confirmed live against the real installed
	/// Assembly-CSharp.dll via this item's own RimSage session (search_source
	/// confirmed GenHostility, PawnGenerator, GenSpawn, GenLocalDate, Rand and
	/// QuestNode_End's real field shapes the same way) rather than guessed.
	///
	/// Stores $cartelSettlement (Settlement) and $cartelFaction (Faction) on the
	/// slate. TestRunInt returning false correctly makes the whole quest
	/// unselectable when the Cartel has no live settlement in range — the
	/// natural "this quest cannot fire yet" behaviour, not a bug to work around.
	/// </summary>
	public class RM_QuestNode_GetHuttCartelSettlement : QuestNode
	{
		public const string HuttCartelFactionDefName = "RUT_Jawa_HuttCartel";

		public int maxTileDistance = 80;

		protected override bool TestRunInt(Slate slate)
		{
			return TryFind(slate, out _, out _);
		}

		protected override void RunInt()
		{
			Slate slate = QuestGen.slate;
			if (!TryFind(slate, out Settlement settlement, out Faction faction))
			{
				return;
			}
			slate.Set("cartelSettlement", settlement);
			slate.Set("cartelFaction", faction);
		}

		private bool TryFind(Slate slate, out Settlement settlement, out Faction faction)
		{
			settlement = null;
			FactionDef cartelDef = DefDatabase<FactionDef>.GetNamedSilentFail(HuttCartelFactionDefName);
			faction = cartelDef != null ? Find.FactionManager?.FirstFactionOfDef(cartelDef) : null;
			if (faction == null)
			{
				return false;
			}

			Map map = slate.Get<Map>("map");
			int fromTile = map != null ? map.Tile : (Find.AnyPlayerHomeMap != null ? Find.AnyPlayerHomeMap.Tile : -1);
			if (fromTile < 0)
			{
				return false;
			}

			int maxDist = maxTileDistance;
			Settlement best = null;
			int bestDist = int.MaxValue;
			List<Settlement> all = Find.WorldObjects.SettlementBases;
			for (int i = 0; i < all.Count; i++)
			{
				Settlement s = all[i];
				if (s == null || s.Faction != faction || s.HasMap)
				{
					continue;
				}
				TradeRequestComp comp = s.GetComponent<TradeRequestComp>();
				if (comp != null && comp.ActiveRequest)
				{
					continue;
				}
				int dist = Find.WorldGrid.TraversalDistanceBetween(fromTile, s.Tile, true, maxDist + 1);
				if (dist > maxDist)
				{
					continue;
				}
				if (dist < bestDist)
				{
					bestDist = dist;
					best = s;
				}
			}

			if (best == null)
			{
				return false;
			}

			settlement = best;
			return true;
		}
	}
}
