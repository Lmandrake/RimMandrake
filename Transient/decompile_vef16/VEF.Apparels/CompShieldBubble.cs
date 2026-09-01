using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using VEF.Abilities;
using VEF.Weapons;
using Verse;
using Verse.Sound;

namespace VEF.Apparels;

[StaticConstructorOnStartup]
public class CompShieldBubble : ThingComp
{
	protected float energy;

	protected int ticksToReset = -1;

	private int lastKeepDisplayTick = -9999;

	private Vector3 impactAngleVect;

	private int lastAbsorbDamageTick = -9999;

	private const float MinDrawSize = 1.2f;

	private const float MaxDrawSize = 1.55f;

	private const float MaxDamagedJitterDist = 0.05f;

	private const int JitterDurationTicks = 8;

	private int StartingTicksToReset = 3200;

	private float EnergyOnReset = 0.2f;

	public float cachedMaxShield;

	public float cachedMaxRecharge;

	protected Material bubbleMat;

	private bool firstTime = true;

	public static HashSet<JobDef> combatJobs = new HashSet<JobDef>
	{
		JobDefOf.AttackMelee,
		JobDefOf.AttackStatic,
		JobDefOf.FleeAndCower,
		JobDefOf.ManTurret,
		JobDefOf.Wait_Combat,
		JobDefOf.Flee
	};

	public float CachedMaxShield
	{
		get
		{
			if (cachedMaxShield == 0f)
			{
				cachedMaxShield = StatExtension.GetStatValue((Thing)(object)base.parent, StatDefOf.EnergyShieldEnergyMax, true, -1);
			}
			return cachedMaxShield;
		}
	}

	public float CachedMaxRecharge
	{
		get
		{
			if (cachedMaxRecharge == 0f)
			{
				cachedMaxRecharge = StatExtension.GetStatValue((Thing)(object)base.parent, StatDefOf.EnergyShieldRechargeRate, true, -1);
			}
			return cachedMaxRecharge;
		}
	}

	public Pawn Pawn
	{
		get
		{
			ThingWithComps parent = base.parent;
			Pawn val = (Pawn)(object)((parent is Pawn) ? parent : null);
			if (val != null)
			{
				return val;
			}
			ThingWithComps parent2 = base.parent;
			Apparel val2 = (Apparel)(object)((parent2 is Apparel) ? parent2 : null);
			if (val2 != null && val2.Wearer != null)
			{
				return val2.Wearer;
			}
			return null;
		}
	}

	protected virtual Material BubbleMat
	{
		get
		{
			//IL_0053: Unknown result type (might be due to invalid IL or missing references)
			//IL_002b: Unknown result type (might be due to invalid IL or missing references)
			if (bubbleMat == null)
			{
				if (GenText.NullOrEmpty(Props.shieldTexPath))
				{
					bubbleMat = MaterialPool.MatFrom("Other/ShieldBubble", ShaderDatabase.Transparent, Props.shieldColor);
				}
				else
				{
					bubbleMat = MaterialPool.MatFrom(Props.shieldTexPath, ShaderDatabase.Transparent, Props.shieldColor);
				}
			}
			return bubbleMat;
		}
	}

	public CompProperties_ShieldBubble Props => (CompProperties_ShieldBubble)(object)base.props;

	public virtual float EnergyMax
	{
		get
		{
			float num = ((Props.EnergyShieldEnergyMax != 0f) ? Props.EnergyShieldEnergyMax : (CachedMaxShield * 100f));
			if (Pawn != null)
			{
				num *= StatExtension.GetStatValue((Thing)(object)Pawn, VEFDefOf.VEF_EnergyShieldEnergyMaxFactor, true, 120);
				num += StatExtension.GetStatValue((Thing)(object)Pawn, VEFDefOf.VEF_EnergyShieldEnergyMaxOffset, true, 120);
			}
			return num;
		}
	}

	protected virtual float EnergyGainPerTick => ((Props.EnergyShieldRechargeRate != 0f) ? Props.EnergyShieldRechargeRate : CachedMaxRecharge) / 60f;

	protected virtual float EnergyLossPerDamage => Props.EnergyLossPerDamage;

	public float Energy
	{
		get
		{
			return energy;
		}
		set
		{
			energy = Mathf.Clamp(value, 0f, EnergyMax);
		}
	}

	public ShieldState ShieldState
	{
		get
		{
			if (ticksToReset <= 0)
			{
				return (ShieldState)0;
			}
			return (ShieldState)1;
		}
	}

	public bool IsApparel => base.parent is Apparel;

	private bool IsBuiltIn => !IsApparel;

	public override void PostExposeData()
	{
		((ThingComp)this).PostExposeData();
		firstTime = false;
		Scribe_Values.Look<bool>(ref firstTime, "firstTime", false, false);
		Scribe_Values.Look<float>(ref energy, "energy", 0f, false);
		Scribe_Values.Look<int>(ref ticksToReset, "ticksToReset", -1, false);
		Scribe_Values.Look<int>(ref lastKeepDisplayTick, "lastKeepDisplayTick", 0, false);
	}

	public override void CompTick()
	{
		//IL_0042: Unknown result type (might be due to invalid IL or missing references)
		//IL_0048: Invalid comparison between Unknown and I4
		//IL_006a: Unknown result type (might be due to invalid IL or missing references)
		((ThingComp)this).CompTick();
		if (Pawn == null)
		{
			energy = 0f;
		}
		else if (firstTime && ((Thing)Pawn).Faction != Faction.OfPlayer)
		{
			energy = EnergyMax;
		}
		if ((int)ShieldState == 1)
		{
			ticksToReset--;
			if (ticksToReset <= 0)
			{
				Reset();
			}
		}
		else if ((int)ShieldState == 0)
		{
			energy += EnergyGainPerTick * EnergyMax;
			if (energy > EnergyMax)
			{
				energy = EnergyMax;
			}
		}
		firstTime = false;
	}

	private bool InCombat(Pawn pawn)
	{
		if (combatJobs.Contains(pawn.CurJobDef))
		{
			return true;
		}
		if (pawn.mindState?.duty?.def.alwaysShowWeapon == true)
		{
			return true;
		}
		JobDef curJobDef = pawn.CurJobDef;
		if (curJobDef != null && curJobDef.alwaysShowWeapon)
		{
			return true;
		}
		return false;
	}

	public override void CompDrawWornExtras()
	{
		((ThingComp)this).CompDrawWornExtras();
		if (IsApparel)
		{
			Draw();
		}
	}

	public override void PostDraw()
	{
		((ThingComp)this).PostDraw();
		if (IsBuiltIn)
		{
			Draw();
		}
	}

	public void Draw()
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c8: Unknown result type (might be due to invalid IL or missing references)
		//IL_00cd: Unknown result type (might be due to invalid IL or missing references)
		//IL_0107: Unknown result type (might be due to invalid IL or missing references)
		//IL_0109: Unknown result type (might be due to invalid IL or missing references)
		//IL_0110: Unknown result type (might be due to invalid IL or missing references)
		//IL_0115: Unknown result type (might be due to invalid IL or missing references)
		//IL_011a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0149: Unknown result type (might be due to invalid IL or missing references)
		//IL_0151: Unknown result type (might be due to invalid IL or missing references)
		//IL_0154: Unknown result type (might be due to invalid IL or missing references)
		//IL_0159: Unknown result type (might be due to invalid IL or missing references)
		//IL_015e: Unknown result type (might be due to invalid IL or missing references)
		//IL_016a: Unknown result type (might be due to invalid IL or missing references)
		if ((int)ShieldState != 0 || !(Energy > 0f))
		{
			return;
		}
		Pawn pawn = Pawn;
		float num = Mathf.Lerp(Props.minShieldSize, Props.maxShieldSize, energy);
		CompProperties_ShieldBubble props = Props;
		if (pawn != null && (props.showAlways || (props.showWhenDrafted && pawn.Drafted) || (props.showOnHostiles && ((Thing)pawn).Faction != Faction.OfPlayer && GenHostility.HostileTo((Thing)(object)pawn, Faction.OfPlayer)) || (props.showOnNeutralInCombat && ((Thing)pawn).Faction != Faction.OfPlayer && !GenHostility.HostileTo((Thing)(object)pawn, Faction.OfPlayer) && InCombat(pawn))))
		{
			Vector3 val = pawn.Drawer.DrawPos;
			val.y = Altitudes.AltitudeFor((AltitudeLayer)28);
			int num2 = Find.TickManager.TicksGame - lastAbsorbDamageTick;
			if (num2 < 8)
			{
				float num3 = (float)(8 - num2) / 8f * 0.05f;
				val += impactAngleVect * num3;
				num -= num3;
			}
			float num4 = ((!props.disableRotation) ? Rand.Range(0, 360) : 0);
			Vector3 val2 = default(Vector3);
			((Vector3)(ref val2))._002Ector(num, 1f, num);
			Matrix4x4 val3 = default(Matrix4x4);
			((Matrix4x4)(ref val3)).SetTRS(val, Quaternion.AngleAxis(num4, Vector3.up), val2);
			Graphics.DrawMesh(MeshPool.plane10, val3, BubbleMat, 0);
		}
	}

	public override void PostPreApplyDamage(ref DamageInfo dinfo, out bool absorbed)
	{
		//IL_000a: Unknown result type (might be due to invalid IL or missing references)
		((ThingComp)this).PostPreApplyDamage(ref dinfo, ref absorbed);
		AbsorbingDamage(dinfo, out absorbed);
	}

	public bool AbsorbingDamage(DamageInfo dinfo, out bool absorbed)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		//IL_00db: Unknown result type (might be due to invalid IL or missing references)
		if ((int)ShieldState != 0)
		{
			absorbed = false;
		}
		else if (((DamageInfo)(ref dinfo)).Def == DamageDefOf.EMP)
		{
			energy = 0f;
			Break();
			absorbed = false;
		}
		else
		{
			if (((DamageInfo)(ref dinfo)).Def.ignoreShields)
			{
				goto IL_00e6;
			}
			if (!Props.blockRangedAttack || (!((DamageInfo)(ref dinfo)).Def.isRanged && !((DamageInfo)(ref dinfo)).Def.isExplosive))
			{
				if (!Props.blockMeleeAttack)
				{
					goto IL_00e6;
				}
				if (((DamageInfo)(ref dinfo)).Weapon != null || !(((DamageInfo)(ref dinfo)).Instigator is Pawn))
				{
					ThingDef weapon = ((DamageInfo)(ref dinfo)).Weapon;
					if (weapon == null || !weapon.IsMeleeWeapon)
					{
						goto IL_00e6;
					}
				}
			}
			energy -= ((DamageInfo)(ref dinfo)).Amount * EnergyLossPerDamage;
			if (energy < 0f)
			{
				Break();
			}
			else
			{
				AbsorbedDamage(dinfo);
			}
			absorbed = true;
		}
		goto IL_00e9;
		IL_00e6:
		absorbed = false;
		goto IL_00e9;
		IL_00e9:
		TeslaProjectile.wasDeflected = absorbed;
		return absorbed;
	}

	public void KeepDisplaying()
	{
		lastKeepDisplayTick = Find.TickManager.TicksGame;
	}

	private void AbsorbedDamage(DamageInfo dinfo)
	{
		//IL_004b: Unknown result type (might be due to invalid IL or missing references)
		//IL_005c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0061: Unknown result type (might be due to invalid IL or missing references)
		//IL_001e: Unknown result type (might be due to invalid IL or missing references)
		//IL_002f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0034: Unknown result type (might be due to invalid IL or missing references)
		//IL_0073: Unknown result type (might be due to invalid IL or missing references)
		//IL_0078: Unknown result type (might be due to invalid IL or missing references)
		//IL_0083: Unknown result type (might be due to invalid IL or missing references)
		//IL_0089: Unknown result type (might be due to invalid IL or missing references)
		//IL_0093: Unknown result type (might be due to invalid IL or missing references)
		//IL_009d: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a2: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a7: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c6: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e4: Unknown result type (might be due to invalid IL or missing references)
		if (Props.absorbDamageSound != null)
		{
			SoundStarter.PlayOneShot(Props.absorbDamageSound, SoundInfo.op_Implicit(new TargetInfo(((Thing)Pawn).Position, ((Thing)Pawn).Map, false)));
		}
		else
		{
			SoundStarter.PlayOneShot(SoundDefOf.EnergyShield_AbsorbDamage, SoundInfo.op_Implicit(new TargetInfo(((Thing)Pawn).Position, ((Thing)Pawn).Map, false)));
		}
		impactAngleVect = Vector3Utility.HorizontalVectorFromAngle(((DamageInfo)(ref dinfo)).Angle);
		Vector3 val = GenThing.TrueCenter((Thing)(object)Pawn) + Vector3Utility.RotatedBy(impactAngleVect, 180f) * 0.5f;
		float num = Mathf.Min(10f, 2f + ((DamageInfo)(ref dinfo)).Amount / 10f);
		FleckMaker.Static(val, ((Thing)Pawn).Map, FleckDefOf.ExplosionFlash, num);
		int num2 = (int)num;
		for (int i = 0; i < num2; i++)
		{
			FleckMaker.ThrowDustPuff(val, ((Thing)Pawn).Map, Rand.Range(0.8f, 1.2f));
		}
		lastAbsorbDamageTick = Find.TickManager.TicksGame;
		KeepDisplaying();
	}

	protected virtual void Break()
	{
		//IL_001d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0082: Unknown result type (might be due to invalid IL or missing references)
		//IL_0093: Unknown result type (might be due to invalid IL or missing references)
		//IL_0098: Unknown result type (might be due to invalid IL or missing references)
		//IL_0055: Unknown result type (might be due to invalid IL or missing references)
		//IL_0066: Unknown result type (might be due to invalid IL or missing references)
		//IL_006b: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a8: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d1: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e2: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f6: Unknown result type (might be due to invalid IL or missing references)
		//IL_00fb: Unknown result type (might be due to invalid IL or missing references)
		Pawn pawn = Pawn;
		if (((pawn != null) ? ((Thing)pawn).Map : null) != null && GenGrid.InBounds(((Thing)Pawn).Position, ((Thing)Pawn).Map))
		{
			if (Props.brokenSound != null)
			{
				SoundStarter.PlayOneShot(Props.brokenSound, SoundInfo.op_Implicit(new TargetInfo(((Thing)Pawn).Position, ((Thing)Pawn).Map, false)));
			}
			else
			{
				SoundStarter.PlayOneShot(VEFDefOf.EnergyShield_Broken, SoundInfo.op_Implicit(new TargetInfo(((Thing)Pawn).Position, ((Thing)Pawn).Map, false)));
			}
			FleckMaker.Static(GenThing.TrueCenter((Thing)(object)Pawn), ((Thing)Pawn).Map, FleckDefOf.ExplosionFlash, 12f);
			for (int i = 0; i < 6; i++)
			{
				FleckMaker.ThrowDustPuff(GenThing.TrueCenter((Thing)(object)Pawn) + Vector3Utility.HorizontalVectorFromAngle((float)Rand.Range(0, 360)) * Rand.Range(0.3f, 0.6f), ((Thing)Pawn).Map, Rand.Range(0.8f, 1.2f));
			}
		}
		energy = 0f;
		ticksToReset = StartingTicksToReset;
	}

	protected virtual void Reset()
	{
		//IL_005b: Unknown result type (might be due to invalid IL or missing references)
		//IL_006c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0071: Unknown result type (might be due to invalid IL or missing references)
		//IL_002e: Unknown result type (might be due to invalid IL or missing references)
		//IL_003f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0044: Unknown result type (might be due to invalid IL or missing references)
		//IL_0081: Unknown result type (might be due to invalid IL or missing references)
		if (((Thing)Pawn).Spawned)
		{
			if (Props.resetSound != null)
			{
				SoundStarter.PlayOneShot(Props.resetSound, SoundInfo.op_Implicit(new TargetInfo(((Thing)Pawn).Position, ((Thing)Pawn).Map, false)));
			}
			else
			{
				SoundStarter.PlayOneShot(SoundDefOf.EnergyShield_Reset, SoundInfo.op_Implicit(new TargetInfo(((Thing)Pawn).Position, ((Thing)Pawn).Map, false)));
			}
			FleckMaker.ThrowLightningGlow(GenThing.TrueCenter((Thing)(object)Pawn), ((Thing)Pawn).Map, 3f);
		}
		ticksToReset = -1;
		energy = EnergyOnReset;
	}

	public override void PostPostMake()
	{
		((ThingComp)this).PostPostMake();
		if (Props.chargeFullyWhenMade)
		{
			Energy = EnergyMax;
		}
		else if (Props.initialChargePct > 0f)
		{
			Energy = EnergyMax * Props.initialChargePct;
		}
	}

	public override IEnumerable<Gizmo> CompGetGizmosExtra()
	{
		if (!typeof(CompAbilities).IsAssignableFrom(((CompProperties)Props).compClass) && Pawn != null && Find.Selector.SingleSelectedThing == Pawn && ((Thing)Pawn).Faction == Faction.OfPlayer)
		{
			Gizmo_EnergyCompShieldStatus gizmo_EnergyCompShieldStatus = new Gizmo_EnergyCompShieldStatus();
			gizmo_EnergyCompShieldStatus.shield = this;
			yield return (Gizmo)(object)gizmo_EnergyCompShieldStatus;
		}
	}

	public override IEnumerable<Gizmo> CompGetWornGizmosExtra()
	{
		if (Pawn == null || Find.Selector.SingleSelectedThing != Pawn || !Pawn.IsColonistPlayerControlled)
		{
			yield break;
		}
		Gizmo_EnergyCompShieldStatus gizmo_EnergyCompShieldStatus = new Gizmo_EnergyCompShieldStatus();
		gizmo_EnergyCompShieldStatus.shield = this;
		yield return (Gizmo)(object)gizmo_EnergyCompShieldStatus;
		if (!DebugSettings.ShowDevGizmos)
		{
			yield break;
		}
		Command_Action val = new Command_Action();
		((Command)val).defaultLabel = "DEV: Break";
		val.action = Break;
		yield return (Gizmo)(object)val;
		if (ticksToReset > 0)
		{
			Command_Action val2 = new Command_Action();
			((Command)val2).defaultLabel = "DEV: Clear reset";
			val2.action = delegate
			{
				ticksToReset = 0;
			};
			yield return (Gizmo)(object)val2;
		}
	}

	public override bool CompAllowVerbCast(Verb verb)
	{
		if (verb.IsMeleeAttack && Props.dontAllowMeleeAttack)
		{
			return false;
		}
		if (!verb.IsMeleeAttack && Props.dontAllowRangedAttack)
		{
			return false;
		}
		return true;
	}
}
