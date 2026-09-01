using System.Collections.Generic;
using System.Linq;
using Verse;

namespace BigAndSmall;

public class SimilarParts : Def
{
	public string groupName;

	/// <summary>
	/// Avoid very low values unless you don't want them to merge.
	/// </summary>
	public float similarity = 1f;

	protected List<string> parts = new List<string>();

	private List<BodyPartDef> _partsCache;

	public List<BodyPartDef> Parts => _partsCache ?? (_partsCache = parts.Select((string x) => DefDatabase<BodyPartDef>.GetNamed(x, false)).ToList());
}
