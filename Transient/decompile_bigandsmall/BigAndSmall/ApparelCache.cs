using System;
using RimWorld;
using UnityEngine;
using Verse;

namespace BigAndSmall;

public class ApparelCache : IExposable
{
	public string apparelID;

	public int highestSeenDurability = 1;

	public int lastSeenTick;

	public float accumulatedHp;

	public ApparelCache()
	{
	}

	public ApparelCache(Apparel apparel)
	{
		apparelID = ((Thing)apparel).ThingID;
		highestSeenDurability = ((Thing)apparel).HitPoints;
		lastSeenTick = Find.TickManager.TicksGame;
	}

	public void RepairDurability(Apparel apparel, int currentTick, float fractionPerDay)
	{
		highestSeenDurability = Mathf.Max(highestSeenDurability, ((Thing)apparel).HitPoints);
		int num = 60000;
		float num2 = (float)(currentTick - lastSeenTick) / (float)num * fractionPerDay;
		float num3 = (float)Mathf.Max(((Thing)apparel).MaxHitPoints, 50) / 50f;
		int maxHitPoints = ((Thing)apparel).MaxHitPoints;
		int hitPoints = ((Thing)apparel).HitPoints;
		float num4 = Mathf.Abs(num2 * (float)(maxHitPoints - hitPoints) * num3);
		accumulatedHp += num4;
		if (accumulatedHp > 1f)
		{
			int val = hitPoints + (int)accumulatedHp;
			val = Math.Min(maxHitPoints, val);
			val = Math.Min(val, highestSeenDurability);
			((Thing)apparel).HitPoints = val;
			accumulatedHp = 0f;
		}
		lastSeenTick = currentTick;
	}

	public void RepairAllDurability(Apparel apparel)
	{
		highestSeenDurability = Mathf.Max(highestSeenDurability, ((Thing)apparel).HitPoints);
		((Thing)apparel).HitPoints = highestSeenDurability;
	}

	public void ExposeData()
	{
		Scribe_Values.Look<string>(ref apparelID, "apparelID", (string)null, false);
		Scribe_Values.Look<int>(ref highestSeenDurability, "highestSeenDurability", 0, false);
		Scribe_Values.Look<int>(ref lastSeenTick, "lastSeenTick", 0, false);
		Scribe_Values.Look<float>(ref accumulatedHp, "accumulatedHp", 0f, false);
	}
}
