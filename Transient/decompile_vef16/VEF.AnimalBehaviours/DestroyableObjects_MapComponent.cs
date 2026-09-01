using System.Collections.Generic;
using Verse;

namespace VEF.AnimalBehaviours;

public class DestroyableObjects_MapComponent : MapComponent
{
	public HashSet<Thing> objects_InMap = new HashSet<Thing>();

	public DestroyableObjects_MapComponent(Map map)
		: base(map)
	{
	}

	public override void FinalizeInit()
	{
		((MapComponent)this).FinalizeInit();
	}

	public void AddObjectToMap(Thing thing)
	{
		if (!objects_InMap.Contains(thing))
		{
			objects_InMap.Add(thing);
		}
	}

	public void RemoveObjectFromMap(Thing thing)
	{
		if (objects_InMap.Contains(thing))
		{
			objects_InMap.Remove(thing);
		}
	}
}
