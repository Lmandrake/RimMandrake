// JawaBenchTpsLifecycle.cs - which GAME a measurement belongs to (BRIDGE_TPS_REVIEW2_FIXES_1, MUST 6).
//
// ⛔ NO Verse, NO UnityEngine, NO HarmonyLib: compiled into the companion AND the offline harness. The
// sampler's Root.Update prefix passes the current Game object and whether it is Playing; this decides
// the menu/game transitions and the GAME-scoped labels.

using System;

namespace JawaBench.BridgeTools
{
    internal sealed class JawaBenchTpsLifecycle
    {
        internal enum Event { None, Menu, Game }

        /// <summary>A load request older than this (monotonic seconds) never labels a game: a failed load must not
        /// name a new game started much later. Map generation of a large save stays well inside it.</summary>
        internal const double LoadRequestTtlSeconds = 1200;

        private object _game;
        internal bool InMenu;
        private string _pendingLoad;
        private double _pendingAt;
        /// <summary>The save the CURRENT game was loaded from ("" = new game, or not known). Game-scoped.</summary>
        internal string SaveName { get; private set; } = "";
        /// <summary>Seconds spent in SaveGame during the current game. Game-scoped.</summary>
        internal double SaveTotal { get; private set; }
        /// <summary>1, 2, ... per game entered in this process: rows carry it so a reader never joins two games.</summary>
        internal int GameSeq { get; private set; }
        private readonly JawaBenchTpsStages _stages;

        internal JawaBenchTpsLifecycle(JawaBenchTpsStages stagesToReset) { _stages = stagesToReset; }

        /// <summary>GameDataSaveLoader.LoadGame only QUEUES a load (decompiled 1.6): this is a request, consumed by
        /// the next game that reaches Playing within the TTL, never a fact about the current game.</summary>
        internal void OnLoadRequested(string name, double now) { _pendingLoad = name ?? ""; _pendingAt = now; }

        internal void OnSave(double seconds) { if (seconds > 0) SaveTotal += seconds; }

        private void GameBoundary()
        {
            SaveTotal = 0;
            _stages?.Reset();          // attribution totals and worst ticks never cross a game boundary
        }

        internal Event OnFrame(object game, bool playing, double now)
        {
            if (game == null || !playing)
            {
                if (!InMenu && game == null)
                {
                    InMenu = true;
                    _game = null;
                    SaveName = "";
                    GameBoundary();
                    return Event.Menu;
                }
                return Event.None;
            }
            if (!ReferenceEquals(game, _game))
            {
                _game = game;
                InMenu = false;
                GameSeq++;
                bool fresh = _pendingLoad != null && now - _pendingAt <= LoadRequestTtlSeconds;
                SaveName = fresh ? _pendingLoad : "";
                _pendingLoad = null;
                GameBoundary();
                return Event.Game;
            }
            return Event.None;
        }
    }
}
