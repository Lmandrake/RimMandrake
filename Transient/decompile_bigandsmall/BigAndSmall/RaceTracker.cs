using System;
using System.Collections.Generic;
using Verse;

namespace BigAndSmall;

public class RaceTracker : HediffWithComps
{
	private List<PawnExtension> pawnExtensions;

	public override bool Visible => true;

	public List<PawnExtension> PawnExtensions => pawnExtensions ?? (pawnExtensions = ((Hediff)this).def.ExtensionsOnDef<PawnExtension, HediffDef>((List<Type>)null, (List<Type>)null, doSort: true));

	public override float PainOffset => 0f;

	public override void PostAdd(DamageInfo? info)
	{
		((Hediff)this).def.isBad = false;
		((Hediff)this).def.everCurableByItem = false;
		((HediffWithComps)this).PostAdd(info);
	}

	public override void PostRemoved()
	{
		((HediffWithComps)this).PostRemoved();
	}

	public override void PostTick()
	{
	}

	public override void Tick()
	{
	}

	public override void Tended(float quality, float maxQuality, int batchPosition = 0)
	{
	}

	/// <summary>
	/// Note: This is the ONLY tick event that runs on a race-tracker.
	/// Others are skipepd for performance reasons.
	/// </summary>
	public override void PostTickInterval(int interval)
	{
		((HediffWithComps)this).PostTickInterval(interval);
	}
}
