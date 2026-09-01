using System.Collections.Generic;
using Verse;

namespace VEF.Pawns;

public class PawnKindDefExtension : DefModExtension
{
	private static readonly PawnKindDefExtension DefaultValues = new PawnKindDefExtension();

	public List<BodyPartGroupDef> factionColourApparelPartList;

	public List<ApparelLayerDef> factionColourApparelLayerList;

	public List<string> shieldTags;

	public FloatRange shieldMoney;

	[Unsaved(false)]
	private List<Pair<BodyPartGroupDef, ApparelLayerDef>> _factionColourApparelWithPartAndLayersList;

	public List<Pair<BodyPartGroupDef, ApparelLayerDef>> FactionColourApparelWithPartAndLayersList
	{
		get
		{
			//IL_0045: Unknown result type (might be due to invalid IL or missing references)
			if (_factionColourApparelWithPartAndLayersList == null)
			{
				_factionColourApparelWithPartAndLayersList = new List<Pair<BodyPartGroupDef, ApparelLayerDef>>();
				if (factionColourApparelPartList != null && factionColourApparelLayerList != null)
				{
					for (int i = 0; i < factionColourApparelPartList.Count; i++)
					{
						_factionColourApparelWithPartAndLayersList.Add(new Pair<BodyPartGroupDef, ApparelLayerDef>(factionColourApparelPartList[i], factionColourApparelLayerList[i]));
					}
				}
			}
			return _factionColourApparelWithPartAndLayersList;
		}
	}

	public static PawnKindDefExtension Get(Def def)
	{
		return def.GetModExtension<PawnKindDefExtension>() ?? DefaultValues;
	}

	public override IEnumerable<string> ConfigErrors()
	{
		if (factionColourApparelPartList != null && factionColourApparelLayerList != null && factionColourApparelPartList.Count != factionColourApparelLayerList.Count)
		{
			yield return "factionColourApparelPartList and factionColourApparelLayerList must be of the same length.";
		}
	}
}
