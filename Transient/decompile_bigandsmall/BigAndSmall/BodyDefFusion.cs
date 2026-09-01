using System.Collections.Generic;
using Verse;

namespace BigAndSmall;

public class BodyDefFusion : Def
{
	public List<MergableBody> mergableBody = new List<MergableBody>();

	public List<Substitutions> substitutions = new List<Substitutions>();

	public List<RetainableTrackers> retainableTrackers = new List<RetainableTrackers>();

	public List<SimilarParts> similarParts = new List<SimilarParts>();

	public List<BodyPartDef> bodyPartToSkip = new List<BodyPartDef>();
}
