using HarmonyLib;
using RimWorld;
using Verse;

namespace RimMandrake.FlowWorks.Swimming
{
	// ════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
	// WET_FOXHOLE_BUILD_COLD_FEET_SHAKY_AIM (canal cover design §5, §10 step 4; owner Q4/Q6/Q8, 2026-10-18). What standing in
	// water costs, each its own setting (RM_SwimSettings, "Standing in water"):
	//   - aim:   the shooter's own factor x0.85 at chest depth (a postfix on ShotReport.HitReportFor, the shooter's half:
	//            factorFromShooterAndDist). It folds into the readout's "shooter and distance" line.
	//   - cold:  +6 C on ComfyTemperatureMin while standing in water (StatPart_RM_WetCold, added to the StatDef by
	//            Patches/Swimming/FlowWorks_WetCold.xml), so vanilla hypothermia arrives sooner. "Wet" here means IN water a
	//            creature may swim in (fresh, salt, icy: RM_SwimWater.LiquidSwimmableAt); rain-soaked (vanilla's SoakingWet
	//            memory) is NOT counted, so FlowWorks does not change rain on every map. Recorded as an agent decision.
	//   - guns:  a swimmer (water over its head, standing) has no ranged verb: a postfix on Verb.CanHitTargetFrom judging
	//            `root` (CastPositionFinder asks about candidate squares, so the AI also stops picking swim squares to shoot
	//            from). Aquatic creatures (they live in water) keep their verbs.
	//   - downed drowning warning (Q8): already built, not duplicated: RM_Swim.Tick calls DrownMessage for dug AND natural
	//     water while deep swimming is on, and RM_PitFillEffects calls it on dug water while it is off (003986dbb).
	// Arithmetic: RM_WetCostMath (Verse-free, SelfTest WetCostChecks).
	// ════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
	public static class RM_WetCosts
	{
		/// <summary>Water (metres) this pawn would stand in on square c: 0 when flying, on a deck (and not in a suspension
		/// deck's floor band), or off the map.</summary>
		public static float WaterAt(Pawn p, IntVec3 c)
		{
			Map map = p?.Map;
			if (map == null || !c.InBounds(map) || p.Flying)
			{
				return 0f;
			}
			// common case first, allocation-free: dry natural ground with no dig
			RM_MapComponent_Excavation ex = RM_SuperdeepTrap.EngineOf(map);
			TerrainDef t = map.terrainGrid.TerrainAt(c);
			if ((t == null || !t.IsWater) && (ex == null || !ex.IsExcavated(c)))
			{
				return 0f;
			}
			if (Pits.RM_PitCoverUtility.IsCovered(map, c) && !(c == p.Position && Pits.RM_SuspensionUnderpass.InFloorBand(p)))
			{
				return 0f;
			}
			return RM_SwimWater.WaterMetresAt(map, ex, c);
		}

		/// <summary>Swimming on square c: standing in water over the head (the same test RM_Swim.Tick uses for exhaustion).</summary>
		public static bool SwimmingAt(Pawn p, IntVec3 c)
		{
			float w = WaterAt(p, c);
			return w > 0f && RM_SwimMath.IsSwimming(w, RM_Drowning.HeightOf(p), RM_Drowning.Lying(p),
				RimMandrakeFlowWorksSettings.pitDrowningHeadFraction);
		}

		/// <summary>The shooter's aim factor on its own square.</summary>
		public static float AimFactorOf(Pawn p)
		{
			if (!RM_SwimSettings.deepWaterAimPenalty || p == null)
			{
				return 1f;
			}
			return RM_WetCostMath.AimFactor(true, WaterAt(p, p.Position), RM_Drowning.HeightOf(p), RM_Drowning.Lying(p),
				RM_SwimSettings.deepWaterAimFactor);
		}

		/// <summary>Standing in swimmable water (fresh, salt or icy) right now.</summary>
		public static bool InWater(Pawn p)
		{
			if (p == null || !p.Spawned)
			{
				return false;
			}
			if (WaterAt(p, p.Position) <= 0f)
			{
				return false;
			}
			RM_MapComponent_Excavation ex = RM_SuperdeepTrap.EngineOf(p.Map);
			// a hot spring (Odyssey) is swimmable water but warm: it never chills
			if ((ex == null || !ex.IsExcavated(p.Position)) && p.Map.terrainGrid.TerrainAt(p.Position)?.defName == WarmWaterTerrain)
			{
				return false;
			}
			return RM_SwimWater.LiquidSwimmableAt(p.Map, ex, p.Position);
		}

		/// <summary>Odyssey's hot spring terrain (Terrain_Water.xml): swimmable, unclaimed by any LiquidDef, and warm.</summary>
		public const string WarmWaterTerrain = "HotSpring";

		/// <summary>static_call surface: "x,z" -&gt; the wet-cost verdict for the first pawn there (the L2 rows read this).</summary>
		public static string ProofWet(string arg)
		{
			Map map = Find.CurrentMap;
			string[] a = (arg ?? "").Split(',');
			if (map == null || a.Length != 2 || !int.TryParse(a[0], out int x) || !int.TryParse(a[1], out int z))
			{
				return "REFUSED: arg must be x,z on a current map";
			}
			IntVec3 c = new IntVec3(x, 0, z);
			if (!c.InBounds(map))
			{
				return "REFUSED: out of bounds";
			}
			foreach (Thing t in c.GetThingList(map))
			{
				if (t is Pawn p)
				{
					return "WET " + p.ThingID + " water=" + WaterAt(p, c).ToString("0.000") + " height=" + RM_Drowning.HeightOf(p).ToString("0.00")
						+ " swimming=" + SwimmingAt(p, c) + " inWater=" + InWater(p) + " aimFactor=" + AimFactorOf(p).ToString("0.000")
						+ " comfyMin=" + p.GetStatValue(StatDefOf.ComfyTemperatureMin).ToString("0.0")
						+ " settings=" + RM_SwimSettings.deepWaterAimPenalty + "/" + RM_SwimSettings.wetFeelsColder + "/" + RM_SwimSettings.swimmersCannotShoot;
				}
			}
			return "NONE: no pawn at " + x + "," + z;
		}

		/// <summary>static_call surface: "x,z,tx,tz" -&gt; the primary weapon verb of the first pawn at x,z against the first pawn
		/// at tx,tz (else the square): ShotReport hit chance, the shooter's factor in it, and CanHitTargetFrom from its square.
		/// The L2 rows read the same pawn with a setting on and off, so skill and distance cancel.</summary>
		public static string ProofShot(string arg)
		{
			Map map = Find.CurrentMap;
			string[] a = (arg ?? "").Split(',');
			int[] v = new int[4];
			if (map == null || a.Length != 4)
			{
				return "REFUSED: arg must be x,z,tx,tz on a current map";
			}
			for (int i = 0; i < 4; i++)
			{
				if (!int.TryParse(a[i], out v[i]))
				{
					return "REFUSED: arg must be x,z,tx,tz on a current map";
				}
			}
			IntVec3 c = new IntVec3(v[0], 0, v[1]), tc = new IntVec3(v[2], 0, v[3]);
			if (!c.InBounds(map) || !tc.InBounds(map))
			{
				return "REFUSED: out of bounds";
			}
			Pawn p = c.GetFirstPawn(map);
			if (p == null)
			{
				return "NONE: no shooter at " + v[0] + "," + v[1];
			}
			Verb verb = p.equipment?.PrimaryEq?.PrimaryVerb;
			if (verb == null || verb.IsMeleeAttack)
			{
				return "NONE: " + p.ThingID + " holds no ranged weapon";
			}
			Pawn tp = tc.GetFirstPawn(map);
			LocalTargetInfo target = tp != null ? new LocalTargetInfo(tp) : new LocalTargetInfo(tc);
			ShotReport r = ShotReport.HitReportFor(p, verb, target);
			return "SHOT " + p.ThingID + " hit=" + r.AimOnTargetChance_IgnoringPosture.ToString("0.0000")
				+ " total=" + r.TotalEstimatedHitChance.ToString("0.0000")
				+ " aimFactor=" + AimFactorOf(p).ToString("0.000") + " canHit=" + verb.CanHitTargetFrom(c, target)
				+ " swimming=" + SwimmingAt(p, c) + " water=" + WaterAt(p, c).ToString("0.000") + " target=" + (tp?.ThingID ?? "cell");
		}
	}

	/// <summary>Cold (Q4): ComfyTemperatureMin + offset while standing in water. Added to the StatDef's parts by
	/// Patches/Swimming/FlowWorks_WetCold.xml (ResolveReferences sets parentStat).</summary>
	public class StatPart_RM_WetCold : StatPart
	{
		private static float OffsetFor(StatRequest req)
		{
			if (!RM_SwimSettings.wetFeelsColder || !(req.Thing is Pawn p))
			{
				return 0f;
			}
			return RM_WetCostMath.ColdOffset(true, RM_WetCosts.InWater(p), RM_SwimSettings.wetColdOffset);
		}

		public override void TransformValue(StatRequest req, ref float val)
		{
			val += OffsetFor(req);
		}

		public override string ExplanationPart(StatRequest req)
		{
			float o = OffsetFor(req);
			return o > 0f ? "Standing in water: " + o.ToStringTemperatureOffset() : null;
		}
	}

	/// <summary>Aim (Q4): the shooter's own factor in chest-deep water.</summary>
	[HarmonyPatch(typeof(ShotReport), nameof(ShotReport.HitReportFor))]
	[RimMandrake.Shared.PatchFeature("Shooting from chest-deep water", typeof(RM_SwimSettings), "deepWaterAimPenalty")]
	public static class RM_Patch_ShotReport_WetAim
	{
		private static readonly AccessTools.StructFieldRef<ShotReport, float> Shooter =
			AccessTools.StructFieldRefAccess<ShotReport, float>("factorFromShooterAndDist");

		[HarmonyPostfix]
		public static void Postfix(Thing caster, ref ShotReport __result)
		{
			if (!RM_SwimSettings.deepWaterAimPenalty || !(caster is Pawn p))
			{
				return;
			}
			float f = RM_WetCosts.AimFactorOf(p);
			if (f < 1f)
			{
				Shooter(ref __result) *= f;
			}
		}
	}

	/// <summary>Swimmers cannot shoot (Q6): every ranged verb refused from a swim square.</summary>
	[HarmonyPatch(typeof(Verb), nameof(Verb.CanHitTargetFrom))]
	[RimMandrake.Shared.PatchFeature("Swimmers can't use guns", typeof(RM_SwimSettings), "swimmersCannotShoot")]
	public static class RM_Patch_Verb_SwimmerNoGuns
	{
		[HarmonyPostfix]
		public static void Postfix(Verb __instance, IntVec3 root, ref bool __result)
		{
			if (!__result || !RM_SwimSettings.swimmersCannotShoot || __instance?.verbProps == null || __instance.IsMeleeAttack
				|| !(__instance.caster is Pawn p))
			{
				return;
			}
			if (!RM_WetCosts.SwimmingAt(p, root))
			{
				return;
			}
			if (RM_Swim.ProfileOf(p).cls == RM_SwimMath.SwimClass.Aquatic)
			{
				return;   // creatures that live in water keep their verbs
			}
			__result = RM_WetCostMath.RangedAllowed(true, true, false);
		}
	}
}
