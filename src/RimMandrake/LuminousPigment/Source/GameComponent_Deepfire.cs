using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.LuminousPigment
{
    // Spec §2.3: the research gate needs to remember, per game, whether a
    // colonist has ever actually seen crowncarpet growing. One flag, one
    // GameComponent — this is the whole "discovery" state.
    public class GameComponent_Deepfire : GameComponent
    {
        public bool matSeen;
        public bool chillMessageShown;

        public GameComponent_Deepfire(Game game)
        {
        }

        public static GameComponent_Deepfire Instance
        {
            get { return Current.Game?.GetComponent<GameComponent_Deepfire>(); }
        }

        // DEEPFIRE_STATUS_THOUGHTS_1, spec §4.1 RM_ImpressedByDeepfire: "cap
        // once per faction per quadrum". Faction.loadID -> absolute quadrum
        // index (GenTicks.TicksAbs / GenDate.TicksPerQuadrum) last impressed.
        private Dictionary<int, int> impressedQuadrum = new Dictionary<int, int>();

        private static int CurrentQuadrumIndex => GenTicks.TicksAbs / GenDate.TicksPerQuadrum;

        public static bool CanImpress(Faction f)
        {
            GameComponent_Deepfire gc = Instance;
            if (gc == null || f == null) return false;
            bool known = gc.impressedQuadrum.TryGetValue(f.loadID, out int q);
            return RM_DeepfireRules.CanImpress(known, q, CurrentQuadrumIndex);
        }

        public static void MarkImpressed(Faction f)
        {
            GameComponent_Deepfire gc = Instance;
            if (gc == null || f == null) return;
            gc.impressedQuadrum[f.loadID] = CurrentQuadrumIndex;
        }

        // Dev proof only: forget the cap so a re-run starts clean.
        public static void ResetImpressCap()
        {
            Instance?.impressedQuadrum.Clear();
        }

        // DEEPFIRE_GOD_BRIDGE_DELTAS_1, spec §5.2 anti-pinning: first-coat god
        // events counted per def key (DeepfireGodDeltas.KeyFor) per game.
        private Dictionary<string, int> godCoatEvents = new Dictionary<string, int>();

        // Returns the count BEFORE this event, then records it. No game ->
        // 0 (undiminished; the bridge no-ops without a game anyway).
        public static int NoteGodCoatEvent(string defKey)
        {
            GameComponent_Deepfire gc = Instance;
            if (gc == null) return 0;
            gc.godCoatEvents.TryGetValue(defKey, out int prior);
            gc.godCoatEvents[defKey] = prior + 1;
            return prior;
        }

        public static int GodCoatEventsFor(string defKey)
        {
            GameComponent_Deepfire gc = Instance;
            if (gc == null) return 0;
            gc.godCoatEvents.TryGetValue(defKey, out int n);
            return n;
        }

        // Dev proof only: forget one def's count so a proof measures the
        // undiminished event.
        public static void ResetGodCoatEvents(string defKey)
        {
            Instance?.godCoatEvents.Remove(defKey);
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref matSeen, "rmDeepfireMatSeen", false);
            Scribe_Values.Look(ref chillMessageShown, "rmDeepfireChillMessageShown", false);
            Scribe_Collections.Look(ref impressedQuadrum, "rmDeepfireImpressedQuadrum", LookMode.Value, LookMode.Value);
            Scribe_Collections.Look(ref godCoatEvents, "rmDeepfireGodCoatEvents", LookMode.Value, LookMode.Value);
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                if (impressedQuadrum == null) impressedQuadrum = new Dictionary<int, int>();
                if (godCoatEvents == null) godCoatEvents = new Dictionary<string, int>();
            }
        }
    }
}
