using UnityEngine;
using Verse;

namespace VEF.Abilities;

[StaticConstructorOnStartup]
public class Command_Ability : Command_Action
{
	public static readonly Texture2D CooldownTex = SolidColorMaterials.NewSolidColorTexture(new Color(1f, 1f, 1f, 0.1f));

	public static readonly Texture2D AutoCastTex = ContentFinder<Texture2D>.Get("UI/CheckAuto", true);

	public Pawn pawn;

	public Ability ability;

	public Command_Ability(Pawn pawn, Ability ability)
	{
		//IL_001b: Unknown result type (might be due to invalid IL or missing references)
		//IL_005a: Unknown result type (might be due to invalid IL or missing references)
		this.pawn = pawn;
		this.ability = ability;
		((Command)this).defaultLabel = TaggedString.op_Implicit(((Def)ability.def).LabelCap);
		((Command)this).defaultDesc = ability.GetDescriptionForPawn();
		((Command)this).icon = (Texture)(object)ability.def.icon;
		((Gizmo)this).disabled = !ability.IsEnabledForPawn(out var reason);
		((Gizmo)this).disabledReason = ColoredText.Colorize(reason, ColorLibrary.RedReadable);
		base.action = ability.DoAction;
		((Gizmo)this).Order = 10f + (float)(int)(((Def)(ability.def.requiredHediff?.hediffDef?)).index).GetValueOrDefault() + (float)(ability.def.requiredHediff?.minimumLevel ?? 0);
		((Command)this).shrinkable = true;
	}

	public override void GizmoUpdateOnMouseover()
	{
		((Command_Action)this).GizmoUpdateOnMouseover();
		ability.GizmoUpdateOnMouseover();
	}

	public override bool GroupsWith(Gizmo other)
	{
		if (other is Command_Ability command_Ability)
		{
			return command_Ability.ability.def == ability.def;
		}
		return false;
	}

	protected override GizmoResult GizmoOnGUIInt(Rect butRect, GizmoRenderParms parms)
	{
		//IL_0000: Unknown result type (might be due to invalid IL or missing references)
		//IL_0034: Unknown result type (might be due to invalid IL or missing references)
		//IL_0035: Unknown result type (might be due to invalid IL or missing references)
		//IL_0036: Unknown result type (might be due to invalid IL or missing references)
		//IL_0019: Unknown result type (might be due to invalid IL or missing references)
		//IL_0048: Unknown result type (might be due to invalid IL or missing references)
		//IL_010c: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ca: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d4: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ef: Unknown result type (might be due to invalid IL or missing references)
		//IL_0077: Unknown result type (might be due to invalid IL or missing references)
		//IL_014c: Unknown result type (might be due to invalid IL or missing references)
		if (parms.shrunk)
		{
			((Command)this).defaultDesc = $"{((Def)ability.def).LabelCap}\n\n{((Command)this).defaultDesc}";
		}
		GizmoResult result = ((Command)this).GizmoOnGUIInt(butRect, parms);
		if (ability.AutoCast)
		{
			float num = (parms.shrunk ? 12f : 24f);
			GUI.DrawTexture(new Rect(((Rect)(ref butRect)).x + ((Rect)(ref butRect)).width - num, ((Rect)(ref butRect)).y, num, num), (Texture)(object)AutoCastTex);
		}
		if (((Gizmo)this).disabled && ability.cooldown > Find.TickManager.TicksGame)
		{
			float num2 = (float)(ability.cooldown - Find.TickManager.TicksGame) / (float)ability.GetCooldownForPawn();
			GUI.DrawTexture(GenUI.RightPartPixels(butRect, ((Rect)(ref butRect)).width * num2), (Texture)(object)CooldownTex);
			Text.Font = (GameFont)0;
			Text.Anchor = (TextAnchor)1;
			Widgets.Label(butRect, GenText.ToStringPercent(1f - num2, "F0"));
			Text.Anchor = (TextAnchor)0;
		}
		if (Mouse.IsOver(butRect) && ability.def.targetModes[0] == AbilityTargetingMode.Self && ability.def.targetCount == 1)
		{
			ability.OnGUI(LocalTargetInfo.op_Implicit((Thing)(object)pawn));
		}
		return result;
	}
}
