using System;
using System.Collections.Generic;
using System.Linq;
using Verse;

namespace BigAndSmall;

public static class BodyDefFusionsHelper
{
	private static List<BodyDefFusion> instances = null;

	public static List<MergableBody> MergabeWithSetBodies = MergableBodies.Where((MergableBody x) => x.fuseSet).ToList();

	private static Dictionary<ThingDef, List<HediffDef>> _racesAndTrackers = null;

	private static List<HashSet<HediffDef>> substitutableTrackers = null;

	public static List<BodyDefFusion> Instances => instances ?? (instances = DefDatabase<BodyDefFusion>.AllDefs.ToList());

	public static List<MergableBody> MergableBodies => Instances.SelectMany((BodyDefFusion x) => x.mergableBody).ToList();

	public static List<SimilarParts> PartSets => Instances.SelectMany((BodyDefFusion x) => x.similarParts).ToList();

	public static List<BodyPartDef> PartsToSkip => Instances.SelectMany((BodyDefFusion x) => x.bodyPartToSkip).ToList();

	public static List<Substitutions> Substitutions => Instances.SelectMany((BodyDefFusion x) => x.substitutions).ToList();

	public static List<RetainableTrackers> RetainableTrackers => Instances.SelectMany((BodyDefFusion x) => x.retainableTrackers).ToList();

	public static Dictionary<ThingDef, List<HediffDef>> RacesAndTrackers => _racesAndTrackers ?? (_racesAndTrackers = (from x in DefDatabase<ThingDef>.AllDefsListForReading
		where GenCollection.Any<RaceExtension>(x.GetRaceExtensions())
		select (x: x, x.GetRaceExtensions().SelectMany((RaceExtension y) => y.RaceHediffs).ToList())).ToDictionary(((ThingDef x, List<HediffDef>) x) => x.x, ((ThingDef x, List<HediffDef>) x) => x.Item2));

	public static List<HashSet<HediffDef>> GetSubstitutableTrackers(HediffDef trackerOne)
	{
		if (substitutableTrackers == null)
		{
			SetupSubstitutableTrackers();
			Log.Warning("Substitutable trackers not set up. This should be done before this runs. It will not perform as expected.");
		}
		return substitutableTrackers.Where((HashSet<HediffDef> x) => x.Contains(trackerOne)).ToList();
	}

	public static void SetupSubstitutableTrackers()
	{
		Dictionary<BodyDef, HashSet<HediffDef>> dictionary = new Dictionary<BodyDef, HashSet<HediffDef>>();
		foreach (RetainableTrackers retainableTracker in RetainableTrackers)
		{
			Dictionary<BodyDef, HashSet<HediffDef>> dictionary2 = dictionary;
			BodyDef target = retainableTracker.target;
			HashSet<HediffDef> hashSet = new HashSet<HediffDef>();
			foreach (HediffDef raceTracker in retainableTracker.raceTrackers)
			{
				hashSet.Add(raceTracker);
			}
			dictionary2.Add(target, hashSet);
		}
		foreach (var item3 in RacesAndTrackers.Select((KeyValuePair<ThingDef, List<HediffDef>> x) => (Key: x.Key, Value: x.Value)))
		{
			ThingDef item = item3.Key;
			List<HediffDef> item2 = item3.Value;
			BodyDef body = item.race.body;
			if (!dictionary.ContainsKey(body))
			{
				dictionary[body] = new HashSet<HediffDef>();
			}
			foreach (HediffDef item4 in item2)
			{
				dictionary[body].Add(item4);
			}
		}
		substitutableTrackers = dictionary.Values.ToList();
	}

	public static float? Equavalence(BodyPartDef partOne, BodyPartDef partTwo)
	{
		float? result = null;
		foreach (SimilarParts partSet in PartSets)
		{
			if (partSet.Parts.Contains(partOne) && partSet.Parts.Contains(partTwo))
			{
				result = Math.Max(result.GetValueOrDefault(), partSet.similarity);
			}
		}
		return result;
	}
}
