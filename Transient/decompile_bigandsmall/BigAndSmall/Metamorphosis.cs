using System;
using System.Collections.Generic;
using System.Linq;
using Verse;

namespace BigAndSmall;

public static class Metamorphosis
{
	public static HashSet<Pawn> pawnsQueuedForMorphing = new HashSet<Pawn>();

	public static bool ValidToMorph(List<PawnExtension> pawnExtensions)
	{
		return GenCollection.Any<PawnExtension>(pawnExtensions, (Predicate<PawnExtension>)((PawnExtension x) => x.morphSettings != null));
	}

	public static MorphTarget TryGetMorphTarget(Pawn pawn, IEnumerable<MorphSettings> triggers, List<PawnExtension> morphTargets)
	{
		//IL_015d: Unknown result type (might be due to invalid IL or missing references)
		//IL_01e6: Unknown result type (might be due to invalid IL or missing references)
		bool? flag = null;
		bool? flag2 = null;
		new List<MorphSettings>();
		foreach (MorphSettings trigger in triggers)
		{
			bool flag3 = trigger.CanMorph(pawn);
			if (trigger.isRetromorph)
			{
				bool valueOrDefault = flag2 == true;
				if (!flag2.HasValue)
				{
					valueOrDefault = true;
					flag2 = valueOrDefault;
				}
				flag2 = flag3 & flag2;
			}
			else
			{
				bool valueOrDefault = flag == true;
				if (!flag.HasValue)
				{
					valueOrDefault = true;
					flag = valueOrDefault;
				}
				flag = flag3 & flag;
			}
		}
		if (!flag.HasValue && !flag2.HasValue)
		{
			return null;
		}
		List<MorphTarget> source = morphTargets.Where((PawnExtension x) => x.morphTargets != null).SelectMany((PawnExtension x) => x.morphTargets).ToList();
		if (flag == true)
		{
			List<MorphTarget> list = source.Where((MorphTarget x) => !x.isRetromorph).ToList();
			if (list.Count != 0)
			{
				return GenCollection.RandomElementByWeight<MorphTarget>((IEnumerable<MorphTarget>)TryFilterByGender(pawn?.gender, list).ToList(), (Func<MorphTarget, float>)((MorphTarget x) => x.GetMorphWeight()));
			}
		}
		if (flag2 == true)
		{
			List<MorphTarget> list2 = source.Where((MorphTarget x) => x.isRetromorph).ToList();
			if (list2.Count != 0)
			{
				return GenCollection.RandomElementByWeight<MorphTarget>((IEnumerable<MorphTarget>)TryFilterByGender(pawn?.gender, list2), (Func<MorphTarget, float>)((MorphTarget x) => x.GetMorphWeight()));
			}
		}
		return null;
	}

	/// <summary>
	/// Tries to filter the options based on gender. E.g. females will prioritise xenotypes with forced-female.
	/// </summary>
	private static List<MorphTarget> TryFilterByGender(Gender? gender, List<MorphTarget> defs)
	{
		//IL_00bd: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c1: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c6: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ea: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ee: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f3: Unknown result type (might be due to invalid IL or missing references)
		//IL_0117: Unknown result type (might be due to invalid IL or missing references)
		//IL_011b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0120: Unknown result type (might be due to invalid IL or missing references)
		//IL_0155: Unknown result type (might be due to invalid IL or missing references)
		//IL_0159: Unknown result type (might be due to invalid IL or missing references)
		//IL_015e: Unknown result type (might be due to invalid IL or missing references)
		Dictionary<Gender, List<MorphTarget>> dictionary = (from x in defs
			group x by x.GetPrefferedGender()).ToDictionary((IGrouping<Gender, MorphTarget> x) => x.Key, (IGrouping<Gender, MorphTarget> x) => x.ToList());
		List<MorphTarget> value;
		List<MorphTarget> list = (dictionary.TryGetValue((Gender)2, out value) ? value : new List<MorphTarget>());
		List<MorphTarget> value2;
		List<MorphTarget> list2 = (dictionary.TryGetValue((Gender)1, out value2) ? value2 : new List<MorphTarget>());
		List<MorphTarget> value3;
		List<MorphTarget> second = (dictionary.TryGetValue((Gender)3, out value3) ? value3 : new List<MorphTarget>());
		IEnumerable<MorphTarget> source = list.Union(second);
		IEnumerable<MorphTarget> source2 = list2.Union(second);
		if (gender == (Gender?)2 && source.Count() > 0)
		{
			return source.ToList();
		}
		if (gender == (Gender?)1 && source2.Count() > 0)
		{
			return source2.ToList();
		}
		if (gender == (Gender?)2 && list2.Count() > 0)
		{
			IEnumerable<MorphTarget> source3 = defs.Except(list2);
			if (source3.Any())
			{
				return source3.ToList();
			}
		}
		else if (gender == (Gender?)1 && list.Count() > 0)
		{
			IEnumerable<MorphTarget> source4 = defs.Except(list);
			if (source4.Any())
			{
				return source4.ToList();
			}
		}
		return defs;
	}

	public static void HandleMetamorph(Pawn pawn, List<PawnExtension> pawnExts)
	{
		if (pawnExts.Count == 0 || pawnsQueuedForMorphing.Contains(pawn))
		{
			return;
		}
		IEnumerable<PawnExtension> enumerable = pawnExts.Where((PawnExtension x) => x.morphSettings != null);
		if (!enumerable.Any())
		{
			return;
		}
		MorphTarget target = null;
		foreach (PawnExtension item in enumerable)
		{
			if (!item.morphSettings.isStandalone)
			{
				continue;
			}
			if (GenList.NullOrEmpty<MorphTarget>((IList<MorphTarget>)item.morphTargets))
			{
				Log.ErrorOnce($"{pawn} had morph settings set to standalone, but lacked targets", 92349231);
				continue;
			}
			MorphTarget morphTarget = TryGetMorphTarget(pawn, new _003C_003Ez__ReadOnlySingleElementList<MorphSettings>(item.morphSettings), new List<PawnExtension>(1) { item });
			if (morphTarget == null)
			{
				continue;
			}
			target = morphTarget;
			break;
		}
		if (target == null)
		{
			IEnumerable<MorphSettings> triggers = enumerable.Select((PawnExtension x) => x.morphSettings);
			List<PawnExtension> allPawnExtensions = pawn.GetAllPawnExtensions();
			target = TryGetMorphTarget(pawn, triggers, allPawnExtensions);
		}
		if (target != null)
		{
			pawnsQueuedForMorphing.Add(pawn);
			BigAndSmallCache.queuedJobs.Enqueue((Action)morphAction);
		}
		void morphAction()
		{
			pawnsQueuedForMorphing.Remove(pawn);
			target.ExecuteMorph(pawn);
		}
	}
}
