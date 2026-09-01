using RimWorld;
using UnityEngine;
using Verse;

namespace VEF.AnimalBehaviours;

[StaticConstructorOnStartup]
public class CompPawnOverlay : CompFireOverlayBase
{
	public CompProperties_PawnOverlay Props => (CompProperties_PawnOverlay)(object)((ThingComp)this).props;

	public override void PostDraw()
	{
		//IL_0013: Unknown result type (might be due to invalid IL or missing references)
		//IL_0018: Unknown result type (might be due to invalid IL or missing references)
		//IL_003e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0045: Unknown result type (might be due to invalid IL or missing references)
		((ThingComp)this).PostDraw();
		CompProperties_PawnOverlay props = Props;
		Vector3 drawPos = ((Thing)((ThingComp)this).parent).DrawPos;
		for (int i = 0; i < props.graphicElements.Count; i++)
		{
			drawPos.y += 3f / 74f;
			props.graphicElements[i].Graphic.Draw(drawPos, ((Thing)((ThingComp)this).parent).Rotation, (Thing)(object)((ThingComp)this).parent, 0f);
		}
	}
}
