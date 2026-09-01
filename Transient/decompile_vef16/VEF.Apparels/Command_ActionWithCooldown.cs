using UnityEngine;
using Verse;

namespace VEF.Apparels;

[StaticConstructorOnStartup]
public class Command_ActionWithCooldown : Command_Action
{
	private static readonly Texture2D cooldownBarTex = SolidColorMaterials.NewSolidColorTexture(new Color(Color.grey.r, Color.grey.g, Color.grey.b, 0.6f));

	private int lastUsedTick;

	private int cooldownTicks;

	public Command_ActionWithCooldown(int lastUsedTick, int cooldownTicks)
	{
		this.lastUsedTick = lastUsedTick;
		this.cooldownTicks = cooldownTicks;
	}

	public override GizmoResult GizmoOnGUI(Vector2 topLeft, float maxWidth, GizmoRenderParms parms)
	{
		//IL_0002: Unknown result type (might be due to invalid IL or missing references)
		//IL_0008: Unknown result type (might be due to invalid IL or missing references)
		//IL_0020: Unknown result type (might be due to invalid IL or missing references)
		//IL_0022: Unknown result type (might be due to invalid IL or missing references)
		//IL_0023: Unknown result type (might be due to invalid IL or missing references)
		//IL_0028: Unknown result type (might be due to invalid IL or missing references)
		//IL_0077: Unknown result type (might be due to invalid IL or missing references)
		//IL_007d: Invalid comparison between Unknown and I4
		//IL_0083: Unknown result type (might be due to invalid IL or missing references)
		//IL_0088: Unknown result type (might be due to invalid IL or missing references)
		//IL_007f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0061: Unknown result type (might be due to invalid IL or missing references)
		//IL_006f: Unknown result type (might be due to invalid IL or missing references)
		Rect val = default(Rect);
		((Rect)(ref val))._002Ector(topLeft.x, topLeft.y, ((Gizmo)this).GetWidth(maxWidth), 75f);
		GizmoResult result = ((Command)this).GizmoOnGUI(topLeft, maxWidth, parms);
		if (lastUsedTick > 0)
		{
			int num = Find.TickManager.TicksGame - lastUsedTick;
			if (num < cooldownTicks)
			{
				float num2 = Mathf.InverseLerp((float)cooldownTicks, 0f, (float)num);
				Widgets.FillableBar(val, Mathf.Clamp01(num2), cooldownBarTex, (Texture2D)null, false);
			}
		}
		if ((int)((GizmoResult)(ref result)).State == 2)
		{
			return result;
		}
		return new GizmoResult(((GizmoResult)(ref result)).State);
	}
}
