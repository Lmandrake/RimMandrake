using RimWorld;
using UnityEngine;
using Verse;

namespace BigAndSmall;

public static class PRN_Ultimate
{
	public static readonly string noImage = "BS_Blank";

	public static Graphic GraphicFor(Pawn pawn, IUltimateRendering uNode, PawnRenderingProps_Ultimate UProps)
	{
		//IL_0074: Unknown result type (might be due to invalid IL or missing references)
		//IL_0137: Unknown result type (might be due to invalid IL or missing references)
		//IL_0142: Unknown result type (might be due to invalid IL or missing references)
		//IL_0147: Unknown result type (might be due to invalid IL or missing references)
		//IL_0150: Unknown result type (might be due to invalid IL or missing references)
		//IL_015b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0160: Unknown result type (might be due to invalid IL or missing references)
		//IL_0169: Unknown result type (might be due to invalid IL or missing references)
		//IL_0174: Unknown result type (might be due to invalid IL or missing references)
		//IL_0179: Unknown result type (might be due to invalid IL or missing references)
		//IL_01f1: Unknown result type (might be due to invalid IL or missing references)
		//IL_01f8: Unknown result type (might be due to invalid IL or missing references)
		//IL_01fa: Unknown result type (might be due to invalid IL or missing references)
		//IL_01fc: Unknown result type (might be due to invalid IL or missing references)
		PawnRenderNode @base = uNode.Base;
		BSCache cache = HumanoidPawnScaler.GetCache(pawn);
		ConditionalGraphicsSet graphicsSet;
		string text;
		string text2;
		ConditionalGraphicProperties graphicProperties;
		if (cache != null)
		{
			graphicsSet = (UProps.generated ?? UProps.GraphicSet).GetGraphicsSet(cache);
			text = graphicsSet.GetPath(cache, noImage);
			text2 = graphicsSet.GetMaskPath(cache, null);
			graphicProperties = graphicsSet.ConditionalProps.GetGraphicProperties(cache);
			if (graphicProperties.drawSize.HasValue)
			{
				uNode.ScaleSet = true;
				uNode.CachedScale = graphicProperties.drawSize.Value;
			}
			else
			{
				uNode.ScaleSet = false;
			}
			if (uNode.AllowTexPathFor && (GenText.NullOrEmpty(text) || text == noImage))
			{
				text = @base.TexPathFor(pawn);
				if (!GenText.NullOrEmpty(text))
				{
					goto IL_0122;
				}
			}
			if (GenText.NullOrEmpty(text))
			{
				Log.WarningOnce($"[BigAndSmall] No texture path for {pawn}. Returning empty image.", ((object)@base).GetHashCode());
				return GraphicDatabase.Get<Graphic_Single>(noImage);
			}
			if (UProps.autoBodyTypeMasks)
			{
				if (text2 == null)
				{
					text2 = text;
				}
				text2 = GetBodyTypedPath(pawn.story.bodyType, text2);
			}
			if (UProps.autoBodyTypePaths)
			{
				text = GetBodyTypedPath(pawn.story.bodyType, text);
			}
			goto IL_0122;
		}
		Log.WarningOnce($"No cache found by {uNode} for {pawn}. Returning empty image.", ((object)@base).GetHashCode());
		return GraphicDatabase.Get<Graphic_Single>(noImage);
		IL_0122:
		if (text2 == text)
		{
			text2 = null;
		}
		Color color = graphicsSet.ColorA.GetColor(@base, Color.white, "someKeyStringClrOne");
		Color color2 = graphicsSet.ColorB.GetColor(@base, Color.white, "clrTwoKeyString");
		Color color3 = graphicsSet.ColorC.GetColor(@base, Color.white, "zomgClrThree");
		object obj;
		if (graphicProperties == null)
		{
			obj = null;
		}
		else
		{
			ShaderTypeDef shader = graphicProperties.shader;
			obj = ((shader != null) ? shader.Shader : null);
		}
		Shader val = (Shader)obj;
		Shader val2;
		if (val != null)
		{
			val2 = val;
		}
		else
		{
			ShaderTypeDef shader2 = UProps.shader;
			val2 = ((shader2 != null) ? shader2.Shader : null);
			if ((Object)(object)val2 == (Object)null)
			{
				if (((PawnRenderNodeProperties)UProps).useSkinShader)
				{
					Shader skinShader = ShaderUtility.GetSkinShader(pawn);
					if ((Object)(object)skinShader != (Object)null)
					{
						val2 = skinShader;
					}
				}
				else if (val2 == null)
				{
					val2 = BSDefs.BS_CutoutThreeColor.Shader;
				}
			}
		}
		return RenderingLib.GetCachableGraphics(text, Vector2.one, val2, color, color2, color3, text2);
	}

	public static string GetBodyTypedPath(BodyTypeDef bodyType, string basePath)
	{
		if (bodyType == null)
		{
			Log.Error("Attempted to get graphic with undefined body type.");
			bodyType = BodyTypeDefOf.Male;
		}
		if (GenText.NullOrEmpty(basePath))
		{
			return basePath;
		}
		return basePath + "_" + ((Def)bodyType).defName;
	}
}
