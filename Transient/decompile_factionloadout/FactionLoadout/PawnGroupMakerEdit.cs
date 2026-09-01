using System;
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace FactionLoadout;

public class PawnGroupMakerEdit : IExposable
{
	public bool IsUserAdded;

	public string KindDefName = "";

	public float Commonality = 100f;

	public float MaxTotalPoints = 9999999f;

	public List<string> DisallowedStrategyDefNames;

	public List<PawnGenOptionEdit> Options = new List<PawnGenOptionEdit>();

	public List<PawnGenOptionEdit> Traders = new List<PawnGenOptionEdit>();

	public List<PawnGenOptionEdit> Carriers = new List<PawnGenOptionEdit>();

	public List<PawnGenOptionEdit> Guards = new List<PawnGenOptionEdit>();

	public bool IsNew => IsUserAdded;

	public PawnGroupKindDef KindDef => DefDatabase<PawnGroupKindDef>.GetNamedSilentFail(KindDefName);

	public int TotalKindCount => Options.Count + Traders.Count + Carriers.Count + Guards.Count;

	public IEnumerable<PawnKindDef> GetAllKinds()
	{
		foreach (PawnGenOptionEdit option in Options)
		{
			PawnKindDef kindDef = option.KindDef;
			if (kindDef != null)
			{
				yield return kindDef;
			}
		}
		foreach (PawnGenOptionEdit trader in Traders)
		{
			PawnKindDef kindDef2 = trader.KindDef;
			if (kindDef2 != null)
			{
				yield return kindDef2;
			}
		}
		foreach (PawnGenOptionEdit carrier in Carriers)
		{
			PawnKindDef kindDef3 = carrier.KindDef;
			if (kindDef3 != null)
			{
				yield return kindDef3;
			}
		}
		foreach (PawnGenOptionEdit guard in Guards)
		{
			PawnKindDef kindDef4 = guard.KindDef;
			if (kindDef4 != null)
			{
				yield return kindDef4;
			}
		}
	}

	public static PawnGroupMakerEdit FromPawnGroupMaker(PawnGroupMaker maker)
	{
		return new PawnGroupMakerEdit
		{
			IsUserAdded = false,
			KindDefName = (((Def)(maker.kindDef?)).defName ?? ""),
			Commonality = maker.commonality,
			MaxTotalPoints = maker.maxTotalPoints,
			DisallowedStrategyDefNames = maker.disallowedStrategies?.Select((RaidStrategyDef s) => ((Def)s).defName).ToList(),
			Options = Convert(maker.options),
			Traders = Convert(maker.traders),
			Carriers = Convert(maker.carriers),
			Guards = Convert(maker.guards)
		};
		static List<PawnGenOptionEdit> Convert(List<PawnGenOption> list)
		{
			if (list != null)
			{
				return list.Select(PawnGenOptionEdit.FromOption).ToList();
			}
			return new List<PawnGenOptionEdit>();
		}
	}

	public PawnGroupMaker ToPawnGroupMaker()
	{
		//IL_0065: Unknown result type (might be due to invalid IL or missing references)
		//IL_006a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0076: Unknown result type (might be due to invalid IL or missing references)
		//IL_0082: Unknown result type (might be due to invalid IL or missing references)
		//IL_008e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0095: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a6: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b7: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c8: Unknown result type (might be due to invalid IL or missing references)
		//IL_00da: Expected O, but got Unknown
		List<RaidStrategyDef> disallowedStrategies = null;
		List<string> disallowedStrategyDefNames = DisallowedStrategyDefNames;
		if (disallowedStrategyDefNames != null && disallowedStrategyDefNames.Count > 0)
		{
			disallowedStrategies = (from d in ((IEnumerable<string>)DisallowedStrategyDefNames).Select((Func<string, RaidStrategyDef>)DefDatabase<RaidStrategyDef>.GetNamedSilentFail)
				where d != null
				select d).ToList();
		}
		return new PawnGroupMaker
		{
			kindDef = KindDef,
			commonality = Commonality,
			maxTotalPoints = MaxTotalPoints,
			disallowedStrategies = disallowedStrategies,
			options = Convert(Options),
			traders = Convert(Traders),
			carriers = Convert(Carriers),
			guards = Convert(Guards)
		};
		static List<PawnGenOption> Convert(List<PawnGenOptionEdit> list)
		{
			return (from opt in list?.Select((PawnGenOptionEdit e) => e.ToPawnGenOption())
				where opt.kind != null
				select opt).ToList() ?? new List<PawnGenOption>();
		}
	}

	public void ExposeData()
	{
		Scribe_Values.Look<bool>(ref IsUserAdded, "isUserAdded", false, false);
		Scribe_Values.Look<string>(ref KindDefName, "kindDef", "", false);
		Scribe_Values.Look<float>(ref Commonality, "commonality", 100f, false);
		Scribe_Values.Look<float>(ref MaxTotalPoints, "maxTotalPoints", 9999999f, false);
		Scribe_Collections.Look<string>(ref DisallowedStrategyDefNames, "disallowedStrategies", (LookMode)1, Array.Empty<object>());
		Scribe_Collections.Look<PawnGenOptionEdit>(ref Options, "options", (LookMode)2, Array.Empty<object>());
		Scribe_Collections.Look<PawnGenOptionEdit>(ref Traders, "traders", (LookMode)2, Array.Empty<object>());
		Scribe_Collections.Look<PawnGenOptionEdit>(ref Carriers, "carriers", (LookMode)2, Array.Empty<object>());
		Scribe_Collections.Look<PawnGenOptionEdit>(ref Guards, "guards", (LookMode)2, Array.Empty<object>());
	}
}
