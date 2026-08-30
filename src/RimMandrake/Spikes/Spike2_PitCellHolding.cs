using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Spikes
{
    // SPIKE 2 — the pit cell as a HOLDING BUILDING (the Anomaly platform pattern),
    // not a room. This is the route that dodges the old prisoner-pit mod's failure
    // (fighting RimWorld's room/bed prisoner logic).
    //
    // VERIFIED-IN-SOURCE (1.6):
    //   Building_HoldingPlatform : Building, IThingHolderWithDrawnPawn, IThingHolder,
    //     IRoofCollapseAlert, ISearchableContents        (Building_HoldingPlatform.cs:10)
    //   - holds ONE pawn in a ThingOwner innerContainer; HeldPawn is
    //     innerContainer.FirstOrDefault(x => x is Pawn)
    //   - the pawn is DRAWN BY THE BUILDING via IThingHolderWithDrawnPawn:
    //     HeldPawnDrawPos_Y / HeldPawnBodyAngle / HeldPawnPosture (the platform lays
    //     the pawn face-up at a fixed y — the pit draws it LOWER, sunken)
    //   CompHoldingPlatformTarget : ThingComp on the CAPTIVE side
    //     (CompHoldingPlatformTarget.cs:11); Notify_HeldOnPlatform() clears lord,
    //     updates dynamic components — the transfer-in choreography to imitate.
    //
    // THE TRICK: implement the same three interfaces on Building_PitCell and let the
    // engine's existing holder plumbing (rendering, save/load via ThingOwner,
    // searchable contents) do the work. Depth = a negative draw offset instead of
    // the platform's +0.15 lift.
    //
    // UNPROVEN UNTIL RUNTIME:
    //   - assignment UI: the platform gets pawns via CompHoldingPlatformTarget
    //     targeting (entity flow). A PRISONER flows differently — likely needs a
    //     custom JobDef (carry downed/prisoner to pit + TryAdd to innerContainer),
    //     modeled on JobDriver_CarryToEntityHolder. Quicktest is the arbiter.
    //   - feeding: platform captives use entity feed jobs; prisoners in a ThingOwner
    //     are NOT room-prisoners, so needs a feed-through-gate job or a
    //     CompAssignableToPawn food hack. Open runtime question.
    //   - drawing at negative offset: HeldPawnDrawPos_Y below terrain altitude may
    //     clip under the terrain mesh; may need a masked "in-pit" portrait render
    //     instead (draw upper body only). Quicktest decides which.
    //   - escape: platform pawns roll escapes via CompHoldingPlatformTarget/activity;
    //     the pit's struggle clock is our own ticker (sketched below, inert here).
    public class Building_PitCell : Building, IThingHolderWithDrawnPawn, IThingHolder
    {
        public ThingOwner innerContainer;

        private const float SunkenYOffset = -0.05f; // below the cover; runtime will tune
        private const int StruggleIntervalTicks = 2500;

        public Building_PitCell()
        {
            innerContainer = new ThingOwner<Thing>(this);
        }

        public Pawn HeldPawn
        {
            get
            {
                for (int i = 0; i < innerContainer.Count; i++)
                {
                    if (innerContainer[i] is Pawn p) return p;
                }
                return null;
            }
        }

        // IThingHolderWithDrawnPawn — the platform's exact surface, sunken.
        public float HeldPawnDrawPos_Y => DrawPos.y + SunkenYOffset;
        public float HeldPawnBodyAngle => Rotation.AsAngle;
        public PawnPosture HeldPawnPosture => PawnPosture.LayingOnGroundFaceUp;

        // IThingHolder
        public void GetChildHolders(List<IThingHolder> outChildren)
        {
            ThingOwnerUtility.AppendThingHoldersFromThings(outChildren, GetDirectlyHeldThings());
        }

        public ThingOwner GetDirectlyHeldThings() => innerContainer;

        protected override void Tick()
        {
            base.Tick();
            // Struggle clock sketch: every interval, escape odds from
            // (bodySize - depthTier), health %, manipulation. Inert here —
            // the real curve lands with the build; this proves the hook point.
            if (this.IsHashIntervalTick(StruggleIntervalTicks) && HeldPawn != null)
            {
                // float odds = EscapeOdds(HeldPawn);  // build-time
            }
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Deep.Look(ref innerContainer, "innerContainer", this);
        }
    }
}
