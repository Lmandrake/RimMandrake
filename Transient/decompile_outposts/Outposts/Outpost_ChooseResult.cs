using System;
using System.Collections;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Runtime.CompilerServices;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;

namespace Outposts;

public class Outpost_ChooseResult : Outpost
{
	[CompilerGenerated]
	private sealed class _003CGetExtraOptions_003Ed__7 : IEnumerable<ResultOption>, IEnumerable, IEnumerator<ResultOption>, IDisposable, IEnumerator
	{
		private int _003C_003E1__state;

		private ResultOption _003C_003E2__current;

		private int _003C_003El__initialThreadId;

		ResultOption IEnumerator<ResultOption>.Current
		{
			[DebuggerHidden]
			get
			{
				return _003C_003E2__current;
			}
		}

		object IEnumerator.Current
		{
			[DebuggerHidden]
			get
			{
				return _003C_003E2__current;
			}
		}

		[DebuggerHidden]
		public _003CGetExtraOptions_003Ed__7(int _003C_003E1__state)
		{
			this._003C_003E1__state = _003C_003E1__state;
			_003C_003El__initialThreadId = Environment.CurrentManagedThreadId;
		}

		[DebuggerHidden]
		void IDisposable.Dispose()
		{
			_003C_003E1__state = -2;
		}

		private bool MoveNext()
		{
			if (_003C_003E1__state != 0)
			{
				return false;
			}
			_003C_003E1__state = -1;
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
		IEnumerator<ResultOption> IEnumerable<ResultOption>.GetEnumerator()
		{
			if (_003C_003E1__state == -2 && _003C_003El__initialThreadId == Environment.CurrentManagedThreadId)
			{
				_003C_003E1__state = 0;
				return this;
			}
			return new _003CGetExtraOptions_003Ed__7(0);
		}

		[DebuggerHidden]
		IEnumerator IEnumerable.GetEnumerator()
		{
			return ((IEnumerable<ResultOption>)this).GetEnumerator();
		}
	}

	private ThingDef choice;

	protected OutpostExtension_Choose ChooseExt => base.Ext as OutpostExtension_Choose;

	public override List<ResultOption> ResultOptions => (from ro in base.Ext.ResultOptions.OrEmpty().Concat(GetExtraOptions())
		where ro.Thing == choice
		select ro).ToList();

	public override IEnumerable<Gizmo> GetGizmos()
	{
		//IL_0006: Unknown result type (might be due to invalid IL or missing references)
		//IL_000b: Unknown result type (might be due to invalid IL or missing references)
		//IL_001d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0034: Unknown result type (might be due to invalid IL or missing references)
		//IL_0039: Unknown result type (might be due to invalid IL or missing references)
		//IL_0048: Unknown result type (might be due to invalid IL or missing references)
		//IL_0059: Unknown result type (might be due to invalid IL or missing references)
		//IL_006f: Expected O, but got Unknown
		return base.GetGizmos().Append((Gizmo)new Command_Action
		{
			action = delegate
			{
				//IL_0036: Unknown result type (might be due to invalid IL or missing references)
				//IL_0040: Expected O, but got Unknown
				Find.WindowStack.Add((Window)new FloatMenu(base.Ext.ResultOptions.OrEmpty().Concat(GetExtraOptions()).Select((Func<ResultOption, FloatMenuOption>)delegate(ResultOption ro)
				{
					//IL_010b: Unknown result type (might be due to invalid IL or missing references)
					//IL_0111: Expected O, but got Unknown
					//IL_008a: Unknown result type (might be due to invalid IL or missing references)
					//IL_008f: Unknown result type (might be due to invalid IL or missing references)
					//IL_0094: Unknown result type (might be due to invalid IL or missing references)
					//IL_00c1: Unknown result type (might be due to invalid IL or missing references)
					//IL_00c7: Expected O, but got Unknown
					List<AmountBySkill> minSkills = ro.MinSkills;
					return (minSkills != null && !minSkills.SatisfiedBy(base.CapablePawns)) ? new FloatMenuOption(TaggedString.op_Implicit(ro.Explain(base.CapablePawns.ToList()) + " - " + TranslatorFormattedStringExtensions.Translate("Outposts.SkillTooLow", NamedArgument.op_Implicit(ro.MinSkills.Max((AmountBySkill abs) => abs.Count)))), (Action)null, ro.Thing, (ThingStyleDef)null, false, (MenuOptionPriority)4, (Action<Rect>)null, (Thing)null, 0f, (Func<Rect, bool>)null, (WorldObject)null, true, 0, (int?)null) : new FloatMenuOption(ro.Explain(base.CapablePawns.ToList()), (Action)delegate
					{
						choice = ro.Thing;
					}, ro.Thing, (ThingStyleDef)null, false, (MenuOptionPriority)4, (Action<Rect>)null, (Thing)null, 0f, (Func<Rect, bool>)null, (WorldObject)null, true, 0, (int?)null);
				})
					.ToList()));
			},
			defaultLabel = TaggedString.op_Implicit(GrammarResolverSimpleStringExtensions.Formatted(ChooseExt.ChooseLabel, NamedArgument.op_Implicit(((Def)choice).label))),
			defaultDesc = ChooseExt.ChooseDesc,
			icon = (Texture)(object)((BuildableDef)choice).uiIcon
		});
	}

	public override void RecachePawnTraits()
	{
		//IL_0095: Unknown result type (might be due to invalid IL or missing references)
		//IL_009b: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a0: Unknown result type (might be due to invalid IL or missing references)
		base.RecachePawnTraits();
		if (choice == null)
		{
			choice = GenCollection.MinBy<ResultOption, float>(base.Ext.ResultOptions.OrEmpty().Concat(GetExtraOptions()), (Func<ResultOption, float>)((ResultOption ro) => ((float?)ro.MinSkills?.Sum((AmountBySkill abs) => abs.Count)) ?? 0f)).Thing;
		}
		ResultOption resultOption = GenCollection.FirstOrDefault<ResultOption>(ResultOptions, (Predicate<ResultOption>)((ResultOption ro) => !(ro.MinSkills?.SatisfiedBy(base.CapablePawns) ?? true)));
		if (resultOption == null)
		{
			return;
		}
		ThingDef thing = resultOption.Thing;
		if (thing == null)
		{
			return;
		}
		string label = ((Def)thing).label;
		Messages.Message(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("Outposts.SkillChange", NamedArgument.op_Implicit(Name), NamedArgument.op_Implicit(label))), LookTargets.op_Implicit((WorldObject)(object)this), MessageTypeDefOf.NegativeEvent, true);
		choice = GenCollection.MinBy<ResultOption, float>(base.Ext.ResultOptions.OrEmpty().Concat(GetExtraOptions()), (Func<ResultOption, float>)((ResultOption ro) => ((float?)ro.MinSkills?.Sum((AmountBySkill abs) => abs.Count)) ?? 0f)).Thing;
	}

	[IteratorStateMachine(typeof(_003CGetExtraOptions_003Ed__7))]
	public virtual IEnumerable<ResultOption> GetExtraOptions()
	{
		//yield-return decompiler failed: Unexpected instruction in Iterator.Dispose()
		return new _003CGetExtraOptions_003Ed__7(-2);
	}

	public override void ExposeData()
	{
		base.ExposeData();
		Scribe_Defs.Look<ThingDef>(ref choice, "choice");
	}
}
