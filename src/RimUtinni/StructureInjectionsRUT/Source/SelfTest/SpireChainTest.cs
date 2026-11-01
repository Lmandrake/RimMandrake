using System;
using RimMandrake.RustCathedral.Hum;
using RimMandrake.Utinni.StructureInjectionsRUT;
using Verse;

namespace StructureInjectionsRUT.SelfTest
{
    // SPIRE_DUNGEONS_MERGE_DARK_TOWER: the real gate chain, attitude component to seal, over the maps a
    // player actually holds: a home off Cathedral ground, the Spire, and a Cathedral map that comes and goes.
    internal static class SpireChainTest
    {
        private static int nextMap = 1;

        private static Map NewMap(bool cathedral, int stage = 0)
        {
            Map map = new Map { uniqueID = nextMap++ };
            map.components.Add(new RM_MapComponent_BiomeAttitude { cathedralGround = cathedral, stage = stage });
            Find.Maps.Add(map);
            return map;
        }

        private static void SetStage(Map map, int stage)
        {
            ((RM_MapComponent_BiomeAttitude)map.components[0]).stage = stage;
        }

        private static GameComponent_SpireEntry NewGame()
        {
            Find.Maps.Clear();
            Scribe_Values.Saved.Clear();
            Game game = new Game();
            GameComponent_SpireEntry entry = new GameComponent_SpireEntry(game);
            game.components.Add(entry);
            Current.Game = game;
            return entry;
        }

        // A fresh seal on the Spire map, run for 300 ticks. True if it opened.
        private static bool SealOpensOn(Map spire, GameComponent_SpireEntry entry)
        {
            Thing seal = new Thing { Map = spire };
            CompSpireSeal comp = new CompSpireSeal { parent = seal };
            for (int i = 0; i < 300; i++)
            {
                Find.TickManager.TicksGame++;
                entry.GameComponentTick();
                comp.CompTick();
            }
            return !seal.Spawned;
        }

        public static void Run(Action<bool, string> check)
        {
            GameComponent_SpireEntry entry = NewGame();
            Map home = NewMap(false);
            Map spire = NewMap(false);
            Map cathedral = NewMap(true);
            check(!SealOpensOn(spire, entry), "spire: chain: WARY on the Cathedral map, seal shut");
            SetStage(cathedral, 1);
            check(!SealOpensOn(spire, entry), "spire: chain: TOLERATED, seal shut");

            SetStage(cathedral, 2);
            check(SealOpensOn(spire, entry), "spire: chain: VOUCHED, seal opens while the Cathedral map is loaded");

            Find.Maps.Remove(cathedral);
            check(SealOpensOn(spire, entry), "spire: chain: Cathedral map gone, off-ground maps forget nothing");

            Map fresh = NewMap(true);
            check(SealOpensOn(spire, entry), "spire: chain: a fresh Cathedral map at 0 does not erase earned trust");
            SetStage(fresh, 3);
            check(SealOpensOn(spire, entry), "spire: chain: a warmer fresh map takes over the reading");
            SetStage(fresh, 0);
            check(!SealOpensOn(spire, entry), "spire: chain: a dark flip on the map that set the reading shuts it");

            // Trust earned, then a save and a load of a game with no Cathedral map.
            SetStage(fresh, 2);
            entry.GameComponentTick();
            Find.TickManager.TicksGame += 250 - Find.TickManager.TicksGame % 250;
            entry.GameComponentTick();
            Scribe_Values.Saved.Clear();
            entry.ExposeData();
            System.Collections.Generic.Dictionary<string, object> saved =
                new System.Collections.Generic.Dictionary<string, object>(Scribe_Values.Saved);
            GameComponent_SpireEntry loaded = NewGame();
            foreach (var pair in saved)
            {
                Scribe_Values.Saved[pair.Key] = pair.Value;
            }
            loaded.ExposeData();
            home = NewMap(false);
            spire = NewMap(false);
            check(SealOpensOn(spire, loaded), "spire: chain: the reading survives save and load");

            // The source map's identity is saved too: after a load it can still lower the reading.
            Find.Maps.Add(fresh);
            SetStage(fresh, 0);
            check(!SealOpensOn(spire, loaded), "spire: chain: the source map survives save and load");

            entry = NewGame();
            NewMap(false);
            spire = NewMap(false);
            NewMap(true);
            check(!SealOpensOn(spire, entry), "spire: chain: never earned, seal shut");
            StructureInjectionsRUTSettings.spireEntryGated = false;
            check(SealOpensOn(spire, entry), "spire: chain: Mod Setting off, seal opens");
            StructureInjectionsRUTSettings.spireEntryGated = true;

            DamageInfo hit = default(DamageInfo);
            new CompSpireHull().PostPreApplyDamage(ref hit, out bool hullTook);
            new CompSpireSeal().PostPreApplyDamage(ref hit, out bool sealTook);
            check(hullTook && sealTook, "spire: chain: hull and seal absorb every hit");

            // The kernel's own edges.
            int source = 5;
            var none = new System.Collections.Generic.KeyValuePair<int, int>[0];
            check(SpireEntryKernel.Fold(2, ref source, none) == 2, "spire: no map at all keeps the last reading");
            var off = new[] { new System.Collections.Generic.KeyValuePair<int, int>(7, -1) };
            check(SpireEntryKernel.Fold(2, ref source, off) == 2, "spire: off Cathedral ground says nothing");
        }
    }
}
