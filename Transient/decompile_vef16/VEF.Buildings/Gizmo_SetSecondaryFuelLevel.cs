using RimWorld;
using UnityEngine;
using Verse;
using Verse.Sound;

namespace VEF.Buildings;

public class Gizmo_SetSecondaryFuelLevel : Gizmo_Slider
{
	private CompRefuelable_DualFuel refuelable;

	protected override float Target
	{
		get
		{
			return refuelable.SecondaryTargetFuelLevel / refuelable.Props.secondaryFuelCapacity;
		}
		set
		{
			refuelable.SecondaryTargetFuelLevel = value * refuelable.Props.secondaryFuelCapacity;
		}
	}

	protected override float ValuePercent => refuelable.SecondaryFuelPercentOfMax;

	protected override string Title => refuelable.Props.SecondaryFuelGizmoLabel;

	protected override bool IsDraggable => refuelable.Props.targetSecondaryFuelLevelConfigurable;

	protected override string BarLabel => GenText.ToStringDecimalIfSmall(refuelable.SecondaryFuel) + " / " + GenText.ToStringDecimalIfSmall(refuelable.Props.secondaryFuelCapacity);

	protected override bool DraggingBar { get; set; }

	public Gizmo_SetSecondaryFuelLevel(CompRefuelable_DualFuel refuelable)
	{
		this.refuelable = refuelable;
	}

	public override GizmoResult GizmoOnGUI(Vector2 topLeft, float maxWidth, GizmoRenderParms parms)
	{
		//IL_0012: Unknown result type (might be due to invalid IL or missing references)
		//IL_0014: Unknown result type (might be due to invalid IL or missing references)
		//IL_0015: Unknown result type (might be due to invalid IL or missing references)
		_ = refuelable.Props.showAllowAutoRefuelSecondaryToggle;
		return ((Gizmo_Slider)this).GizmoOnGUI(topLeft, maxWidth, parms);
	}

	protected override void DrawHeader(Rect headerRect, ref bool mouseOverElement)
	{
		//IL_00bd: Unknown result type (might be due to invalid IL or missing references)
		//IL_0047: Unknown result type (might be due to invalid IL or missing references)
		//IL_005f: Unknown result type (might be due to invalid IL or missing references)
		//IL_008a: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ad: Unknown result type (might be due to invalid IL or missing references)
		if (refuelable.Props.showAllowAutoRefuelSecondaryToggle)
		{
			((Rect)(ref headerRect)).xMax = ((Rect)(ref headerRect)).xMax - 24f;
			Rect val = default(Rect);
			((Rect)(ref val))._002Ector(((Rect)(ref headerRect)).xMax, ((Rect)(ref headerRect)).y, 24f, 24f);
			GUI.DrawTexture(val, (Texture)(object)refuelable.Props.SecondaryFuelIcon);
			GUI.DrawTexture(new Rect(((Rect)(ref val)).center.x, ((Rect)(ref val)).y, ((Rect)(ref val)).width / 2f, ((Rect)(ref val)).height / 2f), (Texture)(object)(refuelable.allowAutoRefuelSecondary ? Widgets.CheckboxOnTex : Widgets.CheckboxOffTex));
			if (Widgets.ButtonInvisible(val, true))
			{
				ToggleAutoRefuel();
			}
		}
		((Gizmo_Slider)this).DrawHeader(headerRect, ref mouseOverElement);
	}

	private void ToggleAutoRefuel()
	{
		refuelable.allowAutoRefuelSecondary = !refuelable.allowAutoRefuelSecondary;
		if (refuelable.allowAutoRefuelSecondary)
		{
			SoundStarter.PlayOneShotOnCamera(SoundDefOf.Tick_High, (Map)null);
		}
		else
		{
			SoundStarter.PlayOneShotOnCamera(SoundDefOf.Tick_Low, (Map)null);
		}
	}

	protected override string GetTooltip()
	{
		return "";
	}
}
