using UnityEngine;
using Verse;

namespace VEF.AnimalBehaviours;

public class HediffCompProperties_SpawnMote : HediffCompProperties
{
	public ThingDef moteDef;

	public Vector3 offset;

	public float maxScale;

	public HediffCompProperties_SpawnMote()
	{
		base.compClass = typeof(HediffComp_SpawnMote);
	}
}
