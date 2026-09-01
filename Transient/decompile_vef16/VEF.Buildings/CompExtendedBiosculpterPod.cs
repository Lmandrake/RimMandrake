using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;

namespace VEF.Buildings;

public class CompExtendedBiosculpterPod : CompBiosculpterPod
{
	private static readonly FieldRef<CompBiosculpterPod, float> currentCycleTicksRemainingField = AccessTools.FieldRefAccess<CompBiosculpterPod, float>("currentCycleTicksRemaining");

	private static readonly FieldRef<CompBiosculpterPod, int> currentCyclePowerCutTicksField = AccessTools.FieldRefAccess<CompBiosculpterPod, int>("currentCyclePowerCutTicks");

	public CompProperties_ExtendedBiosculpterPod Props => (CompProperties_ExtendedBiosculpterPod)(object)((ThingComp)this).props;

	public override void PostDraw()
	{
		//IL_007f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0085: Invalid comparison between Unknown and I4
		//IL_0013: Unknown result type (might be due to invalid IL or missing references)
		//IL_0018: Unknown result type (might be due to invalid IL or missing references)
		//IL_002e: Unknown result type (might be due to invalid IL or missing references)
		//IL_003b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0040: Unknown result type (might be due to invalid IL or missing references)
		//IL_0045: Unknown result type (might be due to invalid IL or missing references)
		//IL_0050: Unknown result type (might be due to invalid IL or missing references)
		//IL_0055: Unknown result type (might be due to invalid IL or missing references)
		//IL_0058: Unknown result type (might be due to invalid IL or missing references)
		//IL_0063: Unknown result type (might be due to invalid IL or missing references)
		//IL_0068: Unknown result type (might be due to invalid IL or missing references)
		//IL_009a: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b9: Unknown result type (might be due to invalid IL or missing references)
		//IL_00be: Unknown result type (might be due to invalid IL or missing references)
		//IL_00cf: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d4: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d9: Unknown result type (might be due to invalid IL or missing references)
		//IL_00de: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ef: Unknown result type (might be due to invalid IL or missing references)
		if (Props.drawBackground)
		{
			Vector3 drawPos = ((Thing)((ThingComp)this).parent).DrawPos;
			drawPos.y -= 0.07317074f;
			Mesh plane = MeshPool.plane10;
			Vector3 val = drawPos + Props.BackgroundOffsetFor(((Thing)((ThingComp)this).parent).Rotation);
			Rot4 rotation = ((Thing)((ThingComp)this).parent).Rotation;
			Graphics.DrawMesh(plane, Matrix4x4.TRS(val, ((Rot4)(ref rotation)).AsQuat, Props.backgroundSize), Props.backgroundMaterial, 0);
		}
		if ((int)((CompBiosculpterPod)this).State == 2 && Props.drawPawn)
		{
			Vector3 val2 = ((Thing)((ThingComp)this).parent).DrawPos + CompBiosculpterPod.FloatingOffset(currentCycleTicksRemainingField.Invoke((CompBiosculpterPod)(object)this) + (float)currentCyclePowerCutTicksField.Invoke((CompBiosculpterPod)(object)this)) + Props.PawnOffsetFor(((Thing)((ThingComp)this).parent).Rotation);
			((CompBiosculpterPod)this).Occupant.Drawer.renderer.RenderPawnAt(val2, Props.pawnFacingDirectionOverride, true);
		}
	}
}
