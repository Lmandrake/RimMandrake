using System;
using System.Linq;
using LudeonTK;
using Verse;

namespace BigAndSmall;

public static class MutationDebugging
{
	[DebugAction(/*Could not decode attribute arguments.*/)]
	public static void EditHeraldicsForSelected()
	{
		Pawn obj = Find.Selector.SelectedObjects.OfType<Pawn>().FirstOrDefault();
		if (obj == null)
		{
			Find.Selector.SelectedObjects.OfType<Thing>().FirstOrDefault();
		}
		if (obj == null)
		{
			throw new Exception("No valid thing selected viewing mutations.");
		}
		Dialog_ViewMutations dialog_ViewMutations = new Dialog_ViewMutations(obj);
		Find.WindowStack.Add((Window)(object)dialog_ViewMutations);
	}
}
