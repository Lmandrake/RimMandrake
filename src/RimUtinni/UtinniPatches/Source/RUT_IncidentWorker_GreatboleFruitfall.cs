using System.Collections.Generic;
using RimMandrake.EnvironmentalHazards;
using RimWorld;
using Verse;

namespace RimMandrake.Utinni.UtinniPatches
{
	// GREATBOLE_HARVEST_LADDER_1 §2d, "Fruitfall — the non-destructive
	// route, and the design's missing half": a random event dropping one or
	// two fruits and a few grubs near a live greatbole, with none of the
	// Great Shaking's interior damage, pawn stagger or visible wound. This
	// is the piece that gives a player who wants Royal Rind a route that
	// costs nothing but patience — "patience or sacrilege" (spec's own
	// words).
	//
	// Never fires on a map with no registered greatbole (RM_MapComponent_
	// LivingRegrowth.AllBoleIds()) — same "no target, no incident" posture
	// every other bespoke IncidentWorker in this kit takes.
	public class RUT_IncidentWorker_GreatboleFruitfall : IncidentWorker
	{
		// INVENTED: "one or two fruits… and a few grubs" (spec's own words,
		// deliberately smaller than either the Great Shaking's or the
		// catastrophe's yield — this route is slow and small by design).
		private static readonly IntRange FruitCountRange = new IntRange(1, 2);
		private static readonly IntRange GrubCountRange = new IntRange(1, 3);

		protected override bool CanFireNowSub(IncidentParms parms)
		{
			if (!base.CanFireNowSub(parms))
			{
				return false;
			}
			Map map = (Map)parms.target;
			return FindBoleCenter(map, out _);
		}

		protected override bool TryExecuteWorker(IncidentParms parms)
		{
			Map map = (Map)parms.target;
			if (!FindBoleCenter(map, out IntVec3 center))
			{
				return false;
			}

			ThingDef fruitDef = DefDatabase<ThingDef>.GetNamedSilentFail("RM_GreatboleFruit");
			PawnKindDef grubKind = DefDatabase<PawnKindDef>.GetNamedSilentFail("RM_GreatboleGrub");

			int fruitCount = FruitCountRange.RandomInRange;
			for (int i = 0; i < fruitCount; i++)
			{
				if (fruitDef == null)
				{
					break;
				}
				if (!CellFinder.TryFindRandomCellNear(center, map, 6,
					c => c.InBounds(map) && c.Standable(map), out IntVec3 cell))
				{
					continue;
				}
				Thing fruit = ThingMaker.MakeThing(fruitDef);
				GenPlace.TryPlaceThing(fruit, cell, map, ThingPlaceMode.Near);
			}

			int grubCount = GrubCountRange.RandomInRange;
			for (int i = 0; i < grubCount; i++)
			{
				if (grubKind == null)
				{
					break;
				}
				if (!CellFinder.TryFindRandomCellNear(center, map, 6,
					c => c.InBounds(map) && c.Standable(map), out IntVec3 cell))
				{
					continue;
				}
				PawnGenerationRequest request = new PawnGenerationRequest(grubKind, null,
					PawnGenerationContext.NonPlayer, map.Tile);
				Pawn grub = PawnGenerator.GeneratePawn(request);
				GenSpawn.Spawn(grub, cell, map);
			}

			Find.LetterStack.ReceiveLetter("RUT_GreatboleFruitfallLabel".Translate(),
				"RUT_GreatboleFruitfallText".Translate(), LetterDefOf.PositiveEvent,
				new TargetInfo(center, map));

			return true;
		}

		private static bool FindBoleCenter(Map map, out IntVec3 center)
		{
			center = IntVec3.Invalid;
			RM_MapComponent_LivingRegrowth regrowth = map?.GetComponent<RM_MapComponent_LivingRegrowth>();
			if (regrowth == null)
			{
				return false;
			}
			List<int> ids = regrowth.AllBoleIds();
			if (ids.Count == 0)
			{
				return false;
			}
			int id = ids[Rand.Range(0, ids.Count)];
			center = regrowth.GetBoleCenter(id);
			return center.IsValid;
		}
	}
}
