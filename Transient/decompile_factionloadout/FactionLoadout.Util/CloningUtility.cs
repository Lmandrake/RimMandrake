using System;
using System.Collections.Generic;
using System.Reflection;
using RimWorld;
using Verse;

namespace FactionLoadout.Util;

public static class CloningUtility
{
	private static Dictionary<string, Func<FactionDef, FieldInfo, object>> customFac;

	private static Dictionary<string, Func<PawnKindDef, FieldInfo, object>> customKind;

	private static List<FieldInfo> toCloneFac;

	private static List<FieldInfo> toCloneKind;

	private static Dictionary<string, PawnKindDef> replacements;

	private static int cloneID;

	static CloningUtility()
	{
		customFac = new Dictionary<string, Func<FactionDef, FieldInfo, object>>
		{
			{ "pawnGroupMakers", CloneGroupMakers },
			{ "basicMemberKind", CloneBasicMemberType },
			{ "fixedLeaderKinds", CloneLeaderKinds },
			{ "apparelStuffFilter", CloneThingFilter }
		};
		customKind = new Dictionary<string, Func<PawnKindDef, FieldInfo, object>> { { "inventoryOptions", CloneInventory } };
		replacements = new Dictionary<string, PawnKindDef>();
		toCloneFac = new List<FieldInfo>();
		toCloneFac.AddRange(typeof(FactionDef).GetFields(BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic));
		toCloneKind = new List<FieldInfo>();
		toCloneKind.AddRange(typeof(PawnKindDef).GetFields(BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic));
	}

	private static object CloneThingFilter(FactionDef def, FieldInfo info)
	{
		//IL_0012: Unknown result type (might be due to invalid IL or missing references)
		//IL_0017: Unknown result type (might be due to invalid IL or missing references)
		//IL_001f: Expected O, but got Unknown
		object value = info.GetValue(def);
		ThingFilter val = (ThingFilter)((value is ThingFilter) ? value : null);
		if (val == null)
		{
			return null;
		}
		ThingFilter val2 = new ThingFilter();
		val2.CopyAllowancesFrom(val);
		return (object)val2;
	}

	private static object CloneList(PawnKindDef def, FieldInfo info)
	{
		object value = info.GetValue(def);
		if (value == null)
		{
			return null;
		}
		return Activator.CreateInstance(typeof(List<>).MakeGenericType(info.FieldType.GetGenericArguments()[0]), value);
	}

	private static object CloneInventory(PawnKindDef def, FieldInfo info)
	{
		object value = info.GetValue(def);
		PawnInventoryOption val = (PawnInventoryOption)((value is PawnInventoryOption) ? value : null);
		if (val == null)
		{
			return val;
		}
		return new InventoryOptionEdit(val).ConvertToVanilla();
	}

	private static object CloneLeaderKinds(FactionDef def, FieldInfo info)
	{
		if (!(info.GetValue(def) is List<PawnKindDef> list))
		{
			return null;
		}
		List<PawnKindDef> list2 = new List<PawnKindDef>();
		foreach (PawnKindDef item in list)
		{
			list2.Add(MakeReplacement(item));
		}
		return list2;
	}

	private static object CloneBasicMemberType(FactionDef def, FieldInfo info)
	{
		object value = info.GetValue(def);
		PawnKindDef val = (PawnKindDef)((value is PawnKindDef) ? value : null);
		if (val == null)
		{
			return null;
		}
		return MakeReplacement(val);
	}

	private static PawnKindDef MakeReplacement(PawnKindDef def)
	{
		if (def == null)
		{
			return null;
		}
		if (replacements.TryGetValue(((Def)def).defName, out var value))
		{
			return value;
		}
		PawnKindDef val = Clone(def);
		replacements.Add(((Def)def).defName, val);
		return val;
	}

	private static object CloneGroupMakers(FactionDef def, FieldInfo info)
	{
		//IL_002c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0033: Expected O, but got Unknown
		if (!(info.GetValue(def) is List<PawnGroupMaker> list))
		{
			return null;
		}
		List<PawnGroupMaker> list2 = new List<PawnGroupMaker>();
		foreach (PawnGroupMaker item in list)
		{
			PawnGroupMaker val = new PawnGroupMaker();
			val.kindDef = item.kindDef;
			val.commonality = item.commonality;
			val.maxTotalPoints = item.maxTotalPoints;
			val.disallowedStrategies = ((item.disallowedStrategies == null) ? null : new List<RaidStrategyDef>(item.disallowedStrategies));
			val.options = CloneOptions(item.options);
			val.carriers = CloneOptions(item.carriers);
			val.guards = CloneOptions(item.guards);
			val.traders = CloneOptions(item.traders);
			list2.Add(val);
		}
		return list2;
		static List<PawnGenOption> CloneOptions(List<PawnGenOption> value)
		{
			if (value == null)
			{
				return null;
			}
			List<PawnGenOption> list3 = new List<PawnGenOption>(value.Count);
			foreach (PawnGenOption item2 in value)
			{
				list3.Add(CloneOption(item2));
			}
			return list3;
		}
	}

	private static PawnGenOption CloneOption(PawnGenOption op)
	{
		//IL_0005: Unknown result type (might be due to invalid IL or missing references)
		//IL_000a: Unknown result type (might be due to invalid IL or missing references)
		//IL_001b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0028: Expected O, but got Unknown
		if (op == null)
		{
			return op;
		}
		return new PawnGenOption
		{
			kind = MakeReplacement(op.kind),
			selectionWeight = op.selectionWeight
		};
	}

	public static FactionDef Clone(FactionDef def)
	{
		//IL_000f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0015: Expected O, but got Unknown
		//IL_0084: Unknown result type (might be due to invalid IL or missing references)
		if (def == null)
		{
			return null;
		}
		replacements.Clear();
		FactionDef val = new FactionDef();
		foreach (FieldInfo item in toCloneFac)
		{
			item.SetValue(val, CloneField(def, item));
		}
		((Def)val).defName = ((Def)val).defName + $"_CLONED_{cloneID++}";
		ModCore.Log(string.Format("Cloned {0}, creating {1} kindDefs: {2}", ((Def)val).LabelCap, replacements.Count, string.Join(", ", replacements.Keys)));
		replacements.Clear();
		return val;
	}

	private static object CloneField(FactionDef def, FieldInfo info)
	{
		if (info == null)
		{
			return null;
		}
		string name = info.Name;
		if (!customFac.TryGetValue(name, out var value))
		{
			return info.GetValue(def);
		}
		return value?.Invoke(def, info);
	}

	public static PawnKindDef Clone(PawnKindDef def)
	{
		//IL_0017: Unknown result type (might be due to invalid IL or missing references)
		//IL_001d: Expected O, but got Unknown
		if (def == null)
		{
			return null;
		}
		if (def is CreepJoinerFormKindDef || def == PawnKindDefOf.WildMan)
		{
			return def;
		}
		PawnKindDef val = new PawnKindDef();
		foreach (FieldInfo item in toCloneKind)
		{
			item.SetValue(val, CloneField(def, item));
		}
		return val;
	}

	private static object CloneField(PawnKindDef def, FieldInfo info)
	{
		if (info == null)
		{
			return null;
		}
		string name = info.Name;
		if (customKind.TryGetValue(name, out var value))
		{
			return value?.Invoke(def, info);
		}
		if (info.FieldType.IsGenericType && info.FieldType.GetGenericTypeDefinition() == typeof(List<>))
		{
			return CloneList(def, info);
		}
		return info.GetValue(def);
	}
}
