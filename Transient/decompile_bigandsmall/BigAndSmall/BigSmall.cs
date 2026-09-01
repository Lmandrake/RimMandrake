using System.Linq;
using System.Threading;
using Verse;

namespace BigAndSmall;

[StaticConstructorOnStartup]
public static class BigSmall
{
	public static Thread mainThread;

	public static bool performScaleCalculations;

	private static bool? _BSGenesActive;

	private static bool? _BSOptionalActive;

	private static bool? _BSTransformGenes;

	private static bool? _BSTestModActive;

	private static bool? _BSSapientAnimalsActive_ForcedByMods;

	private static bool? _BSSapientAnimalsActive;

	private static bool? _BSSapientMechanoidsActive;

	private static bool? _BSAutoCombatFeatureCache;

	public static bool BSTestModActive
	{
		get
		{
			bool valueOrDefault = _BSTestModActive == true;
			if (!_BSTestModActive.HasValue)
			{
				valueOrDefault = ModsConfig.ActiveModsInLoadOrder.Any((ModMetaData x) => x.PackageIdPlayerFacing == "RedMattis.TestMod");
				_BSTestModActive = valueOrDefault;
				return valueOrDefault;
			}
			return valueOrDefault;
		}
	}

	public static bool BSOptionalActive
	{
		get
		{
			bool valueOrDefault = _BSOptionalActive == true;
			if (!_BSOptionalActive.HasValue)
			{
				valueOrDefault = ModsConfig.ActiveModsInLoadOrder.Any((ModMetaData x) => x.PackageIdPlayerFacing == "RedMattis.Optional");
				_BSOptionalActive = valueOrDefault;
				return valueOrDefault;
			}
			return valueOrDefault;
		}
	}

	public static bool BSTransformGenes
	{
		get
		{
			bool valueOrDefault = _BSTransformGenes == true;
			if (!_BSTransformGenes.HasValue)
			{
				valueOrDefault = BSGenesActive || BSOptionalActive || ModsConfig.ActiveModsInLoadOrder.Any((ModMetaData x) => x.PackageIdPlayerFacing == "RedMattis.TransformGenes");
				_BSTransformGenes = valueOrDefault;
				return valueOrDefault;
			}
			return valueOrDefault;
		}
	}

	public static bool BSSapientAnimalsActive_ForcedByMods
	{
		get
		{
			bool valueOrDefault = _BSSapientAnimalsActive_ForcedByMods == true;
			if (!_BSSapientAnimalsActive_ForcedByMods.HasValue)
			{
				valueOrDefault = ModsConfig.ActiveModsInLoadOrder.Any((ModMetaData x) => x.PackageIdPlayerFacing == "RedMattis.SapientAnimals" || x.PackageIdPlayerFacing == "RedMattis.MadApril2025") || BSTestModActive;
				_BSSapientAnimalsActive_ForcedByMods = valueOrDefault;
				return valueOrDefault;
			}
			return valueOrDefault;
		}
	}

	public static bool BSSapientAnimalsActive
	{
		get
		{
			bool valueOrDefault = _BSSapientAnimalsActive == true;
			if (!_BSSapientAnimalsActive.HasValue)
			{
				valueOrDefault = BSSapientAnimalsActive_ForcedByMods || GlobalSettings.IsFeatureEnabled("SapientAnimals") || BigSmallMod.settings.sapientAnimals;
				_BSSapientAnimalsActive = valueOrDefault;
				return valueOrDefault;
			}
			return valueOrDefault;
		}
	}

	public static bool BSSapientMechanoidsActive
	{
		get
		{
			bool valueOrDefault = _BSSapientMechanoidsActive == true;
			if (!_BSSapientMechanoidsActive.HasValue)
			{
				valueOrDefault = GlobalSettings.IsFeatureEnabled("SapientMechanoids") || BigSmallMod.settings.sapientMechanoids;
				_BSSapientMechanoidsActive = valueOrDefault;
				return valueOrDefault;
			}
			return valueOrDefault;
		}
	}

	public static bool RobotsEnabled
	{
		get
		{
			if (!GlobalSettings.IsFeatureEnabled("Robots"))
			{
				return BSSapientMechanoidsActive;
			}
			return true;
		}
	}

	public static bool BSGenesActive
	{
		get
		{
			bool valueOrDefault = _BSGenesActive == true;
			if (!_BSGenesActive.HasValue)
			{
				valueOrDefault = ModsConfig.ActiveModsInLoadOrder.Any((ModMetaData x) => x.PackageIdPlayerFacing == "RedMattis.BigSmall.Core");
				_BSGenesActive = valueOrDefault;
				return valueOrDefault;
			}
			return valueOrDefault;
		}
	}

	public static bool DisableAllExtraWidgets => BigSmallMod.settings.disableExtraWidgets;

	public static bool ShowPalette
	{
		get
		{
			if (!DisableAllExtraWidgets)
			{
				if (!BSGenesActive && !BigSmallMod.settings.showClrPaletteBtn)
				{
					return GlobalSettings.IsFeatureEnabled("RecolorButton");
				}
				return true;
			}
			return false;
		}
	}

	public static bool ShowRaceButton
	{
		get
		{
			if (!DisableAllExtraWidgets)
			{
				if (!BSGenesActive && !BigSmallMod.settings.showRaceBtn)
				{
					return GlobalSettings.IsFeatureEnabled("RaceButton");
				}
				return true;
			}
			return false;
		}
	}

	private static bool IsAutoCombatEnabledCached
	{
		get
		{
			bool valueOrDefault = _BSAutoCombatFeatureCache == true;
			if (!_BSAutoCombatFeatureCache.HasValue)
			{
				valueOrDefault = GlobalSettings.IsFeatureEnabled("AutoCombat");
				_BSAutoCombatFeatureCache = valueOrDefault;
				return valueOrDefault;
			}
			return valueOrDefault;
		}
	}

	public static bool IsAutoCombatEnabled
	{
		get
		{
			if (!BigSmallMod.settings.enableDraftedJobs)
			{
				if (IsAutoCombatEnabledCached)
				{
					return !DisableAllExtraWidgets;
				}
				return false;
			}
			return true;
		}
	}

	static BigSmall()
	{
		mainThread = Thread.CurrentThread;
		performScaleCalculations = true;
		_BSGenesActive = null;
		_BSOptionalActive = null;
		_BSTransformGenes = null;
		_BSTestModActive = null;
		_BSSapientAnimalsActive_ForcedByMods = null;
		_BSSapientAnimalsActive = null;
		_BSSapientMechanoidsActive = null;
		_BSAutoCombatFeatureCache = null;
	}
}
