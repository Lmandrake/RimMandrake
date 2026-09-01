using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace BigAndSmall;

public class GrowthRayHediff : HediffWithComps
{
	public override float Severity
	{
		get
		{
			return ((Hediff)this).Severity;
		}
		set
		{
			((Hediff)this).Severity = value;
			HumanoidPawnScaler.GetCache(((Hediff)this).pawn, forceRefresh: true);
			((Hediff)this).pawn.Drawer.renderer.SetAllGraphicsDirty();
		}
	}

	public override void Tick()
	{
		//IL_0059: Unknown result type (might be due to invalid IL or missing references)
		//IL_007b: Unknown result type (might be due to invalid IL or missing references)
		//IL_01c1: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e3: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e9: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ee: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f3: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f5: Unknown result type (might be due to invalid IL or missing references)
		//IL_00fc: Unknown result type (might be due to invalid IL or missing references)
		//IL_0104: Unknown result type (might be due to invalid IL or missing references)
		//IL_010b: Unknown result type (might be due to invalid IL or missing references)
		((Hediff)this).Tick();
		if (Find.TickManager.TicksGame % 200 == 0)
		{
			HumanoidPawnScaler.GetCache(((Hediff)this).pawn, forceRefresh: true);
			((Hediff)this).pawn.Drawer.renderer.SetAllGraphicsDirty();
		}
		if (!(((Hediff)this).Severity >= ((Hediff)this).def.lethalSeverity))
		{
			return;
		}
		foreach (IntVec3 item in GenRadial.RadialCellsAround(((Thing)((Hediff)this).pawn).Position, ((Hediff)this).pawn.BodySize, true))
		{
			foreach (Thing thing in GridsUtility.GetThingList(item, ((Thing)((Hediff)this).pawn).Map))
			{
				if (thing == null)
				{
					continue;
				}
				Pawn val = (Pawn)(object)((thing is Pawn) ? thing : null);
				if (val != null)
				{
					Pawn_HealthTracker health = val.health;
					object obj;
					if (health == null)
					{
						obj = null;
					}
					else
					{
						HediffSet hediffSet = health.hediffSet;
						obj = ((hediffSet != null) ? hediffSet.GetFirstHediffOfDef(((Hediff)this).def, false) : null);
					}
					Hediff val2 = (Hediff)obj;
					IntVec3 val3 = ((Thing)((Hediff)this).pawn).Position - ((Thing)val).Position;
					float num = Mathf.Sqrt((float)(val3.x * val3.x + val3.z * val3.z));
					float num2 = 0.25f / Mathf.Max(1f, num) * Mathf.Sqrt(((Hediff)this).pawn.BodySize);
					if (val2 == null)
					{
						val2 = HediffMaker.MakeHediff(((Hediff)this).def, val, (BodyPartRecord)null);
						val2.Severity = num2;
						val.health.AddHediff(val2, (BodyPartRecord)null, (DamageInfo?)null, (DamageResult)null);
					}
					else
					{
						Hediff obj2 = val2;
						obj2.Severity += num2;
					}
				}
			}
		}
		GenExplosion.DoExplosion(((Thing)((Hediff)this).pawn).Position, ((Thing)((Hediff)this).pawn).Map, Mathf.Sqrt(((Hediff)this).pawn.BodySize) * 1.5f, DamageDefOf.Bomb, (Thing)null, (int)(Mathf.Sqrt(((Hediff)this).pawn.BodySize) * 6f), 1f, (SoundDef)null, (ThingDef)null, (ThingDef)null, (Thing)null, (ThingDef)null, 0f, 1, (GasType?)null, (float?)null, 255, false, (ThingDef)null, 0f, 1, 0f, false, (float?)null, (List<Thing>)null, (FloatRange?)null, true, 1f, 0f, true, (ThingDef)null, 1f, (SimpleCurve)null, (List<IntVec3>)null, (ThingDef)null, (ThingDef)null);
		((Hediff)this).Severity = 1f;
		((Thing)((Hediff)this).pawn).Kill((DamageInfo?)null, (Hediff)null);
	}

	public override bool CauseDeathNow()
	{
		return false;
	}
}
