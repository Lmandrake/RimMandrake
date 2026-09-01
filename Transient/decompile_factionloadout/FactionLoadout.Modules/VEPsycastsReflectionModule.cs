using System;
using System.Collections.Generic;
using System.Reflection;
using FactionLoadout.Util;
using HarmonyLib;
using JetBrains.Annotations;
using Verse;

namespace FactionLoadout.Modules;

public static class VEPsycastsReflectionModule
{
	public const string VpeExtensionClassName = "VanillaPsycastsExpanded.PawnKindAbilityExtension_Psycasts";

	public const string VEAbilityExtensionClassName = "VanillaPsycastsExpanded.AbilityExtension_Psycast";

	public static Lazy<bool> ModLoaded = new Lazy<bool>(() => ModLister.GetActiveModWithIdentifier("vanillaexpanded.vpsycastse", false) != null);

	public static Lazy<Type> VpeExtensionType = new Lazy<Type>(() => AccessTools.TypeByName("VanillaPsycastsExpanded.PawnKindAbilityExtension_Psycasts"));

	public static Lazy<Type> PathUnlockDataType = new Lazy<Type>(() => AccessTools.TypeByName("VanillaPsycastsExpanded.PathUnlockData"));

	public static Lazy<Type> ClosedUnlockedPathsListGenericType = new Lazy<Type>(() => ReflectionHelper.ListGenericType.Value?.MakeGenericType(PathUnlockDataType.Value));

	public static Lazy<FieldInfo> StatUpgradePointsField = new Lazy<FieldInfo>(() => VpeExtensionType.Value?.GetField("statUpgradePoints"));

	public static Lazy<FieldInfo> LevelField = new Lazy<FieldInfo>(() => VpeExtensionType.Value?.GetField("initialLevel"));

	public static Lazy<FieldInfo> GiveRandomAbilitiesField = new Lazy<FieldInfo>(() => VpeExtensionType.Value?.GetField("giveRandomAbilities"));

	public static Lazy<FieldInfo> ImplantDefField = new Lazy<FieldInfo>(() => VpeExtensionType.Value?.GetField("implantDef"));

	public static Lazy<FieldInfo> UnlockedPathsField = new Lazy<FieldInfo>(() => VpeExtensionType.Value?.GetField("unlockedPaths"));

	public static Lazy<Type> PsycasterPathDefType = new Lazy<Type>(() => AccessTools.TypeByName("VanillaPsycastsExpanded.PsycasterPathDef"));

	[CanBeNull]
	private static PawnKindDef _lastDef = null;

	[CanBeNull]
	private static DefModExtension _lastExtension = null;

	[CanBeNull]
	public static DefModExtension FindVEPsycastsExtension(PawnKindDef currentDef)
	{
		if (_lastDef == currentDef)
		{
			return _lastExtension;
		}
		_lastDef = currentDef;
		_lastExtension = ((Def)currentDef).modExtensions?.Find((DefModExtension me) => ((object)me).GetType().FullName == "VanillaPsycastsExpanded.PawnKindAbilityExtension_Psycasts");
		return _lastExtension;
	}

	public static void ApplyVEPsycastsEdits(PawnKindEdit edit, PawnKindDef def)
	{
		if (ModLoaded.Value && (edit.VEPsycastLevel.HasValue || edit.VEPsycastStatPoints.HasValue || edit.VEPsycastRandomAbilities.HasValue))
		{
			if (((Def)def).modExtensions == null)
			{
				((Def)def).modExtensions = new List<DefModExtension>();
			}
			DefModExtension val = FindVEPsycastsExtension(def);
			if (val == null)
			{
				object obj = AccessTools.CreateInstance(VpeExtensionType.Value);
				val = (DefModExtension)((obj is DefModExtension) ? obj : null);
				ImplantDefField.Value?.SetValue(val, DefDatabase<HediffDef>.GetNamed("VPE_PsycastAbilityImplant", true));
				UnlockedPathsField.Value?.SetValue(val, AccessTools.CreateInstance(ClosedUnlockedPathsListGenericType.Value));
				((Def)def).modExtensions.Add(val);
			}
			if (edit.VEPsycastLevel.HasValue)
			{
				LevelField.Value?.SetValue(val, edit.VEPsycastLevel);
			}
			if (edit.VEPsycastStatPoints.HasValue)
			{
				StatUpgradePointsField.Value?.SetValue(val, edit.VEPsycastStatPoints);
			}
			if (edit.VEPsycastRandomAbilities.HasValue)
			{
				GiveRandomAbilitiesField.Value?.SetValue(val, edit.VEPsycastRandomAbilities);
			}
		}
	}
}
