using System;
using System.Collections;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Runtime.CompilerServices;
using HarmonyLib;
using RimWorld;
using RimWorld.Planet;
using Verse;

namespace Rimesis;

[HarmonyPatch(typeof(PawnGroupMakerUtility), "GeneratePawns")]
public static class Patch_PawnGroupMakerUtility_GeneratePawns
{
	[CompilerGenerated]
	private sealed class <Postfix>d__0 : IEnumerable<Pawn>, IEnumerable, IEnumerator<Pawn>, IDisposable, IEnumerator
	{
		private int <>1__state;

		private Pawn <>2__current;

		private int <>l__initialThreadId;

		private PawnGroupMakerParms parms;

		public PawnGroupMakerParms <>3__parms;

		private IEnumerable<Pawn> __result;

		public IEnumerable<Pawn> <>3____result;

		private IncidentParms <raidParms>5__2;

		private List<Pawn> <yielded>5__3;

		private RimesisRaidPlan <plan>5__4;

		private HashSet<Pawn> <alreadyPresent>5__5;

		private List<RimesisRecord> <records>5__6;

		private IEnumerator<Pawn> <>7__wrap6;

		private List<Pawn>.Enumerator <>7__wrap7;

		private IEnumerator<RimesisRecord> <>7__wrap8;

		private RimesisRecord <record>5__10;

		private int <level>5__11;

		private int <count>5__12;

		private int <index>5__13;

		private PawnKindDef <tunneler>5__14;

		private int <i>5__15;

		Pawn IEnumerator<Pawn>.Current
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
		public <Postfix>d__0(int <>1__state)
		{
			this.<>1__state = <>1__state;
			<>l__initialThreadId = Environment.CurrentManagedThreadId;
		}

		[DebuggerHidden]
		void IDisposable.Dispose()
		{
			switch (<>1__state)
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
			case -4:
			case 2:
				try
				{
				}
				finally
				{
					<>m__Finally2();
				}
				break;
			case -5:
			case 3:
				try
				{
				}
				finally
				{
					<>m__Finally3();
				}
				break;
			case -6:
			case 4:
				try
				{
				}
				finally
				{
					<>m__Finally4();
				}
				break;
			case -7:
			case 5:
				try
				{
				}
				finally
				{
					<>m__Finally5();
				}
				break;
			case -8:
			case 6:
				try
				{
				}
				finally
				{
					<>m__Finally6();
				}
				break;
			}
			<raidParms>5__2 = null;
			<yielded>5__3 = null;
			<plan>5__4 = null;
			<alreadyPresent>5__5 = null;
			<records>5__6 = null;
			<>7__wrap6 = null;
			<>7__wrap7 = default(List<Pawn>.Enumerator);
			<>7__wrap8 = null;
			<record>5__10 = null;
			<tunneler>5__14 = null;
			<>1__state = -2;
		}

		private bool MoveNext()
		{
			try
			{
				switch (<>1__state)
				{
				default:
					return false;
				case 0:
					<>1__state = -1;
					<raidParms>5__2 = RimesisRaidGenerationContext.Active;
					if (parms.groupKind != PawnGroupKindDefOf.Combat || <raidParms>5__2 == null || <raidParms>5__2.faction != parms.faction)
					{
						<>7__wrap6 = __result.GetEnumerator();
						<>1__state = -3;
						goto IL_00b8;
					}
					<yielded>5__3 = new List<Pawn>();
					<>7__wrap6 = __result.GetEnumerator();
					<>1__state = -4;
					goto IL_0134;
				case 1:
					<>1__state = -3;
					goto IL_00b8;
				case 2:
					<>1__state = -4;
					goto IL_0134;
				case 3:
					<>1__state = -5;
					goto IL_0240;
				case 4:
					<>1__state = -6;
					goto IL_034d;
				case 5:
					<>1__state = -7;
					goto IL_04ba;
				case 6:
					{
						<>1__state = -8;
						goto IL_06d1;
					}
					IL_0240:
					while (<>7__wrap6.MoveNext())
					{
						Pawn current = <>7__wrap6.Current;
						if (current != null && !current.Dead && !<alreadyPresent>5__5.Contains(current))
						{
							if (WorldPawnsUtility.IsWorldPawn(current))
							{
								Find.WorldPawns.RemovePawn(current);
							}
							<yielded>5__3.Add(current);
							<alreadyPresent>5__5.Add(current);
							<>2__current = current;
							<>1__state = 3;
							return true;
						}
					}
					<>m__Finally3();
					<>7__wrap6 = null;
					<records>5__6 = (from p in <yielded>5__3
						select RimesisWorldComponent.Current?.Get(p) into r
						where r != null
						select r).Distinct().ToList();
					RimesisRaidBalance.ApplyEscortDoctrines(<yielded>5__3, <records>5__6, <plan>5__4?.records);
					<>7__wrap7 = RimesisShamblermancerUtility.PrepareSacrificePayloads(<yielded>5__3, <records>5__6, parms.faction, <raidParms>5__2).GetEnumerator();
					<>1__state = -6;
					goto IL_034d;
					IL_00b8:
					if (<>7__wrap6.MoveNext())
					{
						Pawn current2 = <>7__wrap6.Current;
						<>2__current = current2;
						<>1__state = 1;
						return true;
					}
					<>m__Finally1();
					<>7__wrap6 = null;
					return false;
					IL_04ba:
					<index>5__13++;
					goto IL_04cc;
					IL_0134:
					if (<>7__wrap6.MoveNext())
					{
						Pawn current3 = <>7__wrap6.Current;
						<yielded>5__3.Add(current3);
						<>2__current = current3;
						<>1__state = 2;
						return true;
					}
					<>m__Finally2();
					<>7__wrap6 = null;
					<plan>5__4 = RimesisRaidPlan.For(parms.faction);
					<alreadyPresent>5__5 = <yielded>5__3.ToHashSet();
					<>7__wrap6 = ((from r in <plan>5__4?.ClaimRecords()
						select r.pawn) ?? Enumerable.Empty<Pawn>()).GetEnumerator();
					<>1__state = -5;
					goto IL_0240;
					IL_06d1:
					<i>5__15++;
					goto IL_06e3;
					IL_06e3:
					if (<i>5__15 < <level>5__11)
					{
						Pawn val = null;
						for (int i = 0; i < 3; i++)
						{
							if (val != null)
							{
								break;
							}
							PawnKindDef val2 = ((i == 0 && <i>5__15 < <index>5__13 && <tunneler>5__14 != null) ? <tunneler>5__14 : RimesisMechanitorCompatibility.ChooseCombatKind(<record>5__10, <count>5__12));
							if (val2 == null)
							{
								break;
							}
							try
							{
								val = PawnGenerator.GeneratePawn(val2, parms.faction, (PlanetTile?)null);
							}
							catch (Exception ex)
							{
								RimesisLog.DevWarning("[Rimesis] Could not generate mechanitor escort " + ((Def)val2).defName + ": " + ex.Message);
							}
						}
						if (val != null)
						{
							<record>5__10.currentRaidMechIds.Add(((Thing)val).thingIDNumber);
							<>2__current = val;
							<>1__state = 6;
							return true;
						}
						goto IL_06d1;
					}
					<tunneler>5__14 = null;
					<record>5__10 = null;
					goto IL_0702;
					IL_04cc:
					if (<index>5__13 < <count>5__12)
					{
						PawnKindDef val3 = RimesisBeastmasterCompatibility.ChooseKind(<record>5__10, <level>5__11);
						if (val3 != null)
						{
							Pawn val4 = null;
							try
							{
								val4 = PawnGenerator.GeneratePawn(val3, parms.faction, (PlanetTile?)null);
							}
							catch (Exception ex2)
							{
								RimesisLog.DevWarning("[Rimesis] Could not generate Beastmaster animal: " + ex2.Message);
							}
							if (val4 != null)
							{
								RimesisBeastmasterCompatibility.ApplyPackProgression(val4, <record>5__10);
								<record>5__10.currentRaidBeastIds.Add(((Thing)val4).thingIDNumber);
								<>2__current = val4;
								<>1__state = 5;
								return true;
							}
						}
						goto IL_04ba;
					}
					<record>5__10 = null;
					goto IL_04e4;
					IL_034d:
					if (<>7__wrap7.MoveNext())
					{
						Pawn current4 = <>7__wrap7.Current;
						<yielded>5__3.Add(current4);
						<>2__current = current4;
						<>1__state = 4;
						return true;
					}
					<>m__Finally4();
					<>7__wrap7 = default(List<Pawn>.Enumerator);
					<>7__wrap8 = <records>5__6.Where((RimesisRecord r) => r.focus == RimesisCombatFocus.Beastmaster && RimesisBeastmasterCompatibility.Supports(r)).OrderByDescending(RimesisProgression.Level).GetEnumerator();
					<>1__state = -7;
					goto IL_04e4;
					IL_04e4:
					if (<>7__wrap8.MoveNext())
					{
						<record>5__10 = <>7__wrap8.Current;
						<record>5__10.currentRaidBeastIds.Clear();
						<level>5__11 = RimesisProgression.Level(<record>5__10);
						<count>5__12 = RimesisRaidBalance.BeastmasterCount(<level>5__11);
						<index>5__13 = 0;
						goto IL_04cc;
					}
					<>m__Finally5();
					<>7__wrap8 = null;
					if (!ModsConfig.BiotechActive)
					{
						return false;
					}
					<>7__wrap8 = <records>5__6.Where((RimesisRecord r) => r.focus == RimesisCombatFocus.Mechanitor && RimesisWorldComponent.SupportsMechanitor(r)).OrderByDescending(RimesisProgression.Level).GetEnumerator();
					<>1__state = -8;
					goto IL_0702;
					IL_0702:
					if (<>7__wrap8.MoveNext())
					{
						<record>5__10 = <>7__wrap8.Current;
						<record>5__10.currentRaidMechIds.Clear();
						<count>5__12 = RimesisProgression.Level(<record>5__10);
						<level>5__11 = RimesisRaidBalance.MechanitorCount(<count>5__12);
						<index>5__13 = ((<record>5__10.tactic == RimesisTactic.BreachSpecialist) ? Math.Min(<level>5__11, RimesisRaidBalance.MechanitorBreacherCount(<count>5__12)) : 0);
						<tunneler>5__14 = RimesisMechanitorCompatibility.BreacherKind(<record>5__10);
						<i>5__15 = 0;
						goto IL_06e3;
					}
					<>m__Finally6();
					<>7__wrap8 = null;
					return false;
				}
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
			if (<>7__wrap6 != null)
			{
				<>7__wrap6.Dispose();
			}
		}

		private void <>m__Finally2()
		{
			<>1__state = -1;
			if (<>7__wrap6 != null)
			{
				<>7__wrap6.Dispose();
			}
		}

		private void <>m__Finally3()
		{
			<>1__state = -1;
			if (<>7__wrap6 != null)
			{
				<>7__wrap6.Dispose();
			}
		}

		private void <>m__Finally4()
		{
			<>1__state = -1;
			((IDisposable)<>7__wrap7/*cast due to .constrained prefix*/).Dispose();
		}

		private void <>m__Finally5()
		{
			<>1__state = -1;
			if (<>7__wrap8 != null)
			{
				<>7__wrap8.Dispose();
			}
		}

		private void <>m__Finally6()
		{
			<>1__state = -1;
			if (<>7__wrap8 != null)
			{
				<>7__wrap8.Dispose();
			}
		}

		[DebuggerHidden]
		void IEnumerator.Reset()
		{
			throw new NotSupportedException();
		}

		[DebuggerHidden]
		IEnumerator<Pawn> IEnumerable<Pawn>.GetEnumerator()
		{
			<Postfix>d__0 <Postfix>d__;
			if (<>1__state == -2 && <>l__initialThreadId == Environment.CurrentManagedThreadId)
			{
				<>1__state = 0;
				<Postfix>d__ = this;
			}
			else
			{
				<Postfix>d__ = new <Postfix>d__0(0);
			}
			<Postfix>d__.__result = <>3____result;
			<Postfix>d__.parms = <>3__parms;
			return <Postfix>d__;
		}

		[DebuggerHidden]
		IEnumerator IEnumerable.GetEnumerator()
		{
			return ((IEnumerable<Pawn>)this).GetEnumerator();
		}
	}

	[IteratorStateMachine(typeof(<Postfix>d__0))]
	[HarmonyPriority(0)]
	public static IEnumerable<Pawn> Postfix(IEnumerable<Pawn> __result, PawnGroupMakerParms parms)
	{
		//yield-return decompiler failed: Unexpected instruction in Iterator.Dispose()
		return new <Postfix>d__0(-2)
		{
			<>3____result = __result,
			<>3__parms = parms
		};
	}
}
You are not using the latest version of the tool, please update.
Latest version is '11.0.0.9375' (yours is '9.0.0.7889')
