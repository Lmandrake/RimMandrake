using System.Collections.Generic;
using System.Linq;
using RimWorld;
using RimWorld.QuestGen;
using UnityEngine;
using Verse;

namespace RimMandrake.Contagion
{
    // CONTAGION_GPT_ENRICHMENT_1, part 1: Draftprints. The Helix watchers
    // post a contract for a particular combination of Unfinished features
    // ("a stump, a misplaced fang, runaway growth") and buy a draftprint that
    // carries all of them.
    //
    // QuestNode_RM_HelixDraftprintContract rolls the combination at offer time
    // and adds QuestPart_RM_DraftprintContract. The quest only offers while
    // the player holds a map whose biome carries RM_ContagionSkyExtension
    // (TestRunInt), and the whole thing is off with the Draftprints toggle.
    //
    // Delivery is a gizmo on the print itself (CompDraftprint), because
    // QuestUtility.GetQuestRelatedGizmos is only consulted by pawns and a few
    // buildings, never by items (RimSage, 1.6). Fulfil consumes the print,
    // drops the silver by pod beside it and fires the completion signal,
    // which the script's QuestNode_End turns into a success.
    public class QuestNode_RM_HelixDraftprintContract : QuestNode
    {
        // Feature pool: the Unfinished's own rolled limbs, plus the monster.
        // Plain fields, not SlateRefs: fixed tuning read straight from the def.
        public List<HediffDef> limbPool;
        public HediffDef monstrousHediff;
        public IntRange limbCountRange = new IntRange(1, 2);
        public float monstrousChance = 0.2f;
        public int silverPerFeature = 120;
        public float monstrousRewardFactor = 2f;

        [NoTranslate]
        public SlateRef<string> outSignalFulfilled;

        [NoTranslate]
        public SlateRef<string> storeTraitsAs;

        [NoTranslate]
        public SlateRef<string> storeRewardAs;

        protected override bool TestRunInt(Slate slate)
        {
            if (!RM_ContagionSettings.draftprintsEnabled || limbPool.NullOrEmpty())
            {
                return false;
            }
            return Find.Maps.Any(m => m.IsPlayerHome && RM_ContagionSky.ExtFor(m) != null);
        }

        protected override void RunInt()
        {
            Slate slate = QuestGen.slate;
            List<HediffDef> pool = limbPool;
            int n = RM_DraftprintKernel.FeatureCount(limbCountRange.RandomInRange, pool.Count);

            QuestPart_RM_DraftprintContract part = new QuestPart_RM_DraftprintContract();
            part.requiredLimbs = pool.InRandomOrder().Take(n).ToList();
            part.requireMonstrous = monstrousHediff != null && Rand.Chance(monstrousChance);
            part.reward = RM_DraftprintKernel.Reward(silverPerFeature, part.requiredLimbs.Count, part.requireMonstrous,
                monstrousRewardFactor, RM_ContagionSettings.helixContractRewardFactor);
            part.inSignalEnable = QuestGen.slate.Get<string>("inSignal");
            string done = outSignalFulfilled.GetValue(slate);
            if (!done.NullOrEmpty())
            {
                part.outSignalsCompleted.Add(QuestGenUtility.HardcodedSignalWithQuestID(done));
            }
            QuestGen.quest.AddPart(part);

            string traitsKey = storeTraitsAs.GetValue(slate);
            if (!traitsKey.NullOrEmpty())
            {
                slate.Set(traitsKey, part.TraitsLabel());
            }
            string rewardKey = storeRewardAs.GetValue(slate);
            if (!rewardKey.NullOrEmpty())
            {
                slate.Set(rewardKey, part.reward);
            }
        }
    }

    public class QuestPart_RM_DraftprintContract : QuestPartActivable
    {
        public List<HediffDef> requiredLimbs = new List<HediffDef>();
        public bool requireMonstrous;
        public int reward;

        public string TraitsLabel()
        {
            IEnumerable<string> words = requiredLimbs.Where(d => d != null).Select(d => d.label);
            if (requireMonstrous)
            {
                words = words.Concat(new[] { RM_ContagionDefOf.RM_UnfinishedMonstrous.label });
            }
            return string.Join(", ", words);
        }

        public override string DescriptionPart =>
            State == QuestPartState.Enabled
                ? "The Helix want a draftprint carrying: " + TraitsLabel() + ". Select a matching print and use \"Transmit to the Helix\"."
                : null;

        public bool Matches(CompDraftprint dp)
        {
            if (dp == null)
            {
                return false;
            }
            List<int> required = requiredLimbs.Select(d => d == null ? -1 : (int)d.index).ToList();
            HashSet<int> have = new HashSet<int>(dp.limbs.Where(d => d != null).Select(d => (int)d.index));
            return RM_DraftprintKernel.Matches(dp.IsRecorded, requireMonstrous, dp.monstrous, required, have);
        }

        public static QuestPart_RM_DraftprintContract FirstOpenMatch(CompDraftprint dp)
        {
            List<Quest> quests = Find.QuestManager.QuestsListForReading;
            for (int i = 0; i < quests.Count; i++)
            {
                Quest q = quests[i];
                if (q.State != QuestState.Ongoing)
                {
                    continue;
                }
                foreach (QuestPart p in q.PartsListForReading)
                {
                    if (p is QuestPart_RM_DraftprintContract c && c.State == QuestPartState.Enabled && c.Matches(dp))
                    {
                        return c;
                    }
                }
            }
            return null;
        }

        public void Fulfil(CompDraftprint dp)
        {
            if (State != QuestPartState.Enabled || !Matches(dp) || !dp.parent.Spawned)
            {
                return;
            }
            Map map = dp.parent.Map;
            IntVec3 cell = dp.parent.Position;
            dp.parent.Destroy();
            if (reward > 0)
            {
                Thing silver = ThingMaker.MakeThing(ThingDefOf.Silver);
                silver.stackCount = reward;
                DropPodUtility.DropThingsNear(cell, map, new List<Thing> { silver }, forbid: false);
            }
            Messages.Message(
                "The Helix took the draftprint (" + TraitsLabel() + ") and paid " + reward + " silver.",
                new TargetInfo(cell, map), MessageTypeDefOf.PositiveEvent);
            Complete();
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Collections.Look(ref requiredLimbs, "requiredLimbs", LookMode.Def);
            Scribe_Values.Look(ref requireMonstrous, "requireMonstrous", false);
            Scribe_Values.Look(ref reward, "reward", 0);
            if (Scribe.mode == LoadSaveMode.PostLoadInit && requiredLimbs == null)
            {
                requiredLimbs = new List<HediffDef>();
            }
        }
    }
}
