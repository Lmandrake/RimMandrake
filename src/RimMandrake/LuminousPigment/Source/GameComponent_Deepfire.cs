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

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref matSeen, "rmDeepfireMatSeen", false);
            Scribe_Values.Look(ref chillMessageShown, "rmDeepfireChillMessageShown", false);
        }
    }
}
