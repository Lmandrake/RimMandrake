using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using FactionLoadout.Util;
using HarmonyLib;
using JetBrains.Annotations;
using Verse;

namespace FactionLoadout.Modules;

public static class VFEAncientsReflectionModule
{
	public const string VfeAncientsExtensionClassName = "VFEAncients.PawnKindExtension_Powers";

	public static Lazy<bool> ModLoaded = new Lazy<bool>(() => ModLister.GetActiveModWithIdentifier("VanillaExpanded.VFEA", false) != null);

	public static Lazy<Type> VfeAncientsExtensionType = new Lazy<Type>(() => AccessTools.TypeByName("VFEAncients.PawnKindExtension_Powers"));

	public static Lazy<Type> PowerDefType = new Lazy<Type>(() => AccessTools.TypeByName("VFEAncients.PowerDef"));

	public static Lazy<FieldInfo> NumRandomSuperpowersField = new Lazy<FieldInfo>(() => VfeAncientsExtensionType.Value?.GetField("numRandomSuperpowers"));

	public static Lazy<FieldInfo> NumRandomWeaknessesField = new Lazy<FieldInfo>(() => VfeAncientsExtensionType.Value?.GetField("numRandomWeaknesses"));

	public static Lazy<FieldInfo> ForcePowersField = new Lazy<FieldInfo>(() => VfeAncientsExtensionType.Value?.GetField("forcePowers"));

	public static Lazy<Type> ClosedDefDatabaseType = new Lazy<Type>(() => ReflectionHelper.DefDatabaseGenericType.Value?.MakeGenericType(PowerDefType.Value));

	public static Lazy<Type> ClosedPowerListGenericType = new Lazy<Type>(() => ReflectionHelper.ListGenericType.Value?.MakeGenericType(PowerDefType.Value));

	public static Lazy<MethodInfo> GetPowerDefMethod = new Lazy<MethodInfo>(() => ClosedDefDatabaseType.Value?.GetMethod("GetNamedSilentFail"));

	public static Lazy<PropertyInfo> GetPowerDefsMethod = new Lazy<PropertyInfo>(() => ClosedDefDatabaseType.Value?.GetProperty("AllDefsListForReading"));

	[CanBeNull]
	private static PawnKindDef _lastDef = null;

	[CanBeNull]
	private static DefModExtension _lastExtension = null;

	[CanBeNull]
	public static DefModExtension FindVEAncientsExtension(PawnKindDef currentDef)
	{
		if (_lastDef == currentDef)
		{
			return _lastExtension;
		}
		_lastDef = currentDef;
		_lastExtension = ((Def)currentDef).modExtensions?.Find((DefModExtension me) => ((object)me).GetType().FullName == "VFEAncients.PawnKindExtension_Powers");
		return _lastExtension;
	}

	public static void ApplyVFEAncientsEdits(PawnKindEdit edit, PawnKindDef def)
	{
		if (!ModLoaded.Value || (!edit.NumVFEAncientsSuperPowers.HasValue && !edit.NumVFEAncientsSuperWeaknesses.HasValue && edit.ForcedVFEAncientsItems == null))
		{
			return;
		}
		if (((Def)def).modExtensions == null)
		{
			((Def)def).modExtensions = new List<DefModExtension>();
		}
		DefModExtension val = FindVEAncientsExtension(def);
		if (val == null)
		{
			object obj = AccessTools.CreateInstance(VfeAncientsExtensionType.Value);
			val = (DefModExtension)((obj is DefModExtension) ? obj : null);
			((Def)def).modExtensions.Add(val);
		}
		if (edit.NumVFEAncientsSuperPowers.HasValue)
		{
			NumRandomSuperpowersField.Value?.SetValue(val, edit.NumVFEAncientsSuperPowers);
		}
		if (edit.NumVFEAncientsSuperWeaknesses.HasValue)
		{
			NumRandomWeaknessesField.Value?.SetValue(val, edit.NumVFEAncientsSuperWeaknesses);
		}
		if (edit.ForcedVFEAncientsItems == null)
		{
			return;
		}
		object obj2 = ForcePowersField.Value?.GetValue(val);
		if (obj2 == null)
		{
			obj2 = AccessTools.CreateInstance(ClosedPowerListGenericType.Value);
			ForcePowersField.Value?.SetValue(val, obj2);
		}
		IList powerList = obj2 as IList;
		if (powerList != null)
		{
			powerList.Clear();
			CollectionExtensions.DoIf<object>(from i in edit.ForcedVFEAncientsItems
				select GetPowerDefMethod.Value.Invoke(null, new object[1] { i }) into p
				where p != null
				select p, (Func<object, bool>)((object p) => !powerList.Contains(p)), (Action<object>)delegate(object p)
			{
				powerList.Add(p);
			});
		}
	}
}
