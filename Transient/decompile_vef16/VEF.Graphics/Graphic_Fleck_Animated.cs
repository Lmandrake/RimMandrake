using UnityEngine;
using Verse;

namespace VEF.Graphics;

public class Graphic_Fleck_Animated : Graphic_FleckCollection
{
	public override void DrawFleck(FleckDrawData drawData, DrawBatch batch)
	{
		//IL_007c: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ac: Unknown result type (might be due to invalid IL or missing references)
		GraphicData_Animated graphicData_Animated = (GraphicData_Animated)(object)((Graphic)this).data;
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
		float num = ((float?)obj) ?? 0f;
		int num2 = ((!graphicData_Animated.random) ? (Mathf.FloorToInt(drawData.ageSecs * 60f / (float)graphicData_Animated.ticksPerFrame) % subGraphics.Length) : (Mathf.FloorToInt(num / (float)graphicData_Animated.ticksPerFrame) % subGraphics.Length));
		Graphic_Fleck[] array = subGraphics;
		if (array != null)
		{
			array[num2].DrawFleck(drawData, batch);
		}
	}
}
