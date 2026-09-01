using HarmonyLib;
using Verse;

namespace BigAndSmall;

[StaticConstructorOnStartup]
internal class BigAndSmall_Early : Mod
{
	public static BigAndSmall_Early instance;

	public BigAndSmall_Early(ModContentPack content)
		: base(content)
	{
		instance = this;
		if (BigSmallMod.settings == null)
		{
			BigSmallMod.settings = ((Mod)this).GetSettings<BSSettings>();
		}
		ApplyHarmonyPatches();
	}

	private static void ApplyHarmonyPatches()
	{
		//IL_0005: Unknown result type (might be due to invalid IL or missing references)
		new Harmony("RedMattis.BigAndSmall_Early").PatchAll();
	}
}
