using System;
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;
using Verse.AI;

namespace VEF.AI;

public class DraftedActionData : IExposable
{
	private Pawn pawn;

	public string pawnID;

	public bool hunt;

	public List<AbilityDef> autocastAbilities = new List<AbilityDef>();

	public Pawn Pawn
	{
		get
		{
			if (pawn == null)
			{
				using (IEnumerator<Pawn> enumerator = (Find.Maps?.SelectMany((Map x) => x.mapPawns.AllPawns)).Where((Pawn x) => ((Thing)x).ThingID == pawnID).GetEnumerator())
				{
					if (enumerator.MoveNext())
					{
						Pawn current = enumerator.Current;
						pawn = current;
					}
				}
				if (pawn == null)
				{
					Log.Error("DraftedActionData could not find pawn with ID " + pawnID + ".");
				}
			}
			return pawn;
		}
	}

	public DraftedActionData(Pawn pawn)
	{
		this.pawn = pawn;
		pawnID = ((Thing)pawn).ThingID;
	}

	public DraftedActionData()
	{
	}

	private void RefreshDraft()
	{
		Pawn.jobs.EndCurrentJob((JobCondition)16, true, true);
	}

	public bool ToggleHuntMode()
	{
		hunt = !hunt;
		RefreshDraft();
		return hunt;
	}

	public bool AutoCastFor(AbilityDef def)
	{
		return autocastAbilities.Contains(def);
	}

	public void ToggleAutoForAll()
	{
		if (GenCollection.Empty<AbilityDef>(autocastAbilities) && Pawn?.abilities?.abilities != null)
		{
			foreach (Ability ability in Pawn.abilities.abilities)
			{
				if (ability.def.aiCanUse)
				{
					autocastAbilities.Add(ability.def);
				}
			}
		}
		else
		{
			autocastAbilities.Clear();
		}
		RefreshDraft();
	}

	public void ToggleAutoCastFor(AbilityDef def)
	{
		if (autocastAbilities.Contains(def))
		{
			autocastAbilities.Remove(def);
		}
		else
		{
			autocastAbilities.Add(def);
		}
		RefreshDraft();
	}

	public void ExposeData()
	{
		Scribe_Values.Look<string>(ref pawnID, "pawnID", (string)null, false);
		Scribe_Values.Look<bool>(ref hunt, "huntMode", false, false);
		Scribe_Collections.Look<AbilityDef>(ref autocastAbilities, "autocastAbilities", (LookMode)4, Array.Empty<object>());
	}
}
