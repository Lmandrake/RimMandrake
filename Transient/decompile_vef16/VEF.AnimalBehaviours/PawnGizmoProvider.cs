using System.Collections.Generic;
using Verse;

namespace VEF.AnimalBehaviours;

public interface PawnGizmoProvider
{
	IEnumerable<Gizmo> GetGizmos();
}
