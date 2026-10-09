// HARMONY_PATCH_RESILIENCE_1 (X-5, design/RimMandrake/gpt_reviews/DESIGN_PASS_2026-10-08.md): a broken game update
// switches off ONE feature, not a whole mod.
//
// Source-linked into each adopting mod (<Compile Include="..\..\_Shared\HarmonyResilience\PatchApplier.cs" />), like
// _Shared/LightLedger: every type here is INTERNAL, so each assembly carries its own copy and its own failure list.
//
// What it replaces: `new Harmony(id).PatchAll()`. PatchAll is CreateClassProcessor(type).Patch() over every type, with
// no catch: the first class whose target a game update renamed throws, and every class after it is never patched.
// This applies one [HarmonyPatch] class at a time inside try/catch (the loop promoted from
// HugeThingsCore.PatchNamespace), names the failed FEATURE in a red log line, switches that feature's Mod Settings
// bool off for the session, and prints one census line: "Harmony: patched N, missing X".
//
// Persistence: a switched-off setting is NOT saved as off. BeforeExpose/AfterExpose put the player's own value back
// while the settings file is written, so the feature returns by itself once an update fixes the patch.
// Only [HarmonyPatch] classes are processed: PatchClassProcessor runs any method named Prepare/Cleanup/TargetMethod on
// the type it is given (HUGETHINGS_TITANIC_CCTOR_THROWS_1).
// Limitation: a class whose patch half-applied before throwing (several targets via TargetMethods) is not unpatched;
// the feature's setting going off is what makes its remaining patches inert, so every patch must gate on its setting.
using System;
using System.Collections.Generic;
using System.Reflection;
using HarmonyLib;
using UnityEngine;
using Verse;

namespace RimMandrake.Shared
{
	/// <summary>Names the player-facing feature a [HarmonyPatch] class belongs to, and (optionally) the static bool Mod
	/// Settings field that switches it, so a failed patch can switch it off. Classes without it are reported by class
	/// name and switch nothing off.</summary>
	[AttributeUsage(AttributeTargets.Class, AllowMultiple = false, Inherited = false)]
	internal sealed class PatchFeatureAttribute : Attribute
	{
		public readonly string label;
		public readonly Type settingsType;
		public readonly string field;

		public PatchFeatureAttribute(string label)
		{
			this.label = label;
		}

		public PatchFeatureAttribute(string label, Type settingsType, string field)
		{
			this.label = label;
			this.settingsType = settingsType;
			this.field = field;
		}
	}

	internal sealed class PatchFailure
	{
		public string feature;
		public string patchClass;
		public string reason;
		public FieldInfo setting;
	}

	internal static class PatchApplier
	{
		private static readonly List<PatchFailure> failures = new List<PatchFailure>();
		// field -> the player's own value, kept so a forced-off setting is never SAVED as off
		private static readonly Dictionary<FieldInfo, bool> userValues = new Dictionary<FieldInfo, bool>();

		public static int Patched { get; private set; }

		public static IReadOnlyList<PatchFailure> Failures => failures;

		/// <summary>Patch every [HarmonyPatch] class of <paramref name="asm"/> (optionally only namespace
		/// <paramref name="ns"/>) one at a time. Returns the number patched; logs one census line tagged
		/// <paramref name="logTag"/>, and one red line per failed feature.</summary>
		public static int Apply(Harmony harmony, Assembly asm, string logTag, string ns = null)
		{
			int patched = 0;
			int before = failures.Count;
			foreach (Type t in AccessTools.GetTypesFromAssembly(asm))
			{
				if (ns != null && t.Namespace != ns)
				{
					continue;
				}
				if (!t.IsDefined(typeof(HarmonyPatch), false))
				{
					continue;
				}
				try
				{
					harmony.CreateClassProcessor(t).Patch();
					patched++;
				}
				catch (Exception e)
				{
					Fail(t, e, logTag);
				}
			}
			Patched += patched;
			int missing = failures.Count - before;
			string line = "[" + logTag + "] Harmony: patched " + patched + ", missing " + missing;
			if (missing > 0)
			{
				var names = new List<string>();
				for (int i = before; i < failures.Count; i++)
				{
					names.Add(failures[i].feature + " (" + failures[i].patchClass + ")");
				}
				Log.Warning(line + ": " + string.Join(", ", names.ToArray())
					+ ". Those features are switched off for this session; everything else is patched.");
			}
			else
			{
				Log.Message(line);
			}
			return patched;
		}

		private static void Fail(Type t, Exception e, string logTag)
		{
			Exception inner = e;
			while (inner.InnerException != null)
			{
				inner = inner.InnerException;
			}
			PatchFeatureAttribute attr = t.GetCustomAttribute<PatchFeatureAttribute>(false);
			var f = new PatchFailure
			{
				feature = attr?.label ?? t.Name,
				patchClass = t.Name,
				reason = inner.GetType().Name + ": " + inner.Message,
			};
			if (attr?.settingsType != null && !attr.field.NullOrEmpty())
			{
				FieldInfo fi = attr.settingsType.GetField(attr.field, BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Static);
				if (fi != null && fi.FieldType == typeof(bool))
				{
					f.setting = fi;
					if (!userValues.ContainsKey(fi))
					{
						userValues[fi] = (bool)fi.GetValue(null);
					}
					fi.SetValue(null, false);
				}
				else
				{
					f.reason += " (and its setting " + attr.settingsType.Name + "." + attr.field + " was not found, so nothing was switched off)";
				}
			}
			failures.Add(f);
			Log.Error("[" + logTag + "] Harmony patch failed, feature switched off: " + f.feature + " ("
				+ f.patchClass + (f.setting != null ? ", setting " + f.setting.Name : "") + "). " + f.reason
				+ ". A game or mod update probably changed the code this hooks.");
		}

		/// <summary>Call first in ModSettings.ExposeData: while SAVING, the player's own values go back into the
		/// forced-off fields so the file keeps them.</summary>
		public static void BeforeExpose()
		{
			if (Scribe.mode != LoadSaveMode.Saving)
			{
				return;
			}
			foreach (KeyValuePair<FieldInfo, bool> kv in userValues)
			{
				kv.Key.SetValue(null, kv.Value);
			}
		}

		/// <summary>Call last in ModSettings.ExposeData: a value just LOADED becomes the remembered player value, and every
		/// failed feature is forced off again.</summary>
		public static void AfterExpose()
		{
			if (Scribe.mode == LoadSaveMode.LoadingVars)
			{
				var keys = new List<FieldInfo>(userValues.Keys);
				foreach (FieldInfo fi in keys)
				{
					userValues[fi] = (bool)fi.GetValue(null);
				}
			}
			ReforceOff();
		}

		/// <summary>Keep every failed feature off (call after drawing the settings window, so a click cannot turn a
		/// feature on whose patch is missing).</summary>
		public static void ReforceOff()
		{
			foreach (FieldInfo fi in userValues.Keys)
			{
				fi.SetValue(null, false);
			}
		}

		/// <summary>True when <paramref name="field"/> (a settings field name) is held off by a failed patch.</summary>
		public static bool IsBroken(string field)
		{
			for (int i = 0; i < failures.Count; i++)
			{
				if (failures[i].setting != null && failures[i].setting.Name == field)
				{
					return true;
				}
			}
			return false;
		}

		/// <summary>A red block at the top of a settings screen naming every switched-off feature and why. Nothing is
		/// drawn when every patch applied.</summary>
		public static void DrawNotice(Listing_Standard list)
		{
			if (failures.Count == 0)
			{
				return;
			}
			// Colorize, not GUI.color: GUI lives in UnityEngine.IMGUIModule, which not every adopting mod references.
			Color red = new Color(1f, 0.45f, 0.4f);
			list.Label(("Switched off: a game or mod update broke the code these features hook into. They stay off "
				+ "(their checkboxes cannot be turned on) until an update fixes them; your own choice is kept.").Colorize(red));
			for (int i = 0; i < failures.Count; i++)
			{
				PatchFailure f = failures[i];
				list.Label(("  " + f.feature + (f.setting != null ? " [" + f.setting.Name + "]" : "") + ": " + f.reason).Colorize(red));
			}
			list.GapLine();
		}
	}
}
