using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Runtime.CompilerServices;
using RimWorld;
using Verse;

namespace VEF.Abilities;

public class CompAbilitiesApparel : ThingComp
{
	private Pawn pawn;

	private List<Ability> abilitiesToTick = new List<Ability>();

	private List<Ability> abilitiesToTickInterval = new List<Ability>();

	private List<Ability> givenAbilities = new List<Ability>();

	public CompProperties_AbilitiesApparel Props => (CompProperties_AbilitiesApparel)(object)base.props;

	private Pawn Pawn
	{
		get
		{
			ThingWithComps parent = base.parent;
			ThingWithComps obj = ((parent is Apparel) ? parent : null);
			if (obj == null)
			{
				return null;
			}
			return ((Apparel)obj).Wearer;
		}
	}

	public List<Ability> GivenAbilities => givenAbilities;

	public override void Initialize(CompProperties props)
	{
		((ThingComp)this).Initialize(props);
		foreach (AbilityDef ability2 in Props.abilities)
		{
			Ability ability = (Ability)Activator.CreateInstance(ability2.abilityClass);
			ability.def = ability2;
			ability.holder = (Thing)(object)base.parent;
			ability.Init();
			givenAbilities.Add(ability);
			if (ability.def.needsTicking)
			{
				abilitiesToTick.Add(ability);
			}
			if (ability.def.needsTickingInterval)
			{
				abilitiesToTickInterval.Add(ability);
			}
		}
	}

	public override IEnumerable<Gizmo> CompGetWornGizmosExtra()
	{
		foreach (Gizmo item in _003C_003En__0())
		{
			yield return item;
		}
		if (Pawn == null)
		{
			yield break;
		}
		if (Pawn != pawn)
		{
			pawn = Pawn;
			foreach (Ability givenAbility in givenAbilities)
			{
				givenAbility.pawn = pawn;
				givenAbility.Init();
			}
		}
		foreach (Ability givenAbility2 in givenAbilities)
		{
			if (givenAbility2.ShowGizmoOnPawn())
			{
				yield return givenAbility2.GetGizmo();
			}
		}
	}

	public override void PostExposeData()
	{
		//IL_0030: Unknown result type (might be due to invalid IL or missing references)
		//IL_0036: Invalid comparison between Unknown and I4
		((ThingComp)this).PostExposeData();
		Scribe_Collections.Look<Ability>(ref givenAbilities, "givenAbilities", (LookMode)2, Array.Empty<object>());
		if (givenAbilities == null)
		{
			givenAbilities = new List<Ability>();
		}
		else
		{
			if ((int)Scribe.mode != 2)
			{
				return;
			}
			foreach (Ability givenAbility in givenAbilities)
			{
				givenAbility.holder = (Thing)(object)base.parent;
			}
			List<Ability> list = givenAbilities;
			if (list != null && GenCollection.Any<Ability>(list))
			{
				abilitiesToTick = givenAbilities.Where((Ability x) => x.def.needsTicking).ToList();
				abilitiesToTickInterval = givenAbilities.Where((Ability x) => x.def.needsTickingInterval).ToList();
			}
		}
	}

	public override void CompTick()
	{
		((ThingComp)this).CompTick();
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

	[CompilerGenerated]
	[DebuggerHidden]
	private IEnumerable<Gizmo> _003C_003En__0()
	{
		return ((ThingComp)this).CompGetWornGizmosExtra();
	}
}
