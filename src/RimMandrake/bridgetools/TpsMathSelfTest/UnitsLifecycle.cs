// Game-scoped state (MUST 6): labels, cumulative save time and attribution never cross loaded games.
using L = JawaBench.BridgeTools.JawaBenchTpsLifecycle;
using S = JawaBench.BridgeTools.JawaBenchTpsStages;

namespace JawaBench.BridgeTools
{
    internal static partial class Units
    {
        private static void T_SustainedStale()
        {
            var low = new System.Collections.Generic.List<JawaBenchTpsMath.StreakWindow>();
            for (int i = 0; i < 6; i++) low.Add(new JawaBenchTpsMath.StreakWindow(0.3, 5.0));
            Check(JawaBenchTpsMath.SustainedFresh(low, 5) == "low", "a fresh low streak is low");
            Check(JawaBenchTpsMath.SustainedFresh(low, 120) == "unknown", "a streak last fed 120 s ago is unknown, not low");
        }

        private static void T_RingKeepsAnHour()
        {
            var at1 = new JawaBenchTpsMath.WindowRing();
            for (int i = 0; i < 5000; i++) at1.Add(i, "r" + i);
            Check(at1.Count == 3600, "1 s windows: the ring holds 3600 rows, not 720: " + at1.Count);
            Check(at1.Lines()[0] == "r1400" && at1.Lines()[3599] == "r4999", "the newest hour is what stays, oldest first");
            var at5 = new JawaBenchTpsMath.WindowRing();
            for (int i = 0; i < 2000; i++) at5.Add(i * 5.0, "r" + i);
            Check(at5.Count == 721, "5 s windows: one hour, both ends inclusive: " + at5.Count);
            var mixed = new JawaBenchTpsMath.WindowRing();
            for (int i = 0; i < 3600; i++) mixed.Add(i, "armed" + i);
            for (int i = 1; i <= 800; i++) mixed.Add(3599 + i * 5.0, "campaign" + i);
            Check(mixed.Count == 721, "after disarming the 1 s rows age out by time, not by count: " + mixed.Count);
        }

        private static void T_LifecycleScopes()
        {
            var st = new S(Freq);
            var life = new L(st);
            object g1 = new object(), g2 = new object(), g3 = new object();
            Check(life.OnFrame(null, false, 1) == L.Event.Menu, "start at the menu");
            life.OnLoadRequested("Ashkarr_A", 2);
            Check(life.OnFrame(g1, false, 3) == L.Event.None, "loading (not Playing) is not a game yet");
            Check(life.OnFrame(g1, true, 60) == L.Event.Game && life.SaveName == "Ashkarr_A" && life.GameSeq == 1,
                  "loaded game 1 carries its save name: " + life.SaveName + " seq " + life.GameSeq);
            life.OnSave(4.5);
            st.TickBegin();
            st.TickEnd(Tk(100), Tk(100.2), 1);                 // 200 ms of game-1 attribution, never emitted
            Check(life.OnFrame(null, false, 70) == L.Event.Menu && life.SaveName == "",
                  "menu clears the game's save label: '" + life.SaveName + "'");
            Check(life.OnFrame(g2, true, 80) == L.Event.Game, "new game 2 entered");
            Check(life.SaveName == "", "a NEW game never inherits the previous load's save name: '" + life.SaveName + "'");
            Check(life.SaveTotal == 0, "cumulative save time is per game: " + life.SaveTotal);
            Check(st.Total(S.CTick) == 0, "attribution from game 1 does not reach game 2's first window: " +
                  st.Total(S.CTick) / Freq + " s carried");
            // a load request that never produced a game (failed load) must not label a much later new game
            life.OnLoadRequested("Broken_Save", 90);
            Check(life.OnFrame(null, false, 91) == L.Event.Menu, "back at the menu");
            Check(life.OnFrame(g3, true, 90 + 3600) == L.Event.Game && life.SaveName == "",
                  "a stale (1 h old) load request does not label a new game: '" + life.SaveName + "'");
        }
    }
}
