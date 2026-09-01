using System;
using System.Collections.Generic;
using System.Linq;
using BigAndSmall.Debugging;
using RimWorld;
using UnityEngine;
using Verse;

namespace BigAndSmall;

public static class RaceViewUIManager
{
	private static readonly List<GeneDef> geneDefs = new List<GeneDef>();

	private static readonly List<IRacialFeature> racialFeatures = new List<IRacialFeature>();

	private static readonly List<HediffDef> displayedHediffs = new List<HediffDef>();

	private static readonly List<Gene> xenogenes = new List<Gene>();

	private static readonly List<Gene> endogenes = new List<Gene>();

	private static float genesHeight;

	private static float racialHeight;

	private static float scrollHeight;

	private static int gcx;

	private static int met;

	private static int arc;

	private static readonly CachedTexture RaceBackground_Bio = new CachedTexture("GeneIcons/BS_BackRaceBio");

	private static readonly CachedTexture RaceBackground_Mech = new CachedTexture("GeneIcons/BS_BackRaceMech");

	private const float OverriddenGeneIconAlpha = 0.75f;

	private const float XenogermIconSize = 34f;

	private const float XenotypeLabelWidth = 140f;

	private const float GeneGap = 6f;

	private const float GeneSize = 90f;

	public const float BiostatsWidth = 38f;

	public static float BiostatsHeight()
	{
		return Text.LineHeight * 3f;
	}

	public static void DrawRacialInfo(Rect rect, Thing target, float initialHeight, ref Vector2 size, ref Vector2 scrollPosition, GeneSet pregnancyGenes = null)
	{
		//IL_0007: Unknown result type (might be due to invalid IL or missing references)
		//IL_0008: Unknown result type (might be due to invalid IL or missing references)
		//IL_0009: Unknown result type (might be due to invalid IL or missing references)
		//IL_000f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0014: Unknown result type (might be due to invalid IL or missing references)
		//IL_0088: Unknown result type (might be due to invalid IL or missing references)
		//IL_00bb: Unknown result type (might be due to invalid IL or missing references)
		//IL_0109: Unknown result type (might be due to invalid IL or missing references)
		//IL_010b: Unknown result type (might be due to invalid IL or missing references)
		//IL_006e: Unknown result type (might be due to invalid IL or missing references)
		//IL_016e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0174: Invalid comparison between Unknown and I4
		//IL_012a: Unknown result type (might be due to invalid IL or missing references)
		size.y = initialHeight;
		Rect val = rect;
		Rect val2 = GenUI.ContractedBy(val, 10f);
		if (Prefs.DevMode)
		{
			Rect buttonRect = default(Rect);
			((Rect)(ref buttonRect))._002Ector(((Rect)(ref val)).xMax - 18f - 125f, 5f, 115f, Text.LineHeight);
			if (ModsConfig.BiotechActive)
			{
				GeneUIUtility.DoDebugButton(new Rect(((Rect)(ref val)).xMax - 18f - 125f, 5f, 115f, Text.LineHeight), target, pregnancyGenes);
			}
			DebugUIPatches.DoGeneDebugButton(ref buttonRect, target);
		}
		GUI.BeginGroup(val2);
		float num = BiostatsHeight();
		Rect rect2 = default(Rect);
		((Rect)(ref rect2))._002Ector(0f, 0f, ((Rect)(ref val2)).width, ((Rect)(ref val2)).height - num - 12f);
		DrawFeatureSection(rect2, target, pregnancyGenes, ref scrollPosition);
		Rect val3 = default(Rect);
		((Rect)(ref val3))._002Ector(0f, ((Rect)(ref rect2)).yMax + 6f, ((Rect)(ref val2)).width - 140f - 4f, num);
		((Rect)(ref val3)).yMax = ((Rect)(ref rect2)).yMax + num + 6f;
		Rect val4 = val3;
		if (!(target is Pawn))
		{
			((Rect)(ref val4)).width = ((Rect)(ref val2)).width;
		}
		if (ModsConfig.BiotechActive)
		{
			BiostatsTable.Draw(val4, gcx, met, arc, false, false, -1);
			TryDrawXenotype(target, ((Rect)(ref val4)).xMax + 4f, ((Rect)(ref val4)).y + Text.LineHeight / 2f);
		}
		if ((int)Event.current.type == 8)
		{
			genesHeight = 0f;
			racialHeight = 0f;
		}
		GUI.EndGroup();
	}

	private static void DrawFeatureSection(Rect rect, Thing target, GeneSet genesOverride, ref Vector2 scrollPosition)
	{
		//IL_000d: Unknown result type (might be due to invalid IL or missing references)
		//IL_003c: Unknown result type (might be due to invalid IL or missing references)
		//IL_003d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0043: Unknown result type (might be due to invalid IL or missing references)
		//IL_004a: Unknown result type (might be due to invalid IL or missing references)
		//IL_004b: Unknown result type (might be due to invalid IL or missing references)
		//IL_01db: Unknown result type (might be due to invalid IL or missing references)
		//IL_01e1: Invalid comparison between Unknown and I4
		//IL_01a2: Unknown result type (might be due to invalid IL or missing references)
		//IL_01a7: Unknown result type (might be due to invalid IL or missing references)
		//IL_01aa: Unknown result type (might be due to invalid IL or missing references)
		//IL_01b0: Invalid comparison between Unknown and I4
		//IL_01d0: Unknown result type (might be due to invalid IL or missing references)
		//IL_00fa: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b9: Unknown result type (might be due to invalid IL or missing references)
		//IL_00de: Unknown result type (might be due to invalid IL or missing references)
		//IL_0149: Unknown result type (might be due to invalid IL or missing references)
		//IL_012c: Unknown result type (might be due to invalid IL or missing references)
		//IL_017b: Unknown result type (might be due to invalid IL or missing references)
		RecacheEntries(target, genesOverride);
		GUI.BeginGroup(rect);
		Rect val = default(Rect);
		((Rect)(ref val))._002Ector(0f, 0f, ((Rect)(ref rect)).width - 16f, scrollHeight);
		float curY = 0f;
		Widgets.BeginScrollView(GenUI.AtZero(rect), ref scrollPosition, val, true);
		Rect val2 = val;
		((Rect)(ref val2)).y = scrollPosition.y;
		((Rect)(ref val2)).height = ((Rect)(ref rect)).height;
		Pawn val3 = (Pawn)(object)((target is Pawn) ? target : null);
		if (val3 != null)
		{
			BSCache cache = HumanoidPawnScaler.GetCache(val3);
			if (cache != null)
			{
				if (GenCollection.Any<IRacialFeature>(racialFeatures))
				{
					string title = (cache.isMechanical ? "BS_RacialFeatures_Mech" : "BS_RacialFeatures");
					DrawSection(rect, title, "BS_RacialFeatureDescription", racialFeatures.Count, ref curY, ref racialHeight, delegate(int i, Rect r)
					{
						//IL_0011: Unknown result type (might be due to invalid IL or missing references)
						DrawFeature(racialFeatures[i], cache, r);
					}, val2);
				}
				if (ModsConfig.BiotechActive)
				{
					if (GenCollection.Any<Gene>(endogenes))
					{
						GeneUIUtility.DrawSection(rect, false, endogenes.Count, ref curY, ref genesHeight, (Action<int, Rect>)delegate(int i, Rect r)
						{
							//IL_000b: Unknown result type (might be due to invalid IL or missing references)
							GeneUIUtility.DrawGene(endogenes[i], r, (GeneType)0, true, true);
						}, val2);
						curY += 12f;
					}
					if (GenCollection.Any<Gene>(xenogenes))
					{
						GeneUIUtility.DrawSection(rect, true, xenogenes.Count, ref curY, ref genesHeight, (Action<int, Rect>)delegate(int i, Rect r)
						{
							//IL_000b: Unknown result type (might be due to invalid IL or missing references)
							GeneUIUtility.DrawGene(xenogenes[i], r, (GeneType)1, true, true);
						}, val2);
					}
				}
				goto IL_01d6;
			}
		}
		if (ModsConfig.BiotechActive)
		{
			GeneType geneType = (GeneType)((genesOverride == null && !(target is HumanEmbryo)) ? 1 : 0);
			GeneUIUtility.DrawSection(rect, (int)geneType == 1, geneDefs.Count, ref curY, ref genesHeight, (Action<int, Rect>)delegate(int i, Rect r)
			{
				//IL_000b: Unknown result type (might be due to invalid IL or missing references)
				//IL_000d: Unknown result type (might be due to invalid IL or missing references)
				GeneUIUtility.DrawGeneDef(geneDefs[i], r, geneType, (Func<string>)null, true, true, false);
			}, val2);
		}
		goto IL_01d6;
		IL_01d6:
		if ((int)Event.current.type == 8)
		{
			scrollHeight = curY;
		}
		Widgets.EndScrollView();
		GUI.EndGroup();
	}

	private static void RecacheEntries(Thing target, GeneSet genesOverride)
	{
		//IL_023a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0240: Invalid comparison between Unknown and I4
		racialFeatures.Clear();
		geneDefs.Clear();
		xenogenes.Clear();
		endogenes.Clear();
		gcx = 0;
		met = 0;
		arc = 0;
		Pawn val = (Pawn)(object)((target is Pawn) ? target : null);
		if (val != null)
		{
			BSCache cache = HumanoidPawnScaler.GetCache(val);
			if (cache != null)
			{
				racialFeatures.AddDistinctRange(cache.racialFeatures);
				racialFeatures.AddDistinctRange(cache.racialFeaturesAuto);
				foreach (Hediff hediff in val.health.hediffSet.hediffs)
				{
					List<PawnExtension> allPawnExtensionsOnHediff = hediff.def.GetAllPawnExtensionsOnHediff();
					IEnumerable<PawnExtension> source = allPawnExtensionsOnHediff.Where((PawnExtension x) => x.traitIcon != null && x.fuseTag == null && x.featureInfo == null);
					if (!source.Any())
					{
						continue;
					}
					RacialFeature racialFeature = new RacialFeature
					{
						label = GenText.CapitalizeFirst(hediff.Label),
						description = hediff.Description,
						iconPath = source.First().traitIcon
					};
					try
					{
						allPawnExtensionsOnHediff.TryGetDescription(out var content);
						if (!string.IsNullOrEmpty(content))
						{
							racialFeature.description = racialFeature.description + "\n\n" + content;
						}
						racialFeatures.Add(racialFeature);
					}
					catch (Exception ex)
					{
						Log.ErrorOnce($"Failed to get PawnExt description{((Def)hediff.def).defName}: {ex} {ex.StackTrace}", 149782384);
					}
				}
				Thing obj = ((target is GeneSetHolderBase) ? target : null);
				GeneSet val2 = ((obj != null) ? ((GeneSetHolderBase)obj).GeneSet : null) ?? genesOverride;
				if (val.genes != null)
				{
					foreach (Gene xenogene in val.genes.Xenogenes)
					{
						if (!xenogene.Overridden)
						{
							AddBiostats(xenogene.def);
						}
						xenogenes.Add(xenogene);
					}
					foreach (Gene endogene in val.genes.Endogenes)
					{
						if ((int)endogene.def.endogeneCategory != 1 || !GenCollection.Any<Gene>(val.genes.Endogenes, (Predicate<Gene>)((Gene x) => x.def.skinColorOverride.HasValue)))
						{
							if (!endogene.Overridden)
							{
								AddBiostats(endogene.def);
							}
							endogenes.Add(endogene);
						}
					}
					GeneUtility.SortGenes(xenogenes);
					GeneUtility.SortGenes(endogenes);
				}
				else
				{
					if (val2 == null)
					{
						return;
					}
					foreach (GeneDef item in val2.GenesListForReading)
					{
						geneDefs.Add(item);
					}
					gcx = val2.ComplexityTotal;
					met = val2.MetabolismTotal;
					arc = val2.ArchitesTotal;
					GeneUtility.SortGeneDefs(geneDefs);
				}
			}
		}
		racialFeatures.Sort((IRacialFeature a, IRacialFeature b) => a.Label.CompareTo(b.Label));
		static void AddBiostats(GeneDef gene)
		{
			gcx += gene.biostatCpx;
			met += gene.biostatMet;
			arc += gene.biostatArc;
		}
	}

	private static void DrawSection(Rect rect, string title, string description, int count, ref float curY, ref float sectionHeight, Action<int, Rect> drawer, Rect containingRect)
	{
		//IL_000f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0014: Unknown result type (might be due to invalid IL or missing references)
		//IL_0018: Unknown result type (might be due to invalid IL or missing references)
		//IL_0023: Unknown result type (might be due to invalid IL or missing references)
		//IL_0028: Unknown result type (might be due to invalid IL or missing references)
		//IL_004a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0115: Unknown result type (might be due to invalid IL or missing references)
		//IL_011b: Invalid comparison between Unknown and I4
		//IL_00d5: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e2: Unknown result type (might be due to invalid IL or missing references)
		float width = ((Rect)(ref rect)).width;
		TaggedString val = Translator.Translate(title);
		Widgets.Label(10f, ref curY, width, TaggedString.op_Implicit(((TaggedString)(ref val)).CapitalizeFirst()), TipSignal.op_Implicit(Translator.Translate(description)));
		float num = curY;
		Widgets.DrawMenuSection(new Rect(((Rect)(ref rect)).x, curY, ((Rect)(ref rect)).width, sectionHeight));
		float num2 = (((Rect)(ref rect)).width - 12f - 630f - 36f) / 2f;
		curY += num2;
		int num3 = 0;
		int num4 = 0;
		Rect val2 = default(Rect);
		for (int i = 0; i < count; i++)
		{
			if (num4 >= 6)
			{
				num4 = 0;
				num3++;
			}
			else if (i > 0)
			{
				num4++;
			}
			((Rect)(ref val2))._002Ector(num2 + (float)num4 * 90f + (float)num4 * 6f, curY + (float)num3 * 90f + (float)num3 * 6f, 90f, 90f);
			if (((Rect)(ref containingRect)).Overlaps(val2))
			{
				drawer(i, val2);
			}
		}
		curY += (float)(num3 + 1) * 90f + (float)num3 * 6f + num2;
		if ((int)Event.current.type == 8)
		{
			sectionHeight = curY - num;
		}
	}

	private static void TryDrawXenotype(Thing target, float x, float y)
	{
		//IL_0041: Unknown result type (might be due to invalid IL or missing references)
		//IL_0061: Unknown result type (might be due to invalid IL or missing references)
		//IL_008d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0097: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ad: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c5: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ea: Unknown result type (might be due to invalid IL or missing references)
		//IL_00cd: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d3: Unknown result type (might be due to invalid IL or missing references)
		//IL_011b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0125: Expected O, but got Unknown
		Pawn sourcePawn = (Pawn)(object)((target is Pawn) ? target : null);
		if (sourcePawn == null || sourcePawn.genes == null)
		{
			return;
		}
		Rect val = default(Rect);
		((Rect)(ref val))._002Ector(x, y, 140f, Text.LineHeight);
		Text.Anchor = (TextAnchor)1;
		Widgets.Label(val, sourcePawn.genes.XenotypeLabelCap);
		Text.Anchor = (TextAnchor)0;
		Rect val2 = default(Rect);
		((Rect)(ref val2))._002Ector(((Rect)(ref val)).center.x - 17f, ((Rect)(ref val)).yMax + 4f, 34f, 34f);
		GUI.color = XenotypeDef.IconColor;
		GUI.DrawTexture(val2, (Texture)(object)sourcePawn.genes.XenotypeIcon);
		GUI.color = Color.white;
		((Rect)(ref val)).yMax = ((Rect)(ref val2)).yMax;
		if (Mouse.IsOver(val))
		{
			Widgets.DrawHighlight(val);
			TooltipHandler.TipRegion(val, (Func<string>)(() => ColoredText.Colorize(Translator.Translate("Xenotype") + ": " + sourcePawn.genes.XenotypeLabelCap, ColoredText.TipSectionTitleColor) + "\n\n" + sourcePawn.genes.XenotypeDescShort), 883938493);
		}
		if (Widgets.ButtonInvisible(val, true) && !sourcePawn.genes.UniqueXenotype)
		{
			Find.WindowStack.Add((Window)new Dialog_InfoCard((Def)(object)sourcePawn.genes.Xenotype, (Precept_ThingStyle)null));
		}
	}

	/// <summary>
	/// Draw Race Feature
	/// </summary>
	public static void DrawFeature(IRacialFeature iRF, BSCache cache, Rect featureRect, bool doBackground = true, bool clickable = true)
	{
		//IL_0002: Unknown result type (might be due to invalid IL or missing references)
		//IL_000c: Unknown result type (might be due to invalid IL or missing references)
		//IL_001f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0045: Unknown result type (might be due to invalid IL or missing references)
		//IL_004a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0058: Unknown result type (might be due to invalid IL or missing references)
		//IL_0068: Unknown result type (might be due to invalid IL or missing references)
		//IL_006a: Unknown result type (might be due to invalid IL or missing references)
		DrawFeatureBasics(iRF, cache, featureRect, doBackground, clickable, overridden: false);
		if (Mouse.IsOver(featureRect))
		{
			string text = ColoredText.Colorize(GenText.CapitalizeFirst(iRF.Label), ColoredText.TipSectionTitleColor) + "\n\n" + iRF.DescriptionFull;
			string text2 = text;
			TaggedString val = Translator.Translate("ClickForMoreInfo");
			text = text2 + "\n" + ColoredText.Colorize(((object)(TaggedString)(ref val)/*cast due to .constrained prefix*/).ToString(), ColoredText.SubtleGrayColor);
			TooltipHandler.TipRegion(featureRect, TipSignal.op_Implicit(text));
		}
	}

	public static void FeatureDefIcon(Rect rect, IRacialFeature iRF, float scale = 1f, Color? color = null, Material material = null)
	{
		//IL_0015: Unknown result type (might be due to invalid IL or missing references)
		//IL_000c: Unknown result type (might be due to invalid IL or missing references)
		//IL_001f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0033: Unknown result type (might be due to invalid IL or missing references)
		GUI.color = (Color)(((_003F?)color) ?? iRF.IconColor);
		Widgets.DrawTextureFitted(rect, (Texture)(object)iRF.Icon, scale, material, 1f);
		GUI.color = Color.white;
	}

	private static void DrawFeatureBasics(IRacialFeature iRF, BSCache cache, Rect featureRect, bool doBackground, bool clickable, bool overridden)
	{
		//IL_0000: Unknown result type (might be due to invalid IL or missing references)
		//IL_0006: Unknown result type (might be due to invalid IL or missing references)
		//IL_0007: Unknown result type (might be due to invalid IL or missing references)
		//IL_000c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0070: Unknown result type (might be due to invalid IL or missing references)
		//IL_0076: Unknown result type (might be due to invalid IL or missing references)
		//IL_007b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0010: Unknown result type (might be due to invalid IL or missing references)
		//IL_002a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0034: Unknown result type (might be due to invalid IL or missing references)
		//IL_003c: Unknown result type (might be due to invalid IL or missing references)
		//IL_008c: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ab: Unknown result type (might be due to invalid IL or missing references)
		//IL_00bd: Unknown result type (might be due to invalid IL or missing references)
		//IL_011c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0135: Unknown result type (might be due to invalid IL or missing references)
		//IL_016a: Unknown result type (might be due to invalid IL or missing references)
		//IL_017c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0196: Unknown result type (might be due to invalid IL or missing references)
		//IL_01bd: Unknown result type (might be due to invalid IL or missing references)
		//IL_01c5: Unknown result type (might be due to invalid IL or missing references)
		//IL_01b3: Unknown result type (might be due to invalid IL or missing references)
		//IL_01bd: Expected O, but got Unknown
		GUI.BeginGroup(featureRect);
		Rect val = GenUI.AtZero(featureRect);
		if (doBackground)
		{
			Widgets.DrawHighlight(val);
			GUI.color = new Color(1f, 1f, 1f, 0.05f);
			Widgets.DrawBox(val, 1, (Texture2D)null);
			GUI.color = Color.white;
		}
		float num = ((Rect)(ref val)).width - Text.LineHeight;
		Rect val2 = new Rect(((Rect)(ref featureRect)).width / 2f - num / 2f, 0f, num, num);
		Color iconColor = iRF.IconColor;
		if (overridden)
		{
			iconColor.a = 0.75f;
			GUI.color = ColoredText.SubtleGrayColor;
		}
		CachedTexture val3 = (cache.isMechanical ? RaceBackground_Mech : RaceBackground_Bio);
		GUI.DrawTexture(val2, (Texture)(object)val3.Texture);
		FeatureDefIcon(val2, iRF, 0.9f, iconColor);
		Text.Font = (GameFont)0;
		float num2 = Text.CalcHeight(iRF.Label, ((Rect)(ref val)).width);
		Rect val4 = default(Rect);
		((Rect)(ref val4))._002Ector(0f, ((Rect)(ref val)).yMax - num2, ((Rect)(ref val)).width, num2);
		GUI.DrawTexture(new Rect(((Rect)(ref val4)).x, ((Rect)(ref val4)).yMax - num2, ((Rect)(ref val4)).width, num2), (Texture)(object)TexUI.GrayTextBG);
		Text.Anchor = (TextAnchor)7;
		if (overridden)
		{
			GUI.color = ColoredText.SubtleGrayColor;
		}
		if (doBackground && num2 < (Text.LineHeight - 2f) * 2f)
		{
			((Rect)(ref val4)).y = ((Rect)(ref val4)).y - 3f;
		}
		Widgets.Label(val4, GenText.CapitalizeFirst(iRF.Label));
		GUI.color = Color.white;
		Text.Anchor = (TextAnchor)0;
		Text.Font = (GameFont)1;
		if (clickable)
		{
			if (Widgets.ButtonInvisible(val, true) && iRF is RacialFeatureDef racialFeatureDef)
			{
				Find.WindowStack.Add((Window)new Dialog_InfoCard((Def)(object)racialFeatureDef, (Precept_ThingStyle)null));
			}
			if (Mouse.IsOver(val))
			{
				Widgets.DrawHighlight(val);
			}
		}
		GUI.EndGroup();
	}

	private static void DrawStat(Rect iconRect, CachedTexture icon, string stat, float iconWidth)
	{
		//IL_0000: Unknown result type (might be due to invalid IL or missing references)
		//IL_0028: Unknown result type (might be due to invalid IL or missing references)
		GUI.DrawTexture(iconRect, (Texture)(object)icon.Texture);
		Text.Anchor = (TextAnchor)5;
		Widgets.LabelFit(new Rect(((Rect)(ref iconRect)).xMax, ((Rect)(ref iconRect)).y, 38f - iconWidth, iconWidth), stat);
		Text.Anchor = (TextAnchor)0;
	}

	public static void DrawBiostats(int gcx, int met, int arc, ref float curX, float curY, float margin = 6f)
	{
		//IL_0030: Unknown result type (might be due to invalid IL or missing references)
		//IL_0059: Unknown result type (might be due to invalid IL or missing references)
		//IL_0062: Unknown result type (might be due to invalid IL or missing references)
		//IL_0069: Unknown result type (might be due to invalid IL or missing references)
		//IL_0070: Unknown result type (might be due to invalid IL or missing references)
		//IL_0075: Unknown result type (might be due to invalid IL or missing references)
		//IL_0079: Unknown result type (might be due to invalid IL or missing references)
		//IL_007e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0097: Unknown result type (might be due to invalid IL or missing references)
		//IL_009c: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a1: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c7: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f0: Unknown result type (might be due to invalid IL or missing references)
		//IL_015f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0189: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f9: Unknown result type (might be due to invalid IL or missing references)
		//IL_0100: Unknown result type (might be due to invalid IL or missing references)
		//IL_0107: Unknown result type (might be due to invalid IL or missing references)
		//IL_010c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0110: Unknown result type (might be due to invalid IL or missing references)
		//IL_0115: Unknown result type (might be due to invalid IL or missing references)
		//IL_012e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0133: Unknown result type (might be due to invalid IL or missing references)
		//IL_0138: Unknown result type (might be due to invalid IL or missing references)
		//IL_0192: Unknown result type (might be due to invalid IL or missing references)
		//IL_0199: Unknown result type (might be due to invalid IL or missing references)
		//IL_01a0: Unknown result type (might be due to invalid IL or missing references)
		//IL_01a5: Unknown result type (might be due to invalid IL or missing references)
		//IL_01a9: Unknown result type (might be due to invalid IL or missing references)
		//IL_01ae: Unknown result type (might be due to invalid IL or missing references)
		//IL_01c7: Unknown result type (might be due to invalid IL or missing references)
		//IL_01cc: Unknown result type (might be due to invalid IL or missing references)
		//IL_01d1: Unknown result type (might be due to invalid IL or missing references)
		float num = GeneCreationDialogBase.GeneSize.y / 3f;
		float num2 = 0f;
		float num3 = Text.LineHeightOf((GameFont)1);
		Rect iconRect = default(Rect);
		((Rect)(ref iconRect))._002Ector(curX, curY + margin + num2, num3, num3);
		DrawStat(iconRect, GeneUtility.GCXTex, gcx.ToString(), num3);
		Rect val = default(Rect);
		((Rect)(ref val))._002Ector(curX, ((Rect)(ref iconRect)).y, 38f, num3);
		TaggedString val3;
		if (Mouse.IsOver(val))
		{
			Widgets.DrawHighlight(val);
			Rect val2 = val;
			val3 = Translator.Translate("Complexity");
			TooltipHandler.TipRegion(val2, TipSignal.op_Implicit(ColoredText.Colorize(((TaggedString)(ref val3)).CapitalizeFirst(), ColoredText.TipSectionTitleColor) + "\n\n" + Translator.Translate("ComplexityDesc")));
		}
		num2 += num;
		if (met != 0)
		{
			Rect iconRect2 = default(Rect);
			((Rect)(ref iconRect2))._002Ector(curX, curY + margin + num2, num3, num3);
			DrawStat(iconRect2, GeneUtility.METTex, GenText.ToStringWithSign(met), num3);
			Rect val4 = default(Rect);
			((Rect)(ref val4))._002Ector(curX, ((Rect)(ref iconRect2)).y, 38f, num3);
			if (Mouse.IsOver(val4))
			{
				Widgets.DrawHighlight(val4);
				Rect val5 = val4;
				val3 = Translator.Translate("Metabolism");
				TooltipHandler.TipRegion(val5, TipSignal.op_Implicit(ColoredText.Colorize(((TaggedString)(ref val3)).CapitalizeFirst(), ColoredText.TipSectionTitleColor) + "\n\n" + Translator.Translate("MetabolismDesc")));
			}
			num2 += num;
		}
		if (arc > 0)
		{
			Rect iconRect3 = default(Rect);
			((Rect)(ref iconRect3))._002Ector(curX, curY + margin + num2, num3, num3);
			DrawStat(iconRect3, GeneUtility.ARCTex, arc.ToString(), num3);
			Rect val6 = default(Rect);
			((Rect)(ref val6))._002Ector(curX, ((Rect)(ref iconRect3)).y, 38f, num3);
			if (Mouse.IsOver(val6))
			{
				Widgets.DrawHighlight(val6);
				Rect val7 = val6;
				val3 = Translator.Translate("ArchitesRequired");
				TooltipHandler.TipRegion(val7, TipSignal.op_Implicit(ColoredText.Colorize(((TaggedString)(ref val3)).CapitalizeFirst(), ColoredText.TipSectionTitleColor) + "\n\n" + Translator.Translate("ArchitesRequiredDesc")));
			}
		}
		curX += 34f;
	}
}
