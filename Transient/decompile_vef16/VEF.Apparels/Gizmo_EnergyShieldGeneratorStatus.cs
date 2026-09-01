using System;
using UnityEngine;
using Verse;

namespace VEF.Apparels;

[StaticConstructorOnStartup]
public class Gizmo_EnergyShieldGeneratorStatus : Gizmo
{
	public CompShieldField shieldGenerator;

	private static readonly Texture2D FullShieldBarTex = SolidColorMaterials.NewSolidColorTexture(new Color(0.2f, 0.2f, 0.24f));

	private static readonly Texture2D EmptyShieldBarTex = SolidColorMaterials.NewSolidColorTexture(Color.clear);

	public Gizmo_EnergyShieldGeneratorStatus()
	{
		((Gizmo)this).Order = -100f;
	}

	public override float GetWidth(float maxWidth)
	{
		return 140f;
	}

	public override GizmoResult GizmoOnGUI(Vector2 topLeft, float maxWidth, GizmoRenderParms parms)
	{
		//IL_000e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0014: Unknown result type (might be due to invalid IL or missing references)
		//IL_0026: Unknown result type (might be due to invalid IL or missing references)
		//IL_002b: Unknown result type (might be due to invalid IL or missing references)
		//IL_003b: Unknown result type (might be due to invalid IL or missing references)
		//IL_005c: Unknown result type (might be due to invalid IL or missing references)
		Rect overRect = new Rect(topLeft.x, topLeft.y, ((Gizmo)this).GetWidth(maxWidth), 75f);
		Find.WindowStack.ImmediateWindow(984688, overRect, (WindowLayer)0, (Action)delegate
		{
			//IL_0001: Unknown result type (might be due to invalid IL or missing references)
			//IL_0006: Unknown result type (might be due to invalid IL or missing references)
			//IL_0010: Unknown result type (might be due to invalid IL or missing references)
			//IL_0015: Unknown result type (might be due to invalid IL or missing references)
			//IL_0016: Unknown result type (might be due to invalid IL or missing references)
			//IL_0035: Unknown result type (might be due to invalid IL or missing references)
			//IL_0050: Unknown result type (might be due to invalid IL or missing references)
			//IL_008d: Unknown result type (might be due to invalid IL or missing references)
			//IL_009a: Unknown result type (might be due to invalid IL or missing references)
			//IL_00ac: Unknown result type (might be due to invalid IL or missing references)
			Rect val;
			Rect val2 = (val = GenUI.ContractedBy(GenUI.AtZero(overRect), 6f));
			((Rect)(ref val)).height = ((Rect)(ref overRect)).height / 2f;
			Text.Font = (GameFont)0;
			Widgets.Label(val, ((Entity)((ThingComp)shieldGenerator).parent).LabelCap);
			Rect val3 = val2;
			((Rect)(ref val3)).yMin = ((Rect)(ref overRect)).height / 2f;
			float energy = shieldGenerator.Energy;
			float num = energy / shieldGenerator.MaxEnergy;
			Widgets.FillableBar(val3, num, FullShieldBarTex, EmptyShieldBarTex, false);
			Text.Font = (GameFont)1;
			Text.Anchor = (TextAnchor)4;
			Widgets.Label(val3, (energy * 100f).ToString("F0") + " / " + (shieldGenerator.MaxEnergy * 100f).ToString("F0"));
			Text.Anchor = (TextAnchor)0;
		}, true, false, 1f, (Action)null, false);
		return new GizmoResult((GizmoState)0);
	}
}
