using System.Collections.Generic;
using RimMandrake.EnvironmentalHazards;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.Sound;

namespace RimMandrake.Utinni.UtinniPatches
{
	// GREATBOLE_HARVEST_LADDER_1. The three named events on the Greatbole's
	// own footprint — the Great Shaking (40%), the violent healing (60%) and
	// the catastrophe (70%) — attach this alongside
	// RimMandrake.EnvironmentalHazards.CompProperties_LivingBoleMarker on
	// RUT_GreatboleCore. It never touches the generic mechanism directly:
	// everything it needs is the small read-only query API
	// (RM_MapComponent_LivingRegrowth.GetRemovedFraction/GetBoleCenter/
	// GetFootprintCells, RM_CompLivingBoleMarker.BoleId) that mechanism
	// already exposes for exactly this — a content mod polling it on its own
	// schedule rather than the generic component knowing this content
	// exists. The 60% healing SPEED-UP itself is not implemented here at
	// all: it is CompProperties_LivingBoleMarker's own
	// acceleratedRegrowThreshold/acceleratedRegrowSpeedMultiplier fields,
	// set in RUT_GreatboleCore.xml — this comp only announces the crossing.
	//
	//   <comps>
	//     <li Class="RimMandrake.Utinni.UtinniPatches.RUT_CompProperties_GreatboleHarvestLadder">
	//       <fruitDef>RM_GreatboleFruit</fruitDef>
	//       <grubKindDef>RM_GreatboleGrub</grubKindDef>
	//       <hardwoodDef>RUT_Hardwood</hardwoodDef>
	//       <trunkSegmentDef>RUT_GreatboleTrunkSegment</trunkSegmentDef>
	//       <deadHuskDef>RUT_GreatboleDeadHusk</deadHuskDef>
	//       <wildsteamFactionDef>RUT_Jawa_WildsteamClan</wildsteamFactionDef>
	//     </li>
	//   </comps>
	public class RUT_CompProperties_GreatboleHarvestLadder : CompProperties
	{
		public ThingDef fruitDef;
		public PawnKindDef grubKindDef;
		public ThingDef hardwoodDef;
		public ThingDef trunkSegmentDef;
		public ThingDef deadHuskDef;
		public FactionDef wildsteamFactionDef;

		// How often the fraction is (re-)read. INVENTED: matches the generic
		// component's own TickInterval (250) — no reason to poll faster than
		// the thing it is reading can possibly change.
		public int pollIntervalTicks = 250;

		// Small dead-zone so a fraction sitting exactly on a threshold does
		// not flip the "fired" flag back and forth on floating-point noise
		// or a single cell regrowing/re-mining. INVENTED.
		public float hysteresis = 0.03f;

		// §2a The Great Shaking (40% removed). All counts/amounts INVENTED —
		// nothing in the spec gives exact numbers, only "fruit and grubs
		// come down", "structures inside take real damage and unlucky ones
		// break", "pawns are staggered, not killed".
		public IntRange shakingFruitCountRange = new IntRange(1, 3);
		public IntRange shakingGrubCountRange = new IntRange(3, 6);
		public float shakingStaggerRadius = 15f;
		public int shakingStaggerTicks = 180;
		public float shakingStructureDamageChance = 0.35f;
		public float shakingStructureDamageAmount = 40f;

		// §2c The catastrophe (70% removed, permanent). Radius is RULED
		// ("unsafe within 50 cells"); the damage amount and yields are
		// INVENTED ("huge logs smashing down… everything gets crushed",
		// "yields a huge amount of wood, grubs and fruit").
		public float catastropheRadius = 50f;
		public float catastropheDamageAmount = 300f;
		public IntRange catastropheFruitYieldRange = new IntRange(6, 10);
		public IntRange catastropheGrubYieldRange = new IntRange(8, 14);
		public IntRange catastropheHardwoodYieldRange = new IntRange(400, 700);
		public IntRange trunkSegmentCountRange = new IntRange(6, 12);
		public int catastropheWildsteamGoodwillChange = -70;
		public int catastropheCameraShakeDurationTicks = 240;
		public float catastropheCameraShakeMagnitude = 4f;

		public RUT_CompProperties_GreatboleHarvestLadder()
		{
			compClass = typeof(RUT_CompGreatboleHarvestLadder);
		}

		public override IEnumerable<string> ConfigErrors(ThingDef parentDef)
		{
			foreach (string err in base.ConfigErrors(parentDef))
			{
				yield return err;
			}

			if (fruitDef == null)
			{
				yield return "RUT_CompProperties_GreatboleHarvestLadder on " + parentDef?.defName + " has no fruitDef.";
			}
		}
	}

	public class RUT_CompGreatboleHarvestLadder : ThingComp
	{
		// Scribed hysteresis flags — see the class header for why this comp
		// polls rather than subscribes to anything.
		private bool shakingArmed; // true once fraction >= threshold; the NEXT crossing fires
		private bool healingAnnounced;
		private bool catastropheDone;

		public RUT_CompProperties_GreatboleHarvestLadder Props => (RUT_CompProperties_GreatboleHarvestLadder)props;

		public override void CompTick()
		{
			base.CompTick();

			if (catastropheDone || !parent.Spawned)
			{
				return;
			}
			if (!parent.IsHashIntervalTick(Props.pollIntervalTicks))
			{
				return;
			}

			RM_CompLivingBoleMarker marker = parent.GetComp<RM_CompLivingBoleMarker>();
			Map map = parent.Map;
			RM_MapComponent_LivingRegrowth regrowth = map?.GetComponent<RM_MapComponent_LivingRegrowth>();
			if (marker == null || regrowth == null || marker.BoleId < 0 || !regrowth.IsRegistered(marker.BoleId))
			{
				return;
			}

			float fraction = regrowth.GetRemovedFraction(marker.BoleId);
			float h = Props.hysteresis;

			if (!shakingArmed && fraction >= UtinniPatchesSettings.greatboleShakingThreshold)
			{
				shakingArmed = true;
				GreatShaking(map);
			}
			else if (shakingArmed && fraction < UtinniPatchesSettings.greatboleShakingThreshold - h)
			{
				shakingArmed = false;
			}

			if (!healingAnnounced && fraction >= UtinniPatchesSettings.greatboleHealingThreshold)
			{
				healingAnnounced = true;
				AnnounceViolentHealing();
			}
			else if (healingAnnounced && fraction < UtinniPatchesSettings.greatboleHealingThreshold - h)
			{
				healingAnnounced = false;
			}

			if (UtinniPatchesSettings.greatboleCatastropheEnabled
			    && fraction >= UtinniPatchesSettings.greatboleCatastropheThreshold)
			{
				Catastrophe(map, marker, regrowth);
			}
		}

		// §2a. Fruit and grubs come down; nearby pawns are staggered, not
		// killed; unlucky nearby structures take real damage. This is the
		// creak's louder sibling (RM_MapComponent_LivingRegrowth's own
		// CreakWarning, same family, bigger).
		private void GreatShaking(Map map)
		{
			Messages.Message("RUT_GreatboleShaking".Translate(), new TargetInfo(parent.Position, map),
				MessageTypeDefOf.ThreatBig);
			SoundDefOf.Building_Complete.PlayOneShot(SoundInfo.InMap(new TargetInfo(parent.Position, map)));
			Find.CameraDriver?.shaker.DoShake(2f);

			SpawnFruitAndGrubs(map, Props.shakingFruitCountRange, Props.shakingGrubCountRange);

			foreach (Thing t in GenRadial.RadialDistinctThingsAround(parent.Position, map, Props.shakingStaggerRadius, useCenter: true))
			{
				if (t is Pawn pawn && pawn.Spawned && !pawn.Dead)
				{
					pawn.stances?.stagger.StaggerFor(Props.shakingStaggerTicks);
				}
				else if (t.def.category == ThingCategory.Building && t.def != Props.deadHuskDef
					&& Rand.Chance(Props.shakingStructureDamageChance))
				{
					t.TakeDamage(new DamageInfo(DamageDefOf.Blunt, Props.shakingStructureDamageAmount, 0f, -1f, null));
				}
			}
		}

		private void AnnounceViolentHealing()
		{
			Messages.Message("RUT_GreatboleViolentHealing".Translate(), new TargetInfo(parent.Position, parent.Map),
				MessageTypeDefOf.ThreatBig);
			SoundDefOf.Building_Complete.PlayOneShot(SoundInfo.InMap(new TargetInfo(parent.Position, parent.Map)));
		}

		// §2c. Permanent, once. Everything within catastropheRadius is
		// crushed; the bole dies forever (deregistered — RM_MapComponent_
		// LivingRegrowth never schedules another regrow for it); Wildsteam
		// takes the sacrilege as the taboo it is (§8).
		private void Catastrophe(Map map, RM_CompLivingBoleMarker marker, RM_MapComponent_LivingRegrowth regrowth)
		{
			catastropheDone = true;

			IntVec3 center = regrowth.GetBoleCenter(marker.BoleId);
			IReadOnlyCollection<IntVec3> footprint = regrowth.GetFootprintCells(marker.BoleId);

			Messages.Message("RUT_GreatboleCatastrophe".Translate(), new TargetInfo(center, map),
				MessageTypeDefOf.ThreatBig);
			SoundDefOf.Building_Complete.PlayOneShot(SoundInfo.InMap(new TargetInfo(center, map)));
			Find.CameraDriver?.shaker.DoShake(Props.catastropheCameraShakeMagnitude, Props.catastropheCameraShakeDurationTicks);

			CrushRadius(map, center, Props.catastropheRadius, Props.catastropheDamageAmount);
			ScatterTrunkSegments(map, center, Props.catastropheRadius);
			DropCatastropheYield(map, center);

			if (Props.wildsteamFactionDef != null)
			{
				// reason: null — TryAffectGoodwillWith's HistoryEventDef param only
				// changes attribution text on the goodwill message/letter; inventing a
				// whole new HistoryEventDef just to word that line is not worth the
				// extra def for a one-off sacrilege hit. The goodwill swing and the
				// message/letter both still fire.
				Faction wildsteam = Find.FactionManager?.FirstFactionOfDef(Props.wildsteamFactionDef);
				wildsteam?.TryAffectGoodwillWith(Faction.OfPlayer, Props.catastropheWildsteamGoodwillChange,
					canSendMessage: true, canSendHostilityLetter: true);
			}

			regrowth.DeregisterBole(marker.BoleId);

			// The bole is dead forever: the core marker and every remaining
			// heartwood cell are destroyed outright (no husk regrowth path
			// exists any more — MapComponent no longer tracks this id at
			// all), and a dead husk building takes the core's place so the
			// interior stays freely buildable — §2c ruling 3.
			foreach (IntVec3 c in footprint)
			{
				if (!c.InBounds(map))
				{
					continue;
				}
				Building edifice = c.GetEdifice(map);
				if (edifice != null && edifice != parent && !edifice.Destroyed)
				{
					edifice.Destroy(DestroyMode.KillFinalize);
				}
			}

			if (Props.deadHuskDef != null)
			{
				Thing husk = ThingMaker.MakeThing(Props.deadHuskDef);
				GenSpawn.Spawn(husk, center, map);
			}

			if (parent.Spawned)
			{
				parent.Destroy(DestroyMode.KillFinalize);
			}
		}

		private void CrushRadius(Map map, IntVec3 center, float radius, float damageAmount)
		{
			foreach (IntVec3 cell in GenRadial.RadialCellsAround(center, radius, useCenter: true))
			{
				if (!cell.InBounds(map))
				{
					continue;
				}

				List<Thing> things = new List<Thing>(cell.GetThingList(map));
				for (int i = 0; i < things.Count; i++)
				{
					Thing t = things[i];
					if (t == null || t.Destroyed || t == parent)
					{
						continue;
					}

					if (t is Pawn pawn)
					{
						pawn.TakeDamage(new DamageInfo(DamageDefOf.Crush, damageAmount, 0f, -1f, null));
						continue;
					}

					if (t.def.category == ThingCategory.Plant || t.def.category == ThingCategory.Building)
					{
						t.TakeDamage(new DamageInfo(DamageDefOf.Crush, damageAmount, 0f, -1f, null));
						continue;
					}

					if (t.def.category == ThingCategory.Item)
					{
						t.Destroy();
					}
				}
			}
		}

		private void ScatterTrunkSegments(Map map, IntVec3 center, float radius)
		{
			if (Props.trunkSegmentDef == null)
			{
				return;
			}
			int count = Props.trunkSegmentCountRange.RandomInRange;
			for (int i = 0; i < count; i++)
			{
				if (!CellFinder.TryFindRandomCellNear(center, map, Mathf.RoundToInt(radius),
					c => c.InBounds(map) && c.Standable(map), out IntVec3 cell))
				{
					continue;
				}
				Thing segment = ThingMaker.MakeThing(Props.trunkSegmentDef);
				GenSpawn.Spawn(segment, cell, map, WipeMode.Vanish);
			}
		}

		private void DropCatastropheYield(Map map, IntVec3 center)
		{
			SpawnFruitAndGrubs(map, Props.catastropheFruitYieldRange, Props.catastropheGrubYieldRange);

			if (Props.hardwoodDef != null)
			{
				Thing wood = ThingMaker.MakeThing(Props.hardwoodDef);
				wood.stackCount = Mathf.Min(wood.def.stackLimit, Props.catastropheHardwoodYieldRange.RandomInRange);
				GenPlace.TryPlaceThing(wood, center, map, ThingPlaceMode.Near);
			}
		}

		private void SpawnFruitAndGrubs(Map map, IntRange fruitRange, IntRange grubRange)
		{
			int fruitCount = fruitRange.RandomInRange;
			for (int i = 0; i < fruitCount; i++)
			{
				if (Props.fruitDef == null)
				{
					break;
				}
				if (!CellFinder.TryFindRandomCellNear(parent.Position, map, 6,
					c => c.InBounds(map) && c.Standable(map), out IntVec3 cell))
				{
					continue;
				}
				Thing fruit = ThingMaker.MakeThing(Props.fruitDef);
				GenPlace.TryPlaceThing(fruit, cell, map, ThingPlaceMode.Near);
			}

			int grubCount = grubRange.RandomInRange;
			for (int i = 0; i < grubCount; i++)
			{
				if (Props.grubKindDef == null)
				{
					break;
				}
				if (!CellFinder.TryFindRandomCellNear(parent.Position, map, 6,
					c => c.InBounds(map) && c.Standable(map), out IntVec3 cell))
				{
					continue;
				}
				PawnGenerationRequest request = new PawnGenerationRequest(Props.grubKindDef, null,
					PawnGenerationContext.NonPlayer, map.Tile);
				Pawn grub = PawnGenerator.GeneratePawn(request);
				GenSpawn.Spawn(grub, cell, map);
			}
		}

		public override void PostExposeData()
		{
			base.PostExposeData();
			Scribe_Values.Look(ref shakingArmed, "rutShakingArmed", false);
			Scribe_Values.Look(ref healingAnnounced, "rutHealingAnnounced", false);
			Scribe_Values.Look(ref catastropheDone, "rutCatastropheDone", false);
		}
	}
}
