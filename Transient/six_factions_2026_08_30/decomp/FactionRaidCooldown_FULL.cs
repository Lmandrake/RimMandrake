using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Reflection;
using System.Runtime.CompilerServices;
using System.Runtime.Versioning;
using HarmonyLib;
using Microsoft.CodeAnalysis;
using Mlie;
using RimWorld;
using UnityEngine;
using Verse;

[assembly: CompilationRelaxations(8)]
[assembly: RuntimeCompatibility(WrapNonExceptionThrows = true)]
[assembly: Debuggable(DebuggableAttribute.DebuggingModes.IgnoreSymbolStoreSequencePoints)]
[assembly: TargetFramework(".NETFramework,Version=v4.8", FrameworkDisplayName = ".NET Framework 4.8")]
[assembly: AssemblyVersion("0.0.0.0")]
[module: RefSafetyRules(11)]
namespace Microsoft.CodeAnalysis
{
	[CompilerGenerated]
	[Embedded]
	internal sealed class EmbeddedAttribute : Attribute
	{
	}
}
namespace System.Runtime.CompilerServices
{
	[CompilerGenerated]
	[Embedded]
	[AttributeUsage(AttributeTargets.Module, AllowMultiple = false, Inherited = false)]
	internal sealed class RefSafetyRulesAttribute : Attribute
	{
		public readonly int Version;

		public RefSafetyRulesAttribute(int P_0)
		{
			Version = P_0;
		}
	}
}
namespace MURFactionRaidCooldown
{
	public class FactionData : IExposable
	{
		private int cooldown;

		private Faction faction;

		public FactionData()
		{
		}

		public FactionData(Faction _faction)
		{
			faction = _faction;
			cooldown = 0;
		}

		public void ExposeData()
		{
			Scribe_References.Look<Faction>(ref faction, "faction", false);
			Scribe_Values.Look<int>(ref cooldown, "cooldown", 0, false);
		}

		public int CurrentCooldown()
		{
			return cooldown;
		}

		public void ChangeHours(int value)
		{
			cooldown += value;
			if (cooldown < 0)
			{
				cooldown = 0;
			}
			if (cooldown > Settings.maxCooldown)
			{
				cooldown = Settings.maxCooldown;
			}
		}

		public static void RegisterFaction(Faction f)
		{
			FactionData value = new FactionData(f);
			FactionDataStorageComponent.data.Add(f, value);
		}
	}
	public static class FactionDataStorageComponent
	{
		public static Dictionary<Faction, FactionData> data = new Dictionary<Faction, FactionData>();
	}
	public class FactionStorage : GameComponent
	{
		private List<FactionData> dataList = new List<FactionData>();

		private List<Faction> factionList = new List<Faction>();

		public FactionStorage(Game game)
		{
		}

		public override void StartedNewGame()
		{
			((GameComponent)this).StartedNewGame();
			if (FactionDataStorageComponent.data == null)
			{
				FactionDataStorageComponent.data = new Dictionary<Faction, FactionData>();
			}
			FactionDataStorageComponent.data.Clear();
			factionCheck();
		}

		public override void LoadedGame()
		{
			((GameComponent)this).LoadedGame();
			if (FactionDataStorageComponent.data == null)
			{
				FactionDataStorageComponent.data = new Dictionary<Faction, FactionData>();
			}
			factionCheck();
		}

		public override void GameComponentTick()
		{
			((GameComponent)this).GameComponentTick();
			if (Find.TickManager.TicksGame % 2500 != 0)
			{
				return;
			}
			if (FactionDataStorageComponent.data == null)
			{
				FactionDataStorageComponent.data = new Dictionary<Faction, FactionData>();
			}
			foreach (FactionData value in FactionDataStorageComponent.data.Values)
			{
				if (value.CurrentCooldown() > 0)
				{
					value.ChangeHours(-1);
				}
			}
		}

		private static void factionCheck()
		{
			foreach (Faction allFaction in Find.FactionManager.AllFactions)
			{
				if (!allFaction.IsPlayer && !allFaction.def.hidden && !FactionDataStorageComponent.data.ContainsKey(allFaction))
				{
					FactionData.RegisterFaction(allFaction);
				}
			}
		}

		public override void ExposeData()
		{
			((GameComponent)this).ExposeData();
			Scribe_Collections.Look<Faction, FactionData>(ref FactionDataStorageComponent.data, "factionDataDict", (LookMode)3, (LookMode)2, ref factionList, ref dataList, true, false, false);
		}
	}
	[HarmonyPatch(typeof(FactionUIUtility), "DrawFactionRow")]
	internal class FactionUIUtility_DrawFactionRow
	{
		private static int drawn;

		private static void Prefix(float rowY, out float __state)
		{
			__state = rowY;
		}

		private static void Postfix(Faction faction, Rect fillRect, float __state, ref float __result)
		{
			//IL_0099: Unknown result type (might be due to invalid IL or missing references)
			//IL_00de: Unknown result type (might be due to invalid IL or missing references)
			//IL_0131: Unknown result type (might be due to invalid IL or missing references)
			if (!Settings.showCooldowns || !FactionDataStorageComponent.data.TryGetValue(faction, out var value))
			{
				return;
			}
			float num = value.CurrentCooldown();
			float num2 = Settings.maxCooldown;
			string arg = ((num / num2 >= 0.66f) ? "#00ff00" : ((!(num / num2 < 0.66f) || !(num / num2 >= 0.33f)) ? "#FF0000" : "#00C0FF"));
			float num3 = __state + __result - 18f;
			if (__result <= 80f)
			{
				num3 += 18f;
			}
			Rect val = default(Rect);
			((Rect)(ref val))..ctor(90f, num3, 500f, 80f);
			string text = string.Format("{0}<color={1}>", Translator.Translate("FRC.raidInfo"), arg);
			text += GenDate.ToStringTicksToPeriodVague(value.CurrentCooldown() * 2500, true, true);
			text += "</color>";
			if (value.CurrentCooldown() > 0)
			{
				Widgets.Label(val, text);
				if (__result <= 80f)
				{
					__result += 18f;
				}
				__result += 3f;
			}
			if (drawn % 2 == 1)
			{
				Rect val2 = default(Rect);
				((Rect)(ref val2))..ctor(0f, num3, ((Rect)(ref fillRect)).width, 18f);
				if (value.CurrentCooldown() > 0)
				{
					Widgets.DrawLightHighlight(val2);
				}
			}
			drawn++;
			if (drawn >= FactionDataStorageComponent.data.Count)
			{
				drawn = 0;
			}
		}
	}
	[HarmonyPatch(typeof(Faction), "Notify_MemberDied")]
	internal class Faction_Notify_MemberDied
	{
		private static void Postfix(ref Faction __instance)
		{
			if (FactionDataStorageComponent.data.ContainsKey(__instance) && FactionUtility.HostileTo(__instance, Faction.OfPlayer))
			{
				FactionDataStorageComponent.data[__instance].ChangeHours(Settings.hoursPerDeath);
			}
		}
	}
	[StaticConstructorOnStartup]
	public static class HarmonyPatcher
	{
		static HarmonyPatcher()
		{
			//IL_0005: Unknown result type (might be due to invalid IL or missing references)
			new Harmony("rimworld.murmur.factionraidcooldown").PatchAll(Assembly.GetExecutingAssembly());
		}
	}
	[HarmonyPatch(typeof(IncidentWorker_RaidEnemy), "FactionCanBeGroupSource")]
	internal class IncidentWorker_RaidEnemy_FactionCanBeGroupSource
	{
		private static void Postfix(Faction f, ref bool __result)
		{
			if (__result && FactionDataStorageComponent.data.ContainsKey(f) && FactionDataStorageComponent.data[f].CurrentCooldown() > 0)
			{
				__result = false;
			}
		}
	}
	public class ModSettingsPage : Mod
	{
		public static Settings settings;

		private static string currentVersion;

		public ModSettingsPage(ModContentPack content)
			: base(content)
		{
			settings = ((Mod)this).GetSettings<Settings>();
			currentVersion = VersionFromManifest.GetVersionFromModMetaData(content.ModMetaData);
		}

		public override string SettingsCategory()
		{
			return "Faction Raid Cooldown";
		}

		public override void DoSettingsWindowContents(Rect inRect)
		{
			//IL_0000: Unknown result type (might be due to invalid IL or missing references)
			//IL_0006: Expected O, but got Unknown
			//IL_002f: Unknown result type (might be due to invalid IL or missing references)
			//IL_0060: Unknown result type (might be due to invalid IL or missing references)
			//IL_006f: Unknown result type (might be due to invalid IL or missing references)
			//IL_0079: Unknown result type (might be due to invalid IL or missing references)
			//IL_0085: Unknown result type (might be due to invalid IL or missing references)
			//IL_0094: Unknown result type (might be due to invalid IL or missing references)
			//IL_009e: Unknown result type (might be due to invalid IL or missing references)
			//IL_00aa: Unknown result type (might be due to invalid IL or missing references)
			//IL_00b9: Unknown result type (might be due to invalid IL or missing references)
			//IL_00c3: Unknown result type (might be due to invalid IL or missing references)
			//IL_0156: Unknown result type (might be due to invalid IL or missing references)
			//IL_016b: Unknown result type (might be due to invalid IL or missing references)
			//IL_0170: Unknown result type (might be due to invalid IL or missing references)
			//IL_017b: Unknown result type (might be due to invalid IL or missing references)
			//IL_0181: Unknown result type (might be due to invalid IL or missing references)
			Listing_Standard val = new Listing_Standard();
			((Listing)val).Begin(new Rect(((Rect)(ref inRect)).x, ((Rect)(ref inRect)).y + 24f, ((Rect)(ref inRect)).width, ((Rect)(ref inRect)).height - 24f));
			((Listing)val).verticalSpacing = 10f;
			((Listing)val).ColumnWidth = 282f;
			((Listing)val).Gap(5f);
			val.Label(Translator.Translate("FRC.hours"), -1f, TaggedString.op_Implicit(Translator.Translate("FRC.hoursTT")));
			val.Label(Translator.Translate("FRC.cooldown"), -1f, TaggedString.op_Implicit(Translator.Translate("FRC.cooldownTT")));
			val.Label(Translator.Translate("FRC.show"), -1f, TaggedString.op_Implicit(Translator.Translate("FRC.showTT")));
			((Listing)val).NewColumn();
			((Listing)val).ColumnWidth = 64f;
			string text = Settings.hoursPerDeath.ToString();
			val.TextFieldNumeric<int>(ref Settings.hoursPerDeath, ref text, 1f, 9999f);
			string text2 = Settings.maxCooldown.ToString();
			val.TextFieldNumeric<int>(ref Settings.maxCooldown, ref text2, 1f, 9999f);
			((Listing)val).ColumnWidth = 24f;
			val.CheckboxLabeled("", ref Settings.showCooldowns, (string)null, 0f, 1f);
			if (currentVersion != null)
			{
				((Listing)val).Gap(12f);
				GUI.contentColor = Color.gray;
				val.Label(TranslatorFormattedStringExtensions.Translate("FRC.modVersion", NamedArgument.op_Implicit(currentVersion)), -1f, (string)null);
				GUI.contentColor = Color.white;
			}
			((Listing)val).End();
		}
	}
	public class Settings : ModSettings
	{
		private static int baseCooldown = 24;

		public static int hoursPerDeath = 12;

		public static int maxCooldown = 360;

		public static bool showCooldowns;

		public override void ExposeData()
		{
			((ModSettings)this).ExposeData();
			Scribe_Values.Look<int>(ref baseCooldown, "baseCooldown", 24, false);
			Scribe_Values.Look<int>(ref hoursPerDeath, "extraHoursPerDeath", 12, false);
			Scribe_Values.Look<int>(ref maxCooldown, "maxCooldown", 360, false);
			Scribe_Values.Look<bool>(ref showCooldowns, "showCooldowns", false, false);
		}
	}
}
You are not using the latest version of the tool, please update.
Latest version is '11.0.0.9375' (yours is '9.0.0.7889')
