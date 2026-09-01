using System;
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using RimWorld.Planet;
using RimWorld.QuestGen;
using Verse;

namespace VEF.Storyteller;

public class QuestNode_GetFaction : QuestNode
{
	[NoTranslate]
	public SlateRef<string> storeAs;

	public SlateRef<FactionDef> factionDef;

	public SlateRef<bool> allowEnemy;

	public SlateRef<bool> allowNeutral;

	public SlateRef<bool> allowAlly;

	public SlateRef<bool> allowAskerFaction;

	public SlateRef<bool?> allowPermanentEnemy;

	public SlateRef<bool> mustBePermanentEnemy;

	public SlateRef<bool> playerCantBeAttackingCurrently;

	public SlateRef<bool> peaceTalksCantExist;

	public SlateRef<bool> leaderMustBeSafe;

	public SlateRef<bool> mustHaveGoodwillRewardsEnabled;

	public SlateRef<Pawn> ofPawn;

	public SlateRef<Thing> mustBeHostileToFactionOf;

	public SlateRef<IEnumerable<Faction>> exclude;

	public SlateRef<IEnumerable<Faction>> allowedHiddenFactions;

	protected override bool TestRunInt(Slate slate)
	{
		Faction faction = default(Faction);
		if (slate.TryGet<Faction>(storeAs.GetValue(slate), ref faction, false) && IsGoodFaction(faction, slate))
		{
			return true;
		}
		if (TryFindFaction(out faction, slate))
		{
			slate.Set<Faction>(storeAs.GetValue(slate), faction, false);
			return true;
		}
		return false;
	}

	protected override void RunInt()
	{
		//IL_0007: Unknown result type (might be due to invalid IL or missing references)
		//IL_000d: Unknown result type (might be due to invalid IL or missing references)
		//IL_007c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0082: Expected O, but got Unknown
		Slate slate = QuestGen.slate;
		Faction faction = default(Faction);
		if ((factionDef != SlateRef<FactionDef>.op_Implicit((FactionDef)null) && SetFaction(out faction, slate)) || ((!QuestGen.slate.TryGet<Faction>(storeAs.GetValue(slate), ref faction, false) || !IsGoodFaction(faction, QuestGen.slate)) && TryFindFaction(out faction, QuestGen.slate)))
		{
			QuestGen.slate.Set<Faction>(storeAs.GetValue(slate), faction, false);
			if (!faction.Hidden)
			{
				QuestPart_InvolvedFactions val = new QuestPart_InvolvedFactions();
				val.factions.Add(faction);
				QuestGen.quest.AddPart((QuestPart)(object)val);
			}
		}
	}

	private bool SetFaction(out Faction faction, Slate slate)
	{
		FactionDef value = factionDef.GetValue(slate);
		if (value != null)
		{
			faction = Find.FactionManager.FirstFactionOfDef(value);
			return faction != null;
		}
		faction = null;
		return false;
	}

	private bool TryFindFaction(out Faction faction, Slate slate)
	{
		return GenCollection.TryRandomElement<Faction>(from x in Find.FactionManager.GetFactions(true, false, true, (TechLevel)0, false)
			where IsGoodFaction(x, slate)
			select x, ref faction);
	}

	private bool IsGoodFaction(Faction faction, Slate slate)
	{
		//IL_00c2: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c8: Invalid comparison between Unknown and I4
		//IL_00db: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e1: Invalid comparison between Unknown and I4
		if (faction == null)
		{
			return false;
		}
		if (faction.Hidden && (allowedHiddenFactions.GetValue(slate) == null || !allowedHiddenFactions.GetValue(slate).Contains(faction)))
		{
			return false;
		}
		if (ofPawn.GetValue(slate) != null && faction != ((Thing)ofPawn.GetValue(slate)).Faction)
		{
			return false;
		}
		if (exclude.GetValue(slate) != null && exclude.GetValue(slate).Contains(faction))
		{
			return false;
		}
		if (mustBePermanentEnemy.GetValue(slate) && !faction.def.permanentEnemy)
		{
			return false;
		}
		if (!allowEnemy.GetValue(slate) && FactionUtility.HostileTo(faction, Faction.OfPlayer))
		{
			return false;
		}
		if (!allowNeutral.GetValue(slate) && (int)faction.PlayerRelationKind == 1)
		{
			return false;
		}
		if (!allowAlly.GetValue(slate) && (int)faction.PlayerRelationKind == 2)
		{
			return false;
		}
		if (!(allowPermanentEnemy.GetValue(slate) ?? true) && faction.def.permanentEnemy)
		{
			return false;
		}
		if (playerCantBeAttackingCurrently.GetValue(slate) && SettlementUtility.IsPlayerAttackingAnySettlementOf(faction))
		{
			return false;
		}
		if (mustHaveGoodwillRewardsEnabled.GetValue(slate) && !faction.allowGoodwillRewards)
		{
			return false;
		}
		if (peaceTalksCantExist.GetValue(slate))
		{
			if (PeaceTalksExist(faction))
			{
				return false;
			}
			string tag = QuestNode_QuestUnique.GetProcessedTag("PeaceTalks", faction);
			if (GenCollection.Any<Quest>(Find.QuestManager.questsInDisplayOrder, (Predicate<Quest>)((Quest q) => q.tags.Contains(tag))))
			{
				return false;
			}
		}
		if (leaderMustBeSafe.GetValue(slate) && (faction.leader == null || ((Thing)faction.leader).Spawned || faction.leader.IsPrisoner))
		{
			return false;
		}
		Thing value = mustBeHostileToFactionOf.GetValue(slate);
		if (value != null && value.Faction != null && (value.Faction == faction || !FactionUtility.HostileTo(faction, value.Faction)))
		{
			return false;
		}
		return true;
	}

	private bool PeaceTalksExist(Faction faction)
	{
		List<PeaceTalks> peaceTalks = Find.WorldObjects.PeaceTalks;
		for (int i = 0; i < peaceTalks.Count; i++)
		{
			if (((WorldObject)peaceTalks[i]).Faction == faction)
			{
				return true;
			}
		}
		return false;
	}
}
