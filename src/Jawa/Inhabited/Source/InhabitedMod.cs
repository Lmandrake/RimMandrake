using System.Reflection;
using HarmonyLib;
using Verse;

namespace Inhabited
{
    /// <summary>
    /// Harmony bootstrap. Nothing else belongs in here.
    ///
    /// Harmony itself must come from brrainz.harmony at runtime, never from this
    /// mod's own folder -- CopyLocalLockFileAssemblies is false in the csproj for
    /// exactly that reason, and About.xml declares the dependency and the load
    /// order.
    /// </summary>
    [StaticConstructorOnStartup]
    public static class InhabitedMod
    {
        static InhabitedMod()
        {
            new Harmony("mandrake.inhabited").PatchAll(Assembly.GetExecutingAssembly());
        }
    }
}
