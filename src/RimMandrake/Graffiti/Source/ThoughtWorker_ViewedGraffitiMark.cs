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
    // A situational thought active only while a mark is nearby, read off the map's list of marks. This worker returns presence/absence
    // only (no stacking) - a content pack wanting quality-scaled intensity
    // (Mural's supportsQuality) can still do so by keying a *different*
    // ThoughtDef for each quality tier, each pointed at this same class.
    public class ThoughtWorker_ViewedGraffitiMark : ThoughtWorker
    {
        private const float ScanRadius = 8f;

        protected override ThoughtState CurrentStateInternal(Pawn p)
        {
            if (!RM_GraffitiKernel.ThoughtActive(RM_GraffitiSettings.viewerReactionEnabled, p.Map != null, p.Spawned, true)) return false;
            return NearbyMatchingMark(p) != null;
        }

        private Thing NearbyMatchingMark(Pawn p)
        {
            Room room = p.Position.GetRoom(p.Map);
            MapComponent_GraffitiSocial comp = MapComponent_GraffitiSocial.For(p.Map);
            if (comp == null) return null;
            for (int i = 0; i < comp.marks.Count; i++)
            {
                Filth_Mark mark = comp.marks[i];
                if ((mark.Position - p.Position).LengthHorizontalSquared > ScanRadius * ScanRadius || mark.Position.Fogged(p.Map) || !RM_GraffitiKernel.StillSpeaks(mark.defaced, false))
                {
                    continue;
                }
                Room cellRoom = mark.Position.GetRoom(p.Map);
                if (!RM_GraffitiKernel.SameRoomOrUnknown(room != null, cellRoom != null, room == cellRoom))
                {
                    continue;
                }
                ModExtension_Graffiti ext = mark.def.GetModExtension<ModExtension_Graffiti>();
                // Relation-keyed (GRAFFITI_PUNK_IDEOLIGION_SCOPE_1 §1.5): ResolveReactionThought picks the ONE ThoughtDef this viewer gets from
                // this mark; this worker instance only fires if that pick is the ThoughtDef it belongs to.
                if (ext == null || ResolveReactionThought(ext, mark, p) != def)
                {
                    continue;
                }
                // Owner ruling #4 (graffiti_spec.md §7): a clan-only mark looks the same to everyone; what it withholds from outsiders is the meaning.
                if (RM_GraffitiKernel.ClanOnlyBlocks(ext.visibility == GraffitiVisibility.ClanOnly, p.Faction == Faction.OfPlayer))
                {
                    continue;
                }
                return mark;
            }
            return null;
        }

        // Priority order per ModExtension_Graffiti's own field comments:
        // I-am-the-subject beats everything, then my own faction made it,
        // then same ideo, then a hostile maker, then a different ideo,
        // and finally the flat viewerReactionThought every mark has always
        // had. A mark with no provenance (mark == null - predates this
        // item, or its placer never stamped a maker) or with none of the
        // relation fields set behaves exactly as before: only the flat
        // field is checked.
        private static ThoughtDef ResolveReactionThought(ModExtension_Graffiti ext, Filth_Mark mark, Pawn viewer)
        {
            bool prov = mark != null;
            RM_ReactionSlot slot = RM_GraffitiKernel.ReactionSlot(prov,
                ext.onViewSubject != null, prov && mark.subject == viewer,
                ext.onViewOwnFaction != null, prov && mark.makerFaction != null && mark.makerFaction == viewer.Faction,
                ext.onViewSameIdeo != null, prov && mark.makerIdeo != null && mark.makerIdeo == GraffitiJobUtility.IdeoOf(viewer),
                ext.onViewHostileMaker != null, prov && mark.makerFaction != null && viewer.Faction != null && mark.makerFaction.HostileTo(viewer.Faction),
                ext.onViewOtherIdeo != null, prov && mark.makerIdeo != null && GraffitiJobUtility.IdeoOf(viewer) != null && mark.makerIdeo != GraffitiJobUtility.IdeoOf(viewer));
            switch (slot)
            {
                case RM_ReactionSlot.Subject: return ext.onViewSubject;
                case RM_ReactionSlot.OwnFaction: return ext.onViewOwnFaction;
                case RM_ReactionSlot.SameIdeo: return ext.onViewSameIdeo;
                case RM_ReactionSlot.HostileMaker: return ext.onViewHostileMaker;
                case RM_ReactionSlot.OtherIdeo: return ext.onViewOtherIdeo;
                default: return ext.viewerReactionThought;
            }
        }
    }
}
