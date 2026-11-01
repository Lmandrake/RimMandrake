using System.Collections.Generic;
using RimWorld;
using RimWorld.Planet;
using RimWorld.QuestGen;
using Verse;

namespace RimMandrake.Utinni.WasteRun
{
    // WASTE_RUN_STUBS_1. Where the ship is, and what a chosen branch does to the world.
    public static class WasteRunWorld
    {
        public static FlightGate Gate(Map map, WasteDestination d)
        {
            bool exists, at;
            Locate(map, d, out exists, out at);
            return WasteRunKernel.GateFlight(WasteRunSettings.flightRequiredEnabled, exists, at);
        }

        private static void Locate(Map map, WasteDestination d, out bool exists, out bool at)
        {
            PlanetTile here = map != null ? map.Tile : PlanetTile.Invalid;
            bool surface = here.Valid && here.Layer != null && here.Layer.IsRootSurface;
            switch (d)
            {
                case WasteDestination.DropOnEmpire:
                    NearEmpire(here, surface, out exists, out at);
                    return;
                case WasteDestination.FreezeColdSide:
                    NearCold(here, surface, out exists, out at);
                    return;
                case WasteDestination.EntombAssailants:
                    NearLab(here, surface, out exists, out at);
                    if (exists) return;
                    // wastes.md section 10: "the remaining Assailants discovered there", the cold side.
                    NearCold(here, surface, out exists, out at);
                    return;
                case WasteDestination.IgnitePropaneLake:
                    InBiomes(here, surface, WasteRunKernel.PropaneBiomes, out exists, out at);
                    return;
                default:
                    InBiomes(here, surface, WasteRunKernel.StenchlandsBiomes, out exists, out at);
                    return;
            }
        }

        private static void NearEmpire(PlanetTile here, bool surface, out bool exists, out bool at)
        {
            exists = at = false;
            List<Settlement> all = Find.WorldObjects.Settlements;
            for (int i = 0; i < all.Count; i++)
            {
                Faction f = all[i].Faction;
                if (f == null || f.def.defName != "Empire" || !all[i].Tile.Layer.IsRootSurface) continue;
                exists = true;
                if (surface && Find.WorldGrid.ApproxDistanceInTiles(here, all[i].Tile) <= WasteRunKernel.EmpireReachTiles) at = true;
            }
        }

        private static void NearLab(PlanetTile here, bool surface, out bool exists, out bool at)
        {
            exists = at = false;
            List<Site> all = Find.WorldObjects.Sites;
            for (int i = 0; i < all.Count; i++)
            {
                bool lab = false;
                for (int p = 0; p < all[i].parts.Count; p++)
                {
                    if (all[i].parts[p].def.defName == WasteRunKernel.WarLabSitePart) lab = true;
                }
                if (!lab || !all[i].Tile.Layer.IsRootSurface) continue;
                exists = true;
                if (surface && Find.WorldGrid.ApproxDistanceInTiles(here, all[i].Tile) <= WasteRunKernel.LabReachTiles) at = true;
            }
        }

        private static void NearCold(PlanetTile here, bool surface, out bool exists, out bool at)
        {
            WorldGrid grid = Find.WorldGrid;
            at = surface && grid[here].temperature <= WasteRunKernel.ColdSideMaxTileTemp;
            exists = at;
            for (int i = 0; !exists && i < grid.TilesCount; i++)
            {
                if (grid[new PlanetTile(i, grid.Surface)].temperature <= WasteRunKernel.ColdSideMaxTileTemp) exists = true;
            }
        }

        private static void InBiomes(PlanetTile here, bool surface, string[] names, out bool exists, out bool at)
        {
            WorldGrid grid = Find.WorldGrid;
            at = surface && Named(grid[here].PrimaryBiome, names);
            exists = at;
            for (int i = 0; !exists && i < grid.TilesCount; i++)
            {
                if (Named(grid[new PlanetTile(i, grid.Surface)].PrimaryBiome, names)) exists = true;
            }
        }

        private static bool Named(BiomeDef b, string[] names)
        {
            return b != null && System.Array.IndexOf(names, b.defName) >= 0;
        }

        // Fired once by the quest part on the branch's signal. `tile` is where the ship stands.
        public static void Apply(WasteEffect e, PlanetTile tile)
        {
            GiveMood(e);
            if (e == WasteEffect.PropaneIgnited && WasteRunSettings.warLabBreachEnabled) BreachWarLab();
            if (WasteRunKernel.IsSlime(e) && WasteRunSettings.slimeWorldEffectsEnabled) SlimeWorld(e, tile);
        }

        public static void GiveMood(WasteEffect e)
        {
            if (!WasteRunSettings.moodMemoriesEnabled) return;
            ThoughtDef def = DefDatabase<ThoughtDef>.GetNamedSilentFail(WasteRunKernel.MoodDefName(e));
            if (def == null)
            {
                Log.Error("[WasteRun] no ThoughtDef " + WasteRunKernel.MoodDefName(e));
                return;
            }
            foreach (Pawn p in PawnsFinder.AllMapsCaravansAndTravellingTransporters_Alive_FreeColonists)
            {
                if (p.needs != null && p.needs.mood != null) p.needs.mood.thoughts.memories.TryGainMemory(def);
            }
        }

        // The crater lives in mandrake.rut.injections, which this mod does not require.
        public static bool BreachWarLab()
        {
            System.Type t = GenTypes.GetTypeInAnyAssembly("RimMandrake.Utinni.StructureInjectionsRUT.WarLabCraterMutation");
            System.Reflection.MethodInfo ignite = t == null ? null : t.GetMethod("Ignite", System.Type.EmptyTypes);
            if (ignite == null)
            {
                Log.Warning("[WasteRun] structure injections absent: the lake ignition changed no tiles.");
                return false;
            }
            bool fired = (bool)ignite.Invoke(null, null);
            Log.Message("[WasteRun] war-lab ignition mutated tiles: " + fired);
            return fired;
        }

        public static void SlimeWorld(WasteEffect e, PlanetTile tile)
        {
            if (e == WasteEffect.SlimeUnknown)
            {
                Current.Game.GetComponent<GameComponent_WasteRunAftermath>().Schedule(tile);
                return;
            }
            bool bloom = e == WasteEffect.SlimeBloomed;
            SpreadPollution(tile, bloom ? WasteRunKernel.SlimeBloomDelta : WasteRunKernel.SlimeNeutralizeDelta);
            if (!bloom) return;
            List<Map> maps = Find.Maps;
            for (int m = 0; m < maps.Count; m++)
            {
                if (!maps[m].IsPlayerHome) continue;
                GameCondition fallout = GameConditionMaker.MakeCondition(GameConditionDefOf.ToxicFallout, WasteRunKernel.SlimeFalloutDays * 60000);
                maps[m].gameConditionManager.RegisterCondition(fallout);
            }
        }

        // Writes Tile.pollution directly: PolluteWorldAtTile would post one message per tile.
        public static int SpreadPollution(PlanetTile center, float delta)
        {
            if (!center.Valid || !center.Layer.IsRootSurface) return 0;
            WorldGrid grid = Find.WorldGrid;
            int touched = 0;
            for (int i = 0; i < grid.TilesCount; i++)
            {
                PlanetTile t = new PlanetTile(i, center.Layer);
                float dist = grid.ApproxDistanceInTiles(center, t);
                if (dist > WasteRunKernel.SlimeReachTiles) continue;
                Tile tile = grid[t];
                if (tile.PrimaryBiome == null || !tile.PrimaryBiome.allowPollution) continue;
                float next = WasteRunKernel.SlimePollution(tile.pollution, delta, dist, WasteRunKernel.SlimeReachTiles);
                if (next == tile.pollution) continue;
                bool rose = next > tile.pollution;
                tile.pollution = next;
                Map map = Current.Game.FindMap(t);
                if (map != null && rose) PollutionUtility.PolluteMapToPercent(map, next);
                Find.World.renderer.Notify_TilePollutionChanged(t);
                touched++;
            }
            return touched;
        }
    }

    // The Slime's third outcome: nothing now, then one answer from below. Saved, so a reload keeps the coin.
    public class GameComponent_WasteRunAftermath : GameComponent
    {
        private int dueTick = -1;
        private int tileId = -1;
        // Where the ship stood when the destination was committed; the branch's effect reads it.
        public int shipTileId = -1;
        private bool bloom;

        public GameComponent_WasteRunAftermath(Game game)
        {
        }

        public bool Pending { get { return dueTick >= 0; } }
        public int DueTick { get { return dueTick; } }

        public void Schedule(PlanetTile tile)
        {
            if (Pending) return;
            tileId = tile.tileId;
            bloom = WasteRunKernel.ResolveUnknown(Rand.Value) == WasteEffect.SlimeBloomed;
            dueTick = Find.TickManager.TicksGame + Rand.RangeInclusive(WasteRunKernel.UnknownMinDays, WasteRunKernel.UnknownMaxDays) * 60000;
        }

        public override void GameComponentTick()
        {
            if (Find.TickManager.TicksGame % GenTicks.TickLongInterval != 0) return;
            if (WasteRunKernel.UnknownDue(dueTick, Find.TickManager.TicksGame)) Resolve();
        }

        public void Resolve()
        {
            WasteEffect e = bloom ? WasteEffect.SlimeBloomed : WasteEffect.SlimeNeutralized;
            dueTick = -1;
            WasteRunWorld.GiveMood(e);
            WasteRunWorld.SlimeWorld(e, new PlanetTile(tileId, Find.WorldGrid.Surface));
            Find.LetterStack.ReceiveLetter(bloom ? "The Throat answered late" : "The Throat went quiet late",
                bloom ? "Weeks after the slime went down, the Stenchlands breathed out. Whatever you poured was not dead. It was thinking it over."
                      : "Weeks after the slime went down, the groaning under the Stenchlands stopped. The ground around the pit is coming back, a little, and nobody is willing to say why.",
                bloom ? LetterDefOf.NegativeEvent : LetterDefOf.PositiveEvent);
        }

        public override void ExposeData()
        {
            Scribe_Values.Look(ref dueTick, "dueTick", -1);
            Scribe_Values.Look(ref tileId, "tileId", -1);
            Scribe_Values.Look(ref shipTileId, "shipTileId", -1);
            Scribe_Values.Look(ref bloom, "bloom");
        }
    }

    public class RUT_QuestPart_WasteRunEffect : QuestPart
    {
        public string inSignal;
        public WasteEffect effect;

        public override void Notify_QuestSignalReceived(Signal signal)
        {
            base.Notify_QuestSignalReceived(signal);
            if (signal.tag != inSignal) return;
            int id = Current.Game.GetComponent<GameComponent_WasteRunAftermath>().shipTileId;
            WasteRunWorld.Apply(effect, new PlanetTile(id, Find.WorldGrid.Surface));
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref inSignal, "inSignal");
            Scribe_Values.Look(ref effect, "effect");
        }
    }

    // Goes inside a QuestNode_Signal branch: the effect fires on that branch's signal.
    public class RUT_QuestNode_WasteRunEffect : QuestNode
    {
        public SlateRef<WasteEffect> effect;

        protected override bool TestRunInt(Slate slate) { return true; }

        protected override void RunInt()
        {
            Slate slate = QuestGen.slate;
            QuestGen.quest.AddPart(new RUT_QuestPart_WasteRunEffect
            {
                inSignal = slate.Get<string>("inSignal"),
                effect = effect.GetValue(slate)
            });
        }
    }
}
