using System;
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace VEF.Graphics;

[HotSwappable]
[StaticConstructorOnStartup]
public class Dialog_GraphicCustomization : Window
{
	public static Texture2D RandomizeIcon = ContentFinder<Texture2D>.Get("UI/Widgets/RandomizeIcon", true);

	public CompGraphicCustomization comp;

	public Texture currentTexture;

	public List<TextureVariant> currentVariants;

	public string currentName;

	public CompGeneratedNames compGeneratedName;

	public Pawn pawn;

	public static Vector2 scrollPosition = Vector2.zero;

	public override Vector2 InitialSize => new Vector2(700f, 500f);

	public Dialog_GraphicCustomization(CompGraphicCustomization comp, Pawn pawn = null)
		: base((IWindowDrawing)null)
	{
		Init(comp);
		this.pawn = pawn;
		base.forcePause = true;
	}

	public void Init(CompGraphicCustomization comp)
	{
		this.comp = comp;
		comp.TryInit();
		currentVariants = comp.texVariants;
		UpdateTexture();
		compGeneratedName = ((ThingComp)this.comp).parent.GetComp<CompGeneratedNames>();
		if (compGeneratedName != null)
		{
			currentName = compGeneratedName.Name;
		}
	}

	private void UpdateTexture()
	{
		List<string> texPaths = comp.GetTexPaths(currentVariants);
		currentTexture = (Texture)(object)comp.GetCombinedTexture(texPaths);
	}

	public override void DoWindowContents(Rect inRect)
	{
		//IL_0003: Unknown result type (might be due to invalid IL or missing references)
		//IL_0008: Unknown result type (might be due to invalid IL or missing references)
		//IL_0080: Unknown result type (might be due to invalid IL or missing references)
		//IL_0087: Unknown result type (might be due to invalid IL or missing references)
		//IL_008d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0095: Unknown result type (might be due to invalid IL or missing references)
		//IL_00cb: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d5: Unknown result type (might be due to invalid IL or missing references)
		//IL_012c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0133: Unknown result type (might be due to invalid IL or missing references)
		Rect val = DrawTitle(ref inRect);
		float scrollHeight = GetScrollHeight();
		Rect val2 = default(Rect);
		((Rect)(ref val2))._002Ector(((Rect)(ref inRect)).x, ((Rect)(ref val)).yMax + 30f, ((Rect)(ref inRect)).width, 350f);
		Rect val3 = default(Rect);
		((Rect)(ref val3))._002Ector(((Rect)(ref inRect)).x, ((Rect)(ref val2)).y, ((Rect)(ref inRect)).width - 16f, scrollHeight);
		Rect itemTextureRect = default(Rect);
		((Rect)(ref itemTextureRect))._002Ector(((Rect)(ref inRect)).x + 10f, ((Rect)(ref val3)).y, 250f, 250f);
		DrawItem(itemTextureRect);
		Widgets.BeginScrollView(val2, ref scrollPosition, val3, true);
		DrawCustomizationArea(itemTextureRect);
		Widgets.EndScrollView();
		if (Widgets.ButtonText(new Rect(((Rect)(ref inRect)).width / 2f - 155f, ((Rect)(ref inRect)).height - 32f, 150f, 32f), TaggedString.op_Implicit(Translator.Translate("VEF.Cancel")), true, true, true, (TextAnchor?)null))
		{
			((Window)this).Close(true);
		}
		Rect confirmRect = default(Rect);
		((Rect)(ref confirmRect))._002Ector(((Rect)(ref inRect)).width / 2f + 5f, ((Rect)(ref inRect)).height - 32f, 150f, 32f);
		DrawConfirmButton(confirmRect, TaggedString.op_Implicit(Translator.Translate("Confirm")), delegate
		{
			//IL_004b: Unknown result type (might be due to invalid IL or missing references)
			comp.texVariantsToCustomize = currentVariants;
			if (compGeneratedName != null)
			{
				ReflectionCache.compGeneratedNamesName.Invoke(compGeneratedName) = currentName;
			}
			pawn.jobs.TryTakeOrderedJob(JobMaker.MakeJob(GraphicCustomization_DefOf.VEF_CustomizeItem, LocalTargetInfo.op_Implicit((Thing)(object)((ThingComp)comp).parent)), (JobTag?)(JobTag)0, false);
			((Window)this).Close(true);
		});
	}

	protected void DrawItem(Rect itemTextureRect)
	{
		//IL_0000: Unknown result type (might be due to invalid IL or missing references)
		//IL_0011: Unknown result type (might be due to invalid IL or missing references)
		//IL_001b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0021: Unknown result type (might be due to invalid IL or missing references)
		//IL_0031: Unknown result type (might be due to invalid IL or missing references)
		//IL_008a: Unknown result type (might be due to invalid IL or missing references)
		Widgets.DrawMenuSection(itemTextureRect);
		GUI.color = ((Thing)((ThingComp)comp).parent).DrawColor;
		GUI.DrawTexture(GenUI.ContractedBy(itemTextureRect, 15f), currentTexture);
		GUI.color = Color.white;
		Widgets.InfoCardButton(((Rect)(ref itemTextureRect)).xMax - 60f, ((Rect)(ref itemTextureRect)).yMax - 30f, (Thing)(object)((ThingComp)comp).parent);
		if (Widgets.ButtonImage(new Rect(((Rect)(ref itemTextureRect)).xMax - 30f, ((Rect)(ref itemTextureRect)).yMax - 30f, 24f, 24f), RandomizeIcon, true, (string)null))
		{
			Randomize();
		}
	}

	public Rect DrawTitle(ref Rect inRect)
	{
		//IL_0017: Unknown result type (might be due to invalid IL or missing references)
		//IL_0028: Unknown result type (might be due to invalid IL or missing references)
		//IL_0052: Unknown result type (might be due to invalid IL or missing references)
		//IL_0057: Unknown result type (might be due to invalid IL or missing references)
		Rect val = new Rect(((Rect)(ref inRect)).x, ((Rect)(ref inRect)).y, ((Rect)(ref inRect)).width, 40f);
		Text.Font = (GameFont)2;
		Text.Anchor = (TextAnchor)4;
		Widgets.Label(val, comp.Props.customizationTitle ?? TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("VEF.CustomizationTitle", NamedArgument.op_Implicit(((Thing)((ThingComp)comp).parent).LabelCapNoCount))));
		Text.Font = (GameFont)1;
		Text.Anchor = (TextAnchor)0;
		return val;
	}

	public void DrawConfirmButton(Rect confirmRect, string confirmLabel, Action action)
	{
		//IL_0000: Unknown result type (might be due to invalid IL or missing references)
		if (Widgets.ButtonText(confirmRect, confirmLabel, true, true, true, (TextAnchor?)null))
		{
			action();
		}
	}

	protected virtual void DrawCustomizationArea(Rect itemTextureRect)
	{
		//IL_0028: Unknown result type (might be due to invalid IL or missing references)
		//IL_002e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0049: Unknown result type (might be due to invalid IL or missing references)
		//IL_004f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0059: Unknown result type (might be due to invalid IL or missing references)
		//IL_0093: Unknown result type (might be due to invalid IL or missing references)
		//IL_00fc: Unknown result type (might be due to invalid IL or missing references)
		//IL_0102: Unknown result type (might be due to invalid IL or missing references)
		//IL_0112: Unknown result type (might be due to invalid IL or missing references)
		//IL_0149: Unknown result type (might be due to invalid IL or missing references)
		//IL_014f: Unknown result type (might be due to invalid IL or missing references)
		//IL_01d6: Unknown result type (might be due to invalid IL or missing references)
		Vector2 val = default(Vector2);
		((Vector2)(ref val))._002Ector(((Rect)(ref itemTextureRect)).xMax + 25f, ((Rect)(ref itemTextureRect)).y);
		if (compGeneratedName != null)
		{
			Rect val2 = default(Rect);
			((Rect)(ref val2))._002Ector(val.x, val.y - 3f, 350f, 25f);
			Widgets.Label(val2, Translator.Translate("VEF.Name") + ": ");
			val.y += 25f;
			Rect val3 = default(Rect);
			((Rect)(ref val3))._002Ector(((Rect)(ref val2)).x, ((Rect)(ref val2)).yMax, 350f, 32f);
			currentName = Widgets.TextField(val3, currentName);
			val.y += 40f;
		}
		Rect floatMenuButtonsRect = default(Rect);
		foreach (GraphicPart graphicPart in comp.Props.graphics)
		{
			Widgets.Label(new Rect(val.x, val.y, 350f, 25f), graphicPart.name + ": ");
			val.y += 25f;
			((Rect)(ref floatMenuButtonsRect))._002Ector(val.x, val.y, 350f, 32f);
			TextureVariant graphicPartVariant = graphicPart.texVariants.First((TextureVariant x) => currentVariants.Contains(x));
			TextureVariant currentVariant = currentVariants.First((TextureVariant x) => graphicPart.texVariants.Contains(x));
			int index = graphicPart.texVariants.IndexOf(graphicPartVariant);
			MakeFloatOptionButtons(floatMenuButtonsRect, delegate
			{
				if (index > 0)
				{
					index--;
				}
				else
				{
					index = graphicPart.texVariants.Count - 1;
				}
				graphicPartVariant = graphicPart.texVariants[index];
				GenCollection.Replace<TextureVariant>((IList<TextureVariant>)currentVariants, currentVariant, graphicPartVariant);
				UpdateTexture();
			}, delegate
			{
				FloatMenuUtility.MakeMenu<TextureVariant>((IEnumerable<TextureVariant>)graphicPart.texVariants, (Func<TextureVariant, string>)((TextureVariant entry) => entry.texName), (Func<TextureVariant, Action>)((TextureVariant variant) => delegate
				{
					GenCollection.Replace<TextureVariant>((IList<TextureVariant>)currentVariants, currentVariant, variant);
					UpdateTexture();
				}));
			}, graphicPartVariant.texName, delegate
			{
				if (index < graphicPart.texVariants.Count - 1)
				{
					index++;
				}
				else
				{
					index = 0;
				}
				graphicPartVariant = graphicPart.texVariants[index];
				GenCollection.Replace<TextureVariant>((IList<TextureVariant>)currentVariants, currentVariant, graphicPartVariant);
				UpdateTexture();
			});
			val.y += 45f;
		}
	}

	protected virtual void Randomize()
	{
		currentVariants = comp.GetRandomizedTexVariants();
		if (compGeneratedName != null)
		{
			currentName = CompGeneratedNames.GenerateName(compGeneratedName.Props);
		}
		List<string> texPaths = comp.GetTexPaths(currentVariants);
		currentTexture = (Texture)(object)comp.GetCombinedTexture(texPaths);
	}

	public void MakeFloatOptionButtons(Rect floatMenuButtonsRect, Action leftAction, Action centerAction, string centerButtonName, Action rightAction)
	{
		//IL_0000: Unknown result type (might be due to invalid IL or missing references)
		//IL_0043: Unknown result type (might be due to invalid IL or missing references)
		//IL_006e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0073: Unknown result type (might be due to invalid IL or missing references)
		//IL_007b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0081: Unknown result type (might be due to invalid IL or missing references)
		//IL_0093: Unknown result type (might be due to invalid IL or missing references)
		//IL_0099: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ae: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b4: Unknown result type (might be due to invalid IL or missing references)
		Widgets.DrawHighlight(floatMenuButtonsRect);
		Rect rect = default(Rect);
		((Rect)(ref rect))._002Ector(((Rect)(ref floatMenuButtonsRect)).x, ((Rect)(ref floatMenuButtonsRect)).y, 32f, 32f);
		Rect rect2 = new Rect(((Rect)(ref floatMenuButtonsRect)).xMax - 32f, ((Rect)(ref floatMenuButtonsRect)).y, 32f, 32f);
		Rect rect3 = new Rect(((Rect)(ref floatMenuButtonsRect)).x + 32f, ((Rect)(ref floatMenuButtonsRect)).y, ((Rect)(ref floatMenuButtonsRect)).width - 64f, 32f);
		if (ButtonTextSubtleCentered(rect, "<"))
		{
			leftAction();
		}
		if (ButtonTextSubtleCentered(rect3, centerButtonName))
		{
			centerAction();
		}
		if (ButtonTextSubtleCentered(rect2, ">"))
		{
			rightAction();
		}
	}

	public virtual float GetScrollHeight()
	{
		float num = 0f;
		if (((ThingComp)comp).parent.GetComp<CompGeneratedNames>() != null)
		{
			num += 70f;
		}
		foreach (GraphicPart graphic in comp.Props.graphics)
		{
			_ = graphic;
			num += 70f;
		}
		return num;
	}

	public static bool ButtonTextSubtleCentered(Rect rect, string label, Vector2 functionalSizeOffset = default(Vector2))
	{
		//IL_0000: Unknown result type (might be due to invalid IL or missing references)
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		//IL_000a: Unknown result type (might be due to invalid IL or missing references)
		//IL_001e: Unknown result type (might be due to invalid IL or missing references)
		//IL_002c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0040: Unknown result type (might be due to invalid IL or missing references)
		//IL_004b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0057: Unknown result type (might be due to invalid IL or missing references)
		//IL_0036: Unknown result type (might be due to invalid IL or missing references)
		//IL_0098: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ab: Unknown result type (might be due to invalid IL or missing references)
		Rect val = rect;
		((Rect)(ref val)).width = ((Rect)(ref val)).width + functionalSizeOffset.x;
		((Rect)(ref val)).height = ((Rect)(ref val)).height + functionalSizeOffset.y;
		bool flag = false;
		if (Mouse.IsOver(val))
		{
			flag = true;
			GUI.color = GenUI.MouseoverColor;
		}
		Widgets.DrawAtlas(rect, Widgets.ButtonSubtleAtlas);
		GUI.color = Color.white;
		Rect val2 = default(Rect);
		((Rect)(ref val2))._002Ector(rect);
		if (flag)
		{
			((Rect)(ref val2)).x = ((Rect)(ref val2)).x + 2f;
			((Rect)(ref val2)).y = ((Rect)(ref val2)).y - 2f;
		}
		Text.Anchor = (TextAnchor)4;
		Text.WordWrap = false;
		Text.Font = (GameFont)1;
		Widgets.Label(val2, label);
		Text.Anchor = (TextAnchor)3;
		Text.WordWrap = true;
		bool result = Widgets.ButtonInvisible(val, false);
		Text.Anchor = (TextAnchor)0;
		return result;
	}
}
