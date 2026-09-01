using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using HarmonyLib;
using Outposts;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;

namespace VOE;

[StaticConstructorOnStartup]
public class Outpost_Defensive : Outpost
{
	private static readonly Func<IncidentWorker_RaidEnemy, IncidentParms, bool> generateFaction;

	public static bool DoRaid;

	[PostToSetings(/*Could not decode attribute arguments.*/)]
	public bool DoIntercept = true;

	[PostToSetings(/*Could not decode attribute arguments.*/)]
	public int FuelAmount = 100;

	[PostToSetings(/*Could not decode attribute arguments.*/)]
	public float InterceptDifficultyMultiplier = 1f;

	[PostToSetings(/*Could not decode attribute arguments.*/)]
	public bool NeedFuel = false;

	[PostToSetings(/*Could not decode attribute arguments.*/)]
	public bool NeedPods = true;

	static Outpost_Defensive()
	{
		//IL_004a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0057: Expected O, but got Unknown
		if (GenCollection.Any<WorldObjectDef>(OutpostsMod.Outposts, (Predicate<WorldObjectDef>)((WorldObjectDef outpost) => typeof(Outpost_Defensive).IsAssignableFrom(outpost.worldObjectClass))))
		{
			OutpostsMod.Harm.Patch((MethodBase)AccessTools.Method(typeof(IncidentWorker_RaidEnemy), "TryExecuteWorker", (Type[])null, (Type[])null), new HarmonyMethod(typeof(Outpost_Defensive), "InterceptRaid", (Type[])null), (HarmonyMethod)null, (HarmonyMethod)null, (HarmonyMethod)null);
		}
	}

	public static string CanSpawnOnWith(PlanetTile tile, List<Pawn> pawns)
	{
		//IL_0058: Unknown result type (might be due to invalid IL or missing references)
		//IL_004c: Unknown result type (might be due to invalid IL or missing references)
		return TaggedString.op_Implicit(pawns.Where((Pawn p) => p.RaceProps.Humanlike).Any((Pawn p) => p.WorkTagIsDisabled((WorkTags)8) || p.equipment.Primary == null) ? Translator.Translate("Outposts.MustBeArmed") : TaggedString.op_Implicit((string)null));
	}

	public static string RequirementsString(PlanetTile tile, List<Pawn> pawns)
	{
		//IL_0005: Unknown result type (might be due to invalid IL or missing references)
		return Utils.Requirement(Translator.Translate("Outposts.MustBeArmed"), pawns.Where((Pawn p) => p.RaceProps.Humanlike).All((Pawn p) => !p.WorkTagIsDisabled((WorkTags)8) && p.equipment.Primary != null));
	}

	public static bool InterceptRaid(IncidentParms parms, IncidentWorker_RaidEnemy __instance)
	{
		if (!DoRaid)
		{
			return true;
		}
		IEnumerable<Outpost_Defensive> source = from outpost in Find.WorldObjects.AllWorldObjects.OfType<Outpost_Defensive>()
			where ((Outpost)outpost).PawnCount > 0 && outpost.DoIntercept
			select outpost;
		float totalSkills = source.Sum((Outpost_Defensive x) => (float)(((Outpost)x).TotalSkill(SkillDefOf.Shooting) + ((Outpost)x).TotalSkill(SkillDefOf.Melee)) * x.InterceptDifficultyMultiplier);
		parms.points *= 1f - GetRaidSizeReductionFactor(totalSkills);
		DoRaid = true;
		((IncidentWorker)__instance).TryExecute(parms);
		DoRaid = false;
		return false;
	}

	public static float GetRaidSizeReductionFactor(float totalSkills)
	{
		float num = totalSkills / 200f * 0.5f;
		return Mathf.Min(num, 0.5f);
	}

	public override IEnumerable<Gizmo> GetGizmos()
	{
		//IL_0007: Unknown result type (might be due to invalid IL or missing references)
		//IL_000c: Unknown result type (might be due to invalid IL or missing references)
		//IL_001e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0024: Unknown result type (might be due to invalid IL or missing references)
		//IL_0033: Unknown result type (might be due to invalid IL or missing references)
		//IL_0039: Unknown result type (might be due to invalid IL or missing references)
		//IL_0048: Unknown result type (might be due to invalid IL or missing references)
		//IL_0057: Unknown result type (might be due to invalid IL or missing references)
		//IL_005e: Unknown result type (might be due to invalid IL or missing references)
		//IL_006e: Expected O, but got Unknown
		string reason;
		return ((Outpost)this).GetGizmos().Append((Gizmo)new Command_Action
		{
			action = delegate
			{
				Find.WorldTargeter.BeginTargeting((Func<GlobalTargetInfo, bool>)delegate(GlobalTargetInfo target)
				{
					//IL_000e: Unknown result type (might be due to invalid IL or missing references)
					//IL_000f: Unknown result type (might be due to invalid IL or missing references)
					//IL_0063: Unknown result type (might be due to invalid IL or missing references)
					if (((GlobalTargetInfo)(ref target)).HasWorldObject)
					{
						WorldObject worldObject = ((GlobalTargetInfo)(ref target)).WorldObject;
						MapParent parent = (MapParent)(object)((worldObject is MapParent) ? worldObject : null);
						if (parent != null && parent.HasMap)
						{
							CameraJumper.TryJump(parent.Map.Center, parent.Map, (MovementMode)0);
							Find.Targeter.BeginTargeting(TargetingParameters.ForDropPodsDestination(), (Action<LocalTargetInfo>)delegate(LocalTargetInfo localTarget)
							{
								//IL_000b: Unknown result type (might be due to invalid IL or missing references)
								//IL_0011: Expected O, but got Unknown
								//IL_0018: Unknown result type (might be due to invalid IL or missing references)
								//IL_003c: Unknown result type (might be due to invalid IL or missing references)
								//IL_0041: Unknown result type (might be due to invalid IL or missing references)
								//IL_004f: Unknown result type (might be due to invalid IL or missing references)
								//IL_0054: Unknown result type (might be due to invalid IL or missing references)
								//IL_005a: Unknown result type (might be due to invalid IL or missing references)
								//IL_0064: Expected O, but got Unknown
								//IL_0133: Unknown result type (might be due to invalid IL or missing references)
								//IL_0138: Unknown result type (might be due to invalid IL or missing references)
								//IL_014c: Unknown result type (might be due to invalid IL or missing references)
								//IL_0153: Unknown result type (might be due to invalid IL or missing references)
								//IL_015d: Expected O, but got Unknown
								TravellingTransporters val = (TravellingTransporters)WorldObjectMaker.MakeWorldObject(WorldObjectDefOf.TravellingTransporters);
								((WorldObject)val).Tile = ((WorldObject)this).Tile;
								((WorldObject)val).SetFaction(((WorldObject)this).Faction);
								val.destinationTile = ((GlobalTargetInfo)(ref target)).Tile;
								val.arrivalAction = (TransportersArrivalAction)new TransportersArrivalAction_LandInSpecificCell(parent, ((LocalTargetInfo)(ref localTarget)).Cell, Rot4.South, false);
								if (NeedFuel)
								{
									foreach (Thing item in ((Outpost)this).TakeItems(ThingDefOf.Chemfuel, FuelAmount))
									{
										item.Destroy((DestroyMode)0);
									}
								}
								foreach (Pawn item2 in (from x in ((Outpost)this).AllPawns
									where x.RaceProps.trainability != TrainabilityDefOf.None
									orderby x.IsColonist descending
									select x).Skip(1).ToList())
								{
									ActiveTransporterInfo val2 = new ActiveTransporterInfo
									{
										SingleContainedThing = (Thing)(object)((Outpost)this).RemovePawn(item2),
										leaveSlag = false,
										openDelay = 30
									};
									val.AddTransporter(val2, false);
								}
								Find.WorldObjects.Add((WorldObject)(object)val);
							}, (Pawn)null, (Action)null, (Texture2D)null, true);
							return true;
						}
					}
					return false;
				}, false, (Texture2D)null, false, (Action)null, (Func<GlobalTargetInfo, TaggedString>)null, (Func<GlobalTargetInfo, bool>)delegate(GlobalTargetInfo target)
				{
					//IL_0007: Unknown result type (might be due to invalid IL or missing references)
					//IL_000d: Unknown result type (might be due to invalid IL or missing references)
					int result;
					if (Find.WorldGrid.ApproxDistanceInTiles(((GlobalTargetInfo)(ref target)).Tile, ((WorldObject)this).Tile) <= (float)((Outpost)this).Range && ((GlobalTargetInfo)(ref target)).HasWorldObject)
					{
						WorldObject worldObject2 = ((GlobalTargetInfo)(ref target)).WorldObject;
						MapParent val3 = (MapParent)(object)((worldObject2 is MapParent) ? worldObject2 : null);
						if (val3 != null && val3.HasMap)
						{
							result = (val3.Map.mapPawns.AnyFreeColonistSpawned ? 1 : 0);
							goto IL_0054;
						}
					}
					result = 0;
					goto IL_0054;
					IL_0054:
					return (byte)result != 0;
				}, (PlanetTile?)null, false);
			},
			defaultLabel = TaggedString.op_Implicit(Translator.Translate("Outposts.Commands.Deploy.Label")),
			defaultDesc = TaggedString.op_Implicit(Translator.Translate("Outposts.Commands.Deploy.Desc")),
			Disabled = ReinforcementsDisabled(out reason),
			disabledReason = reason,
			icon = (Texture)(object)TexDefensive.DeployTex
		});
	}

	private bool ReinforcementsDisabled(out string reason)
	{
		//IL_0024: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a2: Unknown result type (might be due to invalid IL or missing references)
		//IL_007d: Unknown result type (might be due to invalid IL or missing references)
		if (NeedPods && !Outposts_DefOf.TransportPod.IsFinished)
		{
			reason = TaggedString.op_Implicit(Translator.Translate("Outposts.Commands.Deploy.Disabled"));
			return true;
		}
		if (NeedFuel && ((Outpost)this).Things.Sum((Thing x) => (x.def == ThingDefOf.Chemfuel) ? x.stackCount : 0) < FuelAmount)
		{
			reason = TaggedString.op_Implicit(Translator.Translate("Outposts.Commands.Deploy.NotEnoughFuel"));
			return true;
		}
		if (((Outpost)this).PawnCount < 2)
		{
			reason = TaggedString.op_Implicit(Translator.Translate("Outposts.Commands.Deploy.Only1"));
			return true;
		}
		reason = "";
		return false;
	}
}
You are not using the latest version of the tool, please update.
Latest version is '11.0.0.9375' (yours is '9.0.0.7889')
