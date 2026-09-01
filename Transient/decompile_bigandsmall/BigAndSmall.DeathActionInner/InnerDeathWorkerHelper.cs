using System.Collections.Generic;
using RimWorld;
using Verse;

namespace BigAndSmall.DeathActionInner;

public static class InnerDeathWorkerHelper
{
	public static void BigExplosion(Corpse corpse, Pawn posessor, BodyPartRecord mainPart)
	{
		//IL_0031: Unknown result type (might be due to invalid IL or missing references)
		//IL_009b: Unknown result type (might be due to invalid IL or missing references)
		//IL_006f: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e0: Unknown result type (might be due to invalid IL or missing references)
		if (corpse.InnerPawn.BodySize > 1.5f)
		{
			((Thing)posessor).TakeDamage(new DamageInfo(DamageDefOf.Bomb, 120f, 0f, -1f, (Thing)null, mainPart, (ThingDef)null, (SourceCategory)0, (Thing)null, true, true, (QualityCategory)2, true, false));
		}
		else if (corpse.InnerPawn.BodySize > 1f)
		{
			((Thing)posessor).TakeDamage(new DamageInfo(DamageDefOf.Bomb, 60f, 0f, -1f, (Thing)null, mainPart, (ThingDef)null, (SourceCategory)0, (Thing)null, true, true, (QualityCategory)2, true, false));
		}
		else
		{
			((Thing)posessor).TakeDamage(new DamageInfo(DamageDefOf.Bomb, 30f, 0f, -1f, (Thing)null, mainPart, (ThingDef)null, (SourceCategory)0, (Thing)null, true, true, (QualityCategory)2, true, false));
		}
		float num = ((corpse.InnerPawn.ageTracker.CurLifeStageIndex == 0) ? 1.9f : ((corpse.InnerPawn.ageTracker.CurLifeStageIndex != 1) ? 4.9f : 2.9f));
		GenExplosion.DoExplosion(((Thing)posessor).Position, ((Thing)posessor).Map, num, DamageDefOf.Flame, (Thing)(object)corpse.InnerPawn, -1, -1f, (SoundDef)null, (ThingDef)null, (ThingDef)null, (Thing)null, (ThingDef)null, 0f, 1, (GasType?)null, (float?)null, 255, false, (ThingDef)null, 0f, 1, 0f, false, (float?)null, (List<Thing>)null, (FloatRange?)null, true, 1f, 0f, true, (ThingDef)null, 1f, (SimpleCurve)null, (List<IntVec3>)null, (ThingDef)null, (ThingDef)null);
	}

	public static void SmallExplosion(Corpse corpse, Pawn posessor, BodyPartRecord mainPart)
	{
		//IL_001f: Unknown result type (might be due to invalid IL or missing references)
		//IL_002b: Unknown result type (might be due to invalid IL or missing references)
		((Thing)posessor).TakeDamage(new DamageInfo(DamageDefOf.Bomb, 20f, 0f, -1f, (Thing)null, mainPart, (ThingDef)null, (SourceCategory)0, (Thing)null, true, true, (QualityCategory)2, true, false));
		GenExplosion.DoExplosion(((Thing)posessor).Position, ((Thing)posessor).Map, 1.9f, DamageDefOf.Flame, (Thing)(object)corpse.InnerPawn, 10, -1f, (SoundDef)null, (ThingDef)null, (ThingDef)null, (Thing)null, (ThingDef)null, 0f, 1, (GasType?)null, (float?)null, 255, false, (ThingDef)null, 0f, 1, 0f, false, (float?)null, (List<Thing>)null, (FloatRange?)null, true, 1f, 0f, true, (ThingDef)null, 1f, (SimpleCurve)null, (List<IntVec3>)null, (ThingDef)null, (ThingDef)null);
	}
}
