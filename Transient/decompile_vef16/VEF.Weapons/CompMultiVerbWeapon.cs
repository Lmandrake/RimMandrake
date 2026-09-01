using System;
using System.Collections.Generic;
using System.Text;
using JetBrains.Annotations;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;

namespace VEF.Weapons;

public class CompMultiVerbWeapon : ThingComp
{
	protected Verb activeVerb;

	protected CompProperties_MultiVerbWeapon.VerbData activeVerbData;

	protected CompEquippable equippable;

	public virtual Verb ActiveVerb
	{
		get
		{
			if (!VerbValid)
			{
				InitActiveVerb();
			}
			return activeVerb;
		}
		set
		{
			CompProperties_MultiVerbWeapon.VerbData verbData = GenCollection.FirstOrDefault<CompProperties_MultiVerbWeapon.VerbData>(Props.verbs, (Predicate<CompProperties_MultiVerbWeapon.VerbData>)((CompProperties_MultiVerbWeapon.VerbData x) => x.verbLabel == value.verbProps.untranslatedLabel));
			if (verbData != null)
			{
				activeVerb = value;
				activeVerbData = verbData;
			}
			else
			{
				Log.Error(string.Format("[VGE] {0} is trying to set an active verb for {1}, but its props has no data for such verb.", base.parent, "CompMultiVerbWeapon"));
			}
		}
	}

	public virtual CompProperties_MultiVerbWeapon.VerbData ActiveVerbData
	{
		get
		{
			if (!VerbValid)
			{
				InitActiveVerb();
			}
			return activeVerbData;
		}
	}

	protected virtual bool VerbValid
	{
		get
		{
			if (activeVerb != null && activeVerbData != null && equippable != null && equippable.AllVerbs.Contains(activeVerb))
			{
				return true;
			}
			activeVerb = null;
			activeVerbData = null;
			return false;
		}
	}

	public CompProperties_MultiVerbWeapon Props => (CompProperties_MultiVerbWeapon)(object)base.props;

	public override float GetStatOffset(StatDef stat)
	{
		if (ActiveVerbData == null)
		{
			return 0f;
		}
		return StatUtility.GetStatOffsetFromList(ActiveVerbData.statOffsets, stat);
	}

	public override float GetStatFactor(StatDef stat)
	{
		if (ActiveVerbData == null)
		{
			return 0f;
		}
		return StatUtility.GetStatFactorFromList(ActiveVerbData.statFactors, stat);
	}

	public override void GetStatsExplanation(StatDef stat, StringBuilder sb, string whitespace = "")
	{
		if (ActiveVerbData != null)
		{
			float statOffsetFromList = StatUtility.GetStatOffsetFromList(ActiveVerbData.statOffsets, stat);
			if (!Mathf.Approximately(statOffsetFromList, 0f))
			{
				sb.AppendLine(StatModifierText(statOffsetFromList, (ToStringNumberSense)3));
			}
			float statFactorFromList = StatUtility.GetStatFactorFromList(ActiveVerbData.statFactors, stat);
			if (!Mathf.Approximately(statFactorFromList, 1f))
			{
				sb.AppendLine(StatModifierText(statFactorFromList, (ToStringNumberSense)2));
			}
		}
		string StatModifierText(float value, ToStringNumberSense numberSense)
		{
			//IL_0044: Unknown result type (might be due to invalid IL or missing references)
			string text = (GenText.NullOrEmpty(ActiveVerbData.statExplanationLabelOverride) ? Props.statExplanationLabel : ActiveVerbData.statExplanationLabelOverride);
			return whitespace + text + ": " + stat.Worker.ValueToString(value, false, numberSense);
		}
	}

	public override void PostPostMake()
	{
		((ThingComp)this).PostPostMake();
		InitComps();
	}

	public override void PostExposeData()
	{
		//IL_0017: Unknown result type (might be due to invalid IL or missing references)
		//IL_001d: Invalid comparison between Unknown and I4
		//IL_0026: Unknown result type (might be due to invalid IL or missing references)
		//IL_002c: Invalid comparison between Unknown and I4
		((ThingComp)this).PostExposeData();
		Scribe_References.Look<Verb>(ref activeVerb, "activeVerb", false);
		if ((int)Scribe.mode == 2)
		{
			InitComps();
		}
		else if ((int)Scribe.mode == 4 && activeVerb != null)
		{
			activeVerbData = GenCollection.FirstOrDefault<CompProperties_MultiVerbWeapon.VerbData>(Props.verbs, (Predicate<CompProperties_MultiVerbWeapon.VerbData>)((CompProperties_MultiVerbWeapon.VerbData x) => x.verbLabel == activeVerb.verbProps.untranslatedLabel));
			if (activeVerbData == null)
			{
				activeVerb = null;
			}
		}
	}

	public virtual IEnumerable<Command> CompGetSwitchModeGizmo()
	{
		if (equippable == null)
		{
			yield break;
		}
		int i;
		switch (Props.switchMode)
		{
		case CompProperties_MultiVerbWeapon.SwitchMode.FloatMenuGizmo:
			if (!GenCollection.Any<Verb>(equippable.AllVerbs, (Predicate<Verb>)((Verb v) => v != ActiveVerb && GenCollection.Any<CompProperties_MultiVerbWeapon.VerbData>(Props.verbs, (Predicate<CompProperties_MultiVerbWeapon.VerbData>)((CompProperties_MultiVerbWeapon.VerbData d) => d.verbLabel == v.verbProps.untranslatedLabel)))))
			{
				yield break;
			}
			yield return (Command)new Command_Action
			{
				defaultLabel = Props.gizmoLabel,
				defaultDesc = Props.gizmoDescription,
				icon = (Texture)(object)Props.gizmoIcon,
				action = delegate
				{
					//IL_00f0: Unknown result type (might be due to invalid IL or missing references)
					//IL_00fa: Expected O, but got Unknown
					//IL_00a0: Unknown result type (might be due to invalid IL or missing references)
					//IL_00b3: Unknown result type (might be due to invalid IL or missing references)
					//IL_00bd: Expected O, but got Unknown
					List<FloatMenuOption> list = new List<FloatMenuOption>();
					for (int j = 0; j < Props.verbs.Count; j++)
					{
						CompProperties_MultiVerbWeapon.VerbData verbData2 = Props.verbs[j];
						if (verbData2 != activeVerbData)
						{
							Verb verb2 = GenCollection.FirstOrDefault<Verb>(equippable.AllVerbs, (Predicate<Verb>)((Verb x) => x.verbProps.untranslatedLabel == verbData2.verbLabel));
							if (verb2 != null)
							{
								list.Add(new FloatMenuOption(verbData2.gizmoLabelOverride ?? verb2.verbProps.label, (Action)delegate
								{
									ActiveVerb = verb2;
								}, verbData2.gizmoIconOverride, Color.white, (MenuOptionPriority)4, (Action<Rect>)null, (Thing)null, 0f, (Func<Rect, bool>)null, (WorldObject)null, true, 0, (HorizontalJustification)0, false));
							}
						}
					}
					if (list.Count == 0)
					{
						Log.Error("[VGE] CompMultiVerbWeapon doesn't have any supported verbs");
					}
					else
					{
						Find.WindowStack.Add((Window)new FloatMenu(list));
					}
				}
			};
			yield break;
		case CompProperties_MultiVerbWeapon.SwitchMode.DoubleVerbToggle:
		case CompProperties_MultiVerbWeapon.SwitchMode.DoubleVerbToggleMirrored:
		{
			Verb val = ((ActiveVerbData.verbLabel == Props.defaultVerbLabel) ? ActiveVerb : GenCollection.FirstOrDefault<Verb>(equippable.AllVerbs, (Predicate<Verb>)((Verb v) => v.verbProps.untranslatedLabel == Props.defaultVerbLabel)));
			Verb val2 = ((ActiveVerbData.verbLabel != Props.defaultVerbLabel) ? ActiveVerb : GenCollection.FirstOrDefault<Verb>(equippable.AllVerbs, (Predicate<Verb>)((Verb v) => v.verbProps.untranslatedLabel != Props.defaultVerbLabel && GenCollection.Any<CompProperties_MultiVerbWeapon.VerbData>(Props.verbs, (Predicate<CompProperties_MultiVerbWeapon.VerbData>)((CompProperties_MultiVerbWeapon.VerbData d) => d.verbLabel == v.verbProps.untranslatedLabel)))));
			if (val == null || val2 == null)
			{
				yield break;
			}
			Verb verbToSwitchTo = ((ActiveVerb == val) ? val2 : val);
			CompProperties_MultiVerbWeapon.VerbData verbData = GenCollection.FirstOrDefault<CompProperties_MultiVerbWeapon.VerbData>(Props.verbs, (Predicate<CompProperties_MultiVerbWeapon.VerbData>)((CompProperties_MultiVerbWeapon.VerbData d) => d.verbLabel == verbToSwitchTo.verbProps.untranslatedLabel));
			if (verbData != null)
			{
				yield return (Command)new Command_Toggle
				{
					defaultLabel = (verbData.gizmoLabelOverride ?? Props.gizmoLabel),
					defaultDesc = (verbData.gizmoDescriptionOverride ?? Props.gizmoDescription),
					icon = (Texture)(object)(ActiveVerbData.gizmoIconOverride ?? Props.gizmoIcon),
					toggleAction = delegate
					{
						ActiveVerb = verbToSwitchTo;
					},
					isActive = () => (Props.switchMode != 0) ? (ActiveVerb.verbProps.untranslatedLabel != Props.defaultVerbLabel) : (ActiveVerb.verbProps.untranslatedLabel == Props.defaultVerbLabel)
				};
			}
			yield break;
		}
		case CompProperties_MultiVerbWeapon.SwitchMode.MultiSwitchGizmo:
			for (i = 0; i < Props.verbs.Count; i++)
			{
				CompProperties_MultiVerbWeapon.VerbData data = Props.verbs[i];
				if (data == ActiveVerbData)
				{
					continue;
				}
				Verb verb = GenCollection.FirstOrDefault<Verb>(equippable.AllVerbs, (Predicate<Verb>)((Verb v) => v.verbProps.untranslatedLabel == data.verbLabel));
				if (verb != null)
				{
					yield return (Command)new Command_Action
					{
						defaultLabel = (data.gizmoLabelOverride ?? Props.gizmoLabel),
						defaultDesc = (data.gizmoDescriptionOverride ?? Props.gizmoDescription),
						icon = (Texture)(object)(data.gizmoIconOverride ?? Props.gizmoIcon),
						action = delegate
						{
							ActiveVerb = verb;
						}
					};
				}
			}
			yield break;
		}
		i = Props.verbs.IndexOf(ActiveVerbData);
		for (int k = 1; k < Props.verbs.Count; k++)
		{
			CompProperties_MultiVerbWeapon.VerbData data2 = Props.verbs[(i + k) % Props.verbs.Count];
			Verb verb3 = GenCollection.FirstOrDefault<Verb>(equippable.AllVerbs, (Predicate<Verb>)((Verb v) => v.verbProps.untranslatedLabel == data2.verbLabel));
			if (verb3 != null)
			{
				yield return (Command)new Command_Action
				{
					defaultLabel = (data2.gizmoLabelOverride ?? Props.gizmoLabel),
					defaultDesc = (data2.gizmoDescriptionOverride ?? Props.gizmoDescription),
					icon = (Texture)(object)(data2.gizmoIconOverride ?? Props.gizmoIcon),
					action = delegate
					{
						ActiveVerb = verb3;
					}
				};
			}
		}
	}

	protected virtual void InitActiveVerb()
	{
		if (equippable == null)
		{
			return;
		}
		if (!GenText.NullOrEmpty(Props.defaultVerbLabel))
		{
			CompProperties_MultiVerbWeapon.VerbData verbData = GenCollection.FirstOrDefault<CompProperties_MultiVerbWeapon.VerbData>(Props.verbs, (Predicate<CompProperties_MultiVerbWeapon.VerbData>)((CompProperties_MultiVerbWeapon.VerbData x) => x.verbLabel == Props.defaultVerbLabel));
			if (verbData != null)
			{
				activeVerb = GenCollection.FirstOrDefault<Verb>(equippable.AllVerbs, (Predicate<Verb>)((Verb x) => x.verbProps.untranslatedLabel == Props.defaultVerbLabel));
				if (activeVerb != null)
				{
					activeVerbData = verbData;
					return;
				}
			}
		}
		activeVerb = GenCollection.FirstOrDefault<Verb>(equippable.AllVerbs, (Predicate<Verb>)delegate(Verb v)
		{
			CompProperties_MultiVerbWeapon.VerbData verbData2 = GenCollection.FirstOrDefault<CompProperties_MultiVerbWeapon.VerbData>(Props.verbs, (Predicate<CompProperties_MultiVerbWeapon.VerbData>)((CompProperties_MultiVerbWeapon.VerbData d) => d.verbLabel == v.verbProps.untranslatedLabel));
			if (verbData2 == null)
			{
				return false;
			}
			activeVerbData = verbData2;
			return true;
		});
	}

	private void InitComps()
	{
		equippable = base.parent.GetComp<CompEquippable>();
	}

	[UsedImplicitly]
	private static bool HasMultiVerbComp(ThingWithComps thing)
	{
		return thing.GetComp<CompMultiVerbWeapon>() != null;
	}
}
