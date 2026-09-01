using UnityEngine;
using Verse;

namespace VEF.Apparels;

[StaticConstructorOnStartup]
public class Gizmo_EnergyCompShieldStatus : Gizmo
{
	public CompShieldBubble shield;

	private static readonly Texture2D FullShieldBarTex = SolidColorMaterials.NewSolidColorTexture(new Color(0.2f, 0.2f, 0.24f));

	private static readonly Texture2D EmptyShieldBarTex = SolidColorMaterials.NewSolidColorTexture(Color.clear);

	public Gizmo_EnergyCompShieldStatus()
	{
		((Gizmo)this).Order = -100f;
	}

	public override float GetWidth(float maxWidth)
	{
		return 140f;
	}

	public override GizmoResult GizmoOnGUI(Vector2 topLeft, float maxWidth, GizmoRenderParms parms)
	{
		//IL_0002: Unknown result type (might be due to invalid IL or missing references)
		//IL_0008: Unknown result type (might be due to invalid IL or missing references)
		//IL_001f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0025: Unknown result type (might be due to invalid IL or missing references)
		//IL_002a: Unknown result type (might be due to invalid IL or missing references)
		//IL_002b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0031: Unknown result type (might be due to invalid IL or missing references)
		//IL_0032: Unknown result type (might be due to invalid IL or missing references)
		//IL_004d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0063: Unknown result type (might be due to invalid IL or missing references)
		//IL_0064: Unknown result type (might be due to invalid IL or missing references)
		//IL_009a: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a8: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ba: Unknown result type (might be due to invalid IL or missing references)
		//IL_013a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0119: Unknown result type (might be due to invalid IL or missing references)
		//IL_012a: Unknown result type (might be due to invalid IL or missing references)
		//IL_012f: Unknown result type (might be due to invalid IL or missing references)
		Rect val = default(Rect);
		((Rect)(ref val))._002Ector(topLeft.x, topLeft.y, ((Gizmo)this).GetWidth(maxWidth), 75f);
		Rect val2 = GenUI.ContractedBy(val, 6f);
		Widgets.DrawWindowBackground(val);
		Rect val3 = val2;
		((Rect)(ref val3)).height = ((Rect)(ref val)).height / 2f;
		Text.Font = (GameFont)0;
		Widgets.Label(val3, ((Entity)((ThingComp)shield).parent).LabelCap);
		Rect val4 = val2;
		((Rect)(ref val4)).yMin = ((Rect)(ref val2)).y + ((Rect)(ref val2)).height / 2f;
		float num = shield.Energy / shield.EnergyMax;
		Widgets.FillableBar(val4, num, FullShieldBarTex, EmptyShieldBarTex, false);
		Text.Font = (GameFont)1;
		Text.Anchor = (TextAnchor)4;
		Widgets.Label(val4, shield.Energy.ToString("F0") + " / " + shield.EnergyMax.ToString("F0"));
		Text.Anchor = (TextAnchor)0;
		if (!GenText.NullOrEmpty(shield.Props.tooltipKey))
		{
			TooltipHandler.TipRegion(val2, TipSignal.op_Implicit(Translator.Translate(shield.Props.tooltipKey)));
		}
		return new GizmoResult((GizmoState)0);
	}
}
