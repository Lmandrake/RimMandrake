using System;
using System.Collections.Generic;
using System.Linq;
using System.Xml;
using HarmonyLib;
using VEF.Abilities;
using Verse;

namespace VEF;

[StaticConstructorOnStartup]
internal class BackwardsCompatibilityMigrationUtility
{
	public class BackCompatabilityConverter_VEF : BackCompatibilityConverter
	{
		public override bool AppliesToVersion(int majorVer, int minorVer)
		{
			return true;
		}

		public override string BackCompatibleDefName(Type defType, string defName, bool forDefInjections = false, XmlNode node = null)
		{
			if (defNameConverters.Count <= 0)
			{
				return null;
			}
			if (!defNameConverters.TryGetValue(defName, out var value))
			{
				return null;
			}
			if (!value.TryGetValue(defType, out var value2))
			{
				return null;
			}
			return value2;
		}

		public override Type GetBackCompatibleType(Type baseType, string providedClassName, XmlNode node)
		{
			if (baseType == typeof(Ability) && abilityClasses.TryGetValue(providedClassName, out var value))
			{
				return value;
			}
			return null;
		}

		public override void PostExposeData(object obj)
		{
		}
	}

	internal static BackCompatabilityConverter_VEF converter;

	internal static Dictionary<string, Type> abilityClasses;

	internal static Dictionary<string, Dictionary<Type, string>> defNameConverters;

	static BackwardsCompatibilityMigrationUtility()
	{
		abilityClasses = new Dictionary<string, Type>();
		defNameConverters = new Dictionary<string, Dictionary<Type, string>>();
		List<BackCompatibilityConverter> obj = (List<BackCompatibilityConverter>)AccessToolsExtensions.Field(typeof(BackCompatibility), "conversionChain").GetValue(null);
		List<Tuple<string, Type>> list = (List<Tuple<string, Type>>)AccessToolsExtensions.Field(typeof(BackCompatibility), "RemovedDefs").GetValue(null);
		converter = new BackCompatabilityConverter_VEF();
		obj.Add((BackCompatibilityConverter)(object)converter);
		foreach (AbilityDef allDef in DefDatabase<AbilityDef>.AllDefs)
		{
			foreach (AbilityExtension_ClassMigration item in ((Def)allDef).modExtensions.OfType<AbilityExtension_ClassMigration>())
			{
				abilityClasses.Add(item.oldClass, allDef.abilityClass);
			}
		}
		int count = list.Count;
		foreach (DefMigrationDef item2 in DefDatabase<DefMigrationDef>.AllDefs.OrderByDescending((DefMigrationDef x) => x.priority))
		{
			if (GenList.NullOrEmpty<DefMigrationDef.DefMigrationsByType>((IList<DefMigrationDef.DefMigrationsByType>)item2.migratedDefs))
			{
				continue;
			}
			foreach (DefMigrationDef.DefMigrationsByType migrationsByType in item2.migratedDefs)
			{
				foreach (DefMigrationDef.DefMigration migration in migrationsByType.migrations)
				{
					if (defNameConverters.TryGetValue(migration.original, out var value) && value.ContainsKey(migrationsByType.type))
					{
						continue;
					}
					if (migration.replacement == null)
					{
						if (!GenCollection.Any<Tuple<string, Type>>(list, (Predicate<Tuple<string, Type>>)((Tuple<string, Type> x) => x.Item1 == migration.original && x.Item2 == migrationsByType.type)))
						{
							list.Add(new Tuple<string, Type>(migration.original, migrationsByType.type));
						}
						continue;
					}
					int num = list.FindIndex((Tuple<string, Type> x) => x.Item1 == migration.original && x.Item2 == migrationsByType.type);
					if (num >= count)
					{
						list.RemoveAt(num);
					}
					if (value == null)
					{
						value = (defNameConverters[migration.original] = new Dictionary<Type, string>());
					}
					value[migrationsByType.type] = migration.replacement;
				}
			}
		}
	}
}
