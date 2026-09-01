using HarmonyLib;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;

namespace VEF.Abilities;

public class AbilityPawnFlyer : PawnFlyer
{
	private static readonly FieldRef<PawnFlyer, IntVec3> DestCellField = (FieldRef<PawnFlyer, IntVec3>)(object)AccessTools.FieldRefAccess<IntVec3>(typeof(PawnFlyer), "destCell");

	private static readonly FieldRef<PawnFlyer, Vector3> EffectivePosField = (FieldRef<PawnFlyer, Vector3>)(object)AccessTools.FieldRefAccess<Vector3>(typeof(PawnFlyer), "effectivePos");

	private static readonly FieldRef<PawnFlyer, Vector3> GroundPosField = (FieldRef<PawnFlyer, Vector3>)(object)AccessTools.FieldRefAccess<Vector3>(typeof(PawnFlyer), "groundPos");

	private static readonly FieldRef<PawnFlyer, float> EffectiveHeightField = (FieldRef<PawnFlyer, float>)(object)AccessTools.FieldRefAccess<float>(typeof(PawnFlyer), "effectiveHeight");

	public Ability ability;

	public bool selectOnSpawn;

	public ref IntVec3 DestinationCell => ref DestCellField.Invoke((PawnFlyer)(object)this);

	public ref Vector3 EffectivePos => ref EffectivePosField.Invoke((PawnFlyer)(object)this);

	public ref Vector3 GroundPos => ref GroundPosField.Invoke((PawnFlyer)(object)this);

	public ref float EffectiveHeight => ref EffectiveHeightField.Invoke((PawnFlyer)(object)this);

	protected internal virtual bool CustomRecomputePosition()
	{
		return false;
	}

	protected internal virtual bool AutoSelectPawn(Pawn target)
	{
		return true;
	}

	public override void SpawnSetup(Map map, bool respawningAfterLoad)
	{
		((PawnFlyer)this).SpawnSetup(map, respawningAfterLoad);
		if (selectOnSpawn)
		{
			selectOnSpawn = false;
			Find.Selector.Select(((object)((PawnFlyer)this).FlyingThing) ?? ((object)this), true, true);
		}
	}

	protected override void RespawnPawn()
	{
		//IL_002d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0032: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a7: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ad: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b7: Expected O, but got Unknown
		Pawn flyingPawn = ((PawnFlyer)this).FlyingPawn;
		((PawnFlyer)this).RespawnPawn();
		if (flyingPawn != null && ability != null)
		{
			ability.ApplyHediffs((GlobalTargetInfo[])(object)new GlobalTargetInfo[1]
			{
				new GlobalTargetInfo((Thing)(object)flyingPawn)
			});
			AbilityExtension_Hediff modExtension = ((Def)ability.def).GetModExtension<AbilityExtension_Hediff>();
			int? obj;
			if (modExtension == null)
			{
				obj = null;
			}
			else
			{
				HediffCompProperties_Disappears obj2 = modExtension.hediff.CompProps<HediffCompProperties_Disappears>();
				obj = ((obj2 != null) ? new int?(((IntRange)(ref obj2.disappearsAfterTicks)).RandomInRange) : ((int?)null));
			}
			int? num = obj;
			if (num.HasValue)
			{
				flyingPawn.stances.SetStance((Stance)new Stance_Cooldown(num.Value + 1, LocalTargetInfo.op_Implicit((Thing)(object)ability.CasterPawn), (Verb)null));
				flyingPawn.stances.stagger.StaggerFor(num.Value, 0.17f);
			}
		}
	}

	public override void ExposeData()
	{
		((PawnFlyer)this).ExposeData();
		Scribe_References.Look<Ability>(ref ability, "ability", false);
	}
}
