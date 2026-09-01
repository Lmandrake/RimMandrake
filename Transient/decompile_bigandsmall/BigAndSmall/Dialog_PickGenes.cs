using System;
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using UnityEngine;
using Verse;

namespace BigAndSmall;

public class Dialog_PickGenes : Window
{
	private Pawn caster;

	private List<GeneDef> availableGenes;

	private GeneDef selectedGene;

	public string letterTextKey;

	private Vector2 scrollPositionGenes;

	private Vector2 scrollPositionCaster;

	private Vector2 scrollPositionDetails;

	private QuickSearchWidget quickSearchWidget = new QuickSearchWidget();

	private List<Gene> casterXenogenes;

	private List<Gene> casterEndogenes;

	private List<GeneDef> filteredGenes = new List<GeneDef>();

	private static Vector2 lastWindowSize = Vector2.zero;

	public override Vector2 InitialSize
	{
		get
		{
			//IL_0000: Unknown result type (might be due to invalid IL or missing references)
			//IL_0005: Unknown result type (might be due to invalid IL or missing references)
			//IL_0055: Unknown result type (might be due to invalid IL or missing references)
			//IL_004b: Unknown result type (might be due to invalid IL or missing references)
			//IL_0050: Unknown result type (might be due to invalid IL or missing references)
			if (lastWindowSize == Vector2.zero)
			{
				float num = Mathf.Clamp((float)UI.screenWidth * 0.6f, 850f, 1200f);
				float num2 = Mathf.Clamp((float)UI.screenHeight * 0.7f, 650f, 900f);
				lastWindowSize = new Vector2(num, num2);
			}
			return lastWindowSize;
		}
	}

	public static List<string> BodyShapeGeneNames => new List<string> { "Body_Standard", "Body_Hulk", "Body_Fat", "Body_Thin" };

	public static List<string> ForcedGenderGenes => new List<string> { "Body_MaleOnly", "Body_FemaleOnly" };

	public Dialog_PickGenes(Pawn caster, List<GeneDef> availableGenes)
		: base((IWindowDrawing)null)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		//IL_000b: Expected O, but got Unknown
		this.caster = caster;
		this.availableGenes = availableGenes;
		casterXenogenes = caster.genes.Xenogenes;
		casterEndogenes = caster.genes.Endogenes;
		base.forcePause = true;
		base.doCloseX = true;
		base.doCloseButton = false;
		base.absorbInputAroundWindow = true;
		base.closeOnClickedOutside = false;
		base.draggable = true;
		base.resizeable = true;
		base.drawShadow = true;
		UpdateFilteredGenes();
		if (filteredGenes.Count > 0)
		{
			selectedGene = filteredGenes[0];
		}
	}

	private void UpdateFilteredGenes()
	{
		//IL_005f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0064: Unknown result type (might be due to invalid IL or missing references)
		filteredGenes.Clear();
		foreach (GeneDef availableGene in availableGenes)
		{
			if (quickSearchWidget.filter.Matches(((Def)availableGene).label))
			{
				filteredGenes.Add(availableGene);
			}
		}
		scrollPositionGenes = Vector2.zero;
	}

	public override void DoWindowContents(Rect inRect)
	{
		//IL_0016: Unknown result type (might be due to invalid IL or missing references)
		//IL_002c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0031: Unknown result type (might be due to invalid IL or missing references)
		//IL_0036: Unknown result type (might be due to invalid IL or missing references)
		//IL_006b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0170: Unknown result type (might be due to invalid IL or missing references)
		//IL_0177: Unknown result type (might be due to invalid IL or missing references)
		//IL_017e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0183: Unknown result type (might be due to invalid IL or missing references)
		//IL_01d3: Unknown result type (might be due to invalid IL or missing references)
		//IL_01db: Unknown result type (might be due to invalid IL or missing references)
		//IL_01fd: Unknown result type (might be due to invalid IL or missing references)
		//IL_0207: Unknown result type (might be due to invalid IL or missing references)
		//IL_02eb: Unknown result type (might be due to invalid IL or missing references)
		//IL_0302: Unknown result type (might be due to invalid IL or missing references)
		//IL_033b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0340: Unknown result type (might be due to invalid IL or missing references)
		//IL_034b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0350: Unknown result type (might be due to invalid IL or missing references)
		//IL_027c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0275: Unknown result type (might be due to invalid IL or missing references)
		//IL_03a0: Unknown result type (might be due to invalid IL or missing references)
		//IL_03a8: Unknown result type (might be due to invalid IL or missing references)
		//IL_029b: Unknown result type (might be due to invalid IL or missing references)
		//IL_028f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0294: Unknown result type (might be due to invalid IL or missing references)
		//IL_0402: Unknown result type (might be due to invalid IL or missing references)
		//IL_04e5: Unknown result type (might be due to invalid IL or missing references)
		//IL_0527: Unknown result type (might be due to invalid IL or missing references)
		//IL_052d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0533: Unknown result type (might be due to invalid IL or missing references)
		//IL_0538: Unknown result type (might be due to invalid IL or missing references)
		//IL_055e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0569: Unknown result type (might be due to invalid IL or missing references)
		//IL_05a7: Unknown result type (might be due to invalid IL or missing references)
		//IL_066d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0675: Unknown result type (might be due to invalid IL or missing references)
		//IL_0690: Unknown result type (might be due to invalid IL or missing references)
		//IL_07f1: Unknown result type (might be due to invalid IL or missing references)
		//IL_0875: Unknown result type (might be due to invalid IL or missing references)
		//IL_0824: Unknown result type (might be due to invalid IL or missing references)
		//IL_0829: Unknown result type (might be due to invalid IL or missing references)
		//IL_083d: Unknown result type (might be due to invalid IL or missing references)
		//IL_08b9: Unknown result type (might be due to invalid IL or missing references)
		Rect val = new Rect(0f, 0f, ((Rect)(ref inRect)).width, 35f);
		Text.Font = (GameFont)2;
		TaggedString val2 = TranslatorFormattedStringExtensions.Translate("BS_PickAListedGene", NamedArgument.op_Implicit((Thing)(object)caster));
		Widgets.Label(val, ((TaggedString)(ref val2)).Resolve());
		Text.Font = (GameFont)1;
		Rect val3 = default(Rect);
		((Rect)(ref val3))._002Ector(0f, 45f, 300f, 24f);
		quickSearchWidget.OnGUI(val3, (Action)UpdateFilteredGenes, (Action)null);
		Rect val4 = default(Rect);
		((Rect)(ref val4))._002Ector(0f, 85f, ((Rect)(ref inRect)).width, ((Rect)(ref inRect)).height - 85f - 110f);
		Rect val5 = default(Rect);
		((Rect)(ref val5))._002Ector(((Rect)(ref val4)).xMax - 380f, ((Rect)(ref val4)).y, 380f, ((Rect)(ref val4)).height);
		Rect val6 = default(Rect);
		((Rect)(ref val6))._002Ector(((Rect)(ref val4)).x, ((Rect)(ref val4)).y, ((Rect)(ref val4)).width - 380f - 12f, ((Rect)(ref val4)).height);
		int num = Mathf.FloorToInt((((Rect)(ref val6)).width - 16f - 4f) / 91f);
		float num2 = 72f * (float)(filteredGenes.Count / num);
		float num3 = Mathf.Min(108f + num2, ((Rect)(ref val6)).height * 0.6f);
		Rect val7 = default(Rect);
		((Rect)(ref val7))._002Ector(((Rect)(ref val6)).x, ((Rect)(ref val6)).y, ((Rect)(ref val6)).width, num3);
		Widgets.DrawMenuSection(val7);
		Rect val8 = GenUI.ContractedBy(val7, 4f);
		int num4 = Mathf.FloorToInt((((Rect)(ref val8)).width - 16f - 4f) / 91f);
		if (num4 <= 0)
		{
			num4 = 1;
		}
		Rect val9 = default(Rect);
		((Rect)(ref val9))._002Ector(0f, 0f, ((Rect)(ref val8)).width - 16f, CalculateAvailableScrollHeight(num4));
		Widgets.BeginScrollView(val8, ref scrollPositionGenes, val9, true);
		float num5 = 0f;
		Widgets.Label(new Rect(0f, num5, ((Rect)(ref val9)).width, 24f), ColoredText.Colorize("Available to Incorporate:", ColoredText.TipSectionTitleColor));
		num5 += 28f;
		Rect val11 = default(Rect);
		for (int i = 0; i < filteredGenes.Count; i++)
		{
			GeneDef val10 = filteredGenes[i];
			int num6 = i / num4;
			int num7 = i % num4;
			((Rect)(ref val11))._002Ector((float)num7 * 91f, num5 + (float)num6 * 72f, 87f, 68f);
			if (selectedGene == val10)
			{
				Widgets.DrawHighlightSelected(val11);
			}
			if (Widgets.ButtonInvisible(val11, true))
			{
				selectedGene = val10;
				scrollPositionDetails = Vector2.zero;
			}
			GeneUIUtility.DrawGeneDef(val10, val11, (GeneType)1, (Func<string>)null, true, true, false);
		}
		Widgets.EndScrollView();
		Rect val12 = default(Rect);
		((Rect)(ref val12))._002Ector(((Rect)(ref val6)).x, ((Rect)(ref val7)).yMax + 8f, ((Rect)(ref val6)).width, 24f);
		Widgets.Label(val12, ColoredText.Colorize(((Entity)caster).LabelShortCap + "'s genes:", ColoredText.TipSectionTitleColor));
		Rect val13 = new Rect(((Rect)(ref val6)).x, ((Rect)(ref val12)).yMax, ((Rect)(ref val6)).width, ((Rect)(ref val6)).height - ((Rect)(ref val7)).height - 32f);
		Widgets.DrawMenuSection(val13);
		Rect val14 = GenUI.ContractedBy(val13, 4f);
		int num8 = Mathf.FloorToInt((((Rect)(ref val14)).width - 16f - 4f) / 91f);
		if (num8 <= 0)
		{
			num8 = 1;
		}
		Rect val15 = default(Rect);
		((Rect)(ref val15))._002Ector(0f, 0f, ((Rect)(ref val14)).width - 16f, CalculateCasterScrollHeight(num8));
		Widgets.BeginScrollView(val14, ref scrollPositionCaster, val15, true);
		num5 = 0f;
		Rect val16 = default(Rect);
		for (int j = 0; j < casterEndogenes.Count; j++)
		{
			int num9 = j / num8;
			int num10 = j % num8;
			((Rect)(ref val16))._002Ector((float)num10 * 91f, num5 + (float)num9 * 72f, 87f, 68f);
			GeneUIUtility.DrawGeneDef(casterEndogenes[j].def, val16, (GeneType)0, (Func<string>)null, true, false, casterEndogenes[j].Overridden);
		}
		if (casterEndogenes.Count > 0 && casterXenogenes.Count > 0)
		{
			num5 += (float)Mathf.CeilToInt((float)casterEndogenes.Count / (float)num8) * 72f + 4f;
			Widgets.DrawLineHorizontal(4f, num5, ((Rect)(ref val15)).width - 8f);
			num5 += 8f;
		}
		Rect val17 = default(Rect);
		for (int k = 0; k < casterXenogenes.Count; k++)
		{
			int num11 = k / num8;
			int num12 = k % num8;
			((Rect)(ref val17))._002Ector((float)num12 * 91f, num5 + (float)num11 * 72f, 87f, 68f);
			GeneUIUtility.DrawGeneDef(casterXenogenes[k].def, val17, (GeneType)1, (Func<string>)null, true, false, casterXenogenes[k].Overridden);
		}
		Widgets.EndScrollView();
		if (selectedGene != null)
		{
			Widgets.DrawMenuSection(val5);
			Rect val18 = GenUI.ContractedBy(val5, 12f);
			float y = ((Rect)(ref val18)).y;
			Text.Font = (GameFont)2;
			Widgets.Label(new Rect(((Rect)(ref val18)).x, y, ((Rect)(ref val18)).width, 30f), ((Def)selectedGene).LabelCap);
			y += 35f;
			Text.Font = (GameFont)1;
			float num13 = BiostatsTable.HeightForBiostats(selectedGene.biostatArc);
			BiostatsTable.Draw(new Rect(((Rect)(ref val18)).x, y, ((Rect)(ref val18)).width, num13), selectedGene.biostatCpx, selectedGene.biostatMet, selectedGene.biostatArc, false, false, -1);
			y += num13 + 10f;
			Widgets.DrawLineHorizontal(((Rect)(ref val18)).x, y, ((Rect)(ref val18)).width);
			y += 10f;
			Rect val19 = default(Rect);
			((Rect)(ref val19))._002Ector(((Rect)(ref val18)).x, y, ((Rect)(ref val18)).width, ((Rect)(ref val18)).height - (y - ((Rect)(ref val18)).y));
			string descriptionFull = selectedGene.DescriptionFull;
			float num14 = Text.CalcHeight(descriptionFull, ((Rect)(ref val19)).width - 16f);
			Rect val20 = default(Rect);
			((Rect)(ref val20))._002Ector(0f, 0f, ((Rect)(ref val19)).width - 16f, num14);
			Widgets.BeginScrollView(val19, ref scrollPositionDetails, val20, true);
			Widgets.Label(new Rect(0f, 0f, ((Rect)(ref val20)).width, num14), descriptionFull);
			Widgets.EndScrollView();
		}
		Rect val21 = default(Rect);
		((Rect)(ref val21))._002Ector(0f, ((Rect)(ref inRect)).height - 100f, ((Rect)(ref inRect)).width, 100f);
		Widgets.DrawLineHorizontal(0f, ((Rect)(ref val21)).y, ((Rect)(ref inRect)).width);
		int num15 = caster.genes.GenesListForReading.Where((Gene x) => !x.Overridden).Sum((Gene x) => x.def.biostatMet);
		int num16 = num15;
		if (selectedGene != null)
		{
			num16 += selectedGene.biostatMet;
		}
		Rect val22 = default(Rect);
		((Rect)(ref val22))._002Ector(10f, ((Rect)(ref val21)).y + 6f, ((Rect)(ref inRect)).width - 20f, 24f);
		string text = $"Current Metabolic Efficiency: {num15}";
		int num17 = -9;
		if (selectedGene != null)
		{
			string arg = ((num16 < num17) ? "red" : "cyan");
			text += $" -> <color={arg}>{num16}</color> (Min: {num17})";
		}
		else
		{
			text += $" (Min: {num17})";
		}
		Widgets.Label(val22, text);
		if (num16 < num17)
		{
			Rect val23 = new Rect(10f, ((Rect)(ref val22)).yMax - 2f, ((Rect)(ref inRect)).width - 20f, 20f);
			GUI.color = ColorLibrary.RedReadable;
			Widgets.Label(val23, "Warning: Metabolism will be too low. Random genes will be removed!");
			GUI.color = Color.white;
		}
		float num18 = ((Rect)(ref inRect)).height - 40f;
		if (Widgets.ButtonText(new Rect(((Rect)(ref inRect)).width / 2f - 160f, num18, 150f, 38f), "Cancel", true, true, true, (TextAnchor?)null))
		{
			((Window)this).Close(true);
		}
		if (Widgets.ButtonText(new Rect(((Rect)(ref inRect)).width / 2f + 10f, num18, 150f, 38f), "Incorporate Gene", true, true, true, (TextAnchor?)null))
		{
			Accept();
		}
	}

	private float CalculateAvailableScrollHeight(int cols)
	{
		if (filteredGenes.Count == 0)
		{
			return 30f;
		}
		float num = 68f;
		float num2 = 4f;
		return 28f + (float)Mathf.CeilToInt((float)filteredGenes.Count / (float)cols) * (num + num2);
	}

	private float CalculateCasterScrollHeight(int cols)
	{
		float num = 68f;
		float num2 = 4f;
		float num3 = 0f;
		if (casterEndogenes.Count > 0)
		{
			num3 += (float)Mathf.CeilToInt((float)casterEndogenes.Count / (float)cols) * (num + num2);
		}
		if (casterEndogenes.Count > 0 && casterXenogenes.Count > 0)
		{
			num3 += 12f;
		}
		if (casterXenogenes.Count > 0)
		{
			num3 += (float)Mathf.CeilToInt((float)casterXenogenes.Count / (float)cols) * (num + num2);
		}
		return Mathf.Max(num3, 40f);
	}

	public override void PostClose()
	{
		//IL_0006: Unknown result type (might be due to invalid IL or missing references)
		//IL_000b: Unknown result type (might be due to invalid IL or missing references)
		lastWindowSize = ((Rect)(ref base.windowRect)).size;
		((Window)this).PostClose();
	}

	private void Accept()
	{
		if (selectedGene != null)
		{
			GainGene(caster, selectedGene);
			HumanoidPawnScaler.GetInvalidateLater(caster);
			((Window)this).Close(true);
		}
	}

	public static void GainGene(Pawn pawn, GeneDef gene)
	{
		//IL_00f9: Unknown result type (might be due to invalid IL or missing references)
		//IL_012d: Unknown result type (might be due to invalid IL or missing references)
		if (BodyShapeGeneNames.Contains(((Def)gene).defName))
		{
			foreach (Gene item in pawn.genes.GenesListForReading.Where((Gene x) => BodyShapeGeneNames.Contains(((Def)x.def).defName)))
			{
				pawn.genes.RemoveGene(item);
			}
		}
		if (ForcedGenderGenes.Contains(((Def)gene).defName))
		{
			foreach (Gene item2 in pawn.genes.GenesListForReading.Where((Gene x) => ForcedGenderGenes.Contains(((Def)x.def).defName)))
			{
				pawn.genes.RemoveGene(item2);
			}
		}
		if (gene.skinColorOverride.HasValue)
		{
			pawn.story.SkinColorBase = gene.skinColorOverride.Value;
			pawn.story.skinColorOverride = gene.skinColorOverride;
		}
		if (gene.hairColorOverride.HasValue)
		{
			pawn.story.HairColor = gene.hairColorOverride.Value;
		}
		pawn.genes.AddGene(gene, true);
	}
}
