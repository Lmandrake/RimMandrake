using System.Collections.Generic;
using System.Linq;
using Verse;
using Verse.AI;
using Verse.AI.Group;

namespace Outposts;

public class LordToil_Drop : LordToil
{
	public class LordToilData_Drop : LordToilData
	{
		public int TicksPassed;

		public override void ExposeData()
		{
			Scribe_Values.Look<int>(ref TicksPassed, "ticksPassed", 0, false);
		}
	}

	public const string DROPPED_MEMO = "AllDropped";

	public const string AREAFULL_MEMO = "AreaFull";

	public LordToilData_Drop Data => base.data as LordToilData_Drop;

	public LordToil_Drop()
	{
		base.data = (LordToilData)(object)new LordToilData_Drop
		{
			TicksPassed = 0
		};
	}

	public override void UpdateAllDuties()
	{
		//IL_0024: Unknown result type (might be due to invalid IL or missing references)
		//IL_002e: Expected O, but got Unknown
		foreach (Pawn ownedPawn in base.lord.ownedPawns)
		{
			ownedPawn.mindState.duty = new PawnDuty(Outposts_DefOf.VEF_DropAllInInventory);
		}
		Data.TicksPassed = 0;
	}

	public override void LordToilTick()
	{
		((LordToil)this).LordToilTick();
		if (base.lord.ownedPawns.All((Pawn pawn) => !((IEnumerable<Thing>)pawn.inventory.innerContainer).Any()))
		{
			base.lord.ReceiveMemo("AllDropped");
		}
		Data.TicksPassed++;
		if (Data.TicksPassed > 60)
		{
			base.lord.ReceiveMemo("AreaFull");
		}
	}
}
