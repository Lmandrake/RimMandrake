using System.Collections.Generic;
using Verse;

namespace BigAndSmall;

public class DraftedActionHolder : GameComponent
{
	public static Dictionary<string, DraftedActionData> pawnDraftActionData = new Dictionary<string, DraftedActionData>();

	public static DraftedActionData GetData(Pawn pawn)
	{
		if (pawnDraftActionData == null)
		{
			pawnDraftActionData = new Dictionary<string, DraftedActionData>();
		}
		if (pawnDraftActionData.TryGetValue(((Thing)pawn).ThingID, out var value))
		{
			return value;
		}
		pawnDraftActionData[((Thing)pawn).ThingID] = new DraftedActionData(pawn);
		return pawnDraftActionData[((Thing)pawn).ThingID];
	}

	public DraftedActionHolder(Game game)
	{
	}

	public override void ExposeData()
	{
		//IL_0017: Unknown result type (might be due to invalid IL or missing references)
		//IL_001d: Invalid comparison between Unknown and I4
		((GameComponent)this).ExposeData();
		Scribe_Collections.Look<string, DraftedActionData>(ref pawnDraftActionData, "draftedActions", (LookMode)1, (LookMode)2);
		if ((int)Scribe.mode == 4 && !DraftGizmos.AutoCombatEnabled)
		{
			pawnDraftActionData.Clear();
		}
	}
}
