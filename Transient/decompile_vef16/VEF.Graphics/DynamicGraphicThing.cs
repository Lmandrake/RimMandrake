using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace VEF.Graphics;

public class DynamicGraphicThing : ThingWithComps, IDynamicGraphic
{
	protected readonly DynamicGraphicBaseThing baseThing = new DynamicGraphicBaseThing();

	private Pawn pawn;

	private Faction faction;

	private bool stateChanged = true;

	public List<Graphic> GetDynamicGraphics()
	{
		List<Graphic> result = baseThing.DynamicGraphics((Thing)(object)this, stateChanged, (Thing)(object)pawn, faction);
		stateChanged = false;
		return result;
	}

	protected override void DrawAt(Vector3 drawLoc, bool flip = false)
	{
		//IL_002f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0030: Unknown result type (might be due to invalid IL or missing references)
		//IL_0037: Unknown result type (might be due to invalid IL or missing references)
		//IL_003c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0042: Unknown result type (might be due to invalid IL or missing references)
		List<Graphic> list = baseThing.DynamicGraphics((Thing)(object)this, stateChanged, (Thing)(object)pawn, faction);
		for (int i = 0; i < list.Count; i++)
		{
			Graphic val = list[i];
			if (val != null)
			{
				val.Draw(drawLoc + Altitudes.AltIncVect * (float)i, ((Thing)this).Rotation, (Thing)(object)this, 0f);
			}
		}
		stateChanged = false;
	}

	public override void Notify_Equipped(Pawn pawn)
	{
		this.pawn = pawn;
		faction = ((Thing)pawn).Faction;
		((ThingWithComps)this).Notify_Equipped(pawn);
		stateChanged = true;
	}

	public override void Notify_Unequipped(Pawn pawn)
	{
		((ThingWithComps)this).Notify_Unequipped(pawn);
		this.pawn = null;
	}

	public override void Notify_ColorChanged()
	{
		baseThing.Dirty();
		((ThingWithComps)this).Notify_ColorChanged();
	}

	public override void ExposeData()
	{
		((ThingWithComps)this).ExposeData();
		Scribe_References.Look<Pawn>(ref pawn, "pawn", false);
		Scribe_References.Look<Faction>(ref faction, "faction", false);
	}
}
