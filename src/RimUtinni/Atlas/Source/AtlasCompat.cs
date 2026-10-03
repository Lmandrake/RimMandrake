using System;
using System.Reflection;
using Verse;

namespace RimMandrake.Utinni.Atlas
{
    // Reads other mods' story state by reflection, so the Atlas has no hard
    // dependency and loads clean when they are absent. Read-only: the Atlas
    // observes those authorities and never advances them (design §4).
    //
    // Sources (read from our own src, 2026-10-02):
    //   mandrake.rm.lorestages  RimMandrake.LoreStages.GameComponent_LoreStage
    //                           static Current; int GetStage(string ladderId) (0 = absent)
    //   mandrake.rm.ninefold    RimMandrake.Ninefold.GameComponent_Ninefold
    //                           static Instance; bool IsUnveiled(God god);
    //                           enum RimMandrake.Ninefold.God
    public static class AtlasCompat
    {
        private static bool loreLooked;
        private static PropertyInfo loreCurrent;
        private static MethodInfo loreGetStage;

        private static bool nineLooked;
        private static PropertyInfo nineInstance;
        private static MethodInfo nineIsUnveiled;
        private static Type godEnum;

        private static Type FindType(string fullName)
        {
            foreach (ModContentPack mcp in LoadedModManager.RunningModsListForReading)
                foreach (Assembly a in mcp.assemblies.loadedAssemblies)
                {
                    Type t = a.GetType(fullName, false);
                    if (t != null) return t;
                }
            return null;
        }

        private static void LookLore()
        {
            if (loreLooked) return;
            loreLooked = true;
            Type t = FindType("RimMandrake.LoreStages.GameComponent_LoreStage");
            if (t == null) return;
            loreCurrent = t.GetProperty("Current", BindingFlags.Public | BindingFlags.Static);
            loreGetStage = t.GetMethod("GetStage", BindingFlags.Public | BindingFlags.Instance, null, new[] { typeof(string) }, null);
        }

        public static bool LoreStagesAvailable
        {
            get { LookLore(); return loreCurrent != null && loreGetStage != null; }
        }

        public static int LoreStageOf(string ladderId)
        {
            if (!LoreStagesAvailable || ladderId.NullOrEmpty()) return 0;
            object comp = loreCurrent.GetValue(null);
            if (comp == null) return 0;
            return (int)loreGetStage.Invoke(comp, new object[] { ladderId });
        }

        private static void LookNine()
        {
            if (nineLooked) return;
            nineLooked = true;
            Type t = FindType("RimMandrake.Ninefold.GameComponent_Ninefold");
            godEnum = FindType("RimMandrake.Ninefold.God");
            if (t == null || godEnum == null) return;
            nineInstance = t.GetProperty("Instance", BindingFlags.Public | BindingFlags.Static);
            nineIsUnveiled = t.GetMethod("IsUnveiled", BindingFlags.Public | BindingFlags.Instance, null, new[] { godEnum }, null);
        }

        public static bool NinefoldAvailable
        {
            get { LookNine(); return nineInstance != null && nineIsUnveiled != null; }
        }

        public static bool GodNameValid(string god)
        {
            if (!NinefoldAvailable || god.NullOrEmpty()) return false;
            return Enum.IsDefined(godEnum, god);
        }

        public static bool IsUnveiled(string god)
        {
            if (!GodNameValid(god)) return false;
            object comp = nineInstance.GetValue(null);
            if (comp == null) return false;
            object g = Enum.Parse(godEnum, god);
            return (bool)nineIsUnveiled.Invoke(comp, new[] { g });
        }
    }
}
