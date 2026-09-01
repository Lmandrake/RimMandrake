using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Reflection;
using System.Runtime.CompilerServices;
using System.Text.RegularExpressions;
using System.Xml;
using HarmonyLib;
using Verse;

namespace VEF;

public class DefMigrationDef : Def
{
	public class DefMigrationsByType
	{
		public Type type;

		public List<DefMigration> migrations = new List<DefMigration>();

		public void LoadDataFromXmlCustom(XmlNode xmlRoot)
		{
			type = ParseHelper.ParseType(xmlRoot.Name);
			foreach (XmlNode childNode in xmlRoot.ChildNodes)
			{
				if (!(childNode is XmlComment))
				{
					DefMigration defMigration = new DefMigration
					{
						original = childNode["original"]?.InnerText,
						replacement = childNode["replacement"]?.InnerText
					};
					XmlElement xmlElement = childNode["removeIfMissingReplacement"];
					if (xmlElement != null)
					{
						defMigration.removeIfMissingReplacement = ParseHelper.ParseBool(xmlElement.InnerText);
					}
					if (GenText.NullOrEmpty(defMigration.original) && childNode.Name != "li")
					{
						defMigration.original = childNode.Name;
					}
					migrations.Add(defMigration);
				}
			}
		}
	}

	public class DefMigration
	{
		public string original;

		public string replacement;

		public bool removeIfMissingReplacement;
	}

	public float priority;

	public List<DefMigrationsByType> migratedDefs;

	private static readonly Regex AllowedDefNamesRegex;

	static DefMigrationDef()
	{
		FieldInfo fieldInfo = AccessToolsExtensions.DeclaredField(typeof(Def), "AllowedDefNamesRegex");
		if (fieldInfo != null && fieldInfo.IsStatic)
		{
			AllowedDefNamesRegex = fieldInfo.GetValue(null) as Regex;
		}
		if (AllowedDefNamesRegex == null)
		{
			Log.Warning("[VEF] Failed getting value from Def:AllowedDefNamesRegex field. Using a fallback.");
			AllowedDefNamesRegex = new Regex("^[a-zA-Z0-9\\-_]*$");
		}
	}

	public override void ResolveReferences()
	{
		((Def)this).ResolveReferences();
		if (GenList.NullOrEmpty<DefMigrationsByType>((IList<DefMigrationsByType>)migratedDefs))
		{
			return;
		}
		migratedDefs.RemoveAll((DefMigrationsByType x) => !typeof(Def).IsAssignableFrom(x.type));
		foreach (DefMigrationsByType migrations in migratedDefs)
		{
			migrations.migrations.RemoveAll(delegate(DefMigration x)
			{
				if (!IsDefNameValid(x.original))
				{
					return true;
				}
				if (x.replacement == null)
				{
					return false;
				}
				bool result = false;
				if (!IsDefNameValid(x.replacement))
				{
					if (x.replacement != null && !x.removeIfMissingReplacement)
					{
						result = true;
					}
					x.replacement = null;
				}
				else if (!GenDefDatabase.GetAllDefsInDatabaseForDef(migrations.type).Any((Def def) => def.defName == x.replacement))
				{
					x.replacement = null;
					if (!x.removeIfMissingReplacement)
					{
						result = true;
					}
				}
				return result;
			});
		}
		migratedDefs.RemoveAll((DefMigrationsByType x) => GenList.NullOrEmpty<DefMigration>((IList<DefMigration>)x.migrations));
	}

	public override IEnumerable<string> ConfigErrors()
	{
		foreach (string item in _003C_003En__0())
		{
			yield return item;
		}
		if (!GenList.NullOrEmpty<DefMigrationsByType>((IList<DefMigrationsByType>)migratedDefs))
		{
			if (GenCollection.Any<DefMigrationsByType>(migratedDefs, (Predicate<DefMigrationsByType>)((DefMigrationsByType x) => !typeof(Def).IsAssignableFrom(x.type))))
			{
				yield return "all elements in migratedDefs must use def types";
			}
			if (migratedDefs.SelectMany((DefMigrationsByType x) => x.migrations).Any(delegate(DefMigration x)
			{
				bool flag;
				switch (x.original)
				{
				case null:
				case "UnnamedDef":
				case "null":
					flag = true;
					break;
				default:
					flag = false;
					break;
				}
				bool flag2 = flag;
				if (!flag2)
				{
					string replacement = x.replacement;
					bool flag3 = ((replacement == "UnnamedDef" || replacement == "null") ? true : false);
					flag2 = flag3;
				}
				return flag2;
			}))
			{
				yield return "a defName in migratedDefs is not specified, is 'UnnamedDef', or is 'null'";
			}
			else if (migratedDefs.SelectMany((DefMigrationsByType x) => x.migrations).Any((DefMigration x) => !AllowedDefNamesRegex.IsMatch(x.original) || (x.replacement != null && !AllowedDefNamesRegex.IsMatch(x.replacement))))
			{
				yield return "all defNames in migratedDefs should only contain letters, numbers, underscores, or dashes";
			}
		}
	}

	private static bool IsDefNameValid(string defName)
	{
		bool flag;
		switch (defName)
		{
		case null:
		case "UnnamedDef":
		case "null":
			flag = true;
			break;
		default:
			flag = false;
			break;
		}
		if (!flag)
		{
			return AllowedDefNamesRegex.IsMatch(defName);
		}
		return false;
	}

	[CompilerGenerated]
	[DebuggerHidden]
	private IEnumerable<string> _003C_003En__0()
	{
		return ((Def)this).ConfigErrors();
	}
}
