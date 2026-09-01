using System;
using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Storyteller;

[HarmonyPatch(typeof(IncidentWorker_Raid))]
[HarmonyPatch("TryExecuteWorker")]
public static class VanillaExpandedFramework_IncidentWorker_Raid_TryExecuteWorker_Patch
{
	public static readonly Func<IncidentWorker_RaidEnemy, IncidentParms, bool> tryResolveRaidFactionMethod = (Func<IncidentWorker_RaidEnemy, IncidentParms, bool>)Delegate.CreateDelegate(typeof(Func<IncidentWorker_RaidEnemy, IncidentParms, bool>), AccessToolsExtensions.DeclaredMethod(typeof(IncidentWorker_RaidEnemy), "TryResolveRaidFaction", (Type[])null, (Type[])null));

	public static bool Prefix(IncidentWorker_Raid __instance, IncidentParms parms)
	{
		//IL_00eb: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f0: Unknown result type (might be due to invalid IL or missing references)
		//IL_0151: Unknown result type (might be due to invalid IL or missing references)
		//IL_0156: Unknown result type (might be due to invalid IL or missing references)
		//IL_015b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0172: Unknown result type (might be due to invalid IL or missing references)
		//IL_0187: Unknown result type (might be due to invalid IL or missing references)
		//IL_018c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0191: Unknown result type (might be due to invalid IL or missing references)
		//IL_0198: Unknown result type (might be due to invalid IL or missing references)
		//IL_019a: Unknown result type (might be due to invalid IL or missing references)
		StorytellerDefExtension modExtension = ((Def)Find.Storyteller.def).GetModExtension<StorytellerDefExtension>();
		if (modExtension != null)
		{
			StorytellerThreat storytellerThreat = modExtension.storytellerThreat;
			if (storytellerThreat != null)
			{
				IntRange? raidWarningRange = storytellerThreat.raidWarningRange;
				if (raidWarningRange.HasValue)
				{
					IncidentWorker_RaidEnemy val = (IncidentWorker_RaidEnemy)(object)((__instance is IncidentWorker_RaidEnemy) ? __instance : null);
					if (val != null && parms.target is Map && tryResolveRaidFactionMethod(val, parms) && parms.faction != null && FactionUtility.HostileTo(parms.faction, Faction.OfPlayer))
					{
						StorytellerWatcher component = Current.Game.GetComponent<StorytellerWatcher>();
						if (component != null && !GenCollection.Any<RaidQueue>(component.raidQueues, (Predicate<RaidQueue>)((RaidQueue x) => x.parms == parms)))
						{
							int ticksAbs = Find.TickManager.TicksAbs;
							IntRange value = modExtension.storytellerThreat.raidWarningRange.Value;
							int tickToFire = ticksAbs + ((IntRange)(ref value)).RandomInRange;
							__instance.ResolveRaidStrategy(parms, PawnGroupKindDefOf.Combat);
							__instance.ResolveRaidArriveMode(parms);
							RaidQueue item = new RaidQueue(((IncidentWorker)__instance).def, parms, tickToFire);
							component.raidQueues.Add(item);
							TaggedString val2 = TranslatorFormattedStringExtensions.Translate("VFEMech.RaidWarningTitle", NamedArgumentUtility.Named((object)parms.faction, "FACTION"));
							TaggedString val3 = TranslatorFormattedStringExtensions.Translate("VFEMech.RaidWarningText", NamedArgumentUtility.Named((object)parms.faction, "FACTION"), NamedArgument.op_Implicit(parms.raidStrategy.arrivalTextEnemy));
							Find.LetterStack.ReceiveLetter(val2, val3, LetterDefOf.ThreatBig, (string)null, 0, true);
							return false;
						}
					}
				}
			}
		}
		return true;
	}
}
