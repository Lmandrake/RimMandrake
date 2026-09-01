using HarmonyLib;
using Verse;

namespace VEF;

public class VEF_Mod : Mod
{
	public static Harmony harmonyInstance;

	public VEF_Mod(ModContentPack content)
		: base(content)
	{
		//IL_000c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0016: Expected O, but got Unknown
		harmonyInstance = new Harmony("OskarPotocki.VEF");
		VEF_HarmonyCategories.TryPatchAll(harmonyInstance);
	}
}
