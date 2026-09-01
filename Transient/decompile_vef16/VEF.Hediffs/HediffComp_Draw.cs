using UnityEngine;
using Verse;

namespace VEF.Hediffs;

public class HediffComp_Draw : HediffComp
{
	public virtual Graphic Graphic
	{
		get
		{
			HediffCompProperties_Draw obj = base.props as HediffCompProperties_Draw;
			if (obj == null)
			{
				return null;
			}
			GraphicData graphic = obj.graphic;
			if (graphic == null)
			{
				return null;
			}
			return graphic.Graphic;
		}
	}

	public virtual void DrawAt(Vector3 drawPos)
	{
		//IL_000b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0012: Unknown result type (might be due to invalid IL or missing references)
		Graphic graphic = Graphic;
		if (graphic != null)
		{
			graphic.Draw(drawPos, ((Thing)((HediffComp)this).Pawn).Rotation, (Thing)(object)((HediffComp)this).Pawn, 0f);
		}
	}

	public override void CompPostPostAdd(DamageInfo? dinfo)
	{
		((HediffComp)this).CompPostPostAdd(dinfo);
		if (ShieldsSystem.HediffDrawsByPawn.TryGetValue(((HediffComp)this).Pawn, out var value))
		{
			value.Add(this);
		}
	}

	public override void CompPostPostRemoved()
	{
		((HediffComp)this).CompPostPostRemoved();
		if (ShieldsSystem.HediffDrawsByPawn.TryGetValue(((HediffComp)this).Pawn, out var value))
		{
			value.Remove(this);
		}
	}
}
