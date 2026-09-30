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
            return !gc.impressedQuadrum.TryGetValue(f.loadID, out int q) || q != CurrentQuadrumIndex;
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

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref matSeen, "rmDeepfireMatSeen", false);
            Scribe_Values.Look(ref chillMessageShown, "rmDeepfireChillMessageShown", false);
            Scribe_Collections.Look(ref impressedQuadrum, "rmDeepfireImpressedQuadrum", LookMode.Value, LookMode.Value);
            if (Scribe.mode == LoadSaveMode.PostLoadInit && impressedQuadrum == null)
            {
                impressedQuadrum = new Dictionary<int, int>();
            }
        }
    }
}
