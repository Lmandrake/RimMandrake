using Verse;

namespace VEF.Weapons;

public abstract class SpinningLaserGunBase : LaserGun
{
	public enum State
	{
		Idle,
		Spinup,
		Spinning
	}

	private int previousTick;

	public State state;

	private float rotation;

	private float rotationSpeed;

	private float targetRotationSpeed;

	private float rotationAcceleration;

	private int rotationAccelerationTicksRemaing;

	public new SpinningLaserGunDef def => base.def as SpinningLaserGunDef;

	public override Graphic Graphic
	{
		get
		{
			if (def.frames.Count == 0)
			{
				return ((Thing)this).DefaultGraphic;
			}
			UpdateState();
			int ticksGame = Find.TickManager.TicksGame;
			Graphic graphicForTick = GetGraphicForTick(ticksGame - previousTick);
			previousTick = ticksGame;
			return graphicForTick;
		}
	}

	public void ReachRotationSpeed(float target, int ticksUntil)
	{
		targetRotationSpeed = target;
		if (ticksUntil <= 0)
		{
			rotationAccelerationTicksRemaing = 0;
			rotationSpeed = target;
		}
		rotationAccelerationTicksRemaing = ticksUntil;
		rotationAcceleration = (target - rotationSpeed) / (float)ticksUntil;
	}

	private Graphic GetGraphicForTick(int ticksPassed)
	{
		//IL_00a8: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b8: Unknown result type (might be due to invalid IL or missing references)
		if (rotationAccelerationTicksRemaing > 0)
		{
			if (ticksPassed > rotationAccelerationTicksRemaing)
			{
				ticksPassed = rotationAccelerationTicksRemaing;
			}
			rotationAccelerationTicksRemaing -= ticksPassed;
			rotationSpeed += (float)ticksPassed * rotationAcceleration;
			if (rotationAccelerationTicksRemaing <= 0)
			{
				rotationSpeed = targetRotationSpeed;
			}
		}
		rotation += rotationSpeed * (float)ticksPassed;
		int index = (int)rotation % def.frames.Count;
		return def.frames[index].Graphic.GetColoredVersion(ShaderDatabase.CutoutComplex, ((ThingDef)def).graphicData.color, ((ThingDef)def).graphicData.colorTwo);
	}

	public abstract void UpdateState();
}
