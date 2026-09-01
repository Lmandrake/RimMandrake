using System;
using System.Linq;
using System.Reflection;
using RimWorld.Planet;
using UnityEngine;
using Verse;

namespace VEF.Factions;

public class Dialog_NewFactionSpawningSettlements : Window
{
	private readonly Action<int, int> spawnCallback;

	private int settlementsToSpawn;

	private int settlementsRecommended;

	private int distanceToSpawn;

	private int distanceRecommended;

	public static void OpenDialog(Action<int, int> spawnCallback, float settlementSpawnFactor = 1f, int minDistanceToSpawn = -1)
	{
		Find.WindowStack.Add((Window)(object)new Dialog_NewFactionSpawningSettlements(spawnCallback, settlementSpawnFactor, minDistanceToSpawn));
	}

	private Dialog_NewFactionSpawningSettlements(Action<int, int> spawnCallback, float settlementSpawnFactor = 1f, int minDistanceToSpawn = -1)
		: base((IWindowDrawing)null)
	{
		base.doCloseButton = false;
		base.forcePause = true;
		base.absorbInputAroundWindow = true;
		this.spawnCallback = spawnCallback;
		settlementsRecommended = NewFactionSpawningUtility.GetRecommendedSettlementCount();
		settlementsToSpawn = Mathf.Min(4 * settlementsRecommended, NewFactionSpawningUtility.GetRecommendedSettlementCount(settlementSpawnFactor));
		distanceRecommended = SettlementProximityGoodwillUtility.MaxDist;
		if (minDistanceToSpawn <= 0)
		{
			distanceToSpawn = distanceRecommended;
		}
		else
		{
			distanceToSpawn = Mathf.Min(distanceRecommended * 2, minDistanceToSpawn);
		}
	}

	[Obsolete("This issue has been fixed for Faction Control. Users with an old Faction Control version will experience that factions always spawn with a single settlement.")]
	private static void FactionControlFix()
	{
		try
		{
			Type typeInAnyAssembly = GenTypes.GetTypeInAnyAssembly("FactionControl.Controller", "FactionControl");
			FieldInfo field = typeInAnyAssembly.GetField("minFactionSeparation", BindingFlags.Static | BindingFlags.Public);
			FieldInfo field2 = typeInAnyAssembly.GetField("maxFactionSprawl", BindingFlags.Static | BindingFlags.Public);
			FieldInfo field3 = typeInAnyAssembly.GetField("pirateSprawl", BindingFlags.Static | BindingFlags.Public);
			if (((double)field.GetValue(null)).Equals(0.0))
			{
				Log.Message("Found Faction Control mod. Fixing its values to avoid problems.");
				double num = Math.Sqrt(Find.WorldGrid.TilesCount);
				double num2 = Math.Sqrt(Find.FactionManager.AllFactionsVisible.Count() - 1);
				field.SetValue(null, num / (num2 * 2.0));
				double num3 = 0.5;
				field2.SetValue(null, num / (num2 * num3));
				field3.SetValue(null, num / (num2 * num3));
			}
		}
		catch (Exception ex)
		{
			Log.Warning("Something went wrong when trying to initialize FactionControl.Controller:\n" + ex.Message + "\n" + ex.StackTrace);
		}
	}

	public override void DoWindowContents(Rect inRect)
	{
		//IL_0000: Unknown result type (might be due to invalid IL or missing references)
		//IL_0006: Expected O, but got Unknown
		//IL_0007: Unknown result type (might be due to invalid IL or missing references)
		//IL_0008: Unknown result type (might be due to invalid IL or missing references)
		//IL_002a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0035: Unknown result type (might be due to invalid IL or missing references)
		//IL_003a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0045: Unknown result type (might be due to invalid IL or missing references)
		//IL_0084: Unknown result type (might be due to invalid IL or missing references)
		//IL_008f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0094: Unknown result type (might be due to invalid IL or missing references)
		//IL_009f: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d1: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f4: Unknown result type (might be due to invalid IL or missing references)
		Listing_Standard val = new Listing_Standard();
		((Listing)val).Begin(GenUI.AtZero(inRect));
		Text.Font = (GameFont)1;
		Text.Anchor = (TextAnchor)0;
		val.Label(TranslatorFormattedStringExtensions.Translate("VanillaFactionsExpanded.FactionSettlementsToSpawn", NamedArgument.op_Implicit(settlementsRecommended), NamedArgument.op_Implicit(settlementsToSpawn)), -1f, (string)null);
		settlementsToSpawn = Mathf.CeilToInt(val.Slider((float)settlementsToSpawn, 1f, (float)Mathf.Max(settlementsRecommended * 4, 10)));
		val.Label(TranslatorFormattedStringExtensions.Translate("VanillaFactionsExpanded.FactionMinDistance", NamedArgument.op_Implicit(distanceRecommended), NamedArgument.op_Implicit(distanceToSpawn)), -1f, (string)null);
		distanceToSpawn = Mathf.CeilToInt(val.Slider((float)distanceToSpawn, 1f, (float)(distanceRecommended * 2)));
		if (val.ButtonText(TaggedString.op_Implicit(Translator.Translate("VanillaFactionsExpanded.FactionButtonSpawn")), (string)null, 1f))
		{
			Spawn();
		}
		if (val.ButtonText(TaggedString.op_Implicit(Translator.Translate("VanillaFactionsExpanded.FactionButtonCancel")), (string)null, 1f))
		{
			((Window)this).Close(true);
		}
		((Listing)val).End();
	}

	private void Spawn()
	{
		((Window)this).Close(true);
		spawnCallback(settlementsToSpawn, distanceToSpawn);
	}
}
