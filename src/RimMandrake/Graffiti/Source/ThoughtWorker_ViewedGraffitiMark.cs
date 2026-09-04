using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.Graffiti
{
    // GRAFFITI_FRAMEWORK_BUILD_1's viewer ThoughtWorker. Mechanism only -
    // no content ThoughtDef is shipped here (that is the owner-voice work
    // this item's own history reserves). This class is meant to be reused:
    // any future ThoughtDef (Sacred/Mural/Jest/Taunt reaction) sets its own
    // <workerClass>RimMandrake.Graffiti.ThoughtWorker_ViewedGraffitiMark
    // and points the mark's ModExtension_Graffiti.viewerReactionThought
    // back at that same ThoughtDef - the lookup is by "which marks near me
    // name ME", not by category, so one worker class serves every future
    // reaction thought without a content pack ever touching this file.
    //
    // Pattern verified against real vanilla source (RimSage):
    // RimWorld.ThoughtWorker_PyromaniacNearFlames - the same "situational
    // thought active only while an environmental thing is nearby" shape,
    // same room+radius scan idiom. This worker returns presence/absence
    // only (no stacking) - a content pack wanting quality-scaled intensity
    // (Mural's supportsQuality) can still do so by keying a *different*
    // ThoughtDef for each quality tier, each pointed at this same class.
    public class ThoughtWorker_ViewedGraffitiMark : ThoughtWorker
    {
        private const float ScanRadius = 8f;

        protected override ThoughtState CurrentStateInternal(Pawn p)
        {
            if (p.Map == null || !p.Spawned)
            {
                return false;
            }
            return NearbyMatchingMark(p) != null;
        }

        private Thing NearbyMatchingMark(Pawn p)
        {
            Room room = p.Position.GetRoom(p.Map);
            foreach (IntVec3 cell in GenRadial.RadialCellsAround(p.Position, ScanRadius, useCenter: true))
            {
                if (!cell.InBounds(p.Map) || cell.Fogged(p.Map))
                {
                    continue;
                }
                // Filth (RM_Graffiti_Vandal's own thingClass, per
                // GRAFFITI_FRAMEWORK_BUILD_1's third pass) doesn't always
                // report a Room the same way a built Thing does at a wall
                // cell - only gate on room-match when both resolve, so a
                // mark painted on an exterior/edge wall isn't silently
                // invisible to this check.
                Room cellRoom = cell.GetRoom(p.Map);
                if (room != null && cellRoom != null && room != cellRoom)
                {
                    continue;
                }
                List<Thing> thingList = cell.GetThingList(p.Map);
                for (int i = 0; i < thingList.Count; i++)
                {
                    ModExtension_Graffiti ext = thingList[i].def.GetModExtension<ModExtension_Graffiti>();
                    if (ext == null || ext.viewerReactionThought != def)
                    {
                        continue;
                    }
                    // Owner ruling #4 (graffiti_spec.md §7): "Cant renders as a
                    // FAINT SCRAWL to outsiders - they see that marks exist,
                    // never what they mean." RimWorld has one screen, not one
                    // per pawn, so there is no separate graphic to swap - the
                    // mark's Filth Thing renders identically for everyone
                    // (that IS "they see it exists"). What ClanOnly withholds
                    // is the MEANING layer: the reaction this worker grants.
                    // A Public mark (Sacred/Mural/Jest/most Taunts) reads for
                    // any viewer, same as before. GraffitiVisibility.ClanOnly
                    // (Cant's own family default, §1⑤) is gated to the
                    // player's own pawns - the mechanism-level stand-in for
                    // "the clan" this RM-tier engine can use without a hard
                    // dependency on the RSW-tier Jawa xenotype check
                    // (JawaRules.IsJawa) a RUT content pack could still layer
                    // on top later.
                    if (ext.visibility == GraffitiVisibility.ClanOnly && p.Faction != Faction.OfPlayer)
                    {
                        continue;
                    }
                    return thingList[i];
                }
            }
            return null;
        }
    }
}
