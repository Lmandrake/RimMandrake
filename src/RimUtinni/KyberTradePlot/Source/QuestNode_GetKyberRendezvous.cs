// KYBER_TRADE_PLOT_1 spec §6.2 — where the donated kyber is handed over. Vanilla QuestNode_GetNearbySettlement picks
// ANY visitable settlement, which could put a rendezvous for the Rebellion's cause inside an Imperial outpost. This
// node keeps its rules (visitable, no live trade request on it, reachable inside maxTileDistance or any distance with a
// grav engine) and adds one: the settlement belongs to a faction on the smuggling lane, non-hostile to the player, the
// door's own faction first. The Homestead door hands it to the sympathizers' own people; the fixer door to the Hutts,
// whose lanes run past the blockade (spec §4c, §6.3). Stores viaFixer for the description rules.
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using RimWorld.Planet;
using RimWorld.QuestGen;
using Verse;

namespace RimMandrake.Utinni.KyberTradePlot
{
    public class QuestNode_GetKyberRendezvous : QuestNode
    {
        public SlateRef<float> maxTileDistance = 60f;
        public SlateRef<bool> canBeSpace;
        [NoTranslate] public SlateRef<string> storeAs;
        [NoTranslate] public SlateRef<string> storeFactionAs;
        [NoTranslate] public SlateRef<string> storeFactionLeaderAs;
        [NoTranslate] public SlateRef<string> storeCanCaravanAs;
        [NoTranslate] public SlateRef<string> storeViaFixerAs;

        private static bool ViaFixer => KyberTrade.Component?.state.door == KyberDonationDoor.HuttFixer;

        /// <summary>The door's own faction first, the other lane second.</summary>
        private static IEnumerable<string> FactionOrder()
        {
            string homestead = FactionDefOf.OutlanderCivil.defName;
            return ViaFixer ? new[] { KyberTrade.CartelDefName, homestead } : new[] { homestead, KyberTrade.CartelDefName };
        }

        private Settlement Pick(PlanetTile origin, Slate slate)
        {
            List<Settlement> all = Find.WorldObjects.SettlementBases.Where(s => Valid(s, origin, slate)).ToList();
            foreach (string defName in FactionOrder())
            {
                Settlement s = all.Where(x => x.Faction.def.defName == defName).RandomElementWithFallback();
                if (s != null) return s;
            }
            return null;
        }

        private bool Valid(Settlement s, PlanetTile origin, Slate slate)
        {
            if (s == null || !s.Visitable || s.Faction == null || s.Faction.HostileTo(Faction.OfPlayer)) return false;
            if (!FactionOrder().Contains(s.Faction.def.defName)) return false;
            if (!canBeSpace.GetValue(slate) && s.Tile.LayerDef.isSpace) return false;
            TradeRequestComp trc = s.GetComponent<TradeRequestComp>();
            if (trc != null && trc.ActiveRequest) return false;
            foreach (Quest q in Find.QuestManager.QuestsListForReading)
            {
                if (q.Historical) continue;
                foreach (QuestPart part in q.PartsListForReading)
                    if (part is QuestPart_InitiateTradeRequest itr && itr.settlement == s) return false;
            }
            if (GravshipUtility.PlayerHasGravEngine()) return true;
            return Find.WorldReachability.CanReach(origin, s.Tile)
                && Find.WorldGrid.ApproxDistanceInTiles(origin, s.Tile) < maxTileDistance.GetValue(slate);
        }

        private void Store(Slate slate, Map map, Settlement s)
        {
            slate.Set(storeAs.GetValue(slate), s);
            if (!storeFactionAs.GetValue(slate).NullOrEmpty()) slate.Set(storeFactionAs.GetValue(slate), s.Faction);
            if (!storeFactionLeaderAs.GetValue(slate).NullOrEmpty()) slate.Set(storeFactionLeaderAs.GetValue(slate), s.Faction.leader);
            if (!storeViaFixerAs.GetValue(slate).NullOrEmpty()) slate.Set(storeViaFixerAs.GetValue(slate), ViaFixer);
            if (!storeCanCaravanAs.GetValue(slate).NullOrEmpty())
                slate.Set(storeCanCaravanAs.GetValue(slate), s.Tile.Valid && map.Tile.Valid && s.Tile.Layer == map.Tile.Layer
                    && s.Tile.LayerDef.SurfaceTiles);
        }

        protected override void RunInt()
        {
            Slate slate = QuestGen.slate;
            Map map = slate.Get<Map>("map");
            Settlement s = Pick(map.Tile, slate);
            if (s != null) Store(slate, map, s);
        }

        protected override bool TestRunInt(Slate slate)
        {
            Map map = slate.Get<Map>("map");
            if (map == null) return false;
            Settlement s = Pick(map.Tile, slate);
            if (s == null) return false;
            Store(slate, map, s);
            return true;
        }
    }
}
