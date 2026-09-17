using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// The inverse of <see cref="Designator_DigCanal"/>: raise an excavated cell
	/// one level. PHASE 2's other half.
	///
	/// OWNER, 2026-09-16: <i>"There should also be a way to 'fill in' a canal
	/// that displaces liquid BACK. It does not destroy liquid if there's a place
	/// for it to go, but if it would 'overflow' it is destroyed."</i>
	///
	/// Deliberately the same shape as the dig chain — Designator_Cells, a
	/// designation, a WorkGiver_Scanner and a JobDriver_AffectFloor — because
	/// the two are one ladder read in opposite directions and anything that
	/// diverges between them is a defect waiting to be found.
	///
	/// NO MATERIAL COST THIS PASS. §18 argues a fill-in should consume the
	/// rubble or sand it is made of, and that argument stands; it is a hauling
	/// mechanic, not a depth one, and building it here would put a resource
	/// system inside the primitive.
	///
	/// ⚠️ NAMED <c>Designator_FillInCanal</c>, not <c>Designator_FillIn</c>:
	/// vanilla already ships <see cref="RimWorld.Designator_FillIn"/> (the
	/// crater filler). Same-namespace resolution would have made ours win
	/// silently inside this assembly, which is exactly the kind of collision
	/// that is discovered months later by somebody debugging the wrong class.
	/// </summary>
	public class Designator_FillInCanal : Designator_Cells
	{
		public Designator_FillInCanal()
		{
			defaultLabel = "Fill in canal";
			defaultDesc = "Fill an excavated cell back in by one level. Liquid that no longer "
				+ "fits is pushed into the rest of the channel and back into the body it came "
				+ "from; only what finds no room anywhere is lost. Filling a cell all the way "
				+ "back to the surface restores the terrain that was there before it was dug.";
			icon = ContentFinder<Texture2D>.Get("UI/Designators/FillCrater", true);
			useMouseIcon = true;
			soundDragSustain = SoundDefOf.Designate_DragStandard;
			soundDragChanged = SoundDefOf.Designate_DragStandard_Changed;
			soundSucceeded = SoundDefOf.Designate_SmoothSurface;
			hotKey = KeyBindingDefOf.Misc7;
		}

		public override AcceptanceReport CanDesignateCell(IntVec3 c)
		{
			if (!c.InBounds(Map) || c.Fogged(Map))
			{
				return false;
			}
			if (!RimMandrakeFlowWorksSettings.fillInEnabled)
			{
				return "Filling in is switched off in this mod's settings.";
			}
			if (Map.designationManager.DesignationAt(c, RimMandrakeFlowWorks_DefOf.RM_FillInCanal) != null)
			{
				return "Already being filled in.";
			}
			Building edifice = c.GetEdifice(Map);
			if (edifice != null)
			{
				// §19's open question — "filling in a canal that contains a pit:
				// does the pit survive?" — is NOT decided here. Both readings
				// are defensible and neither has been ruled, so the designator
				// refuses rather than picking one silently and shipping it as
				// though it were a decision.
				return "Something is built here. Remove it first.";
			}
			RM_MapComponent_Excavation excavation = Map.GetComponent<RM_MapComponent_Excavation>();
			if (excavation == null)
			{
				return false;
			}
			// PHASE 5. §19's open question — "filling in a canal that contains a
			// pit: does the pit survive?" — is STILL not decided here, and now
			// there is a live occupant to lose by deciding it silently. Refusing
			// while someone is held is the same non-decision the edifice branch
			// above makes, and the engine's own FillIn path still drops an
			// occupant safely if a cell is raised some other way.
			Building_SuperdeepPit holder = RM_SuperdeepCapture.HolderAt(Map, c);
			if (holder != null && holder.Sprung)
			{
				return "Someone is held down there. Get them out first.";
			}
			if (!excavation.CanFillIn(c))
			{
				// Natural water is deliberately excluded: §18 gives filling in a
				// lake its own rule (most-abundant NON-liquid neighbour, mud
				// drying to rich soil, a haul cost) and it is a different
				// mechanic wearing the same word.
				return excavation.IsSourceCell(c)
					? "That is natural water, not an excavation. Filling in natural water is a "
						+ "separate job and is not built yet."
					: "Nothing has been dug here.";
			}
			return AcceptanceReport.WasAccepted;
		}

		public override void DesignateSingleCell(IntVec3 c)
		{
			Map.designationManager.AddDesignation(new Designation(c, RimMandrakeFlowWorks_DefOf.RM_FillInCanal));
		}

		public override void SelectedUpdate()
		{
			GenUI.RenderMouseoverBracket();
		}
	}
}
