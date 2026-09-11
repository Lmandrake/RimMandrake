using System.Collections.Generic;
using System.Linq;
using RimWorld;
using RimWorld.BaseGen;
using Verse;
using BG = RimWorld.BaseGen.BaseGen;

namespace RimMandrake.Utinni.UtinniPatches
{
	// SHRINE_GUARDIAN_BIOME_GATE_1 — piece 4/4 of MECH_PRESENCE_ENFORCEMENT_1.
	//
	// ===========================================================================
	// THE MECHANISM, READ NOT GUESSED (rimsage, RimWorld 1.6, 2026-09-10)
	// ===========================================================================
	// The full shrine chain, end to end:
	//
	//   GenStep_ScatterShrines.ScatterAt          (RimWorld/GenStep_ScatterShrines.cs:55-98)
	//     -> BaseGen.symbolStack.Push("ancientTemple", rp)
	//        with disableSinglePawn/disableHives/makeWarningLetter = true, and
	//        podContentsType = AncientFriendly ONLY under
	//        Find.Storyteller.difficulty.peacefulTemples.
	//   symbol "ancientTemple" -> RuleDef AncientTemple
	//                             (Core/Defs/RuleDefs/Rules_Complex.xml:285-293)
	//     -> SymbolResolver_AncientTemple.Resolve  (RimWorld/BaseGen/SymbolResolver_AncientTemple.cs:10-78)
	//        builds the shell with SketchGen (SketchResolverDefOf.Monument) —
	//        WALLS AND FLOOR ONLY, no pawns, no loot — then pushes
	//        "interior_ancientTemple" for the biggest empty inner rect.
	//   symbol "interior_ancientTemple" -> RuleDef Interior_AncientTemple
	//                             (Core/Defs/RuleDefs/Rules_Interior.xml:20-28)
	//     -> SymbolResolver_Interior_AncientTemple.Resolve
	//                             (RimWorld/BaseGen/SymbolResolver_Interior_AncientTemple.cs:20-72)
	//        THIS is the only place guardian type and loot are decided:
	//          * loot  = ThingSetMakerDefOf.MapGen_AncientTempleContents, hardcoded
	//          * guard = if (!peacefulTemples) one of, in priority order,
	//                    "randomFleshbeastGroup" (Anomaly, 50%),
	//                    "randomMechanoidGroup"  (65%, Faction.OfMechanoids),
	//                    "hives"                 (Faction.OfInsects)
	//          * plus "ancientShrinesGroup" (the cryptosleep caskets — the
	//            Rakatan SLEEPERS, which are canon here and are NOT touched)
	//          * plus an Ideology "edgeThing" AncientBarrel.
	//
	// So the item spec's summary is correct about the chain but WRONG about the
	// route: it calls for a Harmony postfix on SymbolResolver_AncientTemple.Resolve.
	// That is (a) the wrong resolver — AncientTemple only lays walls — and (b)
	// unnecessary, because RuleDef.resolvers is a plain `List<SymbolResolver>`
	// (RimWorld/RuleDef.cs:7-13) loaded from `<li Class="...">` with no
	// LoadDataFromXmlCustom anywhere in the chain. A PatchOperationAttributeSet on
	// that li's Class attribute swaps in this subclass with no Harmony at all —
	// the same plain-subclass shape as GeothermalDensityField.cs and LanternDeeps'
	// GenStep_ScatterCavePortal, and this mod's standing preference.
	// BaseGen.Resolve (RimWorld/BaseGen/BaseGen.cs:108-140) just walks
	// rulesBySymbol[symbol] -> ruleDef.resolvers[j], filters on CanResolve and
	// picks by selectionWeight, so a subclass instance is used exactly as the
	// vanilla instance was. Harmony is not needed and is not used here.
	//
	// ===========================================================================
	// WHAT IT SUBSTITUTES, AND WHY THAT AND NOT "WEAKER MECHS"
	// ===========================================================================
	// The eight biomes below are seven rows where the ratified table in
	// design/Jawa/worldbuilding/mechanoid_biome_presence_draft.md has AMBIENT =
	// DENY, plus Desert, whose AMBIENT is actually RARE (dormant, in shade) —
	// checked against the table directly, not assumed from a paraphrase. Every
	// row's argument column says the same thing in different words:
	//
	//   AB_TarPits          "nothing in the tar is active until dug"
	//   ZBiome_DesertOasis  "guardian-light ... its machines are dead — no
	//                        active mechanoids, no violence"
	//   ZBiome_Badlands     "no machine residents, only road traffic"
	//   Desert              "sparse and dead, never a front"
	//   ExtremeDesert       "sealed, dry, uncorroded" — a rare intact sealed vault
	//   BiomeGRimond        "sealed ancient structures, nothing more"
	//   PoisonForest        "no mech guardians inside" (sheet-explicit)
	//   BiomeCypreJungle    "washed-down wreck deposits"
	//
	// ⚠️ FLAGGED FOR OWNER REVIEW, not resolved here: Wasteland has the same
	// ANCIENT=ALLOW/AMBIENT=RARE(dormant) profile as Desert, and its own
	// argument column is more explicit against a live guardian than Desert's
	// ("a live roaming one breaks the law that danger here is environmental,
	// never creature-shaped") — yet Wasteland is NOT in this set. Either
	// Desert doesn't belong here either (strict AMBIENT=DENY reading) or
	// Wasteland is missing (the "no live mechanoid guardian" reading). Not
	// decided here because it changes shrine behavior on a real biome the
	// owner hasn't ruled on for this specific item.
	//
	// ⚠️ None of those rows asks for a REPLACEMENT living guardian, and four of
	// them explicitly forbid one. So this file does NOT invent a scavenger
	// pawnkind or a desert-raider pawn group to stand in the vault: that would
	// contradict the ratified text it exists to enforce, and it would need a new
	// defName nobody has ruled on. What it does instead:
	//
	//   1. GUARDIANS. The mechanoid / fleshbeast / hive branch is dropped
	//      entirely on these eight biomes. In its place the vault gets MORE OF
	//      ITS OWN DEAD: extra AncientCryptosleepCaskets set to
	//      PodContentsType.AncientHostile. That resolves (verified:
	//      ThingSetMaker_MapGen_AncientPodContents.GenerateAngryAncient_NewTemp,
	//      RimWorld/ThingSetMaker_MapGen_AncientPodContents.cs) to
	//      PawnKindDefOf.AncientSoldier under Faction.OfAncientsHostile — which
	//      in THIS campaign is already the reskinned Forsaken/Rakata
	//      (Patches/AncientsAreRakata.xml retextures AncientSoldier,
	//      AncientSoldier_Leader, AncientSoldierBoss(N), AncientMallGuards,
	//      AncientSlaughter). It is a human-tier, sealed, inert-until-opened
	//      threat: it satisfies AMBIENT-DENY (it is not Faction.OfMechanoids and
	//      spawns no mech), it satisfies "nothing active until dug" (a casket
	//      does nothing until a colonist opens it), and it needs no new def.
	//      The shape is copied from vanilla's own
	//      SymbolResolver_Interior_SleepingAncientSoldiers.Resolve, which pushes
	//      "ancientCryptosleepCasket" with exactly these params.
	//
	//   2. LOOT. MapGen_AncientTempleContents is the elite-ancient table —
	//      power armour, charge weapons, archotech limbs, techprints, luciferium,
	//      antigrain (read in full via get_def_details). That is the haul of an
	//      intact military vault, not of a midden the dunes uncovered. These eight
	//      rows are salvage country, so the loot table is swapped for Core's own
	//      MapGen_AncientComplexRoomLoot_Default — a ThingSetMaker_RandomOption
	//      of ordinary ancient-room stock (survival meals, medicine, silver,
	//      chemfuel, uranium, plasteel/hyperweave, with spacer components,
	//      ultratech medicine and a techprint at 0.15/0.15/0.05 weight). One
	//      Generate() call on a RandomOption yields ONE option, so it is called
	//      2-4 times to make a small pile rather than a single stack.
	//
	// JUDGMENT CALLS, none of them owner-ruled — flagged for his review:
	//   * AncientWatchChance 0.65f mirrors vanilla's own MechanoidsChance so the
	//     odds of a shrine being guarded at all are UNCHANGED; only the register
	//     of the guard changes.
	//   * AncientWatchCountRange 1-3, against vanilla's 1-5 mechanoids: a thawed
	//     AncientSoldier is a heavier unit than the cheap-mech end of
	//     MechClusterGenerator.MechKindSuitableForCluster's weighted pick
	//     (`1f / kind.combatPower` favours the weakest), and every one of the
	//     eight rows says "sparse".
	//   * ScavengedHaulCountRange 2-4 pulls: chosen so the pile reads as a haul
	//     rather than a single crate, while staying well under
	//     MapGen_AncientTempleContents' seven chance-gated options.
	//   * MapGen_AncientComplexRoomLoot_Default is defined TWICE in the shipped
	//     game — Core/Defs/ThingSetMakerDefs/ThingSetMakers_MapGen.xml:265 and
	//     Ideology/Defs/ThingSetMakerDefs/ThingSetMakers_MapGen.xml:5. Ideology
	//     loads later, so with Ideology active its version is what
	//     DefDatabase returns. Both are the same register (ordinary ancient-room
	//     stock); the lookup is deliberately by name via GetNamedSilentFail so it
	//     takes whichever is live, and falls back to the vanilla temple table if
	//     some future cut removes both rather than generating nothing.
	//
	// ⛔ NOT PROVEN YET. A 0W/0E build proves the subclass compiles and the patch
	// xpath matches; it proves NOTHING about this resolver actually being picked
	// at map generation. SHRINE_GUARDIAN_BIOME_GATE_1's Verify block owes a
	// quicktest map on one candidate biome (Desert is the cheapest) before this
	// may be called done.
	public class SymbolResolver_Interior_AncientTemple_AmbientDoctrine : SymbolResolver_Interior_AncientTemple
	{
		// The ANCIENT-ALLOW/RARE ∩ AMBIENT-DENY rows of the ratified table.
		// Every defName here is already carried by a shipped sibling patch that
		// was validated against the live def dump — the four RARE rows by
		// Patches/AncientDangerGenSteps_AmbientDoctrine.xml and all eight by
		// Patches/BiomeCast_Ashkarr.xml (BiomeGRimond via the former) — so none
		// of them is typed from memory here.
		private static readonly HashSet<string> AmbientDenyShrineBiomes = new HashSet<string>
		{
			"AB_TarPits",
			"ZBiome_DesertOasis",
			"ZBiome_Badlands",
			"Desert",
			"ExtremeDesert",
			"BiomeGRimond",
			"PoisonForest",
			"BiomeCypreJungle"
		};

		// Mirrors SymbolResolver_Interior_AncientTemple's own private
		// MechanoidsChance (0.65f) — see the header: the CHANCE of a guard is
		// held constant, only its kind changes.
		private const float AncientWatchChance = 0.65f;

		private static readonly IntRange AncientWatchCountRange = new IntRange(1, 3);

		// Byte-for-byte the vanilla resolver's own private MinSizeForShrines
		// (4, 3); re-declared because it is private there and this override
		// must reproduce the same gate on the "ancientShrinesGroup" push.
		private static readonly IntVec2 MinSizeForShrines = new IntVec2(4, 3);

		private const string ScavengedLootDefName = "MapGen_AncientComplexRoomLoot_Default";

		private static readonly IntRange ScavengedHaulCountRange = new IntRange(2, 4);

		public override void Resolve(ResolveParams rp)
		{
			Map map = BG.globalSettings.map;
			// Anything that is not one of the eight rows gets the stock resolver,
			// unmodified — including every other planet this mod might be loaded
			// on. This subclass is additive-by-exception, never a global rewrite.
			if (map == null || map.Biome == null || !AmbientDenyShrineBiomes.Contains(map.Biome.defName))
			{
				base.Resolve(rp);
				return;
			}
			ResolveAmbientDoctrine(rp);
		}

		// A re-implementation of SymbolResolver_Interior_AncientTemple.Resolve
		// rather than a call to base + fix-up: base.Resolve pushes its guardian
		// symbols onto BaseGen.symbolStack immediately, and the stack has no
		// remove operation, so there is no way to call it and then take the
		// mechanoids back out.
		private void ResolveAmbientDoctrine(ResolveParams rp)
		{
			PushScavengedLoot(rp);

			// Same gate vanilla uses: peacefulTemples means no guard of any kind,
			// and GenStep_ScatterShrines has already set podContentsType to
			// AncientFriendly upstream in that case.
			if (!Find.Storyteller.difficulty.peacefulTemples && Faction.OfAncientsHostile != null)
			{
				PushForsakenWatch(rp);
			}

			// UNCHANGED from vanilla: the shrine group is the Rakatan sleepers
			// themselves, which the ratified table wants in every ANCIENT-ALLOW
			// row. Only the GUARD was ever the problem.
			if (rp.rect.Width >= MinSizeForShrines.x && rp.rect.Height >= MinSizeForShrines.z)
			{
				BG.symbolStack.Push("ancientShrinesGroup", rp);
			}

			// UNCHANGED from vanilla.
			if (ModsConfig.IdeologyActive)
			{
				ResolveParams barrelParams = rp;
				barrelParams.singleThingDef = ThingDefOf.AncientBarrel;
				BG.symbolStack.Push("edgeThing", barrelParams);
			}
		}

		private void PushScavengedLoot(ResolveParams rp)
		{
			ThingSetMakerDef lootMaker = DefDatabase<ThingSetMakerDef>.GetNamedSilentFail(ScavengedLootDefName)
			                             ?? ThingSetMakerDefOf.MapGen_AncientTempleContents;

			List<Thing> haul = new List<Thing>();
			int pulls = ScavengedHaulCountRange.RandomInRange;
			for (int i = 0; i < pulls; i++)
			{
				haul.AddRange(lootMaker.root.Generate());
			}
			// Same sort vanilla applies, and for the same reason: the Ideology
			// hermetic crate below should wrap the single most valuable item.
			haul.SortByDescending((Thing t) => t.MarketValue * (float)t.stackCount);

			for (int i = 0; i < haul.Count; i++)
			{
				ResolveParams thingParams = rp;
				if (ModsConfig.IdeologyActive && i == 0)
				{
					thingParams.singleThingDef = ThingDefOf.AncientHermeticCrate;
					thingParams.singleThingInnerThings = new List<Thing> { haul[0] };
				}
				else
				{
					thingParams.singleThingToSpawn = haul[i];
				}
				BG.symbolStack.Push("thing", thingParams);
			}
		}

		// The dead watch. Shape lifted from
		// SymbolResolver_Interior_SleepingAncientSoldiers.Resolve — including the
		// casket-footprint-plus-one slot search and the ExpandedBy(-1) handed to
		// the casket resolver — except that the count comes from this file's own
		// range instead of threatPoints, because GenStep_ScatterShrines never
		// sets ResolveParams.threatPoints (verified: it sets only rect,
		// disableSinglePawn, disableHives, makeWarningLetter and, under
		// peacefulTemples, podContentsType), so the vanilla soldier resolver's
		// own CanResolve would reject this rp outright.
		private void PushForsakenWatch(ResolveParams rp)
		{
			if (!Rand.Chance(AncientWatchChance))
			{
				return;
			}
			int count = AncientWatchCountRange.RandomInRange;
			ThingDef casketDef = ThingDefOf.AncientCryptosleepCasket;
			IntVec2 slotSize = new IntVec2(casketDef.size.x + 2, casketDef.size.z + 2);
			List<CellRect> used = new List<CellRect>();
			for (int i = 0; i < count; i++)
			{
				CellRect slot;
				if (!rp.rect.TryFindRandomInnerRect(slotSize, out slot,
					    (CellRect other) => !used.Any((CellRect r) => r.Overlaps(other))))
				{
					break; // ran out of room in the interior — take what fitted
				}
				ResolveParams casketParams = rp;
				casketParams.rect = slot.ExpandedBy(-1);
				casketParams.thingRot = casketDef.defaultPlacingRot;
				casketParams.podContentsType = PodContentsType.AncientHostile;
				// SpawnCryptoCasket does not read rp.faction; set anyway so this
				// matches SleepingAncientSoldiers exactly and stays correct if a
				// future resolver in the chain starts reading it.
				casketParams.faction = Faction.OfAncientsHostile;
				BG.symbolStack.Push("ancientCryptosleepCasket", casketParams);
				used.Add(slot);
			}
		}
	}
}
