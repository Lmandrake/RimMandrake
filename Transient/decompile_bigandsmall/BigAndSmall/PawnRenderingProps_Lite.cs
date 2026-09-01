using System;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;
using Verse;

namespace BigAndSmall;

/// <summary>
/// Lightweight version of Ultimate rendering props for quicky setup.
///
/// TECHNICALLY supports all the same features as Ultimate, but is intended to be able to be set up quickly,
///     and auto-generate many properties.
/// </summary>
public class PawnRenderingProps_Lite : PawnRenderingProps_Ultimate
{
	[Flags]
	public enum EnumColorSource
	{
		None = 0,
		Custom = 1,
		Skin = 2,
		Hair = 4,
		Rotted = 8
	}

	public FlagString tag;

	public string identifier;

	private Color? colorA;

	public Color? colorB;

	public Color? colorC;

	public List<ShaderTypeDef> userPickableShaders = new List<ShaderTypeDef>();

	public GraphicSetDef link;

	public (Color? color, EnumColorSource source) GetMainColorData()
	{
		//IL_0026: Unknown result type (might be due to invalid IL or missing references)
		//IL_002c: Invalid comparison between Unknown and I4
		//IL_003d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0043: Invalid comparison between Unknown and I4
		//IL_0054: Unknown result type (might be due to invalid IL or missing references)
		(Color?, EnumColorSource) result = (null, EnumColorSource.None);
		if (((PawnRenderNodeProperties)this).useRottenColor)
		{
			result.Item2 |= EnumColorSource.Rotted;
		}
		if ((int)((PawnRenderNodeProperties)this).colorType == 2)
		{
			result.Item2 |= EnumColorSource.Skin;
		}
		else if ((int)((PawnRenderNodeProperties)this).colorType == 1)
		{
			result.Item2 |= EnumColorSource.Hair;
		}
		else if ((int)((PawnRenderNodeProperties)this).colorType == 0)
		{
			result.Item2 |= EnumColorSource.Custom;
		}
		if (colorA.HasValue)
		{
			result.Item1 = colorA;
		}
		else
		{
			result.Item1 = ((PawnRenderNodeProperties)this).color;
		}
		return result;
	}

	public void TrySetup(bool forceSetup = false)
	{
		if (generated == null || forceSetup)
		{
			CheckConfig();
			if (link != null)
			{
				generated = link.conditionalGraphics;
			}
			else if (base.GraphicSet != null)
			{
				generated = base.GraphicSet;
			}
			else
			{
				generated = GenerateGraphicSet();
			}
		}
	}

	protected void CheckConfig()
	{
		if (base.GraphicSet != null)
		{
			Log.WarningOnce("[BigAndSmall] RenderNodeLite is being used with a full ConditionalGraphicsSet.Consider using PawnRenderNode_Ultimate instead.", 897348254);
		}
	}

	protected ConditionalGraphicsSet GenerateGraphicSet()
	{
		//IL_020c: Unknown result type (might be due to invalid IL or missing references)
		//IL_00dc: Unknown result type (might be due to invalid IL or missing references)
		//IL_013e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0293: Unknown result type (might be due to invalid IL or missing references)
		//IL_026a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0261: Unknown result type (might be due to invalid IL or missing references)
		//IL_01bb: Unknown result type (might be due to invalid IL or missing references)
		//IL_01b2: Unknown result type (might be due to invalid IL or missing references)
		//IL_0354: Unknown result type (might be due to invalid IL or missing references)
		//IL_034b: Unknown result type (might be due to invalid IL or missing references)
		//IL_032c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0323: Unknown result type (might be due to invalid IL or missing references)
		//IL_02f1: Unknown result type (might be due to invalid IL or missing references)
		//IL_02e8: Unknown result type (might be due to invalid IL or missing references)
		ColorSetting colorSetting = null;
		ColorSetting colorSetting2 = null;
		ConditionalGraphicProperties props = null;
		if (identifier != null)
		{
			props = new ConditionalGraphicProperties
			{
				shader = null,
				replaceFlagMinPriority = 1000f,
				replaceFlags = new FlagStringList { tag },
				alts = userPickableShaders.Select((ShaderTypeDef shader) => new ConditionalGraphicProperties
				{
					shader = shader,
					customTagGraphicIsSet = new ConditionalGraphic.HasTagGraphicOverride
					{
						tag = tag,
						customFlags = new FlagStringList
						{
							new FlagString(identifier, ((Def)shader).defName)
						}
					}
				}).ToList()
			};
		}
		(Color? color, EnumColorSource source) mainColorData = GetMainColorData();
		Color? item = mainColorData.color;
		EnumColorSource item2 = mainColorData.source;
		FlagString flagString = tag;
		ColorSetting colorSetting3;
		if ((object)flagString != null)
		{
			colorSetting3 = new ColorSetting
			{
				alts = new List<ColorSetting>(1)
				{
					new ColorSetting
					{
						customTagGraphicIsSet = new ConditionalGraphic.HasTagGraphicOverride
						{
							tag = flagString,
							colorA = true
						},
						customClrTagA = flagString
					}
				}
			};
			if (colorB.HasValue)
			{
				colorSetting = new ColorSetting
				{
					color = colorB.Value,
					alts = new List<ColorSetting>(1)
					{
						new ColorSetting
						{
							customTagGraphicIsSet = new ConditionalGraphic.HasTagGraphicOverride
							{
								tag = flagString,
								colorB = true
							},
							customClrTagB = flagString
						}
					}
				};
			}
			colorSetting2 = ((!colorC.HasValue) ? new ColorSetting
			{
				color = (Color)(((_003F?)colorSetting3?.color) ?? Color.white)
			} : new ColorSetting
			{
				color = colorC.Value,
				alts = new List<ColorSetting>(1)
				{
					new ColorSetting
					{
						customTagGraphicIsSet = new ConditionalGraphic.HasTagGraphicOverride
						{
							tag = flagString,
							colorC = true
						},
						customClrTagC = flagString
					}
				}
			});
		}
		else
		{
			colorSetting3 = new ColorSetting
			{
				altDefs = new List<ColorSettingDef>(1) { DefDatabase<ColorSettingDef>.GetNamed("BS_CustomGlobalA", true) }
			};
			colorSetting = ((!colorB.HasValue) ? new ColorSetting
			{
				color = (Color)(((_003F?)colorSetting?.color) ?? Color.white)
			} : new ColorSetting
			{
				color = colorB.Value,
				altDefs = new List<ColorSettingDef>(1) { DefDatabase<ColorSettingDef>.GetNamed("BS_CustomGlobalB", true) }
			});
			colorSetting2 = ((!colorC.HasValue) ? new ColorSetting
			{
				color = (Color)(((_003F?)colorSetting2?.color) ?? Color.white)
			} : new ColorSetting
			{
				color = colorC.Value,
				altDefs = new List<ColorSettingDef>(1) { DefDatabase<ColorSettingDef>.GetNamed("BS_CustomGlobalC", true) }
			});
		}
		if (item2.HasFlag(EnumColorSource.Custom))
		{
			colorSetting3.color = (Color)(((_003F?)item) ?? Color.white);
		}
		else
		{
			colorSetting3.color = (Color)(((_003F?)item) ?? Color.white);
			colorSetting3.averageColors = false;
		}
		if (item2.HasFlag(EnumColorSource.Skin))
		{
			colorSetting3.skinColor = true;
		}
		if (item2.HasFlag(EnumColorSource.Hair))
		{
			colorSetting3.hairColor = true;
		}
		if (item2.HasFlag(EnumColorSource.Rotted))
		{
			colorSetting3.useRottedColor = true;
		}
		return new ConditionalGraphicsSet(colorSetting3, colorSetting, colorSetting2, props);
	}
}
