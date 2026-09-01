using System.Collections.Generic;
using UnityEngine;
using Verse;

namespace VEF.Graphics;

public class DynamicGraphicBuilding : Building, IDynamicGraphic
{
	protected readonly DynamicGraphicBaseThing baseThing = new DynamicGraphicBaseThing();

	public List<Graphic> GetDynamicGraphics()
	{
		return baseThing.DynamicGraphics((Thing)(object)this);
	}

	protected override void DrawAt(Vector3 drawLoc, bool flip = false)
	{
		//IL_0020: Unknown result type (might be due to invalid IL or missing references)
		//IL_0021: Unknown result type (might be due to invalid IL or missing references)
		//IL_0028: Unknown result type (might be due to invalid IL or missing references)
		//IL_002d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0033: Unknown result type (might be due to invalid IL or missing references)
		List<Graphic> list = baseThing.DynamicGraphics((Thing)(object)this);
		for (int i = 0; i < list.Count; i++)
		{
			Graphic val = list[i];
			if (val != null)
			{
				val.Draw(drawLoc + Altitudes.AltIncVect * (float)i, ((Thing)this).Rotation, (Thing)(object)this, 0f);
			}
		}
	}

	public override void Notify_ColorChanged()
	{
		baseThing.Dirty();
		((ThingWithComps)this).Notify_ColorChanged();
	}
}
