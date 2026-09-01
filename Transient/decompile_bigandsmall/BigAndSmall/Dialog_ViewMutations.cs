using RimWorld;
using UnityEngine;
using Verse;

namespace BigAndSmall;

public class Dialog_ViewMutations : Window
{
	private const float WIDTH = 763f;

	private const float HEADER_HEIGHT = 30f;

	private Pawn target;

	private Vector2 scrollPosition;

	public override Vector2 InitialSize => new Vector2(736f, (float)UI.screenHeight * 0.7f);

	public Dialog_ViewMutations(Pawn target)
		: base((IWindowDrawing)null)
	{
		this.target = target;
		base.forcePause = false;
		base.closeOnAccept = false;
		base.closeOnCancel = false;
		base.doCloseX = true;
		base.draggable = true;
		base.resizeable = true;
		base.absorbInputAroundWindow = false;
		base.preventCameraMotion = false;
		DrawGeneSection.pCache = HumanoidPawnScaler.GetCache(target);
	}

	public override void WindowOnGUI()
	{
		if (base.resizer != null)
		{
			base.resizer.minWindowSize.x = 763f;
		}
		WindowResizer resizer = base.resizer;
		if (resizer != null && !resizer.isResizing && ((Rect)(ref base.windowRect)).width != 763f)
		{
			((Rect)(ref base.windowRect)).width = 763f;
		}
		((Window)this).WindowOnGUI();
	}

	public override void ExtraOnGUI()
	{
		((Window)this).ExtraOnGUI();
	}

	public override void DoWindowContents(Rect inRect)
	{
		//IL_0018: Unknown result type (might be due to invalid IL or missing references)
		//IL_0019: Unknown result type (might be due to invalid IL or missing references)
		//IL_0033: Unknown result type (might be due to invalid IL or missing references)
		//IL_003f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0044: Unknown result type (might be due to invalid IL or missing references)
		//IL_0054: Unknown result type (might be due to invalid IL or missing references)
		//IL_009d: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c0: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c5: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c6: Unknown result type (might be due to invalid IL or missing references)
		//IL_010f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0119: Unknown result type (might be due to invalid IL or missing references)
		//IL_0083: Unknown result type (might be due to invalid IL or missing references)
		((Rect)(ref inRect)).yMax = ((Rect)(ref inRect)).yMax - Window.CloseButSize.y;
		Rect val = inRect;
		((Rect)(ref val)).xMin = ((Rect)(ref val)).xMin + 34f;
		Text.Font = (GameFont)2;
		Widgets.Label(val, TranslatorFormattedStringExtensions.Translate("BS_ViewGenetics", NamedArgument.op_Implicit((Thing)(object)target)));
		Text.Font = (GameFont)1;
		GUI.color = XenotypeDef.IconColor;
		if (target.genes != null)
		{
			GUI.DrawTexture(new Rect(((Rect)(ref inRect)).x, ((Rect)(ref inRect)).y, 30f, 30f), (Texture)(object)target.genes.XenotypeIcon);
		}
		GUI.color = Color.white;
		((Rect)(ref inRect)).yMin = ((Rect)(ref inRect)).yMin + 34f;
		Vector2 size = ((Rect)(ref base.windowRect)).size;
		RaceViewUIManager.DrawRacialInfo(inRect, (Thing)(object)target, ((Rect)(ref inRect)).height, ref size, ref scrollPosition);
		if (Widgets.ButtonText(new Rect(((Rect)(ref inRect)).xMax - Window.CloseButSize.x, ((Rect)(ref inRect)).yMax, Window.CloseButSize.x, Window.CloseButSize.y), TaggedString.op_Implicit(Translator.Translate("Close")), true, true, true, (TextAnchor?)null))
		{
			((Window)this).Close(true);
		}
	}
}
