namespace RimMandrake.FlowWorks
{
    /// <summary>The depth-engine switch is read once per game (the game object is the key), so flipping it mid-game does nothing
    /// until a reload. Pure, so the selftest drives it without a running game.</summary>
    public static class EngineSwitch
    {
        public static bool Resolve(ref object snapKey, ref bool snap, object gameKey, bool setting, bool live)
        {
            if (live)
            {
                return setting;
            }
            if (gameKey == null)
            {
                return setting;
            }
            if (!ReferenceEquals(snapKey, gameKey))
            {
                snapKey = gameKey;
                snap = setting;
            }
            return snap;
        }
    }
}
