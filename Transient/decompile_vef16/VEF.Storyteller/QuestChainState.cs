using System;
using System.Collections.Generic;
using Verse;

namespace VEF.Storyteller;

public class QuestChainState : IExposable
{
	private List<Pawn> deepSavedPawns = new List<Pawn>();

	private Dictionary<string, Pawn> uniquePawnsByTag = new Dictionary<string, Pawn>();

	private List<string> tagKeys;

	private List<Pawn> pawnValues;

	public void ExposeData()
	{
		//IL_0037: Unknown result type (might be due to invalid IL or missing references)
		//IL_003d: Invalid comparison between Unknown and I4
		Scribe_Collections.Look<Pawn>(ref deepSavedPawns, "deepSavedPawns", (LookMode)2, Array.Empty<object>());
		Scribe_Collections.Look<string, Pawn>(ref uniquePawnsByTag, "uniquePawnsByTag", (LookMode)1, (LookMode)3, ref tagKeys, ref pawnValues, true, false, false);
		if ((int)Scribe.mode == 4)
		{
			if (deepSavedPawns == null)
			{
				deepSavedPawns = new List<Pawn>();
			}
			if (uniquePawnsByTag == null)
			{
				uniquePawnsByTag = new Dictionary<string, Pawn>();
			}
			deepSavedPawns.RemoveAll((Pawn p) => p == null);
			GenCollection.RemoveAll<string, Pawn>(uniquePawnsByTag, (Predicate<KeyValuePair<string, Pawn>>)((KeyValuePair<string, Pawn> pair) => pair.Value == null));
		}
	}

	public void StoreUniquePawn(string tag, Pawn pawn, bool deepSave)
	{
		if (!uniquePawnsByTag.ContainsKey(tag))
		{
			uniquePawnsByTag[tag] = pawn;
		}
		if (deepSave)
		{
			deepSavedPawns.Add(pawn);
		}
	}

	public void RemoveFromDeepSave(Pawn pawn)
	{
		deepSavedPawns.Remove(pawn);
	}

	public Pawn GetUniquePawn(string tag)
	{
		uniquePawnsByTag.TryGetValue(tag, out var value);
		return value;
	}
}
