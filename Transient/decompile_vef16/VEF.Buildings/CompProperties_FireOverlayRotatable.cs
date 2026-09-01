using RimWorld;
using UnityEngine;
using Verse;

namespace VEF.Buildings;

public class CompProperties_FireOverlayRotatable : CompProperties_FireOverlay
{
	public Vector3 northOffset;

	public Vector3 southOffset;

	public Vector3 westOffset;

	public Vector3 eastOffset;

	public string texPath = "Things/Special/Fire";

	public Color color = Color.white;

	public Vector2 size = Vector2.one;

	public CompProperties_FireOverlayRotatable()
	{
		//IL_000c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0011: Unknown result type (might be due to invalid IL or missing references)
		//IL_0017: Unknown result type (might be due to invalid IL or missing references)
		//IL_001c: Unknown result type (might be due to invalid IL or missing references)
		((CompProperties)this).compClass = typeof(CompFireOverlayRotatable);
	}
}
