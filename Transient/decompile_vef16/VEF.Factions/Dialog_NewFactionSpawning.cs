using System;
using System.Collections.Generic;
using KCSG;
using RimWorld;
using UnityEngine;
using Verse;

namespace VEF.Factions;

public class Dialog_NewFactionSpawning : Window
{
	private FactionDef factionDef;

	private IEnumerator<FactionDef> factionEnumerator;

	private ForcedFactionData forcedFactionData;

	private bool failedToSpawn;

	private static Color colorCoreMod = new Color(25f / 51f, 0.38039216f, 0.2f);

	private static Color colorMod = new Color(23f / 51f, 54f / 85f, 0.18431373f);

	private static Color colorRed = new Color(1f, 0.3f, 0.35f);

	public static void OpenDialog(IEnumerator<FactionDef> enumerator, FactionDef faction = null)
	{
		Find.WindowStack.Add((Window)(object)new Dialog_NewFactionSpawning(enumerator, faction));
	}

	private Dialog_NewFactionSpawning(IEnumerator<FactionDef> enumerator, FactionDef faction = null)
		: base((IWindowDrawing)null)
	{
		base.doCloseButton = false;
		base.forcePause = true;
		base.absorbInputAroundWindow = true;
		factionEnumerator = enumerator;
		factionDef = faction ?? enumerator.Current;
		forcedFactionData = FactionDefExtension.Get((Def)(object)factionDef).forcedFactionData;
		base.closeOnAccept = false;
		if (forcedFactionData.forcePlayerToAddFactionIfMissing)
		{
			base.closeOnCancel = (base.closeOnClickedOutside = false);
		}
	}

	public override void DoWindowContents(Rect inRect)
	{
		//IL_0000: Unknown result type (might be due to invalid IL or missing references)
		//IL_0006: Expected O, but got Unknown
		//IL_0007: Unknown result type (might be due to invalid IL or missing references)
		//IL_0008: Unknown result type (might be due to invalid IL or missing references)
		//IL_008a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0099: Unknown result type (might be due to invalid IL or missing references)
		//IL_009e: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a9: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d9: Unknown result type (might be due to invalid IL or missing references)
		//IL_00de: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e9: Unknown result type (might be due to invalid IL or missing references)
		//IL_002f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0034: Unknown result type (might be due to invalid IL or missing references)
		//IL_0037: Unknown result type (might be due to invalid IL or missing references)
		//IL_0061: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ff: Unknown result type (might be due to invalid IL or missing references)
		//IL_010f: Unknown result type (might be due to invalid IL or missing references)
		//IL_011a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0196: Unknown result type (might be due to invalid IL or missing references)
		//IL_01ad: Unknown result type (might be due to invalid IL or missing references)
		//IL_01b8: Unknown result type (might be due to invalid IL or missing references)
		//IL_012d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0144: Unknown result type (might be due to invalid IL or missing references)
		//IL_014f: Unknown result type (might be due to invalid IL or missing references)
		//IL_01cc: Unknown result type (might be due to invalid IL or missing references)
		//IL_01dc: Unknown result type (might be due to invalid IL or missing references)
		//IL_01e7: Unknown result type (might be due to invalid IL or missing references)
		//IL_0171: Unknown result type (might be due to invalid IL or missing references)
		//IL_0176: Unknown result type (might be due to invalid IL or missing references)
		//IL_0181: Unknown result type (might be due to invalid IL or missing references)
		//IL_0254: Unknown result type (might be due to invalid IL or missing references)
		//IL_026f: Unknown result type (might be due to invalid IL or missing references)
		//IL_027a: Unknown result type (might be due to invalid IL or missing references)
		//IL_02ba: Unknown result type (might be due to invalid IL or missing references)
		//IL_0202: Unknown result type (might be due to invalid IL or missing references)
		//IL_021d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0222: Unknown result type (might be due to invalid IL or missing references)
		//IL_0243: Unknown result type (might be due to invalid IL or missing references)
		//IL_024e: Unknown result type (might be due to invalid IL or missing references)
		//IL_02df: Unknown result type (might be due to invalid IL or missing references)
		//IL_0329: Unknown result type (might be due to invalid IL or missing references)
		//IL_0319: Unknown result type (might be due to invalid IL or missing references)
		//IL_037f: Unknown result type (might be due to invalid IL or missing references)
		//IL_036f: Unknown result type (might be due to invalid IL or missing references)
		//IL_034f: Unknown result type (might be due to invalid IL or missing references)
		//IL_03c2: Unknown result type (might be due to invalid IL or missing references)
		//IL_03a5: Unknown result type (might be due to invalid IL or missing references)
		Listing_Standard val = new Listing_Standard();
		((Listing)val).Begin(GenUI.AtZero(inRect));
		if (Object.op_Implicit((Object)(object)factionDef.FactionIcon))
		{
			Rect rect = ((Listing)val).GetRect(64f, 1f);
			float x = ((Rect)(ref rect)).center.x;
			((Rect)(ref rect)).xMin = x - 32f;
			((Rect)(ref rect)).xMax = x + 32f;
			GUI.DrawTexture(rect, (Texture)(object)factionDef.FactionIcon);
		}
		Text.Font = (GameFont)2;
		Text.Anchor = (TextAnchor)4;
		val.Label(TranslatorFormattedStringExtensions.Translate("VanillaFactionsExpanded.FactionTitle", new NamedArgument((object)((Def)factionDef).LabelCap, "FactionName")), -1f, (string)null);
		((Listing)val).GapLine(12f);
		Text.Font = (GameFont)1;
		Text.Anchor = (TextAnchor)0;
		string modName = GetModName();
		val.Label(TranslatorFormattedStringExtensions.Translate("VanillaFactionsExpanded.ModInfo", new NamedArgument((object)modName, "ModName")), -1f, (string)null);
		if (factionDef.hidden)
		{
			GUI.color = colorCoreMod;
			val.Label(Translator.Translate("VanillaFactionsExpanded.HiddenFactionInfo"), -1f, (string)null);
			if (forcedFactionData.forcePlayerToAddFactionIfMissing)
			{
				GUI.color = colorRed;
				val.Label(forcedFactionData.GetFactionDiscoveryMessage(factionDef), -1f, (string)null);
			}
			else if (factionDef.requiredCountAtGameStart > 0)
			{
				val.Label(TranslatorFormattedStringExtensions.Translate("VanillaFactionsExpanded.RequiredFactionInfo", new NamedArgument((object)modName, "ModName")), -1f, (string)null);
			}
		}
		else if (forcedFactionData.forcePlayerToAddFactionIfMissing)
		{
			GUI.color = colorRed;
			val.Label(forcedFactionData.GetFactionDiscoveryMessage(factionDef), -1f, (string)null);
		}
		if (factionDef.requiredCountAtGameStart <= 0)
		{
			GUI.color = colorRed;
			val.Label(Translator.Translate("VanillaFactionsExpanded.NonSpawningFactionInfo"), -1f, (string)null);
		}
		if (forcedFactionData.forcePlayerToAddFactionIfMissing && failedToSpawn)
		{
			GUI.color = Color.yellow;
			Log.ErrorOnce(TaggedString.op_Implicit("Displaying fail message:\n" + forcedFactionData.GetFactionDiscoveryFailedMessage(factionDef)), 19278381);
			val.Label(forcedFactionData.GetFactionDiscoveryFailedMessage(factionDef), -1f, (string)null);
		}
		GUI.color = Color.white;
		((Listing)val).Gap(40f);
		val.Label(Translator.Translate("VanillaFactionsExpanded.FactionSelectOption"), -1f, (string)null);
		((Listing)val).Gap(60f);
		if (!factionDef.hidden)
		{
			CustomGenOption modExtension = ((Def)factionDef).GetModExtension<CustomGenOption>();
			if (modExtension == null || modExtension.canSpawnSettlements)
			{
				if (val.ButtonText(TaggedString.op_Implicit(Translator.Translate("VanillaFactionsExpanded.FactionButtonAddFull")), (string)null, 1f))
				{
					SpawnWithBases();
				}
				goto IL_02fc;
			}
		}
		if (val.ButtonText(TaggedString.op_Implicit(Translator.Translate("VanillaFactionsExpanded.FactionButtonAdd")), (string)null, 1f))
		{
			SpawnWithoutBases();
		}
		goto IL_02fc;
		IL_02fc:
		bool flag = forcedFactionData.forcePlayerToAddFactionIfMissing && !failedToSpawn;
		if (flag)
		{
			GUI.color = Color.gray;
		}
		if (val.ButtonText(TaggedString.op_Implicit(Translator.Translate("VanillaFactionsExpanded.FactionButtonSkip")), (string)null, 1f))
		{
			if (flag)
			{
				Messages.Message(TaggedString.op_Implicit(forcedFactionData.GetFactionDiscoveryMessage(factionDef)), MessageTypeDefOf.RejectInput, false);
			}
			else
			{
				Skip();
			}
		}
		if (!flag)
		{
			GUI.color = colorRed;
		}
		if (val.ButtonText(TaggedString.op_Implicit(Translator.Translate("VanillaFactionsExpanded.FactionButtonIgnore")), (string)null, 1f))
		{
			if (flag)
			{
				Messages.Message(TaggedString.op_Implicit(forcedFactionData.GetFactionDiscoveryMessage(factionDef)), MessageTypeDefOf.RejectInput, false);
			}
			else
			{
				Ignore();
			}
		}
		GUI.color = Color.white;
		((Listing)val).End();
	}

	private void SpawnWithBases()
	{
		Dialog_NewFactionSpawningSettlements.OpenDialog(SpawnCallback, forcedFactionData.factionDiscoveryFactionCountFactor, forcedFactionData.factionDiscoveryMinimumDistanceFromPlayer);
		void SpawnCallback(int amount, int minDistance)
		{
			//IL_001b: Unknown result type (might be due to invalid IL or missing references)
			//IL_0059: Unknown result type (might be due to invalid IL or missing references)
			//IL_0069: Unknown result type (might be due to invalid IL or missing references)
			//IL_006e: Unknown result type (might be due to invalid IL or missing references)
			//IL_00e4: Unknown result type (might be due to invalid IL or missing references)
			try
			{
				int spawned;
				Faction val = NewFactionSpawningUtility.SpawnWithSettlements(factionDef, amount, minDistance, out spawned);
				if (val == null || spawned == 0)
				{
					Messages.Message(TaggedString.op_Implicit(Translator.Translate("VanillaFactionsExpanded.FactionMessageFailedFull")), MessageTypeDefOf.RejectInput, false);
					failedToSpawn = true;
					base.closeOnCancel = (base.closeOnClickedOutside = true);
				}
				else
				{
					Messages.Message(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("VanillaFactionsExpanded.FactionMessageSuccessFull", new NamedArgument((object)val.GetCallLabel(), "FactionName"), new NamedArgument((object)spawned, "Amount"))), MessageTypeDefOf.TaskCompletion, true);
					((Window)this).Close(true);
				}
			}
			catch (Exception ex)
			{
				Log.Error("An error occurred when trying to spawn faction " + ((Def)(factionDef?)).defName + ":\n" + ex.Message + "\n" + ex.StackTrace);
				Messages.Message(TaggedString.op_Implicit(Translator.Translate("VanillaFactionsExpanded.FactionMessageFailedFull")), MessageTypeDefOf.RejectInput, false);
				failedToSpawn = true;
				base.closeOnCancel = (base.closeOnClickedOutside = true);
			}
		}
	}

	private void SpawnWithoutBases()
	{
		//IL_001c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0021: Unknown result type (might be due to invalid IL or missing references)
		//IL_0094: Unknown result type (might be due to invalid IL or missing references)
		try
		{
			Faction val = NewFactionSpawningUtility.SpawnWithoutSettlements(factionDef);
			Messages.Message(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("VanillaFactionsExpanded.FactionMessageSuccess", new NamedArgument((object)val.GetCallLabel(), "FactionName"))), MessageTypeDefOf.TaskCompletion, true);
			((Window)this).Close(true);
		}
		catch (Exception ex)
		{
			Log.Error("An error occurred when trying to spawn faction " + ((Def)(factionDef?)).defName + ":\n" + ex.Message + "\n" + ex.StackTrace);
			Messages.Message(TaggedString.op_Implicit(Translator.Translate("VanillaFactionsExpanded.FactionMessageFailed")), MessageTypeDefOf.RejectInput, false);
			failedToSpawn = true;
		}
	}

	private void Skip()
	{
		((Window)this).Close(true);
	}

	private void Ignore()
	{
		Find.World.GetComponent<NewFactionSpawningState>().Ignore(factionDef);
		((Window)this).Close(true);
	}

	public override void PostClose()
	{
		if (!failedToSpawn && forcedFactionData.forcePlayerToAddFactionIfMissing && forcedFactionData.UnderRequiredGameplayFactionCount(factionDef))
		{
			OpenDialog(factionEnumerator, factionDef);
		}
		else if (factionEnumerator.MoveNext())
		{
			OpenDialog(factionEnumerator);
		}
		else
		{
			factionEnumerator.Dispose();
		}
	}

	private string GetModName()
	{
		//IL_0019: Unknown result type (might be due to invalid IL or missing references)
		//IL_0061: Unknown result type (might be due to invalid IL or missing references)
		//IL_0046: Unknown result type (might be due to invalid IL or missing references)
		if (((Def)(factionDef?)).modContentPack == null)
		{
			return TaggedString.op_Implicit(Translator.Translate("VanillaFactionsExpanded.AnUnknownMod"));
		}
		if (((Def)factionDef).modContentPack.IsCoreMod)
		{
			return ColoredText.Colorize(((Def)factionDef).modContentPack.Name, colorCoreMod);
		}
		return ColoredText.Colorize(((Def)factionDef).modContentPack.Name, colorMod);
	}

	public override void OnAcceptKeyPressed()
	{
		((Window)this).OnAcceptKeyPressed();
		if (!factionDef.hidden)
		{
			CustomGenOption modExtension = ((Def)factionDef).GetModExtension<CustomGenOption>();
			if (modExtension == null || modExtension.canSpawnSettlements)
			{
				SpawnWithBases();
				return;
			}
		}
		SpawnWithoutBases();
	}
}
