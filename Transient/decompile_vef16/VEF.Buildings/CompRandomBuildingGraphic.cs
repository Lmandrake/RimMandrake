using System;
using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace VEF.Buildings;

public class CompRandomBuildingGraphic : ThingComp
{
	public Thing thingToGrab;

	public Graphic_Multi newGraphic;

	public Graphic_Single newGraphicSingle;

	public string newGraphicPath = "";

	public string newGraphicSinglePath = "";

	public CompProperties_RandomBuildingGraphic Props => (CompProperties_RandomBuildingGraphic)(object)base.props;

	public override void PostSpawnSetup(bool respawningAfterLoad)
	{
		if (!CorrectDefCheck())
		{
			return;
		}
		thingToGrab = (Thing)(object)base.parent;
		if (((Thing)base.parent).StyleDef == null)
		{
			LongEventHandler.ExecuteWhenFinished((Action)delegate
			{
				ChangeGraphic(random: true, 0);
			});
		}
	}

	public void ChangeGraphic(bool random, int index, bool forceRandom = false)
	{
		//IL_000b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0010: Unknown result type (might be due to invalid IL or missing references)
		//IL_001c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0021: Unknown result type (might be due to invalid IL or missing references)
		//IL_002d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0032: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d1: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d2: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d3: Unknown result type (might be due to invalid IL or missing references)
		//IL_00db: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e5: Expected O, but got Unknown
		//IL_021e: Unknown result type (might be due to invalid IL or missing references)
		//IL_021f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0220: Unknown result type (might be due to invalid IL or missing references)
		//IL_0228: Unknown result type (might be due to invalid IL or missing references)
		//IL_0232: Expected O, but got Unknown
		//IL_0179: Unknown result type (might be due to invalid IL or missing references)
		//IL_017a: Unknown result type (might be due to invalid IL or missing references)
		//IL_017b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0183: Unknown result type (might be due to invalid IL or missing references)
		//IL_018d: Expected O, but got Unknown
		//IL_02c6: Unknown result type (might be due to invalid IL or missing references)
		//IL_02c7: Unknown result type (might be due to invalid IL or missing references)
		//IL_02c8: Unknown result type (might be due to invalid IL or missing references)
		//IL_02d0: Unknown result type (might be due to invalid IL or missing references)
		//IL_02da: Expected O, but got Unknown
		//IL_02f7: Unknown result type (might be due to invalid IL or missing references)
		//IL_0301: Expected O, but got Unknown
		//IL_0155: Unknown result type (might be due to invalid IL or missing references)
		//IL_0156: Unknown result type (might be due to invalid IL or missing references)
		//IL_0157: Unknown result type (might be due to invalid IL or missing references)
		//IL_015f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0169: Expected O, but got Unknown
		//IL_02a2: Unknown result type (might be due to invalid IL or missing references)
		//IL_02a3: Unknown result type (might be due to invalid IL or missing references)
		//IL_02a4: Unknown result type (might be due to invalid IL or missing references)
		//IL_02ac: Unknown result type (might be due to invalid IL or missing references)
		//IL_02b6: Expected O, but got Unknown
		try
		{
			Vector2 drawSize = ((Thing)base.parent).Graphic.drawSize;
			Color color = ((Thing)base.parent).Graphic.color;
			Color colorTwo = ((Thing)base.parent).Graphic.colorTwo;
			GraphicData graphicData = ((Thing)base.parent).def.graphicData;
			ShaderTypeDef shaderType = ((Thing)base.parent).def.graphicData.shaderType;
			if (((Thing)base.parent).Faction == null || !((Thing)base.parent).Faction.IsPlayer)
			{
				return;
			}
			if (((Thing)base.parent).def.graphicData.graphicClass == typeof(Graphic_Multi))
			{
				if (!random)
				{
					newGraphicPath = Props.randomGraphics[index];
					newGraphic = (Graphic_Multi)GraphicDatabase.Get<Graphic_Multi>(newGraphicPath, shaderType.Shader, drawSize, color, colorTwo, graphicData, (string)null);
				}
				else if (newGraphicPath == "")
				{
					if (forceRandom || (!VFEGlobal.settings.randomStartsAsRandom && Props.startAsRandom))
					{
						newGraphicPath = GenCollection.RandomElement<string>((IEnumerable<string>)Props.randomGraphics);
					}
					else
					{
						newGraphicPath = Props.randomGraphics[0];
					}
					newGraphic = (Graphic_Multi)GraphicDatabase.Get<Graphic_Multi>(newGraphicPath, shaderType.Shader, drawSize, color, colorTwo, graphicData, (string)null);
				}
				else
				{
					newGraphic = (Graphic_Multi)GraphicDatabase.Get<Graphic_Multi>(newGraphicPath, shaderType.Shader, drawSize, color, colorTwo, graphicData, (string)null);
				}
				if (((Thing)base.parent).StyleDef != null)
				{
					ReflectionCache.styleGraphic.Invoke(thingToGrab) = (Graphic)(object)newGraphic;
				}
				ReflectionCache.buildingGraphic.Invoke(thingToGrab) = (Graphic)(object)newGraphic;
			}
			else
			{
				if (!(((Thing)base.parent).def.graphicData.graphicClass == typeof(Graphic_Single)))
				{
					return;
				}
				if (!random)
				{
					newGraphicSinglePath = Props.randomGraphics[index];
					newGraphicSingle = (Graphic_Single)GraphicDatabase.Get<Graphic_Single>(newGraphicSinglePath, shaderType.Shader, drawSize, color, colorTwo, graphicData, (string)null);
				}
				else if (newGraphicSinglePath == "")
				{
					if (forceRandom || (!VFEGlobal.settings.randomStartsAsRandom && Props.startAsRandom))
					{
						newGraphicSinglePath = GenCollection.RandomElement<string>((IEnumerable<string>)Props.randomGraphics);
					}
					else
					{
						newGraphicSinglePath = Props.randomGraphics[0];
					}
					newGraphicSingle = (Graphic_Single)GraphicDatabase.Get<Graphic_Single>(newGraphicSinglePath, shaderType.Shader, drawSize, color, colorTwo, graphicData, (string)null);
				}
				else
				{
					newGraphicSingle = (Graphic_Single)GraphicDatabase.Get<Graphic_Single>(newGraphicSinglePath, shaderType.Shader, drawSize, color, colorTwo, graphicData, (string)null);
				}
				if (!((Thing)base.parent).def.graphicData.drawRotated)
				{
					((Graphic)newGraphicSingle).data = new GraphicData();
					((Graphic)newGraphicSingle).data.drawRotated = false;
				}
				if (((Thing)base.parent).StyleDef != null)
				{
					ReflectionCache.styleGraphic.Invoke(thingToGrab) = (Graphic)(object)newGraphicSingle;
				}
				ReflectionCache.buildingGraphic.Invoke(thingToGrab) = (Graphic)(object)newGraphicSingle;
			}
		}
		catch (Exception)
		{
			Log.Message("The variations mod has probably been added to a running save. Ignoring load error.");
		}
	}

	public override void PostExposeData()
	{
		Scribe_Values.Look<string>(ref newGraphicPath, "newGraphicPath", (string)null, false);
		Scribe_Values.Look<string>(ref newGraphicSinglePath, "newGraphicSinglePath", (string)null, false);
	}

	public override IEnumerable<Gizmo> CompGetGizmosExtra()
	{
		if (((Thing)base.parent).Faction == null || !((Thing)base.parent).Faction.IsPlayer || VFEGlobal.settings.hideRandomizeButtons || Props.disableAllButtons || !CorrectDefCheck())
		{
			yield break;
		}
		if (!Props.disableRandomButton)
		{
			yield return (Gizmo)new Command_Action
			{
				defaultLabel = TaggedString.op_Implicit(Translator.Translate("VFE_ChangeGraphic")),
				defaultDesc = TaggedString.op_Implicit(Translator.Translate("VFE_ChangeGraphicDesc")),
				icon = (Texture)(object)ContentFinder<Texture2D>.Get("UI/VEF_ChangeGraphic", true),
				action = delegate
				{
					//IL_003d: Unknown result type (might be due to invalid IL or missing references)
					newGraphicPath = "";
					newGraphicSinglePath = "";
					LongEventHandler.ExecuteWhenFinished((Action)delegate
					{
						ChangeGraphic(random: true, 0, forceRandom: true);
					});
					((Thing)base.parent).Map.mapDrawer.MapMeshDirty(((Thing)base.parent).Position, MapMeshFlagDef.op_Implicit(MapMeshFlagDefOf.Things) | MapMeshFlagDef.op_Implicit(MapMeshFlagDefOf.Buildings));
				}
			};
		}
		if (!Props.disableGraphicChoosingButton)
		{
			yield return (Gizmo)new Command_Action
			{
				defaultLabel = TaggedString.op_Implicit(Translator.Translate("VFE_ChooseGraphic")),
				defaultDesc = TaggedString.op_Implicit(Translator.Translate("VFE_ChooseGraphicDesc")),
				icon = (Texture)(object)ContentFinder<Texture2D>.Get("UI/VEF_ChooseGraphic", true),
				action = delegate
				{
					Dialog_ChooseGraphic dialog_ChooseGraphic = new Dialog_ChooseGraphic((Thing)(object)base.parent, Props);
					Find.WindowStack.Add((Window)(object)dialog_ChooseGraphic);
				}
			};
		}
	}

	public void ResetGraphics()
	{
		ReflectionCache.buildingGraphic.Invoke(thingToGrab) = null;
		ReflectionCache.styleGraphic.Invoke(thingToGrab) = null;
	}

	public bool CorrectDefCheck()
	{
		if (Props.onlyApplyToThisDef == null)
		{
			return true;
		}
		return ((Thing)base.parent).def == Props.onlyApplyToThisDef;
	}
}
