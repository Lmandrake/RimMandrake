using Verse;

namespace RimMandrake.Watchers
{
    /// <summary>
    /// WATCHER_CREATURES_MOD_1. The readable sign a hidden watcher leaves on its cell (owner ruling
    /// 2026-09-30: hide = vanish in place + a sign mark on the cell; "no animal vanishes without a
    /// readable sign"). Ethereal, so it never blocks, wipes or gets hauled or cleaned; the watch job
    /// spawns it and its finish action destroys it on every exit path. It is the Flush order's target.
    /// </summary>
    public class RM_WatcherSign : Thing
    {
        public Pawn owner;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_References.Look(ref owner, "owner");
        }

        public override string GetInspectString()
        {
            string s = base.GetInspectString();
            if (owner != null && !owner.Dead)
            {
                string line = "RM_Watchers_SignInspect".Translate(owner.KindLabel);
                s = s.NullOrEmpty() ? line : s + "\n" + line;
            }
            return s;
        }
    }
}
