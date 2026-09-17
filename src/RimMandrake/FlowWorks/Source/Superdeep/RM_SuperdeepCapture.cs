using System.Collections.Generic;
using RimMandrake.FlowWorks.Pits;
using RimWorld;
using Verse;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// The lifecycle of the SUPERDEEP holder: one <see cref="Building_SuperdeepPit"/>
	/// per cell the depth grid says is at D = 4, and none anywhere else.
	///
	/// WHY A BUILDING AND NOT A GRID FLAG. Ruling 26 says FlowWorks writes no new
	/// capture or escape system, and the one that already exists — Pits'
	/// Building_OpenPit — is a Thing that holds pawns in a ThingOwner. Reusing it
	/// means reusing its save shape, its struggle clock, its release gizmo and
	/// its drop-on-destroy safety net. The cost is one Thing per SUPERDEEP cell,
	/// which is the same cost vanilla pays per trap.
	///
	/// The holder is NOT an edifice (see the def), so it blocks neither the
	/// fill-in designator nor the ladder that has to share its cell.
	/// </summary>
	public static class RM_SuperdeepCapture
	{
		public static Building_SuperdeepPit HolderAt(Map map, IntVec3 c)
		{
			if (map == null || !c.InBounds(map))
			{
				return null;
			}
			List<Thing> things = c.GetThingList(map);
			for (int i = 0; i < things.Count; i++)
			{
				if (things[i] is Building_SuperdeepPit pit)
				{
					return pit;
				}
			}
			return null;
		}

		/// <summary>Idempotent. Safe to call on every dig, every load and every
		/// settings flip.</summary>
		public static void EnsureHolder(Map map, IntVec3 c)
		{
			if (map == null || !c.InBounds(map))
			{
				return;
			}
			if (!RimMandrakeFlowWorksSettings.superdeepCaptureEnabled)
			{
				return;
			}
			if (HolderAt(map, c) != null)
			{
				return;
			}
			ThingDef def = RimMandrakeFlowWorks_DefOf.RM_SuperdeepPit;
			if (def == null)
			{
				return;
			}
			Building_SuperdeepPit pit = (Building_SuperdeepPit)ThingMaker.MakeThing(def);
			// The deepest rung of the Pits ladder, because this IS the deepest
			// rung of the depth ladder — PitEscapeUtility scores the struggle
			// clock off it, so a SUPERDEEP hole must not read as a shallow pit.
			pit.DepthTier = PitDepthTier.Chasm;
			// Set BEFORE spawn: SetFactionDirect is the no-side-effects form
			// (Verse/Thing.cs:1744, and what GenSpawn itself uses at GenSpawn.cs:77).
			// The faction decides who the hole does NOT swallow — see
			// Building_SuperdeepPit.CapturesFaction.
			Faction owner = Faction.OfPlayer;
			if (owner != null)
			{
				pit.SetFactionDirect(owner);
			}
			GenSpawn.Spawn(pit, c, map);
		}

		/// <summary>Called when a cell stops being SUPERDEEP. Destroy — not
		/// Despawn — because Building_OpenPit.Destroy is what drops an occupant
		/// onto the map instead of voiding them with the building.</summary>
		public static void RemoveHolder(Map map, IntVec3 c)
		{
			Building_SuperdeepPit pit = HolderAt(map, c);
			if (pit != null && !pit.Destroyed)
			{
				pit.Destroy(DestroyMode.Vanish);
			}
		}

		/// <summary>Reconcile the whole map with the depth grid. Run on
		/// FinalizeInit so a save written before this phase (or with the toggle
		/// off) grows its holders on load, and so a save written with holders and
		/// loaded with capture OFF sheds them.</summary>
		public static void SyncMap(Map map, RM_MapComponent_Excavation engine)
		{
			if (map == null || engine == null)
			{
				return;
			}
			List<Thing> existing = map.listerThings.ThingsOfDef(RimMandrakeFlowWorks_DefOf.RM_SuperdeepPit);
			// Copy: Destroy mutates the lister's own list.
			List<Thing> stale = new List<Thing>();
			for (int i = 0; i < existing.Count; i++)
			{
				Thing t = existing[i];
				if (!RimMandrakeFlowWorksSettings.superdeepCaptureEnabled
					|| !engine.IsSuperdeepExcavation(t.Position))
				{
					stale.Add(t);
				}
			}
			for (int i = 0; i < stale.Count; i++)
			{
				stale[i].Destroy(DestroyMode.Vanish);
			}
			if (!RimMandrakeFlowWorksSettings.superdeepCaptureEnabled)
			{
				return;
			}
			foreach (IntVec3 c in engine.SuperdeepCells())
			{
				EnsureHolder(map, c);
			}
		}
	}
}
