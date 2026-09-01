using System;
using UnityEngine;
using Verse;

namespace FactionLoadout;

public class Dialog_TextEntry : Window
{
	private string message;

	private string input;

	private Action<string> onConfirm;

	public override Vector2 InitialSize
	{
		get
		{
			//IL_0006: Unknown result type (might be due to invalid IL or missing references)
			//IL_000b: Unknown result type (might be due to invalid IL or missing references)
			//IL_002c: Unknown result type (might be due to invalid IL or missing references)
			Vector2 result = Text.CalcSize(message);
			result.x += 100f;
			result.y *= 7f;
			return result;
		}
	}

	public Dialog_TextEntry(string message, Action<string> onConfirm)
		: base((IWindowDrawing)null)
	{
		this.message = message;
		this.onConfirm = onConfirm;
		input = string.Empty;
		base.doCloseX = true;
		base.closeOnAccept = false;
		base.closeOnCancel = true;
	}

	public override void DoWindowContents(Rect inRect)
	{
		//IL_0000: Unknown result type (might be due to invalid IL or missing references)
		//IL_0006: Expected O, but got Unknown
		//IL_0007: Unknown result type (might be due to invalid IL or missing references)
		//IL_0022: Unknown result type (might be due to invalid IL or missing references)
		//IL_0041: Unknown result type (might be due to invalid IL or missing references)
		//IL_007c: Unknown result type (might be due to invalid IL or missing references)
		Listing_Standard val = new Listing_Standard();
		((Listing)val).Begin(inRect);
		val.Label(message, -1f, (TipSignal?)null);
		input = val.TextEntry(input, 1);
		if (val.ButtonText(TaggedString.op_Implicit(Translator.Translate("Accept")), (string)null, 1f))
		{
			onConfirm?.Invoke(input);
			((Window)this).Close(true);
		}
		if (val.ButtonText(TaggedString.op_Implicit(Translator.Translate("Cancel")), (string)null, 1f))
		{
			((Window)this).Close(true);
		}
		((Listing)val).End();
	}
}
