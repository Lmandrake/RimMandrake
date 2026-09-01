using Verse;

namespace VEF.Graphics;

public class MoteAttachedOneTime : MoteAttached, IAnimationOneTime
{
	public int currentIndex;

	public int CurrentIndex()
	{
		return currentIndex;
	}

	protected override void Tick()
	{
		((Mote)this).Tick();
		if (Gen.IsHashIntervalTick((Thing)(object)this, (((Thing)this).Graphic.data as GraphicData_Animated).ticksPerFrame) && currentIndex < (((Thing)this).Graphic as Graphic_Animated).SubGraphicCount)
		{
			currentIndex++;
		}
	}

	public override void ExposeData()
	{
		((Thing)this).ExposeData();
		Scribe_Values.Look<int>(ref currentIndex, "currentIndex", 0, false);
	}
}
