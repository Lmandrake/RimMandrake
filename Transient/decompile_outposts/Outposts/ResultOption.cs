using System.Collections.Generic;
using System.Linq;
using UnityEngine;
using Verse;

namespace Outposts;

public class ResultOption
{
	public int AmountPerPawn;

	public List<AmountBySkill> AmountsPerSkills;

	public int BaseAmount;

	public List<AmountBySkill> MinSkills;

	public ThingDef Thing;

	public int Amount(List<Pawn> pawns)
	{
		return Mathf.RoundToInt((float)(BaseAmount + AmountPerPawn * pawns.Count + (AmountsPerSkills?.Sum((AmountBySkill x) => x.Amount(pawns)) ?? 0)) * OutpostsMod.Settings.ProductionMultiplier);
	}

	public IEnumerable<Thing> Make(List<Pawn> pawns)
	{
		return Thing.Make(Amount(pawns));
	}

	public string Explain(List<Pawn> pawns)
	{
		//IL_0017: Unknown result type (might be due to invalid IL or missing references)
		return $"{Amount(pawns)}x {((Def)Thing).LabelCap}";
	}
}
