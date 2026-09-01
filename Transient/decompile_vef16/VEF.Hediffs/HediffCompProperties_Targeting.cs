using UnityEngine;
using Verse;

namespace VEF.Hediffs;

public class HediffCompProperties_Targeting : HediffCompProperties
{
	public bool neverMiss;

	public bool neverHit;

	public bool alwaysHit;

	public bool alwaysMiss;

	public ThingDef targetingMote;

	public float initialTargetingMoteScale;

	public bool sizeScalesWithProgress = true;

	public string targetingLineTexPath;

	public Color targetingLineColor = Color.red;

	public float targetingLineWidth = 0.2f;

	public HediffCompProperties_Targeting()
	{
		//IL_0008: Unknown result type (might be due to invalid IL or missing references)
		//IL_000d: Unknown result type (might be due to invalid IL or missing references)
		base.compClass = typeof(HediffComp_Targeting);
	}
}
