using System;
using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Storyteller;

[HarmonyPatch(typeof(IncidentWorker_Raid))]
[HarmonyPatch("TryExecuteWorker")]
public static class VanillaExpandedFramework_IncidentWorker_Raid_TryExecuteWorker_Patch
{
	public static bool Prefix(IncidentWorker_Raid __instance, IncidentParms parms)
	{
		//IL_0104: Unknown result type (might be due to invalid IL or missing references)
		//IL_0109: Unknown result type (might be due to invalid IL or missing references)
		//IL_0167: Unknown result type (might be due to invalid IL or missing references)
		//IL_016c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0171: Unknown result type (might be due to invalid IL or missing references)
		//IL_0188: Unknown result type (might be due to invalid IL or missing references)
		//IL_019d: Unknown result type (might be due to invalid IL or missing references)
		//IL_01a2: Unknown result type (might be due to invalid IL or missing references)
		//IL_01a7: Unknown result type (might be due to invalid IL or missing references)
		//IL_01ae: Unknown result type (might be due to invalid IL or missing references)
		//IL_01b0: Unknown result type (might be due to invalid IL or missing references)
		StorytellerDefExtension modExtension = ((Def)Find.Storyteller.def).GetModExtension<StorytellerDefExtension>();
		if (modExtension != null && modExtension.storytellerThreat != null && modExtension.storytellerThreat.raidWarningRange.HasValue && __instance is IncidentWorker_RaidEnemy && parms.target is Map && (bool)AccessTools.Method(typeof(IncidentWorker_RaidEnemy), "TryResolveRaidFaction", (Type[])null, (Type[])null).Invoke(__instance, new object[1] { parms }) && parms.faction != null && FactionUtility.HostileTo(parms.faction, Faction.OfPlayer))
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
				TaggedString val = TranslatorFormattedStringExtensions.Translate("VFEMech.RaidWarningTitle", NamedArgumentUtility.Named((object)parms.faction, "FACTION"));
				TaggedString val2 = TranslatorFormattedStringExtensions.Translate("VFEMech.RaidWarningText", NamedArgumentUtility.Named((object)parms.faction, "FACTION"), NamedArgument.op_Implicit(parms.raidStrategy.arrivalTextEnemy));
				Find.LetterStack.ReceiveLetter(val, val2, LetterDefOf.ThreatBig, (string)null, 0, true);
				return false;
			}
		}
		return true;
	}
}
You are not using the latest version of the tool, please update.
Latest version is '11.0.0.9375' (yours is '9.0.0.7889')
