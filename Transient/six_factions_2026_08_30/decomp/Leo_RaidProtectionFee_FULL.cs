using System;
using System.Collections;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Reflection;
using System.Runtime.CompilerServices;
using System.Runtime.Versioning;
using HarmonyLib;
using RimWorld;
using RimWorld.Planet;
using RimWorld.QuestGen;
using UnityEngine;
using Verse;
using Verse.AI;
using Verse.Sound;

[assembly: CompilationRelaxations(8)]
[assembly: RuntimeCompatibility(WrapNonExceptionThrows = true)]
[assembly: Debuggable(DebuggableAttribute.DebuggingModes.IgnoreSymbolStoreSequencePoints)]
[assembly: TargetFramework(".NETFramework,Version=v4.7.2", FrameworkDisplayName = ".NET Framework 4.7.2")]
[assembly: AssemblyCompany("Leo.RaidProtectionFee")]
[assembly: AssemblyConfiguration("Release")]
[assembly: AssemblyFileVersion("1.0.0.0")]
[assembly: AssemblyInformationalVersion("1.0.0")]
[assembly: AssemblyProduct("Leo.RaidProtectionFee")]
[assembly: AssemblyTitle("Leo.RaidProtectionFee")]
[assembly: AssemblyVersion("1.0.0.0")]
namespace Leo.RaidProtectionFee;

[StaticConstructorOnStartup]
internal static class DefPreloader
{
	private enum ScanState : byte
	{
		Unknown,
		Visiting,
		NoRaid,
		HasRaid
	}

	private sealed class SubFieldCache
	{
		public FieldInfo[] singleNodeFields = Array.Empty<FieldInfo>();

		public FieldInfo[] nodeEnumerableFields = Array.Empty<FieldInfo>();
	}

	private static readonly Dictionary<QuestScriptDef, ScanState> questScanMemo;

	private static readonly Dictionary<Type, SubFieldCache> subFieldCache;

	static DefPreloader()
	{
		//IL_0092: Unknown result type (might be due to invalid IL or missing references)
		//IL_009c: Expected O, but got Unknown
		questScanMemo = new Dictionary<QuestScriptDef, ScanState>();
		subFieldCache = new Dictionary<Type, SubFieldCache>();
		ProtectionFee_Mod.GroupedFactions = DefDatabase<FactionDef>.AllDefsListForReading.Where((FactionDef faction) => faction.humanlikeFaction && !faction.isPlayer).OrderBy(delegate(FactionDef faction)
		{
			ModContentPack modContentPack = ((Def)faction).modContentPack;
			return ((modContentPack != null) ? modContentPack.Name : null) ?? "#Unknown";
		}).ThenBy((FactionDef faction) => ((Def)faction).label ?? ((Def)faction).defName)
			.GroupBy(delegate(FactionDef faction)
			{
				ModContentPack modContentPack2 = ((Def)faction).modContentPack;
				return ((modContentPack2 != null) ? modContentPack2.Name : null) ?? "#Unknown";
			})
			.ToList();
		ProtectionFee_Mod.AllRaidSources.Clear();
		questScanMemo.Clear();
		Slate staticSlate = new Slate();
		ProtectionFee_Mod.AllRaidSources.AddRange((IEnumerable<Def>)DefDatabase<IncidentDef>.AllDefsListForReading.Where(HasRaidIncident).ToList());
		ProtectionFee_Mod.AllRaidSources.AddRange((IEnumerable<Def>)DefDatabase<QuestScriptDef>.AllDefsListForReading.Where(delegate(QuestScriptDef quest)
		{
			if (quest == null || quest.root == null)
			{
				return false;
			}
			return !((Def)quest).defName.StartsWith("Util_") && quest.IsRootAny && HasRaidQuest(quest, staticSlate);
		}).ToList());
	}

	private static bool HasRaidIncident(IncidentDef incident)
	{
		if (incident?.workerClass == null)
		{
			return false;
		}
		if (!typeof(IncidentWorker_RaidEnemy).IsAssignableFrom(incident.workerClass))
		{
			return false;
		}
		if (incident.workerClass == typeof(IncidentWorker_ShamblerAssault))
		{
			return false;
		}
		if (incident.pawnKind != null && !incident.pawnKind.RaceProps.Humanlike)
		{
			return false;
		}
		return true;
	}

	private static bool HasRaidQuest(QuestScriptDef quest, Slate slate)
	{
		if (quest == null || quest.root == null)
		{
			return false;
		}
		if (questScanMemo.TryGetValue(quest, out var value))
		{
			switch (value)
			{
			case ScanState.HasRaid:
				return true;
			case ScanState.NoRaid:
				return false;
			case ScanState.Visiting:
				return false;
			}
		}
		questScanMemo[quest] = ScanState.Visiting;
		bool flag = ScanNode(quest.root, slate);
		questScanMemo[quest] = (flag ? ScanState.HasRaid : ScanState.NoRaid);
		return flag;
	}

	private static bool ScanNode(QuestNode root, Slate slate)
	{
		if (root == null)
		{
			return false;
		}
		Stack<QuestNode> stack = new Stack<QuestNode>();
		HashSet<QuestNode> hashSet = new HashSet<QuestNode>();
		List<QuestNode> list = new List<QuestNode>(16);
		stack.Push(root);
		while (stack.Count > 0)
		{
			QuestNode val = stack.Pop();
			if (val == null || !hashSet.Add(val))
			{
				continue;
			}
			if (val is QuestNode_Raid || val is QuestNode_RandomRaid)
			{
				return true;
			}
			QuestNode_Incident val2 = (QuestNode_Incident)(object)((val is QuestNode_Incident) ? val : null);
			if (val2 != null)
			{
				if (HasRaidIncident(val2.incidentDef.GetValue(slate)))
				{
					return true;
				}
			}
			else
			{
				QuestNode_CreateIncidents val3 = (QuestNode_CreateIncidents)(object)((val is QuestNode_CreateIncidents) ? val : null);
				if (val3 != null)
				{
					if (HasRaidIncident(val3.incidentDef.GetValue(slate)))
					{
						return true;
					}
				}
				else
				{
					QuestNode_SubScript val4 = (QuestNode_SubScript)(object)((val is QuestNode_SubScript) ? val : null);
					if (val4 != null)
					{
						QuestScriptDef value = val4.def.GetValue(slate);
						if (value != null && HasRaidQuest(value, slate))
						{
							return true;
						}
					}
				}
			}
			CollectSub(val, list);
			for (int i = 0; i < list.Count; i++)
			{
				stack.Push(list[i]);
			}
		}
		return false;
	}

	private static void CollectSub(QuestNode node, List<QuestNode> output)
	{
		output.Clear();
		if (node == null)
		{
			return;
		}
		Type type = ((object)node).GetType();
		if (!subFieldCache.TryGetValue(type, out var value))
		{
			value = BuildSubFieldCache(type);
			subFieldCache[type] = value;
		}
		FieldInfo[] singleNodeFields = value.singleNodeFields;
		for (int i = 0; i < singleNodeFields.Length; i++)
		{
			object value2 = singleNodeFields[i].GetValue(node);
			QuestNode val = (QuestNode)((value2 is QuestNode) ? value2 : null);
			if (val != null && val != null)
			{
				output.Add(val);
			}
		}
		FieldInfo[] nodeEnumerableFields = value.nodeEnumerableFields;
		for (int j = 0; j < nodeEnumerableFields.Length; j++)
		{
			if (!(nodeEnumerableFields[j].GetValue(node) is IEnumerable enumerable))
			{
				continue;
			}
			foreach (object item in enumerable)
			{
				QuestNode val2 = (QuestNode)((item is QuestNode) ? item : null);
				if (val2 != null && val2 != null)
				{
					output.Add(val2);
				}
			}
		}
	}

	private static SubFieldCache BuildSubFieldCache(Type type)
	{
		List<FieldInfo> list = new List<FieldInfo>(4);
		List<FieldInfo> list2 = new List<FieldInfo>(2);
		BindingFlags bindingAttr = BindingFlags.DeclaredOnly | BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic;
		Type type2 = type;
		while (type2 != null && type2 != typeof(object))
		{
			FieldInfo[] fields = type2.GetFields(bindingAttr);
			foreach (FieldInfo fieldInfo in fields)
			{
				if (fieldInfo.IsStatic)
				{
					continue;
				}
				Type fieldType = fieldInfo.FieldType;
				if (typeof(QuestNode).IsAssignableFrom(fieldType))
				{
					list.Add(fieldInfo);
				}
				else if (fieldType.IsArray && typeof(QuestNode).IsAssignableFrom(fieldType.GetElementType()))
				{
					list2.Add(fieldInfo);
				}
				else if (fieldType.IsGenericType && typeof(IEnumerable).IsAssignableFrom(fieldType))
				{
					Type[] genericArguments = fieldType.GetGenericArguments();
					if (genericArguments.Length == 1 && typeof(QuestNode).IsAssignableFrom(genericArguments[0]))
					{
						list2.Add(fieldInfo);
					}
				}
			}
			type2 = type2.BaseType;
		}
		return new SubFieldCache
		{
			singleNodeFields = list.ToArray(),
			nodeEnumerableFields = list2.ToArray()
		};
	}
}
internal class DemandPolicy : Policy
{
	public bool allowHumanlikeFreeColonists;

	public bool allowHumanlikePrisoners = true;

	public bool allowHumanlikeSlaves = true;

	public ThingFilter filter = new ThingFilter();

	protected override string LoadKey => "DemandPolicy";

	private DemandPolicy()
	{
	}//IL_000f: Unknown result type (might be due to invalid IL or missing references)
	//IL_0019: Expected O, but got Unknown


	public DemandPolicy(int id, string label)
		: base(id, label)
	{
	}//IL_000f: Unknown result type (might be due to invalid IL or missing references)
	//IL_0019: Expected O, but got Unknown


	public override void CopyFrom(Policy other)
	{
		//IL_0010: Unknown result type (might be due to invalid IL or missing references)
		//IL_001a: Expected O, but got Unknown
		DemandPolicy demandPolicy = (DemandPolicy)(object)other;
		if (filter == null)
		{
			filter = new ThingFilter();
		}
		if (demandPolicy.filter != null)
		{
			filter.CopyAllowancesFrom(demandPolicy.filter);
		}
		allowHumanlikeFreeColonists = demandPolicy.allowHumanlikeFreeColonists;
		allowHumanlikePrisoners = demandPolicy.allowHumanlikePrisoners;
		allowHumanlikeSlaves = demandPolicy.allowHumanlikeSlaves;
	}

	public override void ExposeData()
	{
		((Policy)this).ExposeData();
		Scribe_Deep.Look<ThingFilter>(ref filter, "filter", Array.Empty<object>());
		Scribe_Values.Look<bool>(ref allowHumanlikeFreeColonists, "allowHumanlikeFreeColonists", false, false);
		Scribe_Values.Look<bool>(ref allowHumanlikePrisoners, "allowHumanlikePrisoners", true, false);
		Scribe_Values.Look<bool>(ref allowHumanlikeSlaves, "allowHumanlikeSlaves", true, false);
	}
}
internal class DemandPolicyDatabase
{
	private static readonly List<DemandPolicy> fallbackDemandPolicies;

	private static List<DemandPolicy> DemandPolicies
	{
		get
		{
			if (ProtectionFee_Mod.Settings != null)
			{
				if (ProtectionFee_Mod.Settings.demandPolicies == null)
				{
					ProtectionFee_Mod.Settings.demandPolicies = new List<DemandPolicy>();
				}
				return ProtectionFee_Mod.Settings.demandPolicies;
			}
			return fallbackDemandPolicies;
		}
	}

	public static List<DemandPolicy> AllDemandPolicies => DemandPolicies;

	static DemandPolicyDatabase()
	{
		fallbackDemandPolicies = new List<DemandPolicy>();
		GenerateStartingPolicies();
	}

	public void ExposeData()
	{
		BackCompatibility.PostExposeData((object)this);
	}

	public static DemandPolicy DefaultDemandPolicy()
	{
		GenerateStartingPolicies();
		return DemandPolicies[0];
	}

	public static void SetDefault(DemandPolicy policy)
	{
		int num = DemandPolicies.IndexOf(policy);
		if (num > 0)
		{
			DemandPolicy value = DemandPolicies[0];
			DemandPolicies[0] = policy;
			DemandPolicies[num] = value;
			ProtectionFee_ModSettings settings = ProtectionFee_Mod.Settings;
			if (settings != null)
			{
				((ModSettings)settings).Write();
			}
		}
	}

	public static AcceptanceReport TryDelete(DemandPolicy policy)
	{
		//IL_008b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0090: Unknown result type (might be due to invalid IL or missing references)
		//IL_009a: Unknown result type (might be due to invalid IL or missing references)
		//IL_00bc: Unknown result type (might be due to invalid IL or missing references)
		//IL_0048: Unknown result type (might be due to invalid IL or missing references)
		//IL_004d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0057: Unknown result type (might be due to invalid IL or missing references)
		//IL_005c: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c2: Unknown result type (might be due to invalid IL or missing references)
		if (ProtectionFee_Mod.Settings?.factionPolicyAssignments != null)
		{
			foreach (KeyValuePair<string, int> factionPolicyAssignment in ProtectionFee_Mod.Settings.factionPolicyAssignments)
			{
				if (factionPolicyAssignment.Value == ((Policy)policy).id)
				{
					return new AcceptanceReport(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("ProtectionFee.DemandPolicyInUse", NamedArgument.op_Implicit(factionPolicyAssignment.Key))));
				}
			}
		}
		if (policy == DefaultDemandPolicy())
		{
			return new AcceptanceReport(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("ProtectionFee.DemandPolicyInDefault", NamedArgument.op_Implicit(((Policy)policy).label))));
		}
		DemandPolicies.Remove(policy);
		ProtectionFee_ModSettings settings = ProtectionFee_Mod.Settings;
		if (settings != null)
		{
			((ModSettings)settings).Write();
		}
		return AcceptanceReport.WasAccepted;
	}

	public static DemandPolicy MakeNewDemandPolicy()
	{
		//IL_0046: Unknown result type (might be due to invalid IL or missing references)
		int id = ((!GenCollection.Any<DemandPolicy>(DemandPolicies)) ? 1 : (DemandPolicies.Max((DemandPolicy o) => ((Policy)o).id) + 1));
		DemandPolicy demandPolicy = new DemandPolicy(id, string.Format("{0} {1}", Translator.Translate("ProtectionFee.DemandPolicy"), id.ToString()));
		demandPolicy.filter.SetAllowAll((ThingFilter)null, false);
		ApplyPawnAllowances(demandPolicy);
		DemandPolicies.Add(demandPolicy);
		ProtectionFee_ModSettings settings = ProtectionFee_Mod.Settings;
		if (settings != null)
		{
			((ModSettings)settings).Write();
		}
		return demandPolicy;
	}

	public static void GenerateStartingPolicies()
	{
		if (DemandPolicies.Count <= 0)
		{
			DemandPolicy demandPolicy = new DemandPolicy(0, "Demand Anything");
			demandPolicy.filter.SetAllowAll((ThingFilter)null, false);
			ApplyPawnAllowances(demandPolicy);
			DemandPolicies.Add(demandPolicy);
			ProtectionFee_ModSettings settings = ProtectionFee_Mod.Settings;
			if (settings != null)
			{
				((ModSettings)settings).Write();
			}
		}
	}

	public static DemandPolicy GetPolicyForTrader(ITrader trader)
	{
		if (trader == null)
		{
			return DefaultDemandPolicy();
		}
		string text = null;
		if (trader.Faction?.def != null && !GenText.NullOrEmpty(((Def)trader.Faction.def).defName))
		{
			text = ((Def)trader.Faction.def).defName;
		}
		else if (trader.TraderKind?.faction != null && !GenText.NullOrEmpty(((Def)trader.TraderKind.faction).defName))
		{
			text = ((Def)trader.TraderKind.faction).defName;
		}
		if (GenText.NullOrEmpty(text) || ProtectionFee_Mod.Settings?.factionPolicyAssignments == null)
		{
			return DefaultDemandPolicy();
		}
		if (ProtectionFee_Mod.Settings.factionPolicyAssignments.TryGetValue(text, out var policyId))
		{
			DemandPolicy demandPolicy = GenCollection.FirstOrDefault<DemandPolicy>(AllDemandPolicies, (Predicate<DemandPolicy>)((DemandPolicy p) => ((Policy)p).id == policyId));
			if (demandPolicy != null)
			{
				return demandPolicy;
			}
		}
		ProtectionFee_Mod.Settings.factionPolicyAssignments[text] = ((Policy)DefaultDemandPolicy()).id;
		ProtectionFee_ModSettings settings = ProtectionFee_Mod.Settings;
		if (settings != null)
		{
			((ModSettings)settings).Write();
		}
		return DefaultDemandPolicy();
	}

	public static void ApplyPawnAllowances(DemandPolicy policy)
	{
		//IL_003a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0040: Invalid comparison between Unknown and I4
		bool flag = policy.allowHumanlikeFreeColonists || policy.allowHumanlikePrisoners || (ModsConfig.IdeologyActive && policy.allowHumanlikeSlaves);
		foreach (ThingDef item in DefDatabase<ThingDef>.AllDefsListForReading)
		{
			if ((int)item.category == 1 && item.race != null)
			{
				bool flag2 = flag && item.race.Humanlike;
				policy.filter.SetAllow(item, flag2);
			}
		}
	}
}
internal class Dialog_ManageDemandPolicies : Dialog_ManagePolicies<DemandPolicy>
{
	[CompilerGenerated]
	private sealed class <HiddenSpecialThingFilters>d__20 : IEnumerable<SpecialThingFilterDef>, IEnumerable, IEnumerator<SpecialThingFilterDef>, IDisposable, IEnumerator
	{
		private int <>1__state;

		private SpecialThingFilterDef <>2__current;

		private int <>l__initialThreadId;

		SpecialThingFilterDef IEnumerator<SpecialThingFilterDef>.Current
		{
			[DebuggerHidden]
			get
			{
				return <>2__current;
			}
		}

		object IEnumerator.Current
		{
			[DebuggerHidden]
			get
			{
				return <>2__current;
			}
		}

		[DebuggerHidden]
		public <HiddenSpecialThingFilters>d__20(int <>1__state)
		{
			this.<>1__state = <>1__state;
			<>l__initialThreadId = Environment.CurrentManagedThreadId;
		}

		[DebuggerHidden]
		void IDisposable.Dispose()
		{
			<>1__state = -2;
		}

		private bool MoveNext()
		{
			switch (<>1__state)
			{
			default:
				return false;
			case 0:
				<>1__state = -1;
				<>2__current = SpecialThingFilterDefOf.AllowFresh;
				<>1__state = 1;
				return true;
			case 1:
				<>1__state = -1;
				if (ModsConfig.IdeologyActive)
				{
					<>2__current = SpecialThingFilterDefOf.AllowVegetarian;
					<>1__state = 2;
					return true;
				}
				break;
			case 2:
				<>1__state = -1;
				<>2__current = SpecialThingFilterDefOf.AllowCarnivore;
				<>1__state = 3;
				return true;
			case 3:
				<>1__state = -1;
				<>2__current = SpecialThingFilterDefOf.AllowCannibal;
				<>1__state = 4;
				return true;
			case 4:
				<>1__state = -1;
				<>2__current = SpecialThingFilterDefOf.AllowInsectMeat;
				<>1__state = 5;
				return true;
			case 5:
				<>1__state = -1;
				break;
			}
			return false;
		}

		bool IEnumerator.MoveNext()
		{
			//ILSpy generated this explicit interface implementation from .override directive in MoveNext
			return this.MoveNext();
		}

		[DebuggerHidden]
		void IEnumerator.Reset()
		{
			throw new NotSupportedException();
		}

		[DebuggerHidden]
		IEnumerator<SpecialThingFilterDef> IEnumerable<SpecialThingFilterDef>.GetEnumerator()
		{
			if (<>1__state == -2 && <>l__initialThreadId == Environment.CurrentManagedThreadId)
			{
				<>1__state = 0;
				return this;
			}
			return new <HiddenSpecialThingFilters>d__20(0);
		}

		[DebuggerHidden]
		IEnumerator IEnumerable.GetEnumerator()
		{
			return ((IEnumerable<SpecialThingFilterDef>)this).GetEnumerator();
		}
	}

	private readonly UIState thingFilterState = new UIState();

	private static ThingFilter demandGlobalFilter;

	public static ThingFilter DemandGlobalFilter
	{
		get
		{
			//IL_0007: Unknown result type (might be due to invalid IL or missing references)
			//IL_0011: Expected O, but got Unknown
			if (demandGlobalFilter == null)
			{
				demandGlobalFilter = new ThingFilter();
				demandGlobalFilter.SetAllow(ThingCategoryDefOf.Root, true, (IEnumerable<ThingDef>)null, (IEnumerable<SpecialThingFilterDef>)null);
			}
			return demandGlobalFilter;
		}
	}

	protected override string TitleKey => "ProtectionFee.DemandPolicyTitle";

	protected override string TipKey => "ProtectionFee.DemandPolicyTip";

	public override Vector2 InitialSize => new Vector2(700f, 700f);

	public Dialog_ManageDemandPolicies(DemandPolicy Policy)
		: base(Policy)
	{
	}//IL_0001: Unknown result type (might be due to invalid IL or missing references)
	//IL_000b: Expected O, but got Unknown


	public override void PreOpen()
	{
		base.PreOpen();
		thingFilterState.quickSearch.Reset();
	}

	protected override DemandPolicy CreateNewPolicy()
	{
		return DemandPolicyDatabase.MakeNewDemandPolicy();
	}

	protected override DemandPolicy GetDefaultPolicy()
	{
		return DemandPolicyDatabase.DefaultDemandPolicy();
	}

	protected override void SetDefaultPolicy(DemandPolicy policy)
	{
		DemandPolicyDatabase.SetDefault(policy);
	}

	protected override AcceptanceReport TryDeletePolicy(DemandPolicy demandPolicy)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		return DemandPolicyDatabase.TryDelete(demandPolicy);
	}

	protected override List<DemandPolicy> GetPolicies()
	{
		return DemandPolicyDatabase.AllDemandPolicies;
	}

	protected override void DoContentsRect(Rect rect)
	{
		//IL_000e: Unknown result type (might be due to invalid IL or missing references)
		//IL_000f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0018: Unknown result type (might be due to invalid IL or missing references)
		//IL_0019: Unknown result type (might be due to invalid IL or missing references)
		//IL_0030: Unknown result type (might be due to invalid IL or missing references)
		//IL_0037: Expected O, but got Unknown
		//IL_0039: Unknown result type (might be due to invalid IL or missing references)
		//IL_003f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0051: Unknown result type (might be due to invalid IL or missing references)
		//IL_0075: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a0: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d1: Unknown result type (might be due to invalid IL or missing references)
		float optionsHeight = GetOptionsHeight(((Rect)(ref rect)).width);
		Rect val = rect;
		((Rect)(ref val)).height = optionsHeight;
		Rect val2 = rect;
		((Rect)(ref val2)).yMin = ((Rect)(ref val)).yMax + 6f;
		bool flag = false;
		Listing_Standard val3 = new Listing_Standard();
		((Listing)val3).Begin(GenUI.ContractedBy(val, 6f));
		flag |= CheckboxChanged(val3, TaggedString.op_Implicit(Translator.Translate("ProtectionFee.AllowColonists")), ref base.SelectedPolicy.allowHumanlikeFreeColonists);
		flag |= CheckboxChanged(val3, TaggedString.op_Implicit(Translator.Translate("ProtectionFee.AllowPrisoners")), ref base.SelectedPolicy.allowHumanlikePrisoners);
		if (ModsConfig.IdeologyActive)
		{
			flag |= CheckboxChanged(val3, TaggedString.op_Implicit(Translator.Translate("ProtectionFee.AllowSlaves")), ref base.SelectedPolicy.allowHumanlikeSlaves);
		}
		((Listing)val3).End();
		if (flag)
		{
			DemandPolicyDatabase.ApplyPawnAllowances(base.SelectedPolicy);
		}
		ThingFilterUI.DoThingFilterConfigWindow(val2, thingFilterState, base.SelectedPolicy.filter, DemandGlobalFilter, 16, (IEnumerable<ThingDef>)null, HiddenSpecialThingFilters(), false, false, false, (List<ThingDef>)null, (Map)null);
	}

	private float GetOptionsHeight(float fullWidth)
	{
		//IL_0018: Unknown result type (might be due to invalid IL or missing references)
		//IL_0029: Unknown result type (might be due to invalid IL or missing references)
		//IL_0047: Unknown result type (might be due to invalid IL or missing references)
		//IL_006c: Unknown result type (might be due to invalid IL or missing references)
		float num = Mathf.Max(1f, fullWidth - 12f);
		float num2 = 12f;
		GameFont font = Text.Font;
		Text.Font = (GameFont)1;
		num2 += Text.CalcHeight(TaggedString.op_Implicit(Translator.Translate("ProtectionFee.AllowColonists")), num) + 2f;
		num2 += Text.CalcHeight(TaggedString.op_Implicit(Translator.Translate("ProtectionFee.AllowPrisoners")), num) + 2f;
		if (ModsConfig.IdeologyActive)
		{
			num2 += Text.CalcHeight(TaggedString.op_Implicit(Translator.Translate("ProtectionFee.AllowSlaves")), num) + 2f;
		}
		Text.Font = font;
		return num2;
	}

	private static bool CheckboxChanged(Listing_Standard listing, string label, ref bool value)
	{
		bool num = value;
		listing.CheckboxLabeled(label, ref value, (string)null, 0f, 1f);
		return num != value;
	}

	[IteratorStateMachine(typeof(<HiddenSpecialThingFilters>d__20))]
	private IEnumerable<SpecialThingFilterDef> HiddenSpecialThingFilters()
	{
		//yield-return decompiler failed: Unexpected instruction in Iterator.Dispose()
		return new <HiddenSpecialThingFilters>d__20(-2);
	}
}
internal class Dialog_Ransom : Dialog_Trade
{
	private Action onCloseAction;

	public Dialog_Ransom(Pawn playerNegotiator, ITrader trader, Action onClose)
		: base(playerNegotiator, trader, false)
	{
		onCloseAction = onClose;
		((Window)this).closeOnAccept = true;
	}

	public override void Close(bool doCloseSound = true)
	{
		((Dialog_Trade)this).Close(doCloseSound);
		onCloseAction?.Invoke();
		onCloseAction = null;
	}
}
internal class ITrader_Ransom : ITrader
{
	[CompilerGenerated]
	private sealed class <ColonyThingsWillingToBuy>d__22 : IEnumerable<Thing>, IEnumerable, IEnumerator<Thing>, IDisposable, IEnumerator
	{
		private int <>1__state;

		private Thing <>2__current;

		private int <>l__initialThreadId;

		private Pawn playerNegotiator;

		public Pawn <>3__playerNegotiator;

		public ITrader_Ransom <>4__this;

		private Map <tradeMap>5__2;

		private List<Thing>.Enumerator <>7__wrap2;

		private List<Building>.Enumerator <>7__wrap3;

		private List<Genepack>.Enumerator <>7__wrap4;

		private IEnumerator<IHaulSource> <>7__wrap5;

		private IEnumerator<Thing> <>7__wrap6;

		private IEnumerator<Pawn> <>7__wrap7;

		Thing IEnumerator<Thing>.Current
		{
			[DebuggerHidden]
			get
			{
				return <>2__current;
			}
		}

		object IEnumerator.Current
		{
			[DebuggerHidden]
			get
			{
				return <>2__current;
			}
		}

		[DebuggerHidden]
		public <ColonyThingsWillingToBuy>d__22(int <>1__state)
		{
			this.<>1__state = <>1__state;
			<>l__initialThreadId = Environment.CurrentManagedThreadId;
		}

		[DebuggerHidden]
		void IDisposable.Dispose()
		{
			int num = <>1__state;
			switch (num)
			{
			case -3:
			case 1:
				try
				{
				}
				finally
				{
					<>m__Finally1();
				}
				break;
			case -5:
			case -4:
			case 2:
				try
				{
					if (num == -5 || num == 2)
					{
						try
						{
						}
						finally
						{
							<>m__Finally3();
						}
					}
				}
				finally
				{
					<>m__Finally2();
				}
				break;
			case -7:
			case -6:
			case 3:
				try
				{
					if (num == -7 || num == 3)
					{
						try
						{
						}
						finally
						{
							<>m__Finally5();
						}
					}
				}
				finally
				{
					<>m__Finally4();
				}
				break;
			case -8:
			case 4:
				try
				{
				}
				finally
				{
					<>m__Finally6();
				}
				break;
			}
			<tradeMap>5__2 = null;
			<>7__wrap2 = default(List<Thing>.Enumerator);
			<>7__wrap3 = default(List<Building>.Enumerator);
			<>7__wrap4 = default(List<Genepack>.Enumerator);
			<>7__wrap5 = null;
			<>7__wrap6 = null;
			<>7__wrap7 = null;
			<>1__state = -2;
		}

		private bool MoveNext()
		{
			//IL_0098: Unknown result type (might be due to invalid IL or missing references)
			//IL_009e: Invalid comparison between Unknown and I4
			//IL_00af: Unknown result type (might be due to invalid IL or missing references)
			//IL_0276: Unknown result type (might be due to invalid IL or missing references)
			//IL_027d: Expected O, but got Unknown
			//IL_00d2: Unknown result type (might be due to invalid IL or missing references)
			try
			{
				int num = <>1__state;
				ITrader_Ransom trader_Ransom = <>4__this;
				CompGenepackContainer val;
				IHaulSource current2;
				switch (num)
				{
				default:
					return false;
				case 0:
				{
					<>1__state = -1;
					Pawn obj = playerNegotiator;
					<tradeMap>5__2 = ((obj != null) ? ((Thing)obj).Map : null);
					if (<tradeMap>5__2 == null)
					{
						return false;
					}
					<>7__wrap2 = <tradeMap>5__2.listerThings.ThingsInGroup((ThingRequestGroup)4).GetEnumerator();
					<>1__state = -3;
					goto IL_0112;
				}
				case 1:
					<>1__state = -3;
					goto IL_0112;
				case 2:
					<>1__state = -5;
					goto IL_01fe;
				case 3:
					<>1__state = -7;
					goto IL_02e3;
				case 4:
					{
						<>1__state = -8;
						break;
					}
					IL_01a8:
					<>7__wrap4 = val.ContainedGenepacks.GetEnumerator();
					<>1__state = -5;
					goto IL_01fe;
					IL_01fe:
					while (<>7__wrap4.MoveNext())
					{
						Genepack current = <>7__wrap4.Current;
						if (TradeUtility.PlayerSellableNow((Thing)(object)current, (ITrader)(object)playerNegotiator))
						{
							<>2__current = (Thing)(object)current;
							<>1__state = 2;
							return true;
						}
					}
					<>m__Finally3();
					<>7__wrap4 = default(List<Genepack>.Enumerator);
					goto IL_021d;
					IL_028d:
					<>7__wrap6 = ((IEnumerable<Thing>)((IThingHolder)current2).GetDirectlyHeldThings()).GetEnumerator();
					<>1__state = -7;
					goto IL_02e3;
					IL_02e3:
					while (<>7__wrap6.MoveNext())
					{
						Thing current3 = <>7__wrap6.Current;
						if (TradeUtility.PlayerSellableNow(current3, (ITrader)(object)playerNegotiator))
						{
							<>2__current = current3;
							<>1__state = 3;
							return true;
						}
					}
					<>m__Finally5();
					<>7__wrap6 = null;
					goto IL_02fd;
					IL_023f:
					<>7__wrap5 = <tradeMap>5__2.listerBuildings.AllColonistBuildingsOfType<IHaulSource>().GetEnumerator();
					<>1__state = -6;
					goto IL_02fd;
					IL_0112:
					while (<>7__wrap2.MoveNext())
					{
						Thing current4 = <>7__wrap2.Current;
						if ((int)current4.def.category == 2 && TradeUtility.PlayerSellableNow(current4, (ITrader)(object)playerNegotiator) && !GridsUtility.Fogged(current4.Position, <tradeMap>5__2) && (((Area)<tradeMap>5__2.areaManager.Home)[current4.Position] || StoreUtility.IsInAnyStorage(current4)) && trader_Ransom.ReachableForTrade(playerNegotiator, current4))
						{
							<>2__current = current4;
							<>1__state = 1;
							return true;
						}
					}
					<>m__Finally1();
					<>7__wrap2 = default(List<Thing>.Enumerator);
					if (ModsConfig.BiotechActive)
					{
						List<Building> list = <tradeMap>5__2.listerBuildings.AllBuildingsColonistOfDef(ThingDefOf.GeneBank);
						<>7__wrap3 = list.GetEnumerator();
						<>1__state = -4;
						goto IL_021d;
					}
					goto IL_023f;
					IL_02fd:
					while (<>7__wrap5.MoveNext())
					{
						current2 = <>7__wrap5.Current;
						Building thing = (Building)current2;
						if (!trader_Ransom.ReachableForTrade(playerNegotiator, (Thing)(object)thing))
						{
							continue;
						}
						goto IL_028d;
					}
					<>m__Finally4();
					<>7__wrap5 = null;
					<>7__wrap7 = TradeUtility.AllSellableColonyPawns(<tradeMap>5__2, true).GetEnumerator();
					<>1__state = -8;
					break;
					IL_021d:
					while (<>7__wrap3.MoveNext())
					{
						Building current5 = <>7__wrap3.Current;
						if (!trader_Ransom.ReachableForTrade(playerNegotiator, (Thing)(object)current5))
						{
							continue;
						}
						val = ThingCompUtility.TryGetComp<CompGenepackContainer>((Thing)(object)current5);
						if (((val != null) ? val.ContainedGenepacks : null) == null)
						{
							continue;
						}
						goto IL_01a8;
					}
					<>m__Finally2();
					<>7__wrap3 = default(List<Building>.Enumerator);
					goto IL_023f;
				}
				while (<>7__wrap7.MoveNext())
				{
					Pawn current6 = <>7__wrap7.Current;
					if (!current6.Downed && trader_Ransom.ReachableForTrade(playerNegotiator, (Thing)(object)current6))
					{
						<>2__current = (Thing)(object)current6;
						<>1__state = 4;
						return true;
					}
				}
				<>m__Finally6();
				<>7__wrap7 = null;
				return false;
			}
			catch
			{
				//try-fault
				((IDisposable)this).Dispose();
				throw;
			}
		}

		bool IEnumerator.MoveNext()
		{
			//ILSpy generated this explicit interface implementation from .override directive in MoveNext
			return this.MoveNext();
		}

		private void <>m__Finally1()
		{
			<>1__state = -1;
			((IDisposable)<>7__wrap2/*cast due to .constrained prefix*/).Dispose();
		}

		private void <>m__Finally2()
		{
			<>1__state = -1;
			((IDisposable)<>7__wrap3/*cast due to .constrained prefix*/).Dispose();
		}

		private void <>m__Finally3()
		{
			<>1__state = -4;
			((IDisposable)<>7__wrap4/*cast due to .constrained prefix*/).Dispose();
		}

		private void <>m__Finally4()
		{
			<>1__state = -1;
			if (<>7__wrap5 != null)
			{
				<>7__wrap5.Dispose();
			}
		}

		private void <>m__Finally5()
		{
			<>1__state = -6;
			if (<>7__wrap6 != null)
			{
				<>7__wrap6.Dispose();
			}
		}

		private void <>m__Finally6()
		{
			<>1__state = -1;
			if (<>7__wrap7 != null)
			{
				<>7__wrap7.Dispose();
			}
		}

		[DebuggerHidden]
		void IEnumerator.Reset()
		{
			throw new NotSupportedException();
		}

		[DebuggerHidden]
		IEnumerator<Thing> IEnumerable<Thing>.GetEnumerator()
		{
			<ColonyThingsWillingToBuy>d__22 <ColonyThingsWillingToBuy>d__;
			if (<>1__state == -2 && <>l__initialThreadId == Environment.CurrentManagedThreadId)
			{
				<>1__state = 0;
				<ColonyThingsWillingToBuy>d__ = this;
			}
			else
			{
				<ColonyThingsWillingToBuy>d__ = new <ColonyThingsWillingToBuy>d__22(0)
				{
					<>4__this = <>4__this
				};
			}
			<ColonyThingsWillingToBuy>d__.playerNegotiator = <>3__playerNegotiator;
			return <ColonyThingsWillingToBuy>d__;
		}

		[DebuggerHidden]
		IEnumerator IEnumerable.GetEnumerator()
		{
			return ((IEnumerable<Thing>)this).GetEnumerator();
		}
	}

	private readonly Faction faction;

	public readonly Map map;

	private readonly Pawn leader;

	private readonly TraderKindDef cachedTraderKind;

	public string TraderName
	{
		get
		{
			//IL_0012: Unknown result type (might be due to invalid IL or missing references)
			if (leader == null)
			{
				return string.Format("{0} {1}", Translator.Translate("ProtectionFee_TraderRep"), faction);
			}
			return $"{((Entity)leader).LabelShort} ({faction})";
		}
	}

	public TraderKindDef TraderKind => cachedTraderKind;

	public IEnumerable<Thing> Goods => Enumerable.Empty<Thing>();

	public int RandomPriceFactorSeed => faction.loadID;

	public bool CanTradeNow => true;

	public float TradePriceImprovementOffsetForPlayer => 0f;

	public Faction Faction => faction;

	public TradeCurrency TradeCurrency => (TradeCurrency)0;

	public bool AcceptsByDemandPolicy(Thing thing)
	{
		if (thing == null)
		{
			return true;
		}
		DemandPolicy policyForTrader = DemandPolicyDatabase.GetPolicyForTrader((ITrader)(object)this);
		if (policyForTrader == null || policyForTrader.filter == null)
		{
			return true;
		}
		if (!policyForTrader.filter.Allows(thing))
		{
			return false;
		}
		Pawn val = (Pawn)(object)((thing is Pawn) ? thing : null);
		if (val != null)
		{
			if (val.RaceProps.Humanlike)
			{
				if (val.IsFreeNonSlaveColonist)
				{
					return policyForTrader.allowHumanlikeFreeColonists;
				}
				if (val.IsPrisonerOfColony)
				{
					return policyForTrader.allowHumanlikePrisoners;
				}
				if (ModsConfig.IdeologyActive && val.IsSlaveOfColony)
				{
					return policyForTrader.allowHumanlikeSlaves;
				}
				return false;
			}
			return false;
		}
		return true;
	}

	public ITrader_Ransom(Faction faction, Map map, Pawn leader = null)
	{
		//IL_0021: Unknown result type (might be due to invalid IL or missing references)
		//IL_0027: Invalid comparison between Unknown and I4
		//IL_004f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0055: Invalid comparison between Unknown and I4
		this.faction = faction;
		this.map = map;
		this.leader = leader;
		if ((int)faction.def.techLevel >= 6)
		{
			cachedTraderKind = DefDatabase<TraderKindDef>.GetNamedSilentFail("Base_Empire_Standard") ?? DefDatabase<TraderKindDef>.GetNamed("Base_Outlander_Standard", true);
		}
		else if ((int)faction.def.techLevel <= 2)
		{
			cachedTraderKind = DefDatabase<TraderKindDef>.GetNamed("Base_Neolithic_Standard", true);
		}
		else
		{
			cachedTraderKind = DefDatabase<TraderKindDef>.GetNamed("Base_Outlander_Standard", true);
		}
	}

	[IteratorStateMachine(typeof(<ColonyThingsWillingToBuy>d__22))]
	public IEnumerable<Thing> ColonyThingsWillingToBuy(Pawn playerNegotiator)
	{
		//yield-return decompiler failed: Unexpected instruction in Iterator.Dispose()
		return new <ColonyThingsWillingToBuy>d__22(-2)
		{
			<>4__this = this,
			<>3__playerNegotiator = playerNegotiator
		};
	}

	private bool ReachableForTrade(Pawn negotiator, Thing thing)
	{
		//IL_0032: Unknown result type (might be due to invalid IL or missing references)
		//IL_0038: Unknown result type (might be due to invalid IL or missing references)
		if (thing == null)
		{
			return false;
		}
		Thing val = thing;
		if (HaulAIUtility.IsInHaulableInventory(thing))
		{
			val = thing.SpawnedParentOrMe;
		}
		if (((Thing)negotiator).Map != val.MapHeld)
		{
			return false;
		}
		return ((Thing)negotiator).Map.reachability.CanReach(((Thing)negotiator).Position, LocalTargetInfo.op_Implicit(val), (PathEndMode)2, (TraverseMode)1, (Danger)2);
	}

	public void GiveSoldThingToTrader(Thing toGive, int countToGive, Pawn playerNegotiator)
	{
		Pawn val = (Pawn)(object)((toGive is Pawn) ? toGive : null);
		if (val != null)
		{
			bool num = val.IsColonist && !val.IsSlave;
			bool flag = QuestUtility.IsQuestLodger(val);
			if (num && !flag)
			{
				PawnDiedOrDownedThoughtsUtility.TryGiveThoughts(val, (DamageInfo?)null, (PawnDiedOrDownedThoughtsKind)1);
			}
			((Thing)val).PreTraded((TradeAction)2, playerNegotiator, (ITrader)(object)this);
			((Thing)val).SetFaction(faction, (Pawn)null);
			if (((Thing)val).Spawned)
			{
				((Entity)val).DeSpawn((DestroyMode)0);
			}
			if (!Find.WorldPawns.Contains(val))
			{
				Find.WorldPawns.PassToWorld(val, (PawnDiscardDecideMode)1);
			}
		}
		else
		{
			toGive.SplitOff(countToGive).Destroy((DestroyMode)0);
		}
	}

	public void GiveSoldThingToPlayer(Thing toGive, int countToGive, Pawn playerNegotiator)
	{
	}
}
public class ProtectionFee_ModSettings : ModSettings
{
	public static readonly Dictionary<string, float> DefaultDoubleCross = new Dictionary<string, float>
	{
		["OutlanderCivil"] = 0.02f,
		["OutlanderRough"] = 0.05f,
		["TribeRough"] = 0.1f,
		["TribeCivil"] = 0.02f,
		["TribeSavage"] = 0.1f,
		["Pirate"] = 0.08f,
		["AncientsHostile"] = 0.15f,
		["Ancients"] = 0.05f,
		["OutlanderRefugee"] = 0.05f,
		["Empire"] = 0.01f,
		["Beggars"] = 0.05f,
		["CannibalPirate"] = 0.12f,
		["TribeCannibal"] = 0.1f,
		["NudistTribe"] = 0.08f,
		["Pilgrims"] = 0.02f,
		["OutlanderRoughPig"] = 0.05f,
		["TribeRoughNeanderthal"] = 0.1f,
		["TribeSavageImpid"] = 0.1f,
		["PirateWaster"] = 0.08f,
		["PirateYttakin"] = 0.06f,
		["Sanguophages"] = 0.02f,
		["HoraxCult"] = 0.5f,
		["Salvagers"] = 0.01f,
		["TradersGuild"] = 0.01f
	};

	public static readonly Dictionary<string, float> DefaultExtortionChances = new Dictionary<string, float>
	{
		["OutlanderCivil"] = 0.05f,
		["OutlanderRough"] = 0.9f,
		["TribeRough"] = 0.72f,
		["TribeCivil"] = 0.05f,
		["TribeSavage"] = 0.65f,
		["Pirate"] = 0.85f,
		["AncientsHostile"] = 0.4f,
		["Ancients"] = 0.2f,
		["OutlanderRefugee"] = 0.9f,
		["Empire"] = 0.2f,
		["Beggars"] = 0.05f,
		["CannibalPirate"] = 0.7f,
		["TribeCannibal"] = 0.65f,
		["NudistTribe"] = 0.2f,
		["Pilgrims"] = 0.05f,
		["OutlanderRoughPig"] = 0.9f,
		["TribeRoughNeanderthal"] = 0.72f,
		["TribeSavageImpid"] = 0.65f,
		["PirateWaster"] = 0.72f,
		["PirateYttakin"] = 0.85f,
		["Sanguophages"] = 0.3f,
		["HoraxCult"] = 0.1f,
		["Salvagers"] = 0.95f,
		["TradersGuild"] = 0.3f
	};

	public static readonly Dictionary<string, FloatRange> DefaultExtortionRanges = new Dictionary<string, FloatRange>
	{
		["OutlanderCivil"] = new FloatRange(0.05f, 0.15f),
		["OutlanderRough"] = new FloatRange(0.12f, 0.25f),
		["TribeRough"] = new FloatRange(0.1f, 0.2f),
		["TribeCivil"] = new FloatRange(0.05f, 0.12f),
		["TribeSavage"] = new FloatRange(0.12f, 0.25f),
		["Pirate"] = new FloatRange(0.15f, 0.3f),
		["AncientsHostile"] = new FloatRange(0.15f, 0.35f),
		["Ancients"] = new FloatRange(0.1f, 0.25f),
		["OutlanderRefugee"] = new FloatRange(0.05f, 0.15f),
		["Empire"] = new FloatRange(0.25f, 0.45f),
		["Beggars"] = new FloatRange(0.01f, 0.05f),
		["CannibalPirate"] = new FloatRange(0.15f, 0.3f),
		["TribeCannibal"] = new FloatRange(0.1f, 0.22f),
		["NudistTribe"] = new FloatRange(0.05f, 0.15f),
		["Pilgrims"] = new FloatRange(0.02f, 0.08f),
		["OutlanderRoughPig"] = new FloatRange(0.12f, 0.25f),
		["TribeRoughNeanderthal"] = new FloatRange(0.1f, 0.2f),
		["TribeSavageImpid"] = new FloatRange(0.12f, 0.25f),
		["PirateWaster"] = new FloatRange(0.15f, 0.3f),
		["PirateYttakin"] = new FloatRange(0.15f, 0.3f),
		["Sanguophages"] = new FloatRange(0.2f, 0.4f),
		["HoraxCult"] = new FloatRange(0.2f, 0.5f),
		["Salvagers"] = new FloatRange(0.1f, 0.25f),
		["TradersGuild"] = new FloatRange(0.15f, 0.35f)
	};

	public static readonly Dictionary<string, FloatRange> DefaultRejectedFeeRaidPointsIncreaseRanges = new Dictionary<string, FloatRange>
	{
		["OutlanderCivil"] = new FloatRange(0.1f, 0.25f),
		["OutlanderRough"] = new FloatRange(0.02f, 0.06f),
		["TribeRough"] = new FloatRange(0.01f, 0.04f),
		["TribeCivil"] = new FloatRange(0.05f, 0.2f),
		["TribeSavage"] = new FloatRange(0.02f, 0.06f),
		["Pirate"] = new FloatRange(0.05f, 0.09f),
		["AncientsHostile"] = new FloatRange(0.3f, 0.5f),
		["Ancients"] = new FloatRange(0.2f, 0.4f),
		["OutlanderRefugee"] = new FloatRange(0.01f, 0.05f),
		["Empire"] = new FloatRange(0.6f, 1f),
		["Beggars"] = new FloatRange(0.05f, 0.1f),
		["CannibalPirate"] = new FloatRange(0.03f, 0.07f),
		["TribeCannibal"] = new FloatRange(0f, 0.04f),
		["NudistTribe"] = new FloatRange(0.05f, 0.2f),
		["Pilgrims"] = new FloatRange(0.1f, 0.2f),
		["OutlanderRoughPig"] = new FloatRange(0.02f, 0.06f),
		["TribeRoughNeanderthal"] = new FloatRange(0.01f, 0.04f),
		["TribeSavageImpid"] = new FloatRange(0.02f, 0.06f),
		["PirateWaster"] = new FloatRange(0.04f, 0.08f),
		["PirateYttakin"] = new FloatRange(0.05f, 0.09f),
		["Sanguophages"] = new FloatRange(0.4f, 0.7f),
		["HoraxCult"] = new FloatRange(0.8f, 1.2f),
		["Salvagers"] = new FloatRange(0.01f, 0.05f),
		["TradersGuild"] = new FloatRange(0.4f, 0.6f)
	};

	public bool doubleCross;

	public bool extortionCooldown = true;

	public bool enableRimWar_WarObjectRaid = true;

	public bool needsWriteAfterLoadRepair;

	public Dictionary<string, float> factionDoubleCrossChances = new Dictionary<string, float>(DefaultDoubleCross);

	public Dictionary<string, float> factionExtortionChances = new Dictionary<string, float>(DefaultExtortionChances);

	public Dictionary<string, FloatRange> factionExtortionRanges = new Dictionary<string, FloatRange>(DefaultExtortionRanges);

	public Dictionary<string, FloatRange> factionRejectedFeeRaidPointsIncreaseRanges = new Dictionary<string, FloatRange>(DefaultRejectedFeeRaidPointsIncreaseRanges);

	public Dictionary<string, bool> incidentSourceEnabledStatus = new Dictionary<string, bool>();

	public Dictionary<string, bool> questSourceEnabledStatus = new Dictionary<string, bool>();

	internal List<DemandPolicy> demandPolicies = new List<DemandPolicy>();

	public Dictionary<string, int> factionPolicyAssignments = new Dictionary<string, int>();

	public override void ExposeData()
	{
		((ModSettings)this).ExposeData();
		Scribe_Values.Look<bool>(ref doubleCross, "doubleCross", false, false);
		Scribe_Values.Look<bool>(ref extortionCooldown, "extortionCooldown", true, false);
		Scribe_Values.Look<bool>(ref enableRimWar_WarObjectRaid, "enableRimWar_WarObjectRaid", true, false);
		Scribe_Collections.Look<string, float>(ref factionDoubleCrossChances, "factionDoubleCrossChances", (LookMode)1, (LookMode)1);
		if (factionDoubleCrossChances == null)
		{
			factionDoubleCrossChances = new Dictionary<string, float>(DefaultDoubleCross);
		}
		Scribe_Collections.Look<string, float>(ref factionExtortionChances, "factionExtortionChances", (LookMode)1, (LookMode)1);
		if (factionExtortionChances == null)
		{
			factionExtortionChances = new Dictionary<string, float>(DefaultExtortionChances);
		}
		Scribe_Collections.Look<string, FloatRange>(ref factionExtortionRanges, "factionExtortionRanges", (LookMode)1, (LookMode)1);
		if (factionExtortionRanges == null)
		{
			factionExtortionRanges = new Dictionary<string, FloatRange>(DefaultExtortionRanges);
		}
		Scribe_Collections.Look<string, FloatRange>(ref factionRejectedFeeRaidPointsIncreaseRanges, "factionRejectedFeeRaidPointsIncreaseRanges", (LookMode)1, (LookMode)1);
		if (factionRejectedFeeRaidPointsIncreaseRanges == null)
		{
			factionRejectedFeeRaidPointsIncreaseRanges = new Dictionary<string, FloatRange>(DefaultRejectedFeeRaidPointsIncreaseRanges);
		}
		Scribe_Collections.Look<string, bool>(ref incidentSourceEnabledStatus, "incidentSourceEnabledStatus", (LookMode)1, (LookMode)1);
		if (incidentSourceEnabledStatus == null)
		{
			incidentSourceEnabledStatus = new Dictionary<string, bool>();
		}
		Scribe_Collections.Look<string, bool>(ref questSourceEnabledStatus, "questSourceEnabledStatus", (LookMode)1, (LookMode)1);
		if (questSourceEnabledStatus == null)
		{
			questSourceEnabledStatus = new Dictionary<string, bool>();
		}
		Scribe_Collections.Look<DemandPolicy>(ref demandPolicies, "demandPolicies", (LookMode)2, Array.Empty<object>());
		if (demandPolicies == null)
		{
			demandPolicies = new List<DemandPolicy>();
		}
		Scribe_Collections.Look<string, int>(ref factionPolicyAssignments, "factionPolicyAssignments", (LookMode)1, (LookMode)1);
		if (factionPolicyAssignments == null)
		{
			factionPolicyAssignments = new Dictionary<string, int>();
		}
	}

	public bool RepairMissingDefs()
	{
		bool flag = false;
		if (demandPolicies == null)
		{
			DemandPolicyDatabase.GenerateStartingPolicies();
			flag = true;
		}
		else if (demandPolicies.RemoveAll((DemandPolicy policy) => policy == null) > 0)
		{
			flag = true;
		}
		flag |= RemoveMissingDefKeys<FactionDef, float>(factionDoubleCrossChances);
		flag |= RemoveMissingDefKeys<FactionDef, float>(factionExtortionChances);
		flag |= RemoveMissingDefKeys<FactionDef, FloatRange>(factionExtortionRanges);
		flag |= RemoveMissingDefKeys<FactionDef, FloatRange>(factionRejectedFeeRaidPointsIncreaseRanges);
		flag |= RemoveMissingDefKeys<FactionDef, int>(factionPolicyAssignments);
		flag |= RemoveMissingDefKeys<IncidentDef, bool>(incidentSourceEnabledStatus);
		return flag | RemoveMissingDefKeys<QuestScriptDef, bool>(questSourceEnabledStatus);
	}

	private static bool RemoveMissingDefKeys<TDef, TValue>(Dictionary<string, TValue> dictionary) where TDef : Def
	{
		if (dictionary == null || dictionary.Count == 0)
		{
			return false;
		}
		List<string> list = null;
		foreach (string key in dictionary.Keys)
		{
			if (GenText.NullOrEmpty(key) || DefDatabase<TDef>.GetNamedSilentFail(key) == null)
			{
				list = list ?? new List<string>();
				list.Add(key);
			}
		}
		if (list == null)
		{
			return false;
		}
		for (int i = 0; i < list.Count; i++)
		{
			dictionary.Remove(list[i]);
		}
		return true;
	}

	public static bool IsProtectionFeeEnabled(ProtectionFee_ModSettings Settings, IncidentWorker worker, IncidentParms parms, out string matchedSource)
	{
		matchedSource = "default:true";
		if (Settings == null)
		{
			return true;
		}
		if (parms != null && parms.questTag == "RimWar_WarObjectRaid")
		{
			bool flag = Settings.enableRimWar_WarObjectRaid;
			matchedSource = $"Forced:RimWar_WarObjectRaid (parms.questTag) => {flag}";
			return flag;
		}
		QuestScriptDef val = parms?.questScriptDef;
		if (val != null && !GenText.NullOrEmpty(((Def)val).defName))
		{
			bool flag2 = GenCollection.TryGetValue<string, bool>((IReadOnlyDictionary<string, bool>)Settings.questSourceEnabledStatus, ((Def)val).defName, false);
			matchedSource = $"Quest:{((Def)val).defName} (parms.questScriptDef) => {flag2}";
			return flag2;
		}
		int num = 0;
		Quest val2 = parms?.quest;
		while (val2 != null)
		{
			QuestScriptDef root = val2.root;
			if (root != null && !GenText.NullOrEmpty(((Def)root).defName))
			{
				bool flag3 = GenCollection.TryGetValue<string, bool>((IReadOnlyDictionary<string, bool>)Settings.questSourceEnabledStatus, ((Def)root).defName, false);
				matchedSource = ((num == 0) ? $"Quest:{((Def)root).defName} (quest.root) => {flag3}" : $"Quest:{((Def)root).defName} (parent.root depth={num}) => {flag3}");
				return flag3;
			}
			val2 = val2.parent;
			num++;
		}
		IncidentDef val3 = worker?.def;
		if (val3 != null && !GenText.NullOrEmpty(((Def)val3).defName))
		{
			bool flag4 = GenCollection.TryGetValue<string, bool>((IReadOnlyDictionary<string, bool>)Settings.incidentSourceEnabledStatus, ((Def)val3).defName, true);
			matchedSource = $"Incident:{((Def)val3).defName} (worker.def) => {flag4}";
			return flag4;
		}
		return true;
	}
}
public class ProtectionFee_Mod : Mod
{
	private enum SettingsPage
	{
		General,
		IncidentFilter
	}

	private static SettingsPage currentPage = SettingsPage.General;

	private static string searchFilter = string.Empty;

	private static bool filterDirty = true;

	private static readonly Dictionary<string, bool> groupExpanded = new Dictionary<string, bool>();

	private static Vector2 scrollGeneral = Vector2.zero;

	private static Vector2 scrollEvent = Vector2.zero;

	private const float GroupHeaderH = 30f;

	private const float RowH_Event = 30f;

	private const float GroupGap = 6f;

	private const float LabelLeftPadding = 8f;

	private const float RowH_GeneralPolicy = 30f;

	private const float RowH_GeneralSlider = 30f;

	private const float RowH_GeneralRange = 30f;

	private const float FactionBlockPad = 6f;

	private const float FactionBlockGap = 3f;

	private const float SliderH = 18f;

	private float cachedTotalHeightFaction;

	private float cachedTotalHeightEvent;

	public static List<Def> AllRaidSources = new List<Def>();

	public static ProtectionFee_ModSettings Settings;

	public static List<IGrouping<string, Def>> FilteredGroupedRaidSources { get; internal set; } = new List<IGrouping<string, Def>>();

	public static List<IGrouping<string, FactionDef>> GroupedFactions { get; internal set; } = new List<IGrouping<string, FactionDef>>();

	public ProtectionFee_Mod(ModContentPack content)
		: base(content)
	{
		//IL_000c: Unknown result type (might be due to invalid IL or missing references)
		new Harmony("Leo.ProtectionFee").PatchAll();
		LongEventHandler.ExecuteWhenFinished((Action)delegate
		{
			Settings = ((Mod)this).GetSettings<ProtectionFee_ModSettings>();
			if (Settings.RepairMissingDefs())
			{
				Log.Warning("[Raid Protection Fee] Cleaned missing Def references.");
				((Mod)this).WriteSettings();
			}
		});
	}

	public override void DoSettingsWindowContents(Rect inRect)
	{
		//IL_0019: Unknown result type (might be due to invalid IL or missing references)
		//IL_001f: Expected O, but got Unknown
		//IL_0020: Unknown result type (might be due to invalid IL or missing references)
		//IL_0031: Unknown result type (might be due to invalid IL or missing references)
		//IL_0036: Unknown result type (might be due to invalid IL or missing references)
		//IL_0059: Unknown result type (might be due to invalid IL or missing references)
		//IL_0063: Unknown result type (might be due to invalid IL or missing references)
		//IL_009c: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a6: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e8: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f2: Unknown result type (might be due to invalid IL or missing references)
		if (Settings == null)
		{
			Settings = ((Mod)this).GetSettings<ProtectionFee_ModSettings>();
		}
		RecalculateFilter();
		Listing_Standard val = new Listing_Standard();
		((Listing)val).Begin(inRect);
		Rect rect = ((Listing)val).GetRect(30f, 1f);
		float num = ((Rect)(ref inRect)).width / 2f;
		if (Widgets.ButtonText(new Rect(((Rect)(ref rect)).x, ((Rect)(ref rect)).y, num, 30f), TaggedString.op_Implicit(Translator.Translate("ProtectionFee.GeneralSettings.Label")), true, true, true, (TextAnchor?)null))
		{
			currentPage = SettingsPage.General;
		}
		if (Widgets.ButtonText(new Rect(((Rect)(ref rect)).x + num, ((Rect)(ref rect)).y, num, 30f), TaggedString.op_Implicit(Translator.Translate("ProtectionFee.EventFilter.Label")), true, true, true, (TextAnchor?)null))
		{
			currentPage = SettingsPage.IncidentFilter;
		}
		((Listing)val).GapLine(12f);
		switch (currentPage)
		{
		case SettingsPage.General:
			DrawGeneralSettings(val, inRect);
			break;
		case SettingsPage.IncidentFilter:
			DrawEventFilter(val, inRect);
			break;
		}
		((Listing)val).End();
	}

	private void DrawGeneralSettings(Listing_Standard listing_Standard, Rect inRect)
	{
		//IL_0006: Unknown result type (might be due to invalid IL or missing references)
		//IL_008f: Unknown result type (might be due to invalid IL or missing references)
		//IL_00da: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f3: Unknown result type (might be due to invalid IL or missing references)
		//IL_0124: Unknown result type (might be due to invalid IL or missing references)
		//IL_013d: Unknown result type (might be due to invalid IL or missing references)
		//IL_017b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0180: Unknown result type (might be due to invalid IL or missing references)
		//IL_018b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0190: Unknown result type (might be due to invalid IL or missing references)
		//IL_01b5: Unknown result type (might be due to invalid IL or missing references)
		//IL_01bb: Unknown result type (might be due to invalid IL or missing references)
		//IL_0216: Unknown result type (might be due to invalid IL or missing references)
		//IL_0241: Unknown result type (might be due to invalid IL or missing references)
		//IL_0289: Unknown result type (might be due to invalid IL or missing references)
		//IL_029a: Unknown result type (might be due to invalid IL or missing references)
		//IL_02c0: Unknown result type (might be due to invalid IL or missing references)
		//IL_0372: Unknown result type (might be due to invalid IL or missing references)
		//IL_0402: Unknown result type (might be due to invalid IL or missing references)
		//IL_040d: Unknown result type (might be due to invalid IL or missing references)
		//IL_040f: Unknown result type (might be due to invalid IL or missing references)
		//IL_041b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0420: Unknown result type (might be due to invalid IL or missing references)
		//IL_044a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0380: Unknown result type (might be due to invalid IL or missing references)
		//IL_04b3: Unknown result type (might be due to invalid IL or missing references)
		//IL_04b8: Unknown result type (might be due to invalid IL or missing references)
		//IL_06c5: Unknown result type (might be due to invalid IL or missing references)
		//IL_06d0: Unknown result type (might be due to invalid IL or missing references)
		//IL_06d1: Unknown result type (might be due to invalid IL or missing references)
		//IL_06e0: Unknown result type (might be due to invalid IL or missing references)
		//IL_06f6: Unknown result type (might be due to invalid IL or missing references)
		//IL_0710: Unknown result type (might be due to invalid IL or missing references)
		//IL_0715: Unknown result type (might be due to invalid IL or missing references)
		//IL_073f: Unknown result type (might be due to invalid IL or missing references)
		//IL_05ba: Unknown result type (might be due to invalid IL or missing references)
		//IL_05c5: Unknown result type (might be due to invalid IL or missing references)
		//IL_05c6: Unknown result type (might be due to invalid IL or missing references)
		//IL_05d5: Unknown result type (might be due to invalid IL or missing references)
		//IL_05eb: Unknown result type (might be due to invalid IL or missing references)
		//IL_0605: Unknown result type (might be due to invalid IL or missing references)
		//IL_060a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0634: Unknown result type (might be due to invalid IL or missing references)
		//IL_07d3: Unknown result type (might be due to invalid IL or missing references)
		//IL_07d5: Unknown result type (might be due to invalid IL or missing references)
		//IL_07e2: Unknown result type (might be due to invalid IL or missing references)
		//IL_07ed: Unknown result type (might be due to invalid IL or missing references)
		//IL_07ee: Unknown result type (might be due to invalid IL or missing references)
		//IL_07fd: Unknown result type (might be due to invalid IL or missing references)
		//IL_080c: Unknown result type (might be due to invalid IL or missing references)
		//IL_081d: Unknown result type (might be due to invalid IL or missing references)
		//IL_082e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0848: Unknown result type (might be due to invalid IL or missing references)
		//IL_0886: Unknown result type (might be due to invalid IL or missing references)
		//IL_088d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0540: Unknown result type (might be due to invalid IL or missing references)
		//IL_054a: Expected O, but got Unknown
		//IL_08a8: Unknown result type (might be due to invalid IL or missing references)
		//IL_08c7: Unknown result type (might be due to invalid IL or missing references)
		//IL_08fa: Unknown result type (might be due to invalid IL or missing references)
		//IL_0896: Unknown result type (might be due to invalid IL or missing references)
		//IL_089d: Unknown result type (might be due to invalid IL or missing references)
		//IL_056a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0574: Expected O, but got Unknown
		//IL_093b: Unknown result type (might be due to invalid IL or missing references)
		//IL_093d: Unknown result type (might be due to invalid IL or missing references)
		//IL_094a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0955: Unknown result type (might be due to invalid IL or missing references)
		//IL_0956: Unknown result type (might be due to invalid IL or missing references)
		//IL_0965: Unknown result type (might be due to invalid IL or missing references)
		//IL_0974: Unknown result type (might be due to invalid IL or missing references)
		//IL_0985: Unknown result type (might be due to invalid IL or missing references)
		//IL_0996: Unknown result type (might be due to invalid IL or missing references)
		//IL_09b0: Unknown result type (might be due to invalid IL or missing references)
		//IL_09b1: Unknown result type (might be due to invalid IL or missing references)
		//IL_09bb: Unknown result type (might be due to invalid IL or missing references)
		//IL_09c0: Unknown result type (might be due to invalid IL or missing references)
		//IL_09e9: Unknown result type (might be due to invalid IL or missing references)
		//IL_0a18: Unknown result type (might be due to invalid IL or missing references)
		//IL_0a1f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0a3a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0a59: Unknown result type (might be due to invalid IL or missing references)
		//IL_0a8c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0a28: Unknown result type (might be due to invalid IL or missing references)
		//IL_0a2f: Unknown result type (might be due to invalid IL or missing references)
		if (listing_Standard.ButtonText(TaggedString.op_Implicit(Translator.Translate("ResetAll")), (string)null, 1f))
		{
			filterDirty = true;
			Settings.doubleCross = false;
			Settings.extortionCooldown = true;
			Settings.factionDoubleCrossChances = new Dictionary<string, float>(ProtectionFee_ModSettings.DefaultDoubleCross);
			Settings.factionExtortionChances = new Dictionary<string, float>(ProtectionFee_ModSettings.DefaultExtortionChances);
			Settings.factionExtortionRanges = new Dictionary<string, FloatRange>(ProtectionFee_ModSettings.DefaultExtortionRanges);
			Settings.factionRejectedFeeRaidPointsIncreaseRanges = new Dictionary<string, FloatRange>(ProtectionFee_ModSettings.DefaultRejectedFeeRaidPointsIncreaseRanges);
		}
		if (listing_Standard.ButtonText(TaggedString.op_Implicit(Translator.Translate("ProtectionFee.ManageDemandPolicies.Label")), (string)null, 1f))
		{
			Find.WindowStack.Add((Window)(object)new Dialog_ManageDemandPolicies(DemandPolicyDatabase.AllDemandPolicies.FirstOrDefault()));
		}
		((Listing)listing_Standard).Gap(12f);
		bool doubleCross = Settings.doubleCross;
		listing_Standard.CheckboxLabeled(TaggedString.op_Implicit(Translator.Translate("ProtectionFee.doubleCross.Label")), ref Settings.doubleCross, TaggedString.op_Implicit(Translator.Translate("ProtectionFee.doubleCross.Tooltip")), 0f, 1f);
		if (doubleCross != Settings.doubleCross)
		{
			filterDirty = true;
		}
		listing_Standard.CheckboxLabeled(TaggedString.op_Implicit(Translator.Translate("ProtectionFee.extortionCooldown.Label")), ref Settings.extortionCooldown, TaggedString.op_Implicit(Translator.Translate("ProtectionFee.extortionCooldown.Tooltip")), 0f, 1f);
		((Listing)listing_Standard).Gap(6f);
		Rect rect = ((Listing)listing_Standard).GetRect(((Rect)(ref inRect)).height - ((Listing)listing_Standard).CurHeight - 10f, 1f);
		Widgets.DrawMenuSection(rect);
		Rect val = GenUI.ContractedBy(rect, 6f);
		Rect val2 = default(Rect);
		((Rect)(ref val2))..ctor(0f, 0f, ((Rect)(ref val)).width - 16f, cachedTotalHeightFaction);
		Widgets.BeginScrollView(val, ref scrollGeneral, val2, true);
		float num = 0f;
		Rect val3 = default(Rect);
		Rect val4 = default(Rect);
		Rect val5 = default(Rect);
		foreach (IGrouping<string, FactionDef> groupedFaction in GroupedFactions)
		{
			string groupStateKey = GetGroupStateKey("General", groupedFaction.Key);
			bool expanded = GetExpanded(groupStateKey);
			((Rect)(ref val3))..ctor(0f, num, ((Rect)(ref val2)).width, 30f);
			Widgets.DrawHighlight(val3);
			GUI.DrawTexture(new Rect(((Rect)(ref val3)).x + 4f, ((Rect)(ref val3)).y + 7f, 16f, 16f), (Texture)(object)(expanded ? TexButton.Collapse : TexButton.Reveal));
			Text.Anchor = (TextAnchor)3;
			Widgets.Label(new Rect(((Rect)(ref val3)).x + 24f, ((Rect)(ref val3)).y, ((Rect)(ref val3)).width - 24f, ((Rect)(ref val3)).height), $"{ColoredText.Colorize(groupedFaction.Key, Color.cyan)} ({groupedFaction.Count()})");
			Text.Anchor = (TextAnchor)0;
			if (Widgets.ButtonInvisible(val3, true))
			{
				SetExpanded(groupStateKey, !expanded);
				filterDirty = true;
				SoundStarter.PlayOneShotOnCamera(SoundDefOf.Click, (Map)null);
			}
			num += 30f;
			int num2 = 0;
			if (expanded)
			{
				num += 3f;
				foreach (FactionDef faction in groupedFaction)
				{
					float num3 = 30f + (Settings.doubleCross ? 30f : 0f) + 30f + 30f + 30f + 12f;
					((Rect)(ref val4))..ctor(0f, num, ((Rect)(ref val2)).width, num3);
					Widgets.DrawMenuSection(val4);
					if (num2 % 2 == 1)
					{
						Widgets.DrawAltRect(val4);
					}
					float num4 = ((Rect)(ref val4)).y + 6f;
					float num5 = ((Rect)(ref val4)).width - 12f;
					float num6 = ((Rect)(ref val4)).x + 6f;
					((Rect)(ref val5))..ctor(num6, num4, num5, 30f);
					Rect val6 = new Rect(((Rect)(ref val5)).xMax - ((Rect)(ref val2)).width / 2f, ((Rect)(ref val5)).y + 1f, ((Rect)(ref val2)).width / 2f, ((Rect)(ref val5)).height - 2f);
					Text.Anchor = (TextAnchor)3;
					Widgets.Label(GenUI.LeftHalf(val5), ColoredText.Colorize(((Def)faction).LabelCap, Color.yellow) + " " + ColoredText.Colorize("(" + ((Def)faction).defName + ")", Color.gray));
					Text.Anchor = (TextAnchor)0;
					Settings.factionPolicyAssignments.TryGetValue(((Def)faction).defName, out var currentId);
					object obj = ((Policy)(GenCollection.FirstOrDefault<DemandPolicy>(DemandPolicyDatabase.AllDemandPolicies, (Predicate<DemandPolicy>)((DemandPolicy p) => ((Policy)p).id == currentId))?)).label;
					if (obj == null)
					{
						TaggedString val7 = Translator.Translate("ProtectionFee.PolicyUnassigned");
						obj = ((object)(TaggedString)(ref val7)/*cast due to .constrained prefix*/).ToString();
					}
					string text = (string)obj;
					if (Widgets.ButtonText(val6, text, true, true, true, (TextAnchor?)null))
					{
						List<FloatMenuOption> list = new List<FloatMenuOption>();
						foreach (DemandPolicy allDemandPolicy in DemandPolicyDatabase.AllDemandPolicies)
						{
							DemandPolicy captured = allDemandPolicy;
							list.Add(new FloatMenuOption(((Policy)captured).label, (Action)delegate
							{
								Settings.factionPolicyAssignments[((Def)faction).defName] = ((Policy)captured).id;
							}, (MenuOptionPriority)4, (Action<Rect>)null, (Thing)null, 0f, (Func<Rect, bool>)null, (WorldObject)null, true, 0));
						}
						Find.WindowStack.Add((Window)new FloatMenu(list));
					}
					num4 += 30f;
					if (Settings.doubleCross)
					{
						float num7 = GenCollection.TryGetValue<string, float>((IReadOnlyDictionary<string, float>)Settings.factionDoubleCrossChances, ((Def)faction).defName, 0.05f);
						Rect val8 = new Rect(num6, num4, num5, 30f);
						Text.Anchor = (TextAnchor)3;
						Widgets.Label(GenUI.LeftHalf(val8), string.Format("{0}: ", Translator.Translate("ProtectionFee.factionDoubleCrossChances.Label")) + ColoredText.Colorize(GenText.ToStringPercent(num7), Color.cyan));
						Text.Anchor = (TextAnchor)0;
						Rect val9 = GenUI.RightHalf(val8);
						float num8 = Mathf.Round(Widgets.HorizontalSlider(new Rect(((Rect)(ref val9)).x, ((Rect)(ref val9)).y + ((Rect)(ref val9)).height - 18f, ((Rect)(ref val9)).width, 18f), num7, 0f, 1f, false, (string)null, (string)null, (string)null, -1f) * 100f) / 100f;
						if (!Mathf.Approximately(num8, num7))
						{
							Settings.factionDoubleCrossChances[((Def)faction).defName] = num8;
						}
						num4 += 30f;
					}
					float num9 = GenCollection.TryGetValue<string, float>((IReadOnlyDictionary<string, float>)Settings.factionExtortionChances, ((Def)faction).defName, 0.35f);
					Rect val10 = new Rect(num6, num4, num5, 30f);
					Text.Anchor = (TextAnchor)3;
					Widgets.Label(GenUI.LeftHalf(val10), string.Format("{0}: ", Translator.Translate("ProtectionFee.factionExtortionChances.Label")) + ColoredText.Colorize(GenText.ToStringPercent(num9), Color.cyan));
					Text.Anchor = (TextAnchor)0;
					Rect val11 = GenUI.RightHalf(val10);
					float num10 = Mathf.Round(Widgets.HorizontalSlider(new Rect(((Rect)(ref val11)).x, ((Rect)(ref val11)).y + ((Rect)(ref val11)).height - 18f, ((Rect)(ref val11)).width, 18f), num9, 0f, 1f, false, (string)null, (string)null, (string)null, -1f) * 100f) / 100f;
					if (!Mathf.Approximately(num10, num9))
					{
						Settings.factionExtortionChances[((Def)faction).defName] = num10;
					}
					num4 += 30f;
					if (!Settings.factionExtortionRanges.TryGetValue(((Def)faction).defName, out var value))
					{
						((FloatRange)(ref value))..ctor(0.1f, 0.2f);
					}
					FloatRange val12 = value;
					Rect val13 = new Rect(num6, num4, num5, 30f);
					Text.Anchor = (TextAnchor)3;
					Widgets.Label(GenUI.LeftHalf(val13), string.Format("{0}: ", Translator.Translate("ProtectionFee.factionExtortionRanges.Label")) + ColoredText.Colorize(GenText.ToStringPercent(value.min) + " - " + GenText.ToStringPercent(value.max), Color.cyan));
					Text.Anchor = (TextAnchor)0;
					Widgets.FloatRange(GenUI.RightHalf(val13), ((Def)faction).defName.GetHashCode(), ref val12, 0f, 1f, (string)null, (ToStringStyle)2, 0f, (GameFont)1, (Color?)null, 0f);
					if (val12.min != value.min || val12.max != value.max)
					{
						val12.min = Mathf.Round(val12.min * 100f) / 100f;
						val12.max = Mathf.Round(val12.max * 100f) / 100f;
						Settings.factionExtortionRanges[((Def)faction).defName] = val12;
					}
					num4 += 30f;
					if (!Settings.factionRejectedFeeRaidPointsIncreaseRanges.TryGetValue(((Def)faction).defName, out var value2))
					{
						((FloatRange)(ref value2))..ctor(0.15f, 0.3f);
					}
					FloatRange val14 = value2;
					Rect val15 = new Rect(num6, num4, num5, 30f);
					Text.Anchor = (TextAnchor)3;
					Widgets.Label(GenUI.LeftHalf(val15), string.Format("{0}: ", Translator.Translate("ProtectionFee.factionRaidBoostRange.Label")) + ColoredText.Colorize(GenText.ToStringPercent(value2.min) + " - " + GenText.ToStringPercent(value2.max), Color.cyan));
					Text.Anchor = (TextAnchor)0;
					TooltipHandler.TipRegion(GenUI.LeftHalf(val15), TipSignal.op_Implicit(Translator.Translate("ProtectionFee.factionRaidBoostRange.Tooltip")));
					int num11 = (((Def)faction).defName.GetHashCode() * 397) ^ 0x2F33A1;
					Widgets.FloatRange(GenUI.RightHalf(val15), num11, ref val14, 0f, 3f, (string)null, (ToStringStyle)2, 0f, (GameFont)1, (Color?)null, 0f);
					if (val14.min != value2.min || val14.max != value2.max)
					{
						val14.min = Mathf.Round(val14.min * 100f) / 100f;
						val14.max = Mathf.Round(val14.max * 100f) / 100f;
						Settings.factionRejectedFeeRaidPointsIncreaseRanges[((Def)faction).defName] = val14;
					}
					num += num3 + 3f;
					num2++;
				}
			}
			else
			{
				num += 6f;
			}
		}
		Widgets.EndScrollView();
	}

	private void DrawEventFilter(Listing_Standard listing_Standard, Rect inRect)
	{
		//IL_0006: Unknown result type (might be due to invalid IL or missing references)
		//IL_0063: Unknown result type (might be due to invalid IL or missing references)
		//IL_006e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0085: Unknown result type (might be due to invalid IL or missing references)
		//IL_008a: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c4: Unknown result type (might be due to invalid IL or missing references)
		//IL_0107: Unknown result type (might be due to invalid IL or missing references)
		//IL_0155: Unknown result type (might be due to invalid IL or missing references)
		//IL_015a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0165: Unknown result type (might be due to invalid IL or missing references)
		//IL_016a: Unknown result type (might be due to invalid IL or missing references)
		//IL_018f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0195: Unknown result type (might be due to invalid IL or missing references)
		//IL_01e8: Unknown result type (might be due to invalid IL or missing references)
		//IL_0213: Unknown result type (might be due to invalid IL or missing references)
		//IL_025b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0265: Unknown result type (might be due to invalid IL or missing references)
		//IL_027a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0392: Unknown result type (might be due to invalid IL or missing references)
		//IL_03bd: Unknown result type (might be due to invalid IL or missing references)
		//IL_02cb: Unknown result type (might be due to invalid IL or missing references)
		//IL_02dc: Unknown result type (might be due to invalid IL or missing references)
		//IL_02e7: Unknown result type (might be due to invalid IL or missing references)
		//IL_02f6: Unknown result type (might be due to invalid IL or missing references)
		//IL_0316: Unknown result type (might be due to invalid IL or missing references)
		//IL_0405: Unknown result type (might be due to invalid IL or missing references)
		//IL_0416: Unknown result type (might be due to invalid IL or missing references)
		//IL_043c: Unknown result type (might be due to invalid IL or missing references)
		//IL_04af: Unknown result type (might be due to invalid IL or missing references)
		//IL_0506: Unknown result type (might be due to invalid IL or missing references)
		//IL_0549: Unknown result type (might be due to invalid IL or missing references)
		//IL_0582: Unknown result type (might be due to invalid IL or missing references)
		//IL_05eb: Unknown result type (might be due to invalid IL or missing references)
		if (listing_Standard.ButtonText(TaggedString.op_Implicit(Translator.Translate("ResetAll")), (string)null, 1f))
		{
			filterDirty = true;
			Settings.enableRimWar_WarObjectRaid = true;
			Settings.incidentSourceEnabledStatus.Clear();
			Settings.questSourceEnabledStatus.Clear();
		}
		((Listing)listing_Standard).Gap(6f);
		Text.Font = (GameFont)2;
		listing_Standard.Label(Translator.Translate("ProtectionFee.checkOn.Label"), -1f, (string)null);
		Text.Font = (GameFont)1;
		Rect rect = ((Listing)listing_Standard).GetRect(24f, 1f);
		Rect val = default(Rect);
		((Rect)(ref val))..ctor(((Rect)(ref rect)).x + 4f, ((Rect)(ref rect)).y + (((Rect)(ref rect)).height - 18f) * 0.5f, 18f, 18f);
		GUI.DrawTexture(val, (Texture)(object)TexButton.Search);
		string text = Widgets.TextField(new Rect(((Rect)(ref val)).xMax + 4f, ((Rect)(ref rect)).y, ((Rect)(ref rect)).width - (((Rect)(ref val)).xMax - ((Rect)(ref rect)).x) - 4f, ((Rect)(ref rect)).height), searchFilter);
		if (text != searchFilter)
		{
			searchFilter = text;
			filterDirty = true;
		}
		((Listing)listing_Standard).Gap(6f);
		Rect rect2 = ((Listing)listing_Standard).GetRect(((Rect)(ref inRect)).height - ((Listing)listing_Standard).CurHeight - 10f, 1f);
		Widgets.DrawMenuSection(rect2);
		Rect val2 = GenUI.ContractedBy(rect2, 6f);
		Rect val3 = default(Rect);
		((Rect)(ref val3))..ctor(0f, 0f, ((Rect)(ref val2)).width - 16f, cachedTotalHeightEvent);
		Widgets.BeginScrollView(val2, ref scrollEvent, val3, true);
		float num = 0f;
		if (ModLister.GetActiveModWithIdentifier("Torann.RimWar", true) != null)
		{
			string groupStateKey = GetGroupStateKey("Event", "RimWar");
			bool expanded = GetExpanded(groupStateKey);
			Rect val4 = default(Rect);
			((Rect)(ref val4))..ctor(0f, num, ((Rect)(ref val3)).width, 30f);
			Widgets.DrawHighlight(val4);
			GUI.DrawTexture(new Rect(((Rect)(ref val4)).x + 4f, ((Rect)(ref val4)).y + 7f, 16f, 16f), (Texture)(object)(expanded ? TexButton.Collapse : TexButton.Reveal));
			Text.Anchor = (TextAnchor)3;
			Widgets.Label(new Rect(((Rect)(ref val4)).x + 24f, ((Rect)(ref val4)).y, ((Rect)(ref val4)).width - 24f, ((Rect)(ref val4)).height), ColoredText.Colorize("RimWar", Color.cyan));
			Text.Anchor = (TextAnchor)0;
			if (Widgets.ButtonInvisible(val4, true))
			{
				SetExpanded(groupStateKey, !expanded);
				filterDirty = true;
				SoundStarter.PlayOneShotOnCamera(SoundDefOf.Click, (Map)null);
			}
			num += 30f;
			if (expanded)
			{
				Rect val5 = new Rect(8f, num, ((Rect)(ref val3)).width - 8f, 30f);
				bool enableRimWar_WarObjectRaid = Settings.enableRimWar_WarObjectRaid;
				Widgets.CheckboxLabeled(val5, "[Incident] " + ColoredText.Colorize("World object raid ", Color.yellow) + ColoredText.Colorize("(WarObjectRaid)", Color.gray), ref enableRimWar_WarObjectRaid, false, (Texture2D)null, (Texture2D)null, false, false);
				TooltipHandler.TipRegion(val5, TipSignal.op_Implicit("If disabled, RimWar war-object raids bypass Protection Fee."));
				Settings.enableRimWar_WarObjectRaid = enableRimWar_WarObjectRaid;
				num += 30f;
			}
			else
			{
				num += 6f;
			}
		}
		Rect val6 = default(Rect);
		Rect val7 = default(Rect);
		Rect val9 = default(Rect);
		foreach (IGrouping<string, Def> filteredGroupedRaidSource in FilteredGroupedRaidSources)
		{
			string groupStateKey2 = GetGroupStateKey("Event", filteredGroupedRaidSource.Key);
			bool expanded2 = GetExpanded(groupStateKey2);
			((Rect)(ref val6))..ctor(0f, num, ((Rect)(ref val3)).width, 30f);
			Widgets.DrawHighlight(val6);
			GUI.DrawTexture(new Rect(((Rect)(ref val6)).x + 4f, ((Rect)(ref val6)).y + 7f, 16f, 16f), (Texture)(object)(expanded2 ? TexButton.Collapse : TexButton.Reveal));
			Text.Anchor = (TextAnchor)3;
			Widgets.Label(new Rect(((Rect)(ref val6)).x + 24f, ((Rect)(ref val6)).y, ((Rect)(ref val6)).width - 24f, ((Rect)(ref val6)).height), $"{ColoredText.Colorize(filteredGroupedRaidSource.Key, Color.cyan)} ({filteredGroupedRaidSource.Count()})");
			Text.Anchor = (TextAnchor)0;
			if (Widgets.ButtonInvisible(val6, true))
			{
				SetExpanded(groupStateKey2, !expanded2);
				filterDirty = true;
				SoundStarter.PlayOneShotOnCamera(SoundDefOf.Click, (Map)null);
			}
			num += 30f;
			int num2 = 0;
			if (expanded2)
			{
				foreach (Def item in filteredGroupedRaidSource)
				{
					((Rect)(ref val7))..ctor(0f, num, ((Rect)(ref val3)).width, 30f);
					if (num2 % 2 == 1)
					{
						Widgets.DrawAltRect(val7);
					}
					bool flag = ((item is QuestScriptDef) ? GenCollection.TryGetValue<string, bool>((IReadOnlyDictionary<string, bool>)Settings.questSourceEnabledStatus, item.defName, false) : GenCollection.TryGetValue<string, bool>((IReadOnlyDictionary<string, bool>)Settings.incidentSourceEnabledStatus, item.defName, true));
					string text2 = ColoredText.Colorize((item is QuestScriptDef) ? "[Quest] " : "[Incident] ", Color.yellow);
					string label = item.label;
					string text3 = text2 + (((label != null) ? GenText.CapitalizeFirst(label) : null) ?? item.defName) + " " + ColoredText.Colorize("(" + item.defName + ")", Color.gray);
					Rect val8 = new Rect(((Rect)(ref val7)).x + 8f, ((Rect)(ref val7)).y, ((Rect)(ref val7)).width - 8f, ((Rect)(ref val7)).height);
					((Rect)(ref val9))..ctor(((Rect)(ref val7)).x + ((Rect)(ref val7)).width * 0.85f + (((Rect)(ref val7)).width * 0.15f - 24f) / 2f, ((Rect)(ref val7)).y + 2f, 24f, 24f);
					Text.Anchor = (TextAnchor)3;
					Widgets.Label(val8, text3);
					Text.Anchor = (TextAnchor)0;
					bool num3 = flag;
					Widgets.Checkbox(((Rect)(ref val9)).position, ref flag, 24f, false, true, (Texture2D)null, (Texture2D)null);
					if (num3 != flag)
					{
						if (item is QuestScriptDef)
						{
							Settings.questSourceEnabledStatus[item.defName] = flag;
						}
						else
						{
							Settings.incidentSourceEnabledStatus[item.defName] = flag;
						}
					}
					num += 30f;
					num2++;
				}
			}
			else
			{
				num += 6f;
			}
		}
		Widgets.EndScrollView();
	}

	private void RecalculateFilter(bool force = false)
	{
		if (!filterDirty && !force)
		{
			return;
		}
		string filterLower = searchFilter.ToLowerInvariant().Trim();
		IEnumerable<Def> source = AllRaidSources;
		if (!string.IsNullOrWhiteSpace(filterLower))
		{
			source = source.Where(delegate(Def def)
			{
				if (!def.defName.ToLowerInvariant().Contains(filterLower) && (def.label == null || !def.label.ToLowerInvariant().Contains(filterLower)))
				{
					ModContentPack modContentPack = def.modContentPack;
					return (((modContentPack != null) ? modContentPack.Name : null) ?? "#Unknown").ToLowerInvariant().Contains(filterLower);
				}
				return true;
			});
		}
		FilteredGroupedRaidSources = source.OrderBy(delegate(Def def)
		{
			ModContentPack modContentPack2 = def.modContentPack;
			return ((modContentPack2 != null) ? modContentPack2.Name : null) ?? "#Unknown";
		}).ThenBy((Def def) => def.label ?? def.defName).GroupBy(delegate(Def def)
		{
			ModContentPack modContentPack3 = def.modContentPack;
			return ((modContentPack3 != null) ? modContentPack3.Name : null) ?? "#Unknown";
		})
			.ToList();
		cachedTotalHeightFaction = 0f;
		foreach (IGrouping<string, FactionDef> groupedFaction in GroupedFactions)
		{
			bool expanded = GetExpanded(GetGroupStateKey("General", groupedFaction.Key));
			cachedTotalHeightFaction += 30f;
			if (expanded)
			{
				float num = 30f + (Settings.doubleCross ? 30f : 0f) + 30f + 30f + 30f + 12f;
				cachedTotalHeightFaction += (float)groupedFaction.Count() * (num + 3f) + 3f;
			}
			else
			{
				cachedTotalHeightFaction += 6f;
			}
		}
		cachedTotalHeightFaction = Mathf.Max(cachedTotalHeightFaction, 1f);
		cachedTotalHeightEvent = 0f;
		if (ModLister.GetActiveModWithIdentifier("Torann.RimWar", true) != null)
		{
			bool expanded2 = GetExpanded(GetGroupStateKey("Event", "RimWar"));
			cachedTotalHeightEvent += 30f;
			if (expanded2)
			{
				cachedTotalHeightEvent += 30f;
			}
			else
			{
				cachedTotalHeightEvent += 6f;
			}
		}
		foreach (IGrouping<string, Def> filteredGroupedRaidSource in FilteredGroupedRaidSources)
		{
			bool expanded3 = GetExpanded(GetGroupStateKey("Event", filteredGroupedRaidSource.Key));
			cachedTotalHeightEvent += 30f;
			if (expanded3)
			{
				cachedTotalHeightEvent += (float)filteredGroupedRaidSource.Count() * 30f;
			}
			else
			{
				cachedTotalHeightEvent += 6f;
			}
		}
		cachedTotalHeightEvent = Mathf.Max(cachedTotalHeightEvent, 1f);
		filterDirty = false;
	}

	private static string GetGroupStateKey(string pageKey, string groupKey)
	{
		return pageKey + "::" + groupKey;
	}

	private static bool GetExpanded(string stateKey)
	{
		if (!groupExpanded.TryGetValue(stateKey, out var value))
		{
			value = false;
			groupExpanded[stateKey] = value;
		}
		return value;
	}

	private static void SetExpanded(string stateKey, bool expanded)
	{
		groupExpanded[stateKey] = expanded;
	}

	public override string SettingsCategory()
	{
		return "Raid Protection Fee";
	}
}
[HarmonyPatch(typeof(Find), "get_HiddenItemsManager")]
internal static class Patch_Find_get_HiddenItemsManager
{
	private static HiddenItemsManager fallback;

	public static bool Prefix(ref HiddenItemsManager __result)
	{
		//IL_0010: Unknown result type (might be due to invalid IL or missing references)
		if (Current.Game == null)
		{
			fallback = (HiddenItemsManager)(((object)fallback) ?? ((object)new HiddenItemsManager()));
			__result = fallback;
			return false;
		}
		return true;
	}
}
[HarmonyPatch(typeof(Find), "get_IdeoManager")]
internal static class Patch_Find_get_IdeoManager
{
	private static IdeoManager fallback;

	public static bool Prefix(ref IdeoManager __result)
	{
		//IL_0039: Unknown result type (might be due to invalid IL or missing references)
		//IL_0043: Expected O, but got Unknown
		if (((Current.Game != null && Current.Game.World != null) ? Current.Game.World : Current.CreatingWorld)?.ideoManager == null)
		{
			if (fallback == null)
			{
				fallback = new IdeoManager();
			}
			__result = fallback;
			return false;
		}
		return true;
	}
}
[HarmonyPatch]
public static class Patch_DynamicTradeInterface_PreOpen
{
	public static bool Prepare()
	{
		return AccessTools.TypeByName("DynamicTradeInterface.UserInterface.Window_DynamicTrade") != null;
	}

	public static MethodBase TargetMethod()
	{
		return AccessTools.Method("DynamicTradeInterface.UserInterface.Window_DynamicTrade:PreOpen", (Type[])null, (Type[])null);
	}

	public static void Postfix(Window __instance)
	{
		if (TradeSession.trader is ITrader_Ransom)
		{
			AccessTools.Field(((object)__instance).GetType(), "_refresh")?.SetValue(__instance, true);
		}
	}
}
[HarmonyPatch]
public static class Patch_DynamicTradeInterface_Close
{
	public static bool Prepare()
	{
		return AccessTools.TypeByName("DynamicTradeInterface.UserInterface.Window_DynamicTrade") != null;
	}

	public static MethodBase TargetMethod()
	{
		return AccessTools.Method("DynamicTradeInterface.UserInterface.Window_DynamicTrade:Close", (Type[])null, (Type[])null);
	}

	public static void Postfix()
	{
		if (TradeSession.trader is ITrader_Ransom)
		{
			WorldComponent_ProtectionFee.OnRansomFinalize?.Invoke();
		}
	}
}
[HarmonyPatch]
public static class Patch_RimWar_WarObjectRaid_TryExecuteWorker
{
	public static bool Prepare()
	{
		return AccessTools.TypeByName("RimWar.Utility.IncidentWorker_WarObjectRaid") != null;
	}

	public static MethodBase TargetMethod()
	{
		return AccessTools.Method("RimWar.Utility.IncidentWorker_WarObjectRaid:TryExecuteWorker", (Type[])null, (Type[])null);
	}

	public static bool Prefix(object __instance, IncidentParms parms, ref bool __result)
	{
		IncidentWorker val = (IncidentWorker)((__instance is IncidentWorker) ? __instance : null);
		if (val != null)
		{
			return ProtectionFee_Raid.Prefix(val, parms, ref __result);
		}
		return true;
	}
}
[HarmonyPatch(typeof(Tradeable), "get_TraderWillTrade")]
internal static class Patch_Tradeable_TraderWillTrade
{
	public static void Postfix(Tradeable __instance, ref bool __result)
	{
		if (TradeSession.Active && TradeSession.trader is ITrader_Ransom trader_Ransom && ((__instance != null) ? ((Transferable)__instance).AnyThing : null) != null && !__instance.IsCurrency)
		{
			__result = trader_Ransom.AcceptsByDemandPolicy(((Transferable)__instance).AnyThing);
		}
	}
}
[HarmonyPatch(typeof(TradeDeal), "TryExecute")]
internal static class Patch_TradeDeal_TryExecute
{
	public static void Postfix(bool __result)
	{
		if (__result && TradeSession.trader is ITrader_Ransom)
		{
			WorldComponent_ProtectionFee.RansomPaidSuccessfully = true;
		}
	}
}
[HarmonyPatch(typeof(TradeDeal), "UpdateCurrencyCount")]
internal static class Patch_TradeDeal_UpdateCurrencyCount
{
	public static void Postfix(TradeDeal __instance)
	{
		if (TradeSession.Active && TradeSession.trader is ITrader_Ransom && __instance.CurrencyTradeable != null)
		{
			int countToTransfer = ((Transferable)__instance.CurrencyTradeable).CountToTransfer;
			int ransomRequiredValue = WorldComponent_ProtectionFee.RansomRequiredValue;
			((Transferable)__instance.CurrencyTradeable).ForceToSource(countToTransfer - ransomRequiredValue);
		}
	}
}
[HarmonyPatch(typeof(TradeUtility), "AllSellableColonyPawns")]
internal static class Patch_TradeUtility_AllSellableColonyPawns
{
	[HarmonyPostfix]
	public static IEnumerable<Pawn> Postfix(IEnumerable<Pawn> __result, Map map)
	{
		if (map == null)
		{
			return __result;
		}
		HashSet<Pawn> hashSet = new HashSet<Pawn>();
		foreach (Pawn item in __result)
		{
			if (item != null && !item.Dead)
			{
				hashSet.Add(item);
			}
		}
		foreach (Pawn item2 in map.mapPawns.FreeColonistsSpawned)
		{
			if (item2 != null && !item2.Dead)
			{
				hashSet.Add(item2);
			}
		}
		return hashSet;
	}
}
internal static class ProtectionFee_Raid
{
	private static readonly MethodInfo ResolveRaidPointsMethod = AccessTools.Method(typeof(IncidentWorker_Raid), "ResolveRaidPoints", (Type[])null, (Type[])null);

	private static readonly MethodInfo TryResolveRaidFactionMethod = AccessTools.Method(typeof(IncidentWorker_RaidEnemy), "TryResolveRaidFaction", (Type[])null, (Type[])null);

	public static bool Prefix(IncidentWorker worker, IncidentParms parms, ref bool __result)
	{
		//IL_0201: Unknown result type (might be due to invalid IL or missing references)
		//IL_020a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0264: Unknown result type (might be due to invalid IL or missing references)
		//IL_026b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0270: Unknown result type (might be due to invalid IL or missing references)
		//IL_0275: Unknown result type (might be due to invalid IL or missing references)
		//IL_027c: Expected O, but got Unknown
		//IL_028a: Unknown result type (might be due to invalid IL or missing references)
		//IL_028f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0299: Unknown result type (might be due to invalid IL or missing references)
		//IL_029e: Unknown result type (might be due to invalid IL or missing references)
		//IL_02b0: Unknown result type (might be due to invalid IL or missing references)
		//IL_02bc: Expected O, but got Unknown
		//IL_02c8: Unknown result type (might be due to invalid IL or missing references)
		//IL_02d2: Unknown result type (might be due to invalid IL or missing references)
		//IL_02d7: Unknown result type (might be due to invalid IL or missing references)
		//IL_02e9: Unknown result type (might be due to invalid IL or missing references)
		//IL_02f5: Expected O, but got Unknown
		//IL_039e: Unknown result type (might be due to invalid IL or missing references)
		//IL_03a8: Expected O, but got Unknown
		//IL_0322: Unknown result type (might be due to invalid IL or missing references)
		//IL_0327: Unknown result type (might be due to invalid IL or missing references)
		//IL_032e: Expected O, but got Unknown
		//IL_0333: Unknown result type (might be due to invalid IL or missing references)
		//IL_033d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0342: Unknown result type (might be due to invalid IL or missing references)
		//IL_034a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0353: Expected O, but got Unknown
		//IL_0366: Unknown result type (might be due to invalid IL or missing references)
		//IL_0370: Unknown result type (might be due to invalid IL or missing references)
		//IL_0375: Unknown result type (might be due to invalid IL or missing references)
		//IL_037d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0386: Expected O, but got Unknown
		if (WorldComponent_ProtectionFee.IsProcessingRansom)
		{
			return true;
		}
		if (worker == null || parms == null)
		{
			return true;
		}
		if (!ProtectionFee_ModSettings.IsProtectionFeeEnabled(ProtectionFee_Mod.Settings, worker, parms, out var _))
		{
			return true;
		}
		if (parms.faction == null)
		{
			if (parms.points <= 0f)
			{
				IncidentWorker obj = worker;
				IncidentWorker_Raid val = (IncidentWorker_Raid)(object)((obj is IncidentWorker_Raid) ? obj : null);
				if (val != null)
				{
					ResolveRaidPointsMethod?.Invoke(val, new object[1] { parms });
				}
			}
			IncidentWorker obj2 = worker;
			IncidentWorker_RaidEnemy val2 = (IncidentWorker_RaidEnemy)(object)((obj2 is IncidentWorker_RaidEnemy) ? obj2 : null);
			if (val2 == null)
			{
				return true;
			}
			if (!(bool)(TryResolveRaidFactionMethod?.Invoke(val2, new object[1] { parms }) ?? ((object)false)) || parms.faction == null)
			{
				return true;
			}
		}
		WorldComponent_ProtectionFee component = Find.World.GetComponent<WorldComponent_ProtectionFee>();
		if (component != null && component.OnCooldown(parms.faction) && ProtectionFee_Mod.Settings.extortionCooldown)
		{
			return true;
		}
		if (!FactionUtility.HostileTo(parms.faction, Faction.OfPlayer) || !parms.faction.def.humanlikeFaction)
		{
			return true;
		}
		float num = GenCollection.TryGetValue<string, float>((IReadOnlyDictionary<string, float>)ProtectionFee_Mod.Settings.factionExtortionChances, ((Def)parms.faction.def).defName, 1f);
		if (num <= 0f || Rand.Value > num)
		{
			return true;
		}
		IIncidentTarget target = parms.target;
		Map val3 = (Map)(object)((target is Map) ? target : null);
		if (val3 == null)
		{
			return true;
		}
		float num2 = Mathf.Pow(Mathf.Clamp01(parms.points / 10000f), 2f);
		if (!ProtectionFee_Mod.Settings.factionExtortionRanges.TryGetValue(((Def)parms.faction.def).defName, out var value))
		{
			((FloatRange)(ref value))..ctor(0.01f, 0.2f);
		}
		float min = value.min;
		float max = value.max;
		float num3 = min + (max - min) * num2;
		int num4 = Mathf.Max(100, (int)(val3.wealthWatcher.WealthItems * num3 / 100f) * 100);
		WorldComponent_ProtectionFee.RansomPaidSuccessfully = false;
		WorldComponent_ProtectionFee.RansomRequiredValue = num4;
		WorldComponent_ProtectionFee.OnRansomFinalize = null;
		DiaNode val4 = new DiaNode(TranslatorFormattedStringExtensions.Translate("ProtectionFee.Dialogue", NamedArgument.op_Implicit(parms.faction), NamedArgument.op_Implicit(num4)));
		val4.options.Add(new DiaOption(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("Accept", NamedArgument.op_Implicit(num4))))
		{
			action = delegate
			{
				StartRansomTrade(parms, worker);
			},
			resolveTree = true
		});
		val4.options.Add(new DiaOption(TaggedString.op_Implicit(Translator.Translate("Reject")))
		{
			action = delegate
			{
				//IL_0035: Unknown result type (might be due to invalid IL or missing references)
				//IL_003a: Unknown result type (might be due to invalid IL or missing references)
				Find.World.GetComponent<WorldComponent_ProtectionFee>()?.SetCooldown(parms.faction, 60000);
				Messages.Message(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("ProtectionFee.Failed", NamedArgument.op_Implicit(parms.faction))), MessageTypeDefOf.ThreatBig, true);
				ResumeRaid(worker, parms, applyRejectedPenalty: true);
			},
			resolveTree = true
		});
		if (parms.quest != null && !parms.quest.hidden)
		{
			DiaNode val5 = new DiaNode(parms.quest.description);
			DiaOption item = new DiaOption(TaggedString.op_Implicit(Translator.Translate("GoBack")))
			{
				link = val4,
				resolveTree = false
			};
			val5.options.Add(item);
			DiaOption item2 = new DiaOption(TaggedString.op_Implicit(Translator.Translate("ViewRelatedQuest")))
			{
				link = val5,
				resolveTree = false
			};
			val4.options.Add(item2);
		}
		Find.WindowStack.Add((Window)new Dialog_NodeTree(val4, true, true, (string)null));
		__result = true;
		return false;
	}

	private static float GetRejectedRaidPointsMultiplier(Faction faction)
	{
		//IL_0044: Unknown result type (might be due to invalid IL or missing references)
		//IL_0055: Unknown result type (might be due to invalid IL or missing references)
		if (faction?.def == null || ProtectionFee_Mod.Settings == null)
		{
			return 1f;
		}
		if (!ProtectionFee_Mod.Settings.factionRejectedFeeRaidPointsIncreaseRanges.TryGetValue(((Def)faction.def).defName, out var value))
		{
			return 1f;
		}
		float num = Mathf.Max(0f, value.min);
		float num2 = Mathf.Max(0f, value.max);
		if (num2 < num)
		{
			float num3 = num2;
			num2 = num;
			num = num3;
		}
		if (num2 <= 0f)
		{
			return 1f;
		}
		float num4 = Rand.Range(num, num2);
		return 1f + num4;
	}

	private static void ApplyRejectedRaidPointsBoost(IncidentWorker worker, IncidentParms parms)
	{
		if (worker == null || parms == null || parms.faction == null)
		{
			return;
		}
		if (parms.points <= 0f)
		{
			IncidentWorker_Raid val = (IncidentWorker_Raid)(object)((worker is IncidentWorker_Raid) ? worker : null);
			if (val != null)
			{
				ResolveRaidPointsMethod?.Invoke(val, new object[1] { parms });
			}
		}
		if (!(parms.points <= 0f))
		{
			float rejectedRaidPointsMultiplier = GetRejectedRaidPointsMultiplier(parms.faction);
			if (!(rejectedRaidPointsMultiplier <= 1f))
			{
				parms.points *= rejectedRaidPointsMultiplier;
			}
		}
	}

	private static void StartRansomTrade(IncidentParms parms, IncidentWorker worker)
	{
		//IL_0125: Unknown result type (might be due to invalid IL or missing references)
		IIncidentTarget target = parms.target;
		Map val = (Map)(((object)((target is Map) ? target : null)) ?? ((object)(Find.AnyPlayerHomeMap ?? Find.CurrentMap)));
		ITrader_Ransom trader = new ITrader_Ransom(parms.faction, val, parms.faction.leader);
		StatDef tradePriceImprovement = StatDefOf.TradePriceImprovement;
		Pawn val2 = null;
		float num = -1f;
		List<Pawn> freeColonistsSpawned = val.mapPawns.FreeColonistsSpawned;
		for (int i = 0; i < freeColonistsSpawned.Count; i++)
		{
			Pawn val3 = freeColonistsSpawned[i];
			if (!val3.Dead && !val3.Downed && !val3.InMentalState && !tradePriceImprovement.Worker.IsDisabledFor((Thing)(object)val3) && val3.health.capacities.CapableOf(PawnCapacityDefOf.Talking))
			{
				float statValue = StatExtension.GetStatValue((Thing)(object)val3, tradePriceImprovement, true, -1);
				if (val2 == null || statValue > num)
				{
					val2 = val3;
					num = statValue;
				}
			}
		}
		if (val2 == null)
		{
			Find.World.GetComponent<WorldComponent_ProtectionFee>()?.SetCooldown(parms.faction, 60000);
			Messages.Message(TaggedString.op_Implicit(Translator.Translate("ProtectionFee.NoNegotiator")), MessageTypeDefOf.RejectInput, true);
			ResumeRaid(worker, parms, applyRejectedPenalty: false);
			return;
		}
		WorldComponent_ProtectionFee.OnRansomFinalize = delegate
		{
			//IL_00a1: Unknown result type (might be due to invalid IL or missing references)
			//IL_00a6: Unknown result type (might be due to invalid IL or missing references)
			//IL_0169: Unknown result type (might be due to invalid IL or missing references)
			//IL_016e: Unknown result type (might be due to invalid IL or missing references)
			//IL_005b: Unknown result type (might be due to invalid IL or missing references)
			//IL_0060: Unknown result type (might be due to invalid IL or missing references)
			//IL_00ee: Unknown result type (might be due to invalid IL or missing references)
			//IL_0128: Unknown result type (might be due to invalid IL or missing references)
			if (WorldComponent_ProtectionFee.RansomPaidSuccessfully)
			{
				if (ProtectionFee_Mod.Settings.doubleCross && Rand.Value < GenCollection.TryGetValue<string, float>((IReadOnlyDictionary<string, float>)ProtectionFee_Mod.Settings.factionDoubleCrossChances, ((Def)parms.faction.def).defName, 0.05f))
				{
					Messages.Message(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("ProtectionFee.DoubleCross", NamedArgument.op_Implicit(parms.faction.Name))), MessageTypeDefOf.ThreatBig, true);
					ResumeRaid(worker, parms, applyRejectedPenalty: false);
				}
				else
				{
					Messages.Message(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("ProtectionFee.Success", NamedArgument.op_Implicit(parms.faction.Name))), MessageTypeDefOf.PositiveEvent, true);
					if (parms.quest != null)
					{
						if (!GenText.NullOrEmpty(parms.inSignalEnd))
						{
							Find.SignalManager.SendSignal(new Signal(parms.inSignalEnd, false));
						}
						if (!GenText.NullOrEmpty(parms.questTag))
						{
							Find.SignalManager.SendSignal(new Signal(parms.questTag + ".AllEnemiesDefeated", false));
						}
					}
				}
			}
			else
			{
				Find.World.GetComponent<WorldComponent_ProtectionFee>()?.SetCooldown(parms.faction, 60000);
				Messages.Message(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("ProtectionFee.Failed", NamedArgument.op_Implicit(parms.faction))), MessageTypeDefOf.ThreatBig, true);
				ResumeRaid(worker, parms, applyRejectedPenalty: false);
			}
			WorldComponent_ProtectionFee.OnRansomFinalize = null;
		};
		Dialog_Ransom dialog_Ransom = new Dialog_Ransom(val2, (ITrader)(object)trader, WorldComponent_ProtectionFee.OnRansomFinalize);
		Find.WindowStack.Add((Window)(object)dialog_Ransom);
	}

	private static void ResumeRaid(IncidentWorker worker, IncidentParms parms, bool applyRejectedPenalty)
	{
		if (parms.target == null)
		{
			parms.target = (IIncidentTarget)(object)(Find.AnyPlayerHomeMap ?? Find.CurrentMap);
		}
		if (applyRejectedPenalty)
		{
			ApplyRejectedRaidPointsBoost(worker, parms);
		}
		WorldComponent_ProtectionFee.IsProcessingRansom = true;
		try
		{
			worker.TryExecute(parms);
		}
		finally
		{
			WorldComponent_ProtectionFee.IsProcessingRansom = false;
		}
	}
}
[HarmonyPatch(typeof(IncidentWorker_RaidEnemy), "TryExecuteWorker")]
internal static class Patch_IncidentWorker_RaidEnemy_TryExecuteWorker
{
	public static bool Prefix(IncidentWorker_RaidEnemy __instance, IncidentParms parms, ref bool __result)
	{
		return ProtectionFee_Raid.Prefix((IncidentWorker)(object)__instance, parms, ref __result);
	}
}
internal class WorldComponent_ProtectionFee : WorldComponent
{
	public static bool IsProcessingRansom;

	public static bool RansomPaidSuccessfully;

	public static int RansomRequiredValue;

	public static Action OnRansomFinalize;

	public Dictionary<int, int> factionCooldowns = new Dictionary<int, int>();

	public WorldComponent_ProtectionFee(World world)
		: base(world)
	{
	}

	public override void ExposeData()
	{
		((WorldComponent)this).ExposeData();
		Scribe_Collections.Look<int, int>(ref factionCooldowns, "factionCooldowns", (LookMode)1, (LookMode)1);
		if (factionCooldowns == null)
		{
			factionCooldowns = new Dictionary<int, int>();
		}
	}

	public bool OnCooldown(Faction faction)
	{
		if (faction == null)
		{
			return false;
		}
		if (factionCooldowns.TryGetValue(faction.loadID, out var value))
		{
			if (Find.TickManager.TicksGame < value)
			{
				return true;
			}
			factionCooldowns.Remove(faction.loadID);
		}
		return false;
	}

	public void SetCooldown(Faction faction, int durationTicks)
	{
		if (faction != null && ProtectionFee_Mod.Settings.extortionCooldown)
		{
			factionCooldowns[faction.loadID] = Find.TickManager.TicksGame + durationTicks;
		}
	}
}
You are not using the latest version of the tool, please update.
Latest version is '11.0.0.9375' (yours is '9.0.0.7889')
