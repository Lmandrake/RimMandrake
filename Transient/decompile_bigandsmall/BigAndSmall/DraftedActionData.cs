using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using HarmonyLib;
using RimWorld;
using Verse;
using Verse.AI;

namespace BigAndSmall;

[StaticConstructorOnStartup]
public class DraftedActionData : IExposable
{
	protected delegate void VEFAbilityVerbPostfixDelegate(Pawn __instance, ref Verb __result, Thing target);

	private static readonly bool VEFLoaded = ModsConfig.IsActive("OskarPotocki.VanillaFactionsExpanded.Core");

	private static bool delegatesInitialized = false;

	protected static VEFAbilityVerbPostfixDelegate vefDelegate = null;

	private Pawn pawn;

	public string pawnID;

	public bool hunt;

	public bool takeCover;

	public bool meleeCharge = true;

	public bool fullAIControl;

	public List<AbilityDef> autocastAbilities = new List<AbilityDef>();

	public Pawn Pawn
	{
		get
		{
			if (pawn == null)
			{
				using (IEnumerator<Pawn> enumerator = (Find.Maps?.SelectMany((Map x) => x.mapPawns.AllPawns)).Where((Pawn x) => ((Thing)x).ThingID == pawnID).GetEnumerator())
				{
					if (enumerator.MoveNext())
					{
						Pawn current = enumerator.Current;
						pawn = current;
					}
				}
				if (pawn == null)
				{
					Log.Error("DraftedActionData could not find pawn with ID " + pawnID + ".");
				}
			}
			return pawn;
		}
	}

	public static Verb TryGetVEFAbilityVerb(Pawn pawn, Thing target)
	{
		if (VEFLoaded && !delegatesInitialized)
		{
			InitializeVEFDelegates();
		}
		if (vefDelegate != null)
		{
			Verb __result = null;
			vefDelegate(pawn, ref __result, target);
			return __result;
		}
		return null;
	}

	public static void InitializeVEFDelegates()
	{
		if (delegatesInitialized)
		{
			return;
		}
		try
		{
			MethodInfo method = AccessTools.Method(AccessTools.TypeByName("VEF.Abilities.VanillaExpandedFramework_Pawn_TryGetAttackVerb_Patch"), "Postfix", (Type[])null, (Type[])null);
			vefDelegate = (VEFAbilityVerbPostfixDelegate)Delegate.CreateDelegate(typeof(VEFAbilityVerbPostfixDelegate), method);
			delegatesInitialized = true;
		}
		catch (Exception arg)
		{
			Log.Error($"Big and Small failed to initialize VEF Ability Verb delegate: {arg}");
		}
	}

	public DraftedActionData(Pawn pawn)
	{
		this.pawn = pawn;
		pawnID = ((Thing)pawn).ThingID;
	}

	public DraftedActionData()
	{
	}

	private void RefreshDraft()
	{
		Pawn.jobs.EndCurrentJob((JobCondition)16, true, true);
	}

	public bool ToggleCoverMode(bool? force = null)
	{
		bool num;
		if (force.HasValue)
		{
			bool valueOrDefault = force == true;
			num = valueOrDefault;
		}
		else
		{
			num = !takeCover;
		}
		bool flag = num;
		takeCover = flag;
		RefreshDraft();
		return takeCover;
	}

	public bool ToggleMeleeCharge(bool? force = null)
	{
		bool num;
		if (force.HasValue)
		{
			bool valueOrDefault = force == true;
			num = valueOrDefault;
		}
		else
		{
			num = !meleeCharge;
		}
		bool flag = num;
		meleeCharge = flag;
		RefreshDraft();
		return meleeCharge;
	}

	public bool ToggleHuntMode()
	{
		hunt = !hunt;
		RefreshDraft();
		return hunt;
	}

	public bool ToggleFullAIControl(bool? force = null)
	{
		bool num;
		if (force.HasValue)
		{
			bool valueOrDefault = force == true;
			num = valueOrDefault;
		}
		else
		{
			num = !fullAIControl;
		}
		bool flag = num;
		fullAIControl = flag;
		RefreshDraft();
		return fullAIControl;
	}

	public bool AutoCastFor(AbilityDef def)
	{
		return autocastAbilities.Contains(def);
	}

	public void ToggleAutoForAll(bool? force = null)
	{
		bool num;
		if (force.HasValue)
		{
			bool valueOrDefault = force == true;
			num = valueOrDefault;
		}
		else
		{
			num = GenCollection.Empty<AbilityDef>(autocastAbilities);
		}
		if (num)
		{
			Pawn obj = Pawn;
			object obj2;
			if (obj == null)
			{
				obj2 = null;
			}
			else
			{
				Pawn_AbilityTracker abilities = obj.abilities;
				obj2 = ((abilities != null) ? abilities.AllAbilitiesForReading : null);
			}
			if (obj2 != null)
			{
				foreach (Ability item in Pawn.abilities.AllAbilitiesForReading)
				{
					if (item.def.aiCanUse || GenCollection.Any<AutoCombatExtension>(item.def.ExtensionsOnDef<AutoCombatExtension, AbilityDef>((List<Type>)null, (List<Type>)null, doSort: true), (Predicate<AutoCombatExtension>)((AutoCombatExtension x) => x.canMassToggle)))
					{
						autocastAbilities.Add(item.def);
					}
				}
				goto IL_00df;
			}
		}
		autocastAbilities.Clear();
		goto IL_00df;
		IL_00df:
		RefreshDraft();
	}

	public void ToggleAutoCastFor(AbilityDef def)
	{
		if (autocastAbilities.Contains(def))
		{
			autocastAbilities.Remove(def);
		}
		else
		{
			autocastAbilities.Add(def);
		}
		RefreshDraft();
	}

	public void ExposeData()
	{
		Scribe_Values.Look<string>(ref pawnID, "pawnID", (string)null, false);
		Scribe_Values.Look<bool>(ref hunt, "huntMode", false, false);
		Scribe_Values.Look<bool>(ref takeCover, "takeCoverMode", false, false);
		Scribe_Values.Look<bool>(ref meleeCharge, "meleeChargeMode", true, false);
		Scribe_Values.Look<bool>(ref fullAIControl, "fullAIControl", false, false);
		Scribe_Collections.Look<AbilityDef>(ref autocastAbilities, "autocastAbilities", (LookMode)4, Array.Empty<object>());
	}
}
