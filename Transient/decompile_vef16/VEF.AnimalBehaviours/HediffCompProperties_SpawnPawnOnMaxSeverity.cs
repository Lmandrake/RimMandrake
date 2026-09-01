using System.Collections.Generic;
using Verse;

namespace VEF.AnimalBehaviours;

public class HediffCompProperties_SpawnPawnOnMaxSeverity : HediffCompProperties
{
	public List<PawnKindDef> pawnKindOptions = new List<PawnKindDef>();

	public ThingDef filthCreated;

	public IntRange filthCountRange;

	public SoundDef sound;

	public DamageDef damage;

	public FloatRange damageAmount;

	public HediffCompProperties_SpawnPawnOnMaxSeverity()
	{
		base.compClass = typeof(HediffComp_SpawnPawnOnMaxSeverity);
	}
}
