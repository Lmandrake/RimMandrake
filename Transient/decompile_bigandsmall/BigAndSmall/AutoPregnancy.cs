using System;
using System.Collections;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Runtime.CompilerServices;
using RimWorld;
using UnityEngine;
using Verse;

namespace BigAndSmall;

public class AutoPregnancy : TickdownGene
{
	[CompilerGenerated]
	private sealed class _003CGetGizmos_003Ed__8 : IEnumerable<Gizmo>, IEnumerable, IEnumerator<Gizmo>, IDisposable, IEnumerator
	{
		private int _003C_003E1__state;

		private Gizmo _003C_003E2__current;

		private int _003C_003El__initialThreadId;

		public AutoPregnancy _003C_003E4__this;

		Gizmo IEnumerator<Gizmo>.Current
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
		public _003CGetGizmos_003Ed__8(int _003C_003E1__state)
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
			//IL_0022: Unknown result type (might be due to invalid IL or missing references)
			//IL_0027: Unknown result type (might be due to invalid IL or missing references)
			//IL_0041: Unknown result type (might be due to invalid IL or missing references)
			//IL_0035: Unknown result type (might be due to invalid IL or missing references)
			//IL_0050: Unknown result type (might be due to invalid IL or missing references)
			//IL_005e: Unknown result type (might be due to invalid IL or missing references)
			//IL_0074: Unknown result type (might be due to invalid IL or missing references)
			//IL_0094: Unknown result type (might be due to invalid IL or missing references)
			//IL_00ab: Expected O, but got Unknown
			int num = _003C_003E1__state;
			AutoPregnancy autoPregnancy = _003C_003E4__this;
			switch (num)
			{
			default:
				return false;
			case 0:
				_003C_003E1__state = -1;
				_003C_003E2__current = (Gizmo)new Command_Action
				{
					defaultLabel = TaggedString.op_Implicit(autoPregnancy.autoPregDisabled ? Translator.Translate("BS_RestoreAutoPregnancy") : Translator.Translate("BS_EnoughAutoPregnancy")),
					defaultDesc = (autoPregnancy.autoPregDisabled ? "BS_RestoreAutoPregnancyDesc" : TaggedString.op_Implicit(Translator.Translate("BS_EnoughAutoPregnancyDesc"))),
					icon = (Texture)(object)ContentFinder<Texture2D>.Get(autoPregnancy.autoPregDisabled ? "GeneIcons/BS_AutoPregnancyGizmo" : "GeneIcons/BS_AutoPregnancyGizmo_STHAP", true),
					action = autoPregnancy.ToggleAutoPregnancy
				};
				_003C_003E1__state = 1;
				return true;
			case 1:
				_003C_003E1__state = -1;
				return false;
			}
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
		IEnumerator<Gizmo> IEnumerable<Gizmo>.GetEnumerator()
		{
			_003CGetGizmos_003Ed__8 result;
			if (_003C_003E1__state == -2 && _003C_003El__initialThreadId == Environment.CurrentManagedThreadId)
			{
				_003C_003E1__state = 0;
				result = this;
			}
			else
			{
				result = new _003CGetGizmos_003Ed__8(0)
				{
					_003C_003E4__this = _003C_003E4__this
				};
			}
			return result;
		}

		[DebuggerHidden]
		IEnumerator IEnumerable.GetEnumerator()
		{
			return ((IEnumerable<Gizmo>)this).GetEnumerator();
		}
	}

	private bool? _isFemale;

	protected bool autoPregDisabled;

	protected bool IsFemale
	{
		get
		{
			//IL_001f: Unknown result type (might be due to invalid IL or missing references)
			//IL_0025: Invalid comparison between Unknown and I4
			bool valueOrDefault = _isFemale == true;
			if (!_isFemale.HasValue)
			{
				valueOrDefault = (int)((Gene)this).pawn.gender != 1;
				_isFemale = valueOrDefault;
				return valueOrDefault;
			}
			return valueOrDefault;
		}
	}

	public override void ResetCountdown()
	{
		tickDown = Rand.Range(60000, 300000);
	}

	public override void TickEvent()
	{
		//IL_0117: Unknown result type (might be due to invalid IL or missing references)
		//IL_011e: Expected O, but got Unknown
		if (autoPregDisabled)
		{
			return;
		}
		AutoPregnancySettings modExtension = ((Def)((Gene)this).def).GetModExtension<AutoPregnancySettings>();
		HediffSet hediffSet = ((Gene)this).pawn.health.hediffSet;
		Pawn pawn = ((Gene)this).pawn;
		if (pawn == null || !pawn.ageTracker.Adult || StatExtension.GetStatValue((Thing)(object)((Gene)this).pawn, StatDefOf.Fertility, true, -1) <= 0f || !IsFemale || hediffSet.HasHediff(HediffDefOf.Lactating, false))
		{
			return;
		}
		Pawn val = null;
		if (Rand.Chance(modExtension.randomExtraParentChance))
		{
			bool canHaveArchiteFather = Rand.Chance(modExtension.randomExtraParentChanceArchites);
			val = GenCollection.RandomElementByWeight<Pawn>(PawnsFinder.All_AliveOrDead.Where(delegate(Pawn x)
			{
				if ((x == null || !x.IsMechanical()) && (x == null || !x.IsUndead()) && x != null)
				{
					Pawn_GeneTracker genes = x.genes;
					bool? obj;
					if (genes == null)
					{
						obj = null;
					}
					else
					{
						List<Gene> genesListForReading = genes.GenesListForReading;
						obj = ((genesListForReading != null) ? new bool?(GenCollection.Any<Gene>(genesListForReading)) : ((bool?)null));
					}
					bool? flag = obj;
					if (flag == true && x.genes.GenesListForReading.Count > 3)
					{
						if (!canHaveArchiteFather)
						{
							return !GenCollection.Any<Gene>(x.genes.GenesListForReading, (Predicate<Gene>)((Gene x) => x.def.biostatArc > 1));
						}
						return true;
					}
				}
				return false;
			}), (Func<Pawn, float>)delegate(Pawn x)
			{
				if (x.genes?.xenotype != XenotypeDefOf.Baseliner)
				{
					Pawn_GeneTracker genes2 = x.genes;
					if (genes2 == null || !genes2.hybrid)
					{
						return 1f;
					}
					return 0.1f;
				}
				return 0.001f;
			});
			if (val == null)
			{
				Log.Message($"[AutoPregnancy] Could not find a valid random father for {((Gene)this).pawn.Name}");
			}
		}
		bool flag2 = default(bool);
		GeneSet inheritedGeneSet = PregnancyUtility.GetInheritedGeneSet(val, ((Gene)this).pawn, ref flag2);
		if (flag2)
		{
			Hediff_Pregnant val2 = (Hediff_Pregnant)HediffMaker.MakeHediff(HediffDefOf.PregnantHuman, ((Gene)this).pawn, (BodyPartRecord)null);
			((HediffWithParents)val2).SetParents(((Gene)this).pawn, (Pawn)null, inheritedGeneSet);
			((Gene)this).pawn.health.AddHediff((Hediff)(object)val2, (BodyPartRecord)null, (DamageInfo?)null, (DamageResult)null);
		}
	}

	public override void PostAdd()
	{
		tickDown = Rand.Range(10000, 60000);
		((Gene)this).PostAdd();
	}

	public void ToggleAutoPregnancy()
	{
		autoPregDisabled = !autoPregDisabled;
	}

	[IteratorStateMachine(typeof(_003CGetGizmos_003Ed__8))]
	public override IEnumerable<Gizmo> GetGizmos()
	{
		//yield-return decompiler failed: Unexpected instruction in Iterator.Dispose()
		return new _003CGetGizmos_003Ed__8(-2)
		{
			_003C_003E4__this = this
		};
	}

	public override void ExposeData()
	{
		base.ExposeData();
		Scribe_Values.Look<bool>(ref autoPregDisabled, "BS_AutoPregDisabled", false, false);
	}
}
