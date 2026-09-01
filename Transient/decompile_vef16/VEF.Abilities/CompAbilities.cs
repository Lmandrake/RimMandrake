using System;
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using VEF.AnimalBehaviours;
using VEF.Apparels;
using Verse;
using Verse.Sound;

namespace VEF.Abilities;

public class CompAbilities : CompShieldBubble, PawnGizmoProvider
{
	private List<Ability> learnedAbilities = new List<Ability>();

	private List<Ability> abilitiesToTick = new List<Ability>();

	private List<Ability> abilitiesToTickInterval = new List<Ability>();

	public Ability currentlyCasting;

	public GlobalTargetInfo[] currentlyCastingTargets;

	private float energyMax;

	private float breakTicks = -1f;

	public List<GlobalTargetInfo> tmpCurrentlyCastingTargets;

	private string currentShieldPath;

	private string shieldPath;

	private new Pawn Pawn => (Pawn)((ThingComp)this).parent;

	public override float EnergyMax => energyMax;

	protected override float EnergyGainPerTick => 0f;

	public List<Ability> LearnedAbilities => learnedAbilities;

	protected override Material BubbleMat
	{
		get
		{
			//IL_0041: Unknown result type (might be due to invalid IL or missing references)
			if (bubbleMat == null || currentShieldPath != shieldPath)
			{
				if (GenText.NullOrEmpty(shieldPath))
				{
					return base.BubbleMat;
				}
				bubbleMat = MaterialPool.MatFrom(shieldPath, ShaderDatabase.Transparent, base.Props.shieldColor);
				currentShieldPath = shieldPath;
			}
			return bubbleMat;
		}
	}

	public override void PostSpawnSetup(bool respawningAfterLoad)
	{
		((ThingComp)this).PostSpawnSetup(respawningAfterLoad);
		if (learnedAbilities == null)
		{
			learnedAbilities = new List<Ability>();
		}
		ticksToReset = int.MaxValue;
	}

	public override void PostPostMake()
	{
		base.PostPostMake();
		ticksToReset = int.MaxValue;
	}

	public void GiveAbility(AbilityDef abilityDef)
	{
		if (!GenCollection.Any<Ability>(learnedAbilities, (Predicate<Ability>)((Ability ab) => ab.def == abilityDef)))
		{
			Ability ability = (Ability)Activator.CreateInstance(abilityDef.abilityClass);
			ability.def = abilityDef;
			ability.pawn = Pawn;
			ability.holder = (Thing)(object)Pawn;
			ability.Init();
			learnedAbilities.Add(ability);
			if (ability.def.needsTicking)
			{
				abilitiesToTick.Add(ability);
			}
			if (ability.def.needsTickingInterval)
			{
				abilitiesToTickInterval.Add(ability);
			}
			learnedAbilities = (from ab in LearnedAbilities
				orderby ab.def.requiredHediff?.minimumLevel ?? 0
				group ab by ab.Hediff).SelectMany((IGrouping<Hediff_Abilities, Ability> grp) => grp).ToList();
		}
	}

	public bool HasAbility(AbilityDef abilityDef)
	{
		foreach (Ability learnedAbility in learnedAbilities)
		{
			if (learnedAbility.def == abilityDef)
			{
				return true;
			}
		}
		return false;
	}

	public override void CompTick()
	{
		//IL_0007: Unknown result type (might be due to invalid IL or missing references)
		base.CompTick();
		if ((int)base.ShieldState == 0)
		{
			breakTicks -= 1f;
			if (breakTicks <= 0f)
			{
				Break();
			}
		}
		int count = abilitiesToTick.Count;
		for (int i = 0; i < count; i++)
		{
			abilitiesToTick[i].Tick();
		}
	}

	public override void CompTickInterval(int delta)
	{
		((ThingComp)this).CompTickInterval(delta);
		for (int i = 0; i < abilitiesToTickInterval.Count; i++)
		{
			abilitiesToTickInterval[i].TickInterval(delta);
		}
	}

	public override string CompInspectStringExtra()
	{
		return string.Empty;
	}

	public override void PostExposeData()
	{
		//IL_00bc: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c2: Invalid comparison between Unknown and I4
		//IL_00fd: Unknown result type (might be due to invalid IL or missing references)
		//IL_0103: Invalid comparison between Unknown and I4
		base.PostExposeData();
		Scribe_Collections.Look<Ability>(ref learnedAbilities, "learnedAbilities", (LookMode)2, Array.Empty<object>());
		Scribe_References.Look<Ability>(ref currentlyCasting, "currentlyCasting", false);
		tmpCurrentlyCastingTargets = currentlyCastingTargets?.ToList() ?? new List<GlobalTargetInfo>();
		Scribe_Collections.Look<GlobalTargetInfo>(ref tmpCurrentlyCastingTargets, "currentlyCastingTargets", (LookMode)0, Array.Empty<object>());
		currentlyCastingTargets = tmpCurrentlyCastingTargets?.ToArray();
		Scribe_Values.Look<float>(ref energyMax, "energyMax", 0f, false);
		Scribe_Values.Look<string>(ref shieldPath, "shieldPath", (string)null, false);
		if (learnedAbilities == null)
		{
			learnedAbilities = new List<Ability>();
		}
		else if ((int)Scribe.mode == 2)
		{
			foreach (Ability learnedAbility in learnedAbilities)
			{
				learnedAbility.holder = (Thing)(object)((ThingComp)this).parent;
			}
		}
		else if ((int)Scribe.mode == 4)
		{
			foreach (Ability learnedAbility2 in learnedAbilities)
			{
				if (learnedAbility2.pawn == null)
				{
					ThingWithComps parent = ((ThingComp)this).parent;
					Pawn val = (Pawn)(object)((parent is Pawn) ? parent : null);
					if (val != null)
					{
						learnedAbility2.pawn = val;
					}
				}
			}
		}
		List<Ability> list = learnedAbilities;
		if (list != null && GenCollection.Any<Ability>(list))
		{
			abilitiesToTick = learnedAbilities.Where((Ability x) => x.def.needsTicking).ToList();
			abilitiesToTickInterval = learnedAbilities.Where((Ability x) => x.def.needsTickingInterval).ToList();
		}
	}

	protected override void Break()
	{
		base.Break();
		energyMax = 0f;
	}

	protected override void Reset()
	{
		ticksToReset = int.MaxValue;
	}

	public bool ReinitShield(float newEnergy, string shieldTexturePath, int duration)
	{
		//IL_0023: Unknown result type (might be due to invalid IL or missing references)
		//IL_0034: Unknown result type (might be due to invalid IL or missing references)
		//IL_0039: Unknown result type (might be due to invalid IL or missing references)
		//IL_0049: Unknown result type (might be due to invalid IL or missing references)
		if (newEnergy < energy)
		{
			return false;
		}
		if (((Thing)Pawn).Spawned)
		{
			SoundStarter.PlayOneShot(SoundDefOf.EnergyShield_Reset, SoundInfo.op_Implicit(new TargetInfo(((Thing)Pawn).Position, ((Thing)Pawn).Map, false)));
			FleckMaker.ThrowLightningGlow(GenThing.TrueCenter((Thing)(object)Pawn), ((Thing)Pawn).Map, 3f);
		}
		ticksToReset = -1;
		breakTicks = duration;
		energyMax = newEnergy;
		energy = newEnergy;
		shieldPath = shieldTexturePath;
		return true;
	}

	public IEnumerable<Gizmo> GetGizmos()
	{
		foreach (Ability learnedAbility in learnedAbilities)
		{
			if (learnedAbility.ShowGizmoOnPawn())
			{
				yield return learnedAbility.GetGizmo();
			}
		}
		List<Hediff_Abilities> list = new List<Hediff_Abilities>();
		Pawn.health.hediffSet.GetHediffs<Hediff_Abilities>(ref list, (Predicate<Hediff_Abilities>)null);
		foreach (Hediff_Abilities item in list)
		{
			foreach (Gizmo item2 in item.DrawGizmos())
			{
				yield return item2;
			}
		}
	}
}
