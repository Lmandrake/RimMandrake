using System;
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;

namespace VEF.Graphics;

public class CompGraphicCustomization : ThingComp
{
	public List<string> texPaths;

	public List<TextureVariant> texVariants;

	public List<TextureVariant> texVariantsToCustomize;

	public Graphic graphicInt;

	private Texture2D textureInt;

	public CompProperties_GraphicCustomization Props => base.props as CompProperties_GraphicCustomization;

	public Graphic Graphic
	{
		get
		{
			//IL_0067: Unknown result type (might be due to invalid IL or missing references)
			//IL_007c: Unknown result type (might be due to invalid IL or missing references)
			//IL_0091: Unknown result type (might be due to invalid IL or missing references)
			//IL_00c4: Unknown result type (might be due to invalid IL or missing references)
			if (graphicInt == null)
			{
				TryInit();
				GraphicRequest req = default(GraphicRequest);
				((GraphicRequest)(ref req))._002Ector(((Thing)base.parent).def.graphicData.graphicClass, ((Thing)base.parent).def.graphicData.texPath, ((Thing)base.parent).def.graphicData.shaderType.Shader, ((Thing)base.parent).def.graphicData.drawSize, ((Thing)base.parent).def.graphicData.color, ((Thing)base.parent).def.graphicData.colorTwo, ((Thing)base.parent).def.graphicData, 0, ((Thing)base.parent).def.graphicData.shaderParameters, (string)null);
				graphicInt = (Graphic)(object)GetGraphic(req);
			}
			return graphicInt;
		}
	}

	public Texture2D Texture
	{
		get
		{
			if (textureInt == null)
			{
				TryInit();
				textureInt = GetCombinedTexture(texPaths);
			}
			return textureInt;
		}
	}

	public void TryInit()
	{
		if (GenList.NullOrEmpty<string>((IList<string>)texPaths))
		{
			texVariants = GetRandomizedTexVariants();
			texPaths = GetTexPaths(texVariants);
		}
	}

	public List<string> GetTexPaths(List<TextureVariant> texVariants)
	{
		List<string> list = new List<string>();
		foreach (TextureVariant texVariant in texVariants)
		{
			list.Add(texVariant.outline);
		}
		foreach (TextureVariant texVariant2 in texVariants)
		{
			list.Add(texVariant2.texture);
		}
		return list;
	}

	public List<TextureVariant> GetRandomizedTexVariants()
	{
		Dictionary<string, TextureVariant> dictionary = new Dictionary<string, TextureVariant>();
		foreach (GraphicPart graphic in Props.graphics)
		{
			dictionary[graphic.name] = GenCollection.RandomElementByWeight<TextureVariant>((IEnumerable<TextureVariant>)graphic.texVariants, (Func<TextureVariant, float>)((TextureVariant x) => x.chanceOverride));
		}
		new List<TextureVariant>();
		foreach (string item in dictionary.Keys.ToList())
		{
			TextureVariant variant = dictionary[item];
			if (variant.textureVariantOverride != null && Rand.Chance(variant.textureVariantOverride.chance))
			{
				GraphicPart graphicPart = Props.graphics.First((GraphicPart x) => x.name == variant.textureVariantOverride.groupName);
				dictionary[graphicPart.name] = graphicPart.texVariants.First((TextureVariant x) => x.texName == variant.textureVariantOverride.texName);
			}
		}
		return dictionary.Values.ToList();
	}

	public Graphic_Single GetGraphic(GraphicRequest req)
	{
		//IL_0000: Unknown result type (might be due to invalid IL or missing references)
		//IL_0006: Expected O, but got Unknown
		//IL_0007: Unknown result type (might be due to invalid IL or missing references)
		//IL_000f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0024: Unknown result type (might be due to invalid IL or missing references)
		//IL_0037: Unknown result type (might be due to invalid IL or missing references)
		//IL_003c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0049: Unknown result type (might be due to invalid IL or missing references)
		//IL_004e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0055: Unknown result type (might be due to invalid IL or missing references)
		//IL_0062: Unknown result type (might be due to invalid IL or missing references)
		//IL_0078: Unknown result type (might be due to invalid IL or missing references)
		Graphic_Single val = new Graphic_Single();
		((Graphic)val).Init(req);
		MaterialRequest val2 = default(MaterialRequest);
		val2.mainTex = (Texture)(object)Texture;
		val2.shader = req.shader;
		val2.color = ((Thing)base.parent).DrawColor;
		val2.colorTwo = ((Thing)base.parent).DrawColorTwo;
		val2.renderQueue = req.renderQueue;
		val2.shaderParameters = req.shaderParameters;
		ReflectionCache.graphicMat.Invoke(val) = MaterialPool.MatFrom(val2);
		return val;
	}

	public Texture2D GetCombinedTexture(List<string> paths)
	{
		Texture2D val = TextureUtils.GetReadableTexture(ContentFinder<Texture2D>.Get(paths[0], true));
		for (int i = 1; i < paths.Count; i++)
		{
			Texture2D readableTexture = TextureUtils.GetReadableTexture(ContentFinder<Texture2D>.Get(paths[i], true));
			val = TextureUtils.CombineTextures(val, readableTexture, 0, 0);
		}
		return val;
	}

	public override IEnumerable<FloatMenuOption> CompFloatMenuOptions(Pawn selPawn)
	{
		if (Props.customizable)
		{
			yield return new FloatMenuOption(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("VEF.Customize", NamedArgument.op_Implicit(((Entity)base.parent).LabelShort))), (Action)delegate
			{
				Find.WindowStack.Add((Window)(object)new Dialog_GraphicCustomization(this, selPawn));
			}, (MenuOptionPriority)4, (Action<Rect>)null, (Thing)null, 0f, (Func<Rect, bool>)null, (WorldObject)null, true, 0);
		}
	}

	public void Customize()
	{
		//IL_0096: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ab: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c0: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f3: Unknown result type (might be due to invalid IL or missing references)
		//IL_0138: Unknown result type (might be due to invalid IL or missing references)
		texVariants = GenList.ListFullCopy<TextureVariant>(texVariantsToCustomize);
		texVariantsToCustomize.Clear();
		texPaths = GetTexPaths(texVariants);
		textureInt = GetCombinedTexture(texPaths);
		GraphicRequest req = default(GraphicRequest);
		((GraphicRequest)(ref req))._002Ector(((Thing)base.parent).def.graphicData.graphicClass, ((Thing)base.parent).def.graphicData.texPath, ((Thing)base.parent).def.graphicData.shaderType.Shader, ((Thing)base.parent).def.graphicData.drawSize, ((Thing)base.parent).def.graphicData.color, ((Thing)base.parent).def.graphicData.colorTwo, ((Thing)base.parent).def.graphicData, 0, ((Thing)base.parent).def.graphicData.shaderParameters, (string)null);
		graphicInt = (Graphic)(object)GetGraphic(req);
		ReflectionCache.itemGraphic.Invoke((Thing)(object)base.parent) = graphicInt;
		if (((Thing)base.parent).Spawned)
		{
			((Thing)base.parent).Map.mapDrawer.MapMeshDirty(((Thing)base.parent).Position, MapMeshFlagDef.op_Implicit(MapMeshFlagDefOf.Things));
		}
	}

	public override void PostExposeData()
	{
		((ThingComp)this).PostExposeData();
		Scribe_Collections.Look<string>(ref texPaths, "texPaths", (LookMode)1, Array.Empty<object>());
		Scribe_Collections.Look<TextureVariant>(ref texVariants, "texVariants", (LookMode)2, Array.Empty<object>());
		Scribe_Collections.Look<TextureVariant>(ref texVariantsToCustomize, "texVariantsToCustomize", (LookMode)2, Array.Empty<object>());
	}
}
