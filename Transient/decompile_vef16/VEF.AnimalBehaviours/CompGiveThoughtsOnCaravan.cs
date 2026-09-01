using RimWorld;
using RimWorld.Planet;
using Verse;

namespace VEF.AnimalBehaviours;

public class CompGiveThoughtsOnCaravan : ThingComp
{
	public CompProperties_GiveThoughtsOnCaravan Props => (CompProperties_GiveThoughtsOnCaravan)(object)base.props;

	public override void CompTickInterval(int delta)
	{
		if (!Gen.IsHashIntervalTick((Thing)(object)base.parent, Props.intervalTicks, delta))
		{
			return;
		}
		ThingWithComps parent = base.parent;
		Pawn val = (Pawn)(object)((parent is Pawn) ? parent : null);
		Caravan caravan = CaravanUtility.GetCaravan((Thing)(object)val);
		if (caravan == null)
		{
			return;
		}
		foreach (Pawn item in caravan.PawnsListForReading)
		{
			if (!Props.causeNegativeAtRandom)
			{
				Pawn_NeedsTracker needs = item.needs;
				if (needs == null)
				{
					continue;
				}
				Need_Mood mood = needs.mood;
				if (mood == null)
				{
					continue;
				}
				ThoughtHandler thoughts = mood.thoughts;
				if (thoughts != null)
				{
					MemoryThoughtHandler memories = thoughts.memories;
					if (memories != null)
					{
						memories.TryGainMemory(Props.thought, val, (Precept)null);
					}
				}
				continue;
			}
			if (Rand.Chance(Props.randomNegativeChance))
			{
				Pawn_NeedsTracker needs2 = item.needs;
				object obj;
				if (needs2 == null)
				{
					obj = null;
				}
				else
				{
					Need_Mood mood2 = needs2.mood;
					if (mood2 == null)
					{
						obj = null;
					}
					else
					{
						ThoughtHandler thoughts2 = mood2.thoughts;
						if (thoughts2 == null)
						{
							obj = null;
						}
						else
						{
							MemoryThoughtHandler memories2 = thoughts2.memories;
							obj = ((memories2 != null) ? memories2.GetFirstMemoryOfDef(Props.thought) : null);
						}
					}
				}
				if (obj != null)
				{
					continue;
				}
				Pawn_NeedsTracker needs3 = item.needs;
				if (needs3 == null)
				{
					continue;
				}
				Need_Mood mood3 = needs3.mood;
				if (mood3 == null)
				{
					continue;
				}
				ThoughtHandler thoughts3 = mood3.thoughts;
				if (thoughts3 != null)
				{
					MemoryThoughtHandler memories3 = thoughts3.memories;
					if (memories3 != null)
					{
						memories3.TryGainMemory(Props.negativeThought, val, (Precept)null);
					}
				}
				continue;
			}
			Pawn_NeedsTracker needs4 = item.needs;
			object obj2;
			if (needs4 == null)
			{
				obj2 = null;
			}
			else
			{
				Need_Mood mood4 = needs4.mood;
				if (mood4 == null)
				{
					obj2 = null;
				}
				else
				{
					ThoughtHandler thoughts4 = mood4.thoughts;
					if (thoughts4 == null)
					{
						obj2 = null;
					}
					else
					{
						MemoryThoughtHandler memories4 = thoughts4.memories;
						obj2 = ((memories4 != null) ? memories4.GetFirstMemoryOfDef(Props.negativeThought) : null);
					}
				}
			}
			if (obj2 != null)
			{
				continue;
			}
			Pawn_NeedsTracker needs5 = item.needs;
			if (needs5 == null)
			{
				continue;
			}
			Need_Mood mood5 = needs5.mood;
			if (mood5 == null)
			{
				continue;
			}
			ThoughtHandler thoughts5 = mood5.thoughts;
			if (thoughts5 != null)
			{
				MemoryThoughtHandler memories5 = thoughts5.memories;
				if (memories5 != null)
				{
					memories5.TryGainMemory(Props.thought, val, (Precept)null);
				}
			}
		}
	}
}
