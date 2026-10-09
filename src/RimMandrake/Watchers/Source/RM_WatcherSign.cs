using Verse;

namespace RimMandrake.Watchers
{
    /// <summary>
    /// WATCHER_CREATURES_MOD_1. The readable sign a hidden watcher leaves on its cell (owner ruling
    /// 2026-09-30: hide = vanish in place + a sign mark on the cell; "no animal vanishes without a
    /// readable sign"). Ethereal, so it never blocks, wipes or gets hauled or cleaned, and explosions
    /// skip it (DamageWorker.ExplosionAffectCell ignores Ethereal). The watch job spawns it and its finish
    /// action destroys it on every exit path. It also checks itself every rare tick
    /// (RM_WatcherKernel.SignValid): a sign whose owner is dead, gone or out of the watch job (an orphan,
    /// e.g. after a load), or that is not the one its owner's job holds (a duplicate), removes itself.
    /// </summary>
    public class RM_WatcherSign : Thing
    {
        public Pawn owner;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_References.Look(ref owner, "owner");
        }

        public bool StillValid
        {
            get
            {
                var driver = owner?.jobs?.curDriver as RM_JobDriver_Watch;
                return RM_WatcherKernel.SignValid(owner != null, owner != null && owner.Spawned, owner != null && owner.Dead,
                    driver != null, driver != null && driver.Sign == this);
            }
        }

        public override void TickRare()
        {
            // No base.TickRare(): Verse.Thing.TickRare throws NotImplementedException (only ThingWithComps overrides it).
            if (Spawned && !StillValid)
            {
                Map.designationManager.RemoveAllDesignationsOn(this);
                Destroy();
            }
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
