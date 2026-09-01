using System;
using System.Collections.Generic;
using System.Linq;
using BigAndSmall.FilteredLists;
using RimWorld;
using Verse;

namespace BigAndSmall;

public class RaceExtension : DefModExtension
{
	protected HediffDef raceHediff;

	private List<HediffDef> raceHediffList = new List<HediffDef>();

	public float? femaleGenderChance;

	public List<ThingDef> isFusionOf;

	public RomanceTags romanceTags;

	public List<HediffDef> RaceHediffs
	{
		get
		{
			if (raceHediff != null)
			{
				List<HediffDef> list = raceHediffList;
				List<HediffDef> list2 = new List<HediffDef>(1 + list.Count);
				list2.AddRange(list);
				list2.Add(raceHediff);
				return list2;
			}
			return raceHediffList;
		}
		private set
		{
			if (value.Count > 0)
			{
				raceHediff = null;
				raceHediffList = value;
			}
			else
			{
				raceHediff = null;
				raceHediffList = new List<HediffDef>();
			}
		}
	}

	public List<PawnExtension> PawnExtensionOnRace => RaceHediffs.ExtensionsOnDefList<PawnExtension, HediffDef>((List<Type>)null, (List<Type>)null, doSort: true);

	public FilterListSet<RecipeDef> SurgeryRecipes => (from pe in PawnExtensionOnRace
		where pe.surgeryRecipes != null
		select pe.surgeryRecipes).Aggregate(new FilterListSet<RecipeDef>(), (FilterListSet<RecipeDef> acc, FilterListSet<RecipeDef> x) => acc.MergeFilters(x));

	/// <summary>
	/// Used only for DefGeneration.
	/// </summary>
	public void SetHediff(HediffDef hediff)
	{
		raceHediff = null;
		raceHediffList = new List<HediffDef>(1) { hediff };
	}

	public RaceExtension()
	{
	}

	public RaceExtension(List<RaceExtension> sources)
	{
		if (sources.Count > 0)
		{
			RaceHediffs = sources.Where((RaceExtension other) => other.RaceHediffs != null).SelectMany((RaceExtension other) => other.RaceHediffs).ToList();
			List<float?> list = (from other in sources
				where other.femaleGenderChance.HasValue
				select other.femaleGenderChance).ToList();
			if (list.Count > 0)
			{
				femaleGenderChance = list.Average();
			}
		}
	}

	public void ApplyTrackerIfMissing(Pawn pawn, BSCache cache = null)
	{
		if (TrackerMissing(pawn))
		{
			ApplyHediffToPawn(pawn, cache);
		}
	}

	public bool TrackerMissing(Pawn pawn)
	{
		List<HediffDef> list = new List<HediffDef>();
		foreach (RaceExtension raceExtension in ((Thing)pawn).def.GetRaceExtensions())
		{
			list.AddRange(raceExtension.RaceHediffs);
		}
		if (list.Count == 0)
		{
			return false;
		}
		List<HashSet<HediffDef>> list2 = new List<HashSet<HediffDef>>();
		foreach (HediffDef item in list)
		{
			List<HashSet<HediffDef>> substitutableTrackers = BodyDefFusionsHelper.GetSubstitutableTrackers(item);
			list2.AddRange(substitutableTrackers);
			if (substitutableTrackers.Count == 0)
			{
				list2.Add(new HashSet<HediffDef> { item });
			}
		}
		foreach (HashSet<HediffDef> item2 in list2)
		{
			if (item2.All((HediffDef h) => !pawn.health.hediffSet.HasHediff(h, false)))
			{
				return true;
			}
		}
		return false;
	}

	private void ApplyHediffToPawn(Pawn pawn, BSCache cache = null)
	{
		if (RaceHediffs.Count > 0)
		{
			List<HediffDef> list = RemoveOldRaceTrackers(pawn).ToList();
			if (cache != null)
			{
				list.AddRange(cache.raceTrackerHistory);
			}
			{
				foreach (HediffDef raceHediff in RaceHediffs)
				{
					HediffDef val = raceHediff;
					List<HashSet<HediffDef>> substitutableTrackers = BodyDefFusionsHelper.GetSubstitutableTrackers(raceHediff);
					HashSet<HediffDef> validSubstitutes = GetValidSubstitutes(list, substitutableTrackers);
					if (GenCollection.Any<HediffDef>(validSubstitutes))
					{
						val = GenCollection.FirstOrFallback<HediffDef>((IEnumerable<HediffDef>)validSubstitutes, raceHediff);
					}
					if (typeof(RaceTracker).IsAssignableFrom(val.hediffClass))
					{
						pawn.health.AddHediff(val, (BodyPartRecord)null, (DamageInfo?)null, (DamageResult)null);
					}
					else
					{
						Log.Error(string.Format("{0}'s raceDef needs to be a {1} or subclass thereof ({2}/{3}).", pawn, "RaceTracker", raceHediff, val));
					}
					if (!val.HasComp(typeof(HediffComp_Race)))
					{
						Log.Error(string.Format("{0}'s raceDef needs to have a {1} component. ({2}/{3})", pawn, "HediffComp_Race", raceHediff, val));
					}
				}
				return;
			}
		}
		Log.Error($"{pawn} has a BigAndSmall.RaceExtension without an associated raceDef!");
	}

	private static HashSet<HediffDef> GetValidSubstitutes(List<HediffDef> allRemovedTrackers, List<HashSet<HediffDef>> substituteSets)
	{
		HashSet<HediffDef> hashSet = new HashSet<HediffDef>();
		foreach (HashSet<HediffDef> substituteSet in substituteSets)
		{
			foreach (HediffDef item in allRemovedTrackers.Where(substituteSet.Contains))
			{
				hashSet.Add(item);
			}
		}
		return hashSet;
	}

	public static List<HediffDef> RemoveOldRaceTrackers(Pawn pawn)
	{
		List<HediffDef> list = new List<HediffDef>();
		IEnumerable<Hediff> enumerable = pawn.health?.hediffSet?.hediffs?.Where((Hediff h) => h is RaceTracker);
		if (enumerable == null)
		{
			return list;
		}
		List<PawnExtension> hediffExtensions = pawn.GetHediffExtensions<PawnExtension>(new List<Type>(1) { typeof(RaceTracker) });
		List<Hediff> list2 = enumerable.ToList();
		for (int num = list2.Count - 1; num >= 0; num--)
		{
			Hediff val = list2[num];
			if (val is RaceTracker)
			{
				list.Add(val.def);
				pawn.health.hediffSet.hediffs.Remove(val);
			}
		}
		List<GeneDef> list3 = hediffExtensions.SelectMany((PawnExtension x) => x.genesDependentOnRace).ToList();
		List<TraitDef> list4 = hediffExtensions.SelectMany((PawnExtension x) => x.traitsDependentOnRace).ToList();
		foreach (PawnExtension item in hediffExtensions)
		{
			if (item.forcedHediffs != null)
			{
				foreach (HediffDef forcedHediff in item.forcedHediffs)
				{
					if (pawn.health.hediffSet.HasHediff(forcedHediff, false))
					{
						pawn.health.hediffSet.hediffs.Remove(pawn.health.hediffSet.GetFirstHediffOfDef(forcedHediff, false));
					}
				}
			}
			HashSet<GeneDef> hashSet = new HashSet<GeneDef>();
			foreach (GeneDef item2 in item.forcedEndogenes ?? new List<GeneDef>())
			{
				hashSet.Add(item2);
			}
			foreach (GeneDef item3 in item.forcedXenogenes ?? new List<GeneDef>())
			{
				hashSet.Add(item3);
			}
			foreach (GeneDef item4 in item.immutableEndogenes ?? new List<GeneDef>())
			{
				hashSet.Add(item4);
			}
			foreach (GeneDef gene in hashSet.Where(list3.Contains))
			{
				if (GenCollection.Any<Gene>(pawn.genes.GenesListForReading, (Predicate<Gene>)((Gene g) => g.def == gene)))
				{
					pawn.genes.RemoveGene(pawn.genes.GenesListForReading.First((Gene g) => g.def == gene));
				}
			}
			foreach (TraitDef item5 in (from x in item.GetForcedTraits()
				select x.Def).ToList().Where(list4.Contains))
			{
				if (pawn.story.traits.HasTrait(item5))
				{
					pawn.story.traits.allTraits.Remove(pawn.story.traits.GetTrait(item5));
				}
			}
		}
		return list;
	}
}
