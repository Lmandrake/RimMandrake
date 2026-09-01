using Verse;

namespace BigAndSmall;

public static class BS
{
	private static bool? prePatcherActive;

	private static int internalTick;

	private static int internalTick10;

	private static int internalTick100;

	public static BSSettings Settings => BigSmallMod.settings;

	/// <summary>
	/// Used when you need to make sure ticks aren't randomly skipped. Thanks Ludeon or whatever mod causes this. Ó_ò
	/// </summary>
	public static int Tick => internalTick;

	public static int Tick10 => internalTick10;

	public static int Tick100 => internalTick100;

	public static bool PrePatcherActive
	{
		get
		{
			bool valueOrDefault = prePatcherActive == true;
			if (!prePatcherActive.HasValue)
			{
				valueOrDefault = ModsConfig.IsActive("zetrith.prepatcher");
				prePatcherActive = valueOrDefault;
				return valueOrDefault;
			}
			return valueOrDefault;
		}
	}

	public static void IncrementTick()
	{
		if (internalTick == int.MaxValue)
		{
			internalTick = 0;
		}
		internalTick++;
		internalTick10 = internalTick / 10;
		internalTick100 = internalTick / 100;
	}

	public static void SetTick(int tick)
	{
		internalTick = tick;
	}
}
