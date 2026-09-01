using System;
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using VEF.Utils;
using Verse;
using Verse.Sound;

namespace VEF.Planet;

public class Dialog_Hire : Window
{
	private static Ideo hiredIdeo;

	private readonly float availableSilver;

	private readonly Hireable hireable;

	private readonly Dictionary<PawnKindDef, Pair<int, string>> hireData;

	private readonly float riskMultiplier;

	private readonly Map targetMap;

	private HireableFactionDef curFaction;

	private int daysAmount;

	private string daysAmountBuffer;

	public override Vector2 InitialSize => new Vector2(750f, 650f);

	protected override float Margin => 15f;

	private float CostBase => CostDays * CostPawns();

	private float CostDays => Mathf.Pow((float)daysAmount, 0.8f);

	private float CostFinal => CostBase * (riskMultiplier + 1f);

	public Dialog_Hire(Thing negotiator, Hireable hireable)
		: base((IWindowDrawing)null)
	{
		targetMap = negotiator.Map;
		this.hireable = hireable;
		hireData = hireable.SelectMany((HireableFactionDef def) => def.pawnKinds).ToDictionary((PawnKindDef def) => def, (PawnKindDef _) => new Pair<int, string>(0, ""));
		base.closeOnCancel = true;
		base.forcePause = true;
		base.closeOnAccept = true;
		availableSilver = (from x in targetMap.listerThings.ThingsOfDef(ThingDefOf.Silver)
			where !GridsUtility.Fogged(x.Position, x.Map) && (((Area)targetMap.areaManager.Home)[x.Position] || StoreUtility.IsInAnyStorage(x))
			select x).Sum((Thing t) => t.stackCount);
		riskMultiplier = Find.World.GetComponent<HiringContractTracker>().GetFactorForHireable(hireable);
	}

	private float CostPawns(ICollection<PawnKindDef> except = null)
	{
		return (from kv in hireData
			select new Pair<PawnKindDef, int>(kv.Key, kv.Value.First) into pair
			where pair.Second > 0 && (except == null || !except.Contains(pair.First))
			select pair).Sum((Pair<PawnKindDef, int> pair) => Mathf.Pow((float)pair.Second, 1.2f) * pair.First.combatPower);
	}

	public override void OnAcceptKeyPressed()
	{
		//IL_02b7: Unknown result type (might be due to invalid IL or missing references)
		//IL_02bc: Unknown result type (might be due to invalid IL or missing references)
		//IL_0220: Unknown result type (might be due to invalid IL or missing references)
		//IL_0242: Unknown result type (might be due to invalid IL or missing references)
		//IL_0255: Unknown result type (might be due to invalid IL or missing references)
		//IL_025c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0261: Unknown result type (might be due to invalid IL or missing references)
		//IL_0268: Expected O, but got Unknown
		//IL_0186: Unknown result type (might be due to invalid IL or missing references)
		((Window)this).OnAcceptKeyPressed();
		SoundStarter.PlayOneShotOnCamera(SoundDefOf.ExecuteTrade, (Map)null);
		if (daysAmount <= 0 || !hireData.Any((KeyValuePair<PawnKindDef, Pair<int, string>> kvp) => kvp.Value.First > 0))
		{
			return;
		}
		List<Pawn> list = new List<Pawn>();
		int num = Mathf.RoundToInt(CostFinal);
		List<Thing> source = (from x in targetMap.listerThings.ThingsOfDef(ThingDefOf.Silver)
			where !GridsUtility.Fogged(x.Position, x.Map) && (((Area)targetMap.areaManager.Home)[x.Position] || StoreUtility.IsInAnyStorage(x))
			select x).ToList();
		while (num > 0)
		{
			Thing val = source.First((Thing t) => t.stackCount > 0);
			int num2 = Mathf.Min(num, val.stackCount);
			val.SplitOff(num2).Destroy((DestroyMode)0);
			num -= num2;
		}
		foreach (KeyValuePair<PawnKindDef, Pair<int, string>> hireDatum in hireData)
		{
			bool ignoreFactionApparelStuffRequirements;
			PawnKindDef key;
			Faction ofPlayer;
			object obj;
			Ideo val3;
			Pawn val4;
			IntVec3 val5;
			ActiveTransporterInfo val6;
			for (int i = 0; i < hireDatum.Value.First; val3 = (Ideo)obj, val4 = PawnGenerator.GeneratePawn(new PawnGenerationRequest(key, ofPlayer, (PawnGenerationContext)2, (PlanetTile?)null, false, false, false, true, true, 1f, false, true, false, true, true, false, false, false, false, 0f, 0f, (Pawn)null, 1f, (Predicate<Pawn>)null, (Predicate<Pawn>)null, (IEnumerable<TraitDef>)null, (IEnumerable<TraitDef>)null, (float?)null, (float?)null, (float?)null, (Gender?)null, (string)null, (string)null, (RoyalTitleDef)null, val3, false, false, true, false, (List<GeneDef>)null, (List<GeneDef>)null, (XenotypeDef)null, (CustomXenotype)null, (List<XenotypeDef>)null, 0f, (DevelopmentalStage)8, (Func<XenotypeDef, PawnKindDef>)null, (FloatRange?)null, (FloatRange?)null, false, false, false, -1, 0, false)), hireDatum.Key.ignoreFactionApparelStuffRequirements = ignoreFactionApparelStuffRequirements, val4.playerSettings.hostilityResponse = (HostilityResponseMode)1, list.Add(val4), val5 = DropCellFinder.TryFindSafeLandingSpotCloseToColony(targetMap, IntVec2.Two, (Faction)null, 2), val6 = new ActiveTransporterInfo(), val6.innerContainer.TryAdd((Thing)(object)val4, 1, true), val6.openDelay = 60, val6.leaveSlag = false, val6.despawnPodBeforeSpawningThing = true, val6.spawnWipeMode = (WipeMode)0, DropPodUtility.MakeDropPodAt(val5, targetMap, val6, (Faction)null), i++)
			{
				ignoreFactionApparelStuffRequirements = hireDatum.Key.ignoreFactionApparelStuffRequirements;
				hireDatum.Key.ignoreFactionApparelStuffRequirements = true;
				key = hireDatum.Key;
				ofPlayer = Faction.OfPlayer;
				if (curFaction.referencedFaction != null)
				{
					Faction val2 = Find.World.factionManager.FirstFactionOfDef(curFaction.referencedFaction);
					if (val2 != null)
					{
						obj = val2.ideos.GetRandomIdeoForNewPawn();
						continue;
					}
				}
				obj = hiredIdeo ?? (hiredIdeo = IdeoGenerator.GenerateIdeo(new IdeoGenerationParms(Faction.OfPlayer.def, false, (List<PreceptDef>)null, (List<MemeDef>)null, (List<MemeDef>)null, true, false, false, false, "", (List<StyleCategoryDef>)null, (List<DeityPreset>)null, false, "", false)));
			}
		}
		Find.World.GetComponent<HiringContractTracker>().SetNewContract(daysAmount, list, hireable, curFaction, CostFinal);
	}

	public override void DoWindowContents(Rect inRect)
	{
		//IL_0002: Unknown result type (might be due to invalid IL or missing references)
		//IL_0008: Unknown result type (might be due to invalid IL or missing references)
		//IL_000d: Unknown result type (might be due to invalid IL or missing references)
		//IL_000e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0013: Unknown result type (might be due to invalid IL or missing references)
		//IL_003a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0082: Unknown result type (might be due to invalid IL or missing references)
		//IL_0098: Unknown result type (might be due to invalid IL or missing references)
		//IL_009d: Unknown result type (might be due to invalid IL or missing references)
		//IL_00fa: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ff: Unknown result type (might be due to invalid IL or missing references)
		//IL_011f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0125: Unknown result type (might be due to invalid IL or missing references)
		//IL_012a: Unknown result type (might be due to invalid IL or missing references)
		//IL_012c: Unknown result type (might be due to invalid IL or missing references)
		//IL_012e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0138: Unknown result type (might be due to invalid IL or missing references)
		//IL_014e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0150: Unknown result type (might be due to invalid IL or missing references)
		//IL_015a: Unknown result type (might be due to invalid IL or missing references)
		//IL_015f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0187: Unknown result type (might be due to invalid IL or missing references)
		//IL_018e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0190: Unknown result type (might be due to invalid IL or missing references)
		//IL_019a: Unknown result type (might be due to invalid IL or missing references)
		//IL_01aa: Unknown result type (might be due to invalid IL or missing references)
		//IL_01ac: Unknown result type (might be due to invalid IL or missing references)
		//IL_0212: Unknown result type (might be due to invalid IL or missing references)
		//IL_0219: Unknown result type (might be due to invalid IL or missing references)
		//IL_021b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0225: Unknown result type (might be due to invalid IL or missing references)
		//IL_022f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0231: Unknown result type (might be due to invalid IL or missing references)
		//IL_025a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0261: Unknown result type (might be due to invalid IL or missing references)
		//IL_0263: Unknown result type (might be due to invalid IL or missing references)
		//IL_026d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0277: Unknown result type (might be due to invalid IL or missing references)
		//IL_0279: Unknown result type (might be due to invalid IL or missing references)
		//IL_02a1: Unknown result type (might be due to invalid IL or missing references)
		//IL_02a8: Unknown result type (might be due to invalid IL or missing references)
		//IL_02aa: Unknown result type (might be due to invalid IL or missing references)
		//IL_02b4: Unknown result type (might be due to invalid IL or missing references)
		//IL_02be: Unknown result type (might be due to invalid IL or missing references)
		//IL_02c0: Unknown result type (might be due to invalid IL or missing references)
		//IL_02dd: Unknown result type (might be due to invalid IL or missing references)
		//IL_02e7: Unknown result type (might be due to invalid IL or missing references)
		//IL_02f1: Unknown result type (might be due to invalid IL or missing references)
		//IL_031c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0326: Unknown result type (might be due to invalid IL or missing references)
		//IL_0330: Unknown result type (might be due to invalid IL or missing references)
		//IL_0384: Unknown result type (might be due to invalid IL or missing references)
		//IL_038f: Unknown result type (might be due to invalid IL or missing references)
		//IL_03a4: Unknown result type (might be due to invalid IL or missing references)
		//IL_03a9: Unknown result type (might be due to invalid IL or missing references)
		//IL_03ae: Unknown result type (might be due to invalid IL or missing references)
		//IL_03bd: Unknown result type (might be due to invalid IL or missing references)
		//IL_03c3: Unknown result type (might be due to invalid IL or missing references)
		//IL_0361: Unknown result type (might be due to invalid IL or missing references)
		Rect rect = default(Rect);
		((Rect)(ref rect))._002Ector(inRect);
		TextAnchor anchor = Text.Anchor;
		GameFont font = Text.Font;
		Text.Anchor = (TextAnchor)3;
		Text.Font = (GameFont)2;
		Widgets.Label(new Rect(((Rect)(ref rect)).x, ((Rect)(ref rect)).y, ((Rect)(ref rect)).width, 40f), hireable.GetCallLabel());
		Text.Font = (GameFont)1;
		((Rect)(ref rect)).yMin = ((Rect)(ref rect)).yMin + 40f;
		Widgets.Label(new Rect(((Rect)(ref rect)).x, ((Rect)(ref rect)).y, ((Rect)(ref rect)).width, 20f), TranslatorFormattedStringExtensions.Translate("VEF.AvailableSilver", NamedArgument.op_Implicit(GenText.ToStringMoney(availableSilver, (string)null))));
		((Rect)(ref rect)).yMin = ((Rect)(ref rect)).yMin + 30f;
		foreach (HireableFactionDef item in hireable)
		{
			DoHireableFaction(ref rect, item);
		}
		Rect val = rect.TakeTopPart(100f);
		((Rect)(ref val)).xMin = ((Rect)(ref val)).xMin + 115f;
		Text.Anchor = (TextAnchor)0;
		Text.Font = (GameFont)1;
		Rect val2 = GenUI.TopPartPixels(val, 20f);
		Widgets.Label(GenUI.LeftHalf(val2), Translator.Translate("VEF.Breakdown"));
		Text.Anchor = (TextAnchor)4;
		Text.Font = (GameFont)0;
		Widgets.Label(GenUI.RightHalf(val2), ColoredText.Colorize(Translator.Translate("VEF.LongTerm"), ColoredText.SubtleGrayColor));
		Text.Font = (GameFont)1;
		((Rect)(ref val2)).y = ((Rect)(ref val2)).y + 20f;
		Widgets.DrawLightHighlight(val2);
		Widgets.Label(GenUI.LeftHalf(val2), Translator.Translate("VEF.DayAmount"));
		UIUtility.DrawCountAdjuster(ref daysAmount, GenUI.RightHalf(val2), ref daysAmountBuffer, 0, 60, readOnly: false, null, Mathf.Max(Mathf.FloorToInt(Mathf.Pow(availableSilver / (riskMultiplier + 1f) / CostPawns(), 1.25f)), 1));
		((Rect)(ref val2)).y = ((Rect)(ref val2)).y + 20f;
		Widgets.DrawHighlight(val2);
		Widgets.Label(GenUI.LeftHalf(val2), Translator.Translate("VEF.Cost"));
		Widgets.Label(GenUI.RightHalf(val2), GenText.ToStringMoney(CostBase, (string)null));
		((Rect)(ref val2)).y = ((Rect)(ref val2)).y + 20f;
		Widgets.DrawLightHighlight(val2);
		Widgets.Label(GenUI.LeftHalf(val2), Translator.Translate("VEF.RiskMult"));
		Widgets.Label(GenUI.RightHalf(val2), GenText.ToStringPercent(riskMultiplier));
		((Rect)(ref val2)).y = ((Rect)(ref val2)).y + 20f;
		Widgets.DrawHighlight(val2);
		Widgets.Label(GenUI.LeftHalf(val2), Translator.Translate("VEF.TotalPrice"));
		Widgets.Label(GenUI.RightHalf(val2), GenText.ToStringMoney(CostFinal, (string)null));
		if (Widgets.ButtonText(GenUI.BottomPartPixels(rect.TakeLeftPart(120f), 40f), TaggedString.op_Implicit(Translator.Translate("Cancel")), true, true, true, (TextAnchor?)null))
		{
			((Window)this).OnCancelKeyPressed();
		}
		if (Widgets.ButtonText(GenUI.BottomPartPixels(rect.TakeRightPart(120f), 40f), TaggedString.op_Implicit(Translator.Translate("Confirm")), true, true, true, (TextAnchor?)null))
		{
			if (CostFinal > availableSilver)
			{
				Messages.Message(TaggedString.op_Implicit(Translator.Translate("NotEnoughSilver")), MessageTypeDefOf.RejectInput, true);
			}
			else
			{
				((Window)this).OnAcceptKeyPressed();
			}
		}
		Text.Font = (GameFont)0;
		Widgets.Label(GenUI.ContractedBy(rect, 30f, 0f), ColoredText.Colorize(TranslatorFormattedStringExtensions.Translate("VEF.HiringDesc", NamedArgument.op_Implicit(hireable.Key)), ColoredText.SubtleGrayColor));
		Text.Anchor = anchor;
		Text.Font = font;
	}

	private void DoHireableFaction(ref Rect inRect, HireableFactionDef def)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		//IL_0028: Unknown result type (might be due to invalid IL or missing references)
		//IL_002d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0049: Unknown result type (might be due to invalid IL or missing references)
		//IL_004e: Unknown result type (might be due to invalid IL or missing references)
		//IL_004f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0055: Unknown result type (might be due to invalid IL or missing references)
		//IL_005f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0085: Unknown result type (might be due to invalid IL or missing references)
		//IL_008b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0092: Unknown result type (might be due to invalid IL or missing references)
		//IL_0097: Unknown result type (might be due to invalid IL or missing references)
		//IL_009c: Unknown result type (might be due to invalid IL or missing references)
		//IL_00cd: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d3: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d9: Unknown result type (might be due to invalid IL or missing references)
		//IL_0104: Unknown result type (might be due to invalid IL or missing references)
		//IL_0110: Unknown result type (might be due to invalid IL or missing references)
		//IL_0116: Unknown result type (might be due to invalid IL or missing references)
		//IL_011b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0130: Unknown result type (might be due to invalid IL or missing references)
		//IL_0137: Unknown result type (might be due to invalid IL or missing references)
		//IL_0156: Unknown result type (might be due to invalid IL or missing references)
		//IL_0206: Unknown result type (might be due to invalid IL or missing references)
		//IL_0209: Unknown result type (might be due to invalid IL or missing references)
		//IL_0219: Unknown result type (might be due to invalid IL or missing references)
		//IL_0235: Unknown result type (might be due to invalid IL or missing references)
		//IL_023a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0250: Unknown result type (might be due to invalid IL or missing references)
		//IL_01f2: Unknown result type (might be due to invalid IL or missing references)
		//IL_02f5: Unknown result type (might be due to invalid IL or missing references)
		Rect rect = GenUI.TopPartPixels(inRect, Mathf.Max(20f + (float)def.pawnKinds.Count * 30f, 120f));
		((Rect)(ref inRect)).yMin = ((Rect)(ref inRect)).yMin + ((Rect)(ref rect)).height;
		Rect val = rect.TakeTopPart(20f);
		Rect val2 = GenUI.ContractedBy(GenUI.LeftPartPixels(rect, 105f), 5f);
		((Rect)(ref val)).x = ((Rect)(ref val)).x + 115f;
		Text.Anchor = (TextAnchor)3;
		Text.Font = (GameFont)0;
		Rect val3 = default(Rect);
		((Rect)(ref val3))._002Ector(val);
		Widgets.Label(val, TranslatorFormattedStringExtensions.Translate("VEF.Hire", NamedArgument.op_Implicit(((Def)def).LabelCap)));
		((Rect)(ref val)).x = ((Rect)(ref val)).x + 200f;
		((Rect)(ref val)).width = 60f;
		Text.Anchor = (TextAnchor)4;
		Rect val4 = default(Rect);
		((Rect)(ref val4))._002Ector(val);
		Widgets.Label(val, Translator.Translate("VEF.Value"));
		((Rect)(ref val)).x = ((Rect)(ref val)).x + 100f;
		((Rect)(ref val)).width = 300f;
		Rect inRect2 = default(Rect);
		((Rect)(ref inRect2))._002Ector(val);
		Text.Font = (GameFont)0;
		Widgets.Label(val, ColoredText.Colorize(Translator.Translate("VEF.ChooseNumberOfUnits"), ColoredText.SubtleGrayColor));
		Text.Font = (GameFont)1;
		Widgets.DrawLightHighlight(val2);
		GUI.color = def.color;
		Widgets.DrawTextureFitted(val2, (Texture)(object)def.Texture, 1f, 1f);
		GUI.color = Color.white;
		bool flag = true;
		Rect val5 = default(Rect);
		foreach (PawnKindDef pawnKind in def.pawnKinds)
		{
			((Rect)(ref val3)).y = ((Rect)(ref val3)).y + 20f;
			((Rect)(ref val4)).y = ((Rect)(ref val4)).y + 20f;
			((Rect)(ref inRect2)).y = ((Rect)(ref inRect2)).y + 20f;
			((Rect)(ref val5))._002Ector(((Rect)(ref val3)).x - 4f, ((Rect)(ref val3)).y, ((Rect)(ref val3)).width + ((Rect)(ref val4)).width + ((Rect)(ref inRect2)).width, 20f);
			if (flag)
			{
				Widgets.DrawHighlight(val5);
			}
			flag = !flag;
			Text.Anchor = (TextAnchor)3;
			Widgets.Label(val3, ((Def)pawnKind).LabelCap);
			Text.Anchor = (TextAnchor)4;
			Widgets.Label(val4, GenText.ToStringByStyle(pawnKind.combatPower, (ToStringStyle)0, (ToStringNumberSense)1));
			Pair<int, string> val6 = hireData[pawnKind];
			int value = val6.First;
			string buffer = val6.Second;
			UIUtility.DrawCountAdjuster(ref value, inRect2, ref buffer, 0, 99, curFaction != null && curFaction != def, null, Mathf.Max(Mathf.FloorToInt(Mathf.Pow((availableSilver / (riskMultiplier + 1f) / CostDays - CostPawns(new HashSet<PawnKindDef> { pawnKind })) / pawnKind.combatPower, 5f / 6f)), 0));
			if (value != val6.First || buffer != val6.Second)
			{
				hireData[pawnKind] = new Pair<int, string>(value, buffer);
				if (value > 0 && curFaction == null)
				{
					curFaction = def;
				}
				if (value == 0 && curFaction == def && def.pawnKinds.All((PawnKindDef pk) => hireData[pk].First == 0))
				{
					curFaction = null;
				}
			}
		}
	}
}
