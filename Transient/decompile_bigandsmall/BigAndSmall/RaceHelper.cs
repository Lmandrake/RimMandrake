using System;
using System.Collections.Generic;
using System.Linq;
using Verse;

namespace BigAndSmall;

public static class RaceHelper
{
	public static List<RaceTracker> GetRaceTrackers(this Pawn pawn)
	{
		return pawn.health.hediffSet.hediffs.Where((Hediff h) => h is RaceTracker).Cast<RaceTracker>().ToList();
	}

	public static List<RaceExtension> GetRaceExtensions(this ThingDef def)
	{
		return def.ExtensionsOnDef<RaceExtension, ThingDef>((List<Type>)null, (List<Type>)null, doSort: true);
	}

	private static List<HediffComp_Race> GetRaceComps(this Pawn pawn)
	{
		return (from x in pawn.GetRaceTrackers()
			select HediffUtility.TryGetComp<HediffComp_Race>((Hediff)(object)x) ?? null into x
			where x != null
			select x).ToList();
	}

	public static List<PawnExtension> GetRacePawnExtensions(this Pawn pawn)
	{
		List<PawnExtension> allExtensions = pawn.GetAllExtensions<PawnExtension>(new List<Type>(1) { typeof(RaceTracker) });
		if (allExtensions.Count > 0)
		{
			return allExtensions;
		}
		return new List<PawnExtension>(1) { PawnExtension.defaultPawnExtension };
	}

	public static List<CompProperties_Race> GetRaceCompProps(this Pawn pawn)
	{
		List<CompProperties_Race> list = (from x in pawn.GetRaceComps()
			where x.Props != null
			select x.Props).ToList();
		if (GenCollection.Any<CompProperties_Race>(list))
		{
			return list;
		}
		return new List<CompProperties_Race>(1) { CompProperties_Race.defaultMissingProps };
	}

	public static bool IsMechanical(this Pawn pawn)
	{
		if (!GenCollection.Any<PawnExtension>(pawn.GetAllPawnExtensions(), (Predicate<PawnExtension>)((PawnExtension x) => x.isMechanical)))
		{
			return pawn.RaceProps.IsMechanoid;
		}
		return true;
	}

	public static bool IsMechanicalDef(this ThingDef def)
	{
		if (FusedBody.FusedBodyByThing.TryGetValue(def, out var value) && value.isMechanical)
		{
			return true;
		}
		return def.GetRaceExtensions().SelectMany((RaceExtension x) => x.PawnExtensionOnRace).Any((PawnExtension x) => x.isMechanical);
	}
}
