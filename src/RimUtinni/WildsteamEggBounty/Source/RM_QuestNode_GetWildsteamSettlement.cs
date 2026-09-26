using System.Collections.Generic;
using RimWorld;
using RimWorld.Planet;
using RimWorld.QuestGen;
using Verse;

namespace RimMandrake.Utinni.WildsteamEggBounty
{
	/// <summary>
	/// WEBWORK_NEST_EGG_ECONOMY_1, S6 ruling 2. Vanilla's own
	/// QuestNode_GetNearbySettlement (Core's Script_TradeRequest.xml, and
	/// this repo's own RUT_FungalSoilTradeRequest.xml, which copies it) has
	/// no faction-filter field — that quest's own header flags this exact
	/// gap for its "Moisture Farmers specifically" case and settles for any
	/// nearby settlement. The Wildsteam bounty cannot settle for that: it is
	/// specifically the Wildsteam Clan's own outlet (sitting §1e/§1f — the
	/// deliberately lower-paying, deliberately NAMED-faction legal
	/// alternative to the Cartel black market), so this small node does the
	/// one thing vanilla's cannot: find the nearest live settlement
	/// belonging specifically to RUT_Jawa_WildsteamClan.
	///
	/// Faction.FirstFactionOfDef is the exact call already verified live in
	/// this repo (src/RimUtinni/PyrelandsMechanics/Source/
	/// PyrelandsFactions.cs, "Find.FactionManager?.FirstFactionOfDef(...)").
	/// Find.WorldObjects.SettlementBases / TradeRequestComp / WorldGrid
	/// distance are standard RimWorld.Planet API unchanged since 1.0;
	/// UNVERIFIED against the real engine this session (no bridge/game
	/// access from this seat — see CLAUDE.md's RimSage-desktop-only note)
	/// but confirmed to COMPILE clean against the real installed
	/// Assembly-CSharp.dll via the Windows-native dotnet build this item
	/// ran. Live-verify at next game load (needs game-up, not bridge —
	/// quest firing needs a real map + world with the Wildsteam Clan
	/// generated).
	///
	/// Stores $settlement (Settlement) and $faction (Faction) on the slate,
	/// matching what QuestNode_GetNearbySettlement's own storeAs/
	/// storeFactionLeaderAs pair would have produced — the rest of
	/// RUT_WildsteamEggBounty.xml is unmodified vanilla TradeRequest
	/// plumbing from that point on.
	/// </summary>
	public class RM_QuestNode_GetWildsteamSettlement : QuestNode
	{
		public const string WildsteamFactionDefName = "RUT_Jawa_WildsteamClan";

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
			slate.Set("settlement", settlement);
			slate.Set("faction", faction);
		}

		private bool TryFind(Slate slate, out Settlement settlement, out Faction faction)
		{
			settlement = null;
			FactionDef wildsteamDef = DefDatabase<FactionDef>.GetNamedSilentFail(WildsteamFactionDefName);
			faction = wildsteamDef != null ? Find.FactionManager?.FirstFactionOfDef(wildsteamDef) : null;
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
					continue; // same "allowActiveTradeRequest=false" gate vanilla's own node applies
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
