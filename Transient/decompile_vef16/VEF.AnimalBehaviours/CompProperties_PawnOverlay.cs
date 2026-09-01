using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace VEF.AnimalBehaviours;

public class CompProperties_PawnOverlay : CompProperties_FireOverlay
{
	public List<GraphicData> graphicElements;

	public CompProperties_PawnOverlay()
	{
		((CompProperties)this).compClass = typeof(CompPawnOverlay);
	}

	public override void DrawGhost(IntVec3 center, Rot4 rot, ThingDef thingDef, Color ghostCol, AltitudeLayer drawAltitude, Thing thing = null)
	{
		//IL_0002: Unknown result type (might be due to invalid IL or missing references)
		//IL_0004: Unknown result type (might be due to invalid IL or missing references)
		//IL_0009: Unknown result type (might be due to invalid IL or missing references)
		//IL_0020: Unknown result type (might be due to invalid IL or missing references)
		//IL_0028: Unknown result type (might be due to invalid IL or missing references)
		//IL_0029: Unknown result type (might be due to invalid IL or missing references)
		Vector3 val = ((IntVec3)(ref center)).ToVector3ShiftedWithAltitude(drawAltitude);
		for (int i = 0; i < graphicElements.Count; i++)
		{
			GhostUtility.GhostGraphicFor(graphicElements[i].Graphic, thingDef, ghostCol, (ThingDef)null).DrawFromDef(val, rot, thingDef, 0f);
			val.y += 3f / 74f;
		}
	}
}
