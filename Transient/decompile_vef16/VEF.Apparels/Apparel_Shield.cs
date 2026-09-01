using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI.Group;

namespace VEF.Apparels;

public class Apparel_Shield : Apparel
{
	private CompShield comp;

	private Graphic shieldGraphic;

	public CompShield CompShield
	{
		get
		{
			if (comp == null)
			{
				comp = ((ThingWithComps)this).GetComp<CompShield>();
			}
			return comp;
		}
	}

	public Graphic ShieldGraphic
	{
		get
		{
			if (shieldGraphic == null)
			{
				shieldGraphic = CompShield.Props.offHandGraphicData.GraphicColoredFor((Thing)(object)this);
			}
			return shieldGraphic;
		}
	}

	private bool CarryWeaponOpenly()
	{
		Pawn wearer = ((Apparel)this).Wearer;
		if (wearer.carryTracker != null && wearer.carryTracker.CarriedThing != null)
		{
			return false;
		}
		if (wearer.Drafted)
		{
			return true;
		}
		if (wearer.CurJob != null && wearer.CurJob.def.alwaysShowWeapon)
		{
			return true;
		}
		if (wearer.mindState.duty != null && wearer.mindState.duty.def.alwaysShowWeapon)
		{
			return true;
		}
		Lord lord = LordUtility.GetLord(wearer);
		if (lord != null && lord.LordJob != null && lord.LordJob.AlwaysShowWeapon)
		{
			return true;
		}
		return false;
	}

	private Vector3 GetAimingVector(Vector3 rootLoc, Rot4 rot4)
	{
		//IL_00e6: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e7: Unknown result type (might be due to invalid IL or missing references)
		//IL_0122: Unknown result type (might be due to invalid IL or missing references)
		//IL_0123: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f3: Unknown result type (might be due to invalid IL or missing references)
		//IL_0103: Unknown result type (might be due to invalid IL or missing references)
		//IL_0108: Unknown result type (might be due to invalid IL or missing references)
		//IL_010d: Unknown result type (might be due to invalid IL or missing references)
		//IL_011f: Unknown result type (might be due to invalid IL or missing references)
		//IL_01d8: Unknown result type (might be due to invalid IL or missing references)
		//IL_01de: Unknown result type (might be due to invalid IL or missing references)
		//IL_015e: Unknown result type (might be due to invalid IL or missing references)
		//IL_015f: Unknown result type (might be due to invalid IL or missing references)
		//IL_012f: Unknown result type (might be due to invalid IL or missing references)
		//IL_013f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0144: Unknown result type (might be due to invalid IL or missing references)
		//IL_0149: Unknown result type (might be due to invalid IL or missing references)
		//IL_015b: Unknown result type (might be due to invalid IL or missing references)
		//IL_019a: Unknown result type (might be due to invalid IL or missing references)
		//IL_019b: Unknown result type (might be due to invalid IL or missing references)
		//IL_016b: Unknown result type (might be due to invalid IL or missing references)
		//IL_017b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0180: Unknown result type (might be due to invalid IL or missing references)
		//IL_0185: Unknown result type (might be due to invalid IL or missing references)
		//IL_0197: Unknown result type (might be due to invalid IL or missing references)
		//IL_0064: Unknown result type (might be due to invalid IL or missing references)
		//IL_0069: Unknown result type (might be due to invalid IL or missing references)
		//IL_006d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0057: Unknown result type (might be due to invalid IL or missing references)
		//IL_01a7: Unknown result type (might be due to invalid IL or missing references)
		//IL_01b7: Unknown result type (might be due to invalid IL or missing references)
		//IL_01bc: Unknown result type (might be due to invalid IL or missing references)
		//IL_01c1: Unknown result type (might be due to invalid IL or missing references)
		//IL_01d3: Unknown result type (might be due to invalid IL or missing references)
		//IL_0072: Unknown result type (might be due to invalid IL or missing references)
		//IL_0079: Unknown result type (might be due to invalid IL or missing references)
		//IL_007b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0080: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a3: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b3: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b9: Unknown result type (might be due to invalid IL or missing references)
		//IL_00be: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c3: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d5: Unknown result type (might be due to invalid IL or missing references)
		//IL_0091: Unknown result type (might be due to invalid IL or missing references)
		//IL_0093: Unknown result type (might be due to invalid IL or missing references)
		//IL_0098: Unknown result type (might be due to invalid IL or missing references)
		Pawn wearer = ((Apparel)this).Wearer;
		if (wearer != null)
		{
			Stance curStance = wearer.stances.curStance;
			Stance_Busy val = (Stance_Busy)(object)((curStance is Stance_Busy) ? curStance : null);
			if (val != null && !val.neverAimWeapon && ((LocalTargetInfo)(ref val.focusTarg)).IsValid)
			{
				Vector3 val2;
				if (((LocalTargetInfo)(ref val.focusTarg)).HasThing)
				{
					val2 = ((LocalTargetInfo)(ref val.focusTarg)).Thing.DrawPos;
				}
				else
				{
					IntVec3 cell = ((LocalTargetInfo)(ref val.focusTarg)).Cell;
					val2 = ((IntVec3)(ref cell)).ToVector3Shifted();
				}
				Vector3 val3 = val2;
				float num = 0f;
				if (GenGeo.MagnitudeHorizontalSquared(val3 - ((Thing)wearer).DrawPos) > 0.001f)
				{
					num = Vector3Utility.AngleFlat(val3 - ((Thing)wearer).DrawPos);
				}
				Vector3 result = rootLoc + Vector3Utility.RotatedBy(new Vector3(0f, 0f, 0.4f), num);
				result.y += 0.036734693f;
				return result;
			}
		}
		if (wearer == null || CarryWeaponOpenly())
		{
			if (rot4 == Rot4.South)
			{
				Vector3 result2 = rootLoc + new Vector3(0f, 0f, -0.22f);
				result2.y += 0.036734693f;
				return result2;
			}
			if (rot4 == Rot4.North)
			{
				Vector3 result3 = rootLoc + new Vector3(0f, 0f, -0.11f);
				result3.y += 0f;
				return result3;
			}
			if (rot4 == Rot4.East)
			{
				Vector3 result4 = rootLoc + new Vector3(0.2f, 0f, -0.22f);
				result4.y += 0.036734693f;
				return result4;
			}
			if (rot4 == Rot4.West)
			{
				Vector3 result5 = rootLoc + new Vector3(-0.2f, 0f, -0.22f);
				result5.y += 0.036734693f;
				return result5;
			}
		}
		return default(Vector3);
	}

	public override void DrawWornExtras()
	{
		//IL_0044: Unknown result type (might be due to invalid IL or missing references)
		//IL_004a: Unknown result type (might be due to invalid IL or missing references)
		Pawn wearer = ((Apparel)this).Wearer;
		if (!wearer.Dead && ((Thing)wearer).Spawned && (wearer.CurJob == null || !wearer.CurJob.def.neverShowWeapon))
		{
			CompShield compShield = CompShield;
			if (compShield.UsableNow)
			{
				DrawShield(compShield, ((Thing)wearer).DrawPos, ((Thing)wearer).Rotation);
			}
		}
	}

	public void DrawShield(CompShield comp, Vector3 drawPos, Rot4 rot4)
	{
		//IL_000b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0013: Unknown result type (might be due to invalid IL or missing references)
		//IL_0014: Unknown result type (might be due to invalid IL or missing references)
		//IL_0015: Unknown result type (might be due to invalid IL or missing references)
		//IL_001b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0020: Unknown result type (might be due to invalid IL or missing references)
		//IL_0043: Unknown result type (might be due to invalid IL or missing references)
		//IL_0048: Unknown result type (might be due to invalid IL or missing references)
		//IL_004d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0054: Unknown result type (might be due to invalid IL or missing references)
		//IL_0062: Unknown result type (might be due to invalid IL or missing references)
		//IL_005d: Unknown result type (might be due to invalid IL or missing references)
		HoldOffset val = comp.Props.offHandHoldOffset.Pick(rot4);
		Vector3 val2 = GetAimingVector(drawPos, rot4) + val.offset + new Vector3(0f, val.behind ? (-5f / 128f) : (5f / 128f), 0f);
		ShieldGraphic.Draw(val2, val.flip ? ((Rot4)(ref rot4)).Opposite : rot4, (Thing)(object)this, 0f);
	}

	public override void ExposeData()
	{
		//IL_0006: Unknown result type (might be due to invalid IL or missing references)
		//IL_000c: Invalid comparison between Unknown and I4
		((Apparel)this).ExposeData();
		if ((int)Scribe.mode != 4 || ((Apparel)this).Wearer == null)
		{
			return;
		}
		CompEquippable val = ((ThingWithComps)this).GetComp<CompEquippable>();
		if (val == null)
		{
			return;
		}
		foreach (Verb allVerb in val.AllVerbs)
		{
			allVerb.caster = (Thing)(object)((Apparel)this).Wearer;
			allVerb.Reset();
		}
	}
}
