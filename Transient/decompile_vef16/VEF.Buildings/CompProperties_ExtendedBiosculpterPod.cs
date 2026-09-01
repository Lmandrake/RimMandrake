using System;
using System.Linq;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;

namespace VEF.Buildings;

public class CompProperties_ExtendedBiosculpterPod : CompProperties_BiosculpterPod
{
	public ThingDef copyCyclesFrom;

	public bool drawPawn = true;

	public Rot4? pawnFacingDirectionOverride;

	public Vector3 pawnOffsetNorth = Vector3.zero;

	public Vector3 pawnOffsetSouth = Vector3.zero;

	public Vector3 pawnOffsetEast = Vector3.zero;

	public Vector3 pawnOffsetWest = Vector3.zero;

	public bool drawBackground = true;

	public Vector3 backgroundOffsetNorth = Vector3.zero;

	public Vector3 backgroundOffsetSouth = Vector3.zero;

	public Vector3 backgroundOffsetEast = Vector3.zero;

	public Vector3 backgroundOffsetWest = Vector3.zero;

	public Vector3 backgroundSize = Vector3.zero;

	public string backgroundMaterialPath;

	[Unsaved(false)]
	public Material backgroundMaterial;

	public CompProperties_ExtendedBiosculpterPod()
	{
		//IL_0008: Unknown result type (might be due to invalid IL or missing references)
		//IL_000d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0013: Unknown result type (might be due to invalid IL or missing references)
		//IL_0018: Unknown result type (might be due to invalid IL or missing references)
		//IL_001e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0023: Unknown result type (might be due to invalid IL or missing references)
		//IL_0029: Unknown result type (might be due to invalid IL or missing references)
		//IL_002e: Unknown result type (might be due to invalid IL or missing references)
		//IL_003b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0040: Unknown result type (might be due to invalid IL or missing references)
		//IL_0046: Unknown result type (might be due to invalid IL or missing references)
		//IL_004b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0051: Unknown result type (might be due to invalid IL or missing references)
		//IL_0056: Unknown result type (might be due to invalid IL or missing references)
		//IL_005c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0061: Unknown result type (might be due to invalid IL or missing references)
		//IL_0067: Unknown result type (might be due to invalid IL or missing references)
		//IL_006c: Unknown result type (might be due to invalid IL or missing references)
		((CompProperties)this).compClass = typeof(CompExtendedBiosculpterPod);
	}

	public override void ResolveReferences(ThingDef parentDef)
	{
		//IL_0130: Unknown result type (might be due to invalid IL or missing references)
		//IL_0135: Unknown result type (might be due to invalid IL or missing references)
		//IL_0180: Unknown result type (might be due to invalid IL or missing references)
		//IL_018a: Expected O, but got Unknown
		((CompProperties)this).ResolveReferences(parentDef);
		try
		{
			if (copyCyclesFrom?.comps != null)
			{
				foreach (CompProperties comp in copyCyclesFrom.comps)
				{
					CompProperties_BiosculpterPod_BaseCycle cycle = (CompProperties_BiosculpterPod_BaseCycle)(object)((comp is CompProperties_BiosculpterPod_BaseCycle) ? comp : null);
					if (cycle != null && cycle.key != null && !parentDef.comps.OfType<CompProperties_BiosculpterPod_BaseCycle>().Any((CompProperties_BiosculpterPod_BaseCycle x) => x.key == cycle.key))
					{
						parentDef.comps.Add((CompProperties)(object)Gen.MemberwiseClone<CompProperties_BiosculpterPod_BaseCycle>(cycle));
					}
				}
			}
		}
		catch (Exception arg)
		{
			Log.Error($"Error occured trying to copy vanilla BiosculpterPod cycles to {((Def)parentDef).defName}:\n{arg}");
		}
		if (backgroundSize.x <= 0f || backgroundSize.y <= 0f || backgroundSize.z <= 0f)
		{
			backgroundSize = new Vector3(parentDef.graphicData.drawSize.x * 0.8f, 1f, parentDef.graphicData.drawSize.y * 0.8f);
		}
		if (!GenText.NullOrEmpty(backgroundMaterialPath))
		{
			backgroundMaterial = MaterialPool.MatFrom(backgroundMaterialPath);
		}
		if (BaseContent.NullOrBad(backgroundMaterial))
		{
			backgroundMaterial = (Material)AccessToolsExtensions.DeclaredField(typeof(CompBiosculpterPod), "BackgroundMat").GetValue(null);
		}
	}

	public Vector3 PawnOffsetFor(Rot4 rotation)
	{
		//IL_0021: Unknown result type (might be due to invalid IL or missing references)
		//IL_0026: Unknown result type (might be due to invalid IL or missing references)
		//IL_0033: Unknown result type (might be due to invalid IL or missing references)
		//IL_0038: Unknown result type (might be due to invalid IL or missing references)
		//IL_002a: Unknown result type (might be due to invalid IL or missing references)
		//IL_002f: Unknown result type (might be due to invalid IL or missing references)
		//IL_003c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0041: Unknown result type (might be due to invalid IL or missing references)
		//IL_004a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0044: Unknown result type (might be due to invalid IL or missing references)
		//IL_0049: Unknown result type (might be due to invalid IL or missing references)
		return (Vector3)(((Rot4)(ref rotation)).AsInt switch
		{
			0 => pawnOffsetNorth, 
			2 => pawnOffsetSouth, 
			1 => pawnOffsetEast, 
			3 => pawnOffsetWest, 
			_ => Vector3.zero, 
		});
	}

	public Vector3 BackgroundOffsetFor(Rot4 rotation)
	{
		//IL_0021: Unknown result type (might be due to invalid IL or missing references)
		//IL_0026: Unknown result type (might be due to invalid IL or missing references)
		//IL_0033: Unknown result type (might be due to invalid IL or missing references)
		//IL_0038: Unknown result type (might be due to invalid IL or missing references)
		//IL_002a: Unknown result type (might be due to invalid IL or missing references)
		//IL_002f: Unknown result type (might be due to invalid IL or missing references)
		//IL_003c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0041: Unknown result type (might be due to invalid IL or missing references)
		//IL_004a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0044: Unknown result type (might be due to invalid IL or missing references)
		//IL_0049: Unknown result type (might be due to invalid IL or missing references)
		return (Vector3)(((Rot4)(ref rotation)).AsInt switch
		{
			0 => backgroundOffsetNorth, 
			2 => backgroundOffsetSouth, 
			1 => backgroundOffsetEast, 
			3 => backgroundOffsetWest, 
			_ => Vector3.zero, 
		});
	}
}
