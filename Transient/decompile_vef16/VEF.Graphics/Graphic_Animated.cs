using UnityEngine;
using Verse;

namespace VEF.Graphics;

public class Graphic_Animated : Graphic_Collection
{
	private readonly int offset = Rand.Range(1, 1000);

	public override Material MatSingle
	{
		get
		{
			Graphic curFrame = CurFrame;
			if (curFrame == null)
			{
				return null;
			}
			return curFrame.MatSingle;
		}
	}

	private Graphic CurFrame
	{
		get
		{
			Graphic[] subGraphics = base.subGraphics;
			if (subGraphics == null)
			{
				return null;
			}
			Game game = Current.Game;
			int? obj;
			if (game == null)
			{
				obj = null;
			}
			else
			{
				TickManager tickManager = game.tickManager;
				obj = ((tickManager != null) ? new int?(tickManager.TicksGame) : ((int?)null));
			}
			return subGraphics[Mathf.FloorToInt(((((float?)obj) ?? 0f) + (float)offset) / (float)((GraphicData_Animated)(object)((Graphic)this).data).ticksPerFrame) % base.subGraphics.Length];
		}
	}

	public int SubGraphicCount => base.subGraphics.Length - 1;

	public override void DrawWorker(Vector3 loc, Rot4 rot, ThingDef thingDef, Thing thing, float extraRotation)
	{
		//IL_003c: Unknown result type (might be due to invalid IL or missing references)
		//IL_003d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0024: Unknown result type (might be due to invalid IL or missing references)
		//IL_0025: Unknown result type (might be due to invalid IL or missing references)
		if (thing is IAnimationOneTime animationOneTime)
		{
			int num = animationOneTime.CurrentIndex();
			Graphic[] subGraphics = base.subGraphics;
			if (subGraphics != null)
			{
				Graphic obj = subGraphics[num];
				if (obj != null)
				{
					obj.DrawWorker(loc, rot, thingDef, thing, extraRotation);
				}
			}
		}
		else
		{
			Graphic curFrame = CurFrame;
			if (curFrame != null)
			{
				curFrame.DrawWorker(loc, rot, thingDef, thing, extraRotation);
			}
		}
	}
}
