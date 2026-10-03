using System.Linq;
using LudeonTK;
using Verse;

namespace RimMandrake.Utinni.Atlas
{
    // Dev-mode test harness for the Atlas. Gameplay never calls these. The poll
    // action is the deterministic way to prove a trigger without waiting for the
    // cadence; the light/forget actions exercise the window and the reward path.
    public static class AtlasDebugActions
    {
        private const string Cat = "RimUtinni.Atlas";

        [DebugAction(Cat, "Poll all triggers now", allowedGameStates = AllowedGameStates.Playing)]
        private static void PollNow()
        {
            GameComponent_Atlas c = GameComponent_Atlas.Instance;
            if (c == null) { Log.Error("[Atlas] no GameComponent_Atlas on the current game."); return; }
            int n = c.PollAll(includeExpensive: true, backfill: false);
            Log.Message("[Atlas] POLL lit=" + n + " detection=" + AtlasSettings.detectionEnabled);
        }

        [DebugAction(Cat, "Light one entry", allowedGameStates = AllowedGameStates.Playing)]
        private static void LightOne()
        {
            GameComponent_Atlas c = GameComponent_Atlas.Instance;
            if (c == null) return;
            Dialog_DebugOptionListLister.ShowSimpleDebugMenu(
                DefDatabase<AtlasEntryDef>.AllDefsListForReading.Where(d => !c.IsDiscovered(d)).ToList(),
                d => d.defName, d => c.Discover(d, backfill: false));
        }

        [DebugAction(Cat, "Forget one entry", allowedGameStates = AllowedGameStates.Playing)]
        private static void ForgetOne()
        {
            GameComponent_Atlas c = GameComponent_Atlas.Instance;
            if (c == null) return;
            Dialog_DebugOptionListLister.ShowSimpleDebugMenu(
                DefDatabase<AtlasEntryDef>.AllDefsListForReading.Where(d => c.IsDiscovered(d)).ToList(),
                d => d.defName, d => c.Forget(d));
        }

        [DebugAction(Cat, "Forget all entries", allowedGameStates = AllowedGameStates.Playing)]
        private static void ForgetAll()
        {
            GameComponent_Atlas.Instance?.ForgetAll();
            Log.Message("[Atlas] FORGOT all");
        }

        [DebugAction(Cat, "Report entry availability", allowedGameStates = AllowedGameStates.Playing)]
        private static void Report()
        {
            GameComponent_Atlas c = GameComponent_Atlas.Instance;
            foreach (AtlasEntryDef d in DefDatabase<AtlasEntryDef>.AllDefsListForReading)
                Log.Message("[Atlas] REPORT entry=" + d.defName + " available=" + d.Available + " lit=" + (c != null && c.IsDiscovered(d))
                    + " triggers=" + string.Join(",", d.triggers.Select(t => t.GetType().Name + (t.Available ? "" : "(absent)"))));
            if (c != null) Log.Message("[Atlas] archived records (def gone): " + c.ArchivedCount);
        }
    }
}
