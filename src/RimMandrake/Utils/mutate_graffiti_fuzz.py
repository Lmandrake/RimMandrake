#!/usr/bin/env python3
"""Mutation proof for the Graffiti fuzz: plants each defect in the production kernel, runs the fuzz wrapper, demands a FAIL,
restores the file byte-identical (engine: mutate_explosivegrowth_fuzz.run_mutations).

    python3 src/RimMandrake/Utils/mutate_graffiti_fuzz.py [name-substring]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mutate_explosivegrowth_fuzz import run_mutations  # noqa: E402

MUTATIONS = [
    ("spree takes Stencil", "form == GraffitiForm.Scrawl || form == GraffitiForm.Tag || form == GraffitiForm.ThrowUp || form == GraffitiForm.Glyph", "form == GraffitiForm.Scrawl || form == GraffitiForm.Tag || form == GraffitiForm.ThrowUp || form == GraffitiForm.Glyph || form == GraffitiForm.Stencil"),
    ("spree drops Glyph", "|| form == GraffitiForm.ThrowUp || form == GraffitiForm.Glyph;", "|| form == GraffitiForm.ThrowUp;"),
    ("paint interval unclamped low", "return setting < MinPaintInterval ? MinPaintInterval : (setting > MaxPaintInterval ? MaxPaintInterval : setting);", "return setting > MaxPaintInterval ? MaxPaintInterval : setting;"),
    ("paint interval unclamped high", "return setting < MinPaintInterval ? MinPaintInterval : (setting > MaxPaintInterval ? MaxPaintInterval : setting);", "return setting < MinPaintInterval ? MinPaintInterval : setting;"),
    ("meme gate open without an ideo", "return placerHasIdeo && ideoHoldsAny;", "return ideoHoldsAny;"),
    ("meme gate closes ungated marks", "if (!hasRequirement) return true;", ""),
    ("skill gate passes a pawn with no skills", "return hasSkillRecord && level >= minArtistic;", "return !hasSkillRecord || level >= minArtistic;"),
    ("skill gate off by one", "return hasSkillRecord && level >= minArtistic;", "return hasSkillRecord && level > minArtistic;"),
    ("skill gate gates minArtistic 0", "if (minArtistic <= 0) return true;", "if (minArtistic < 0) return true;"),
    ("hostility gate closed on no Royalty", "if (!targetDefExists) return true;", "if (!targetDefExists) return false;"),
    ("hostility gate closed on no Empire", "if (!targetFactionExists) return true;", "if (!targetFactionExists) return false;"),
    ("hostility gate open for no faction", "if (!placerHasFaction) return false;", "if (!placerHasFaction) return true;"),
    ("hostility gate open for the target itself", "if (placerIsTarget) return false;", ""),
    ("hostility gate ignores hostility", "return placerHostileToTarget;", "return true;"),
    ("pool ignores a gate", "return memeOk && skillOk && hostileOk && poolWeight > 0f;", "return memeOk && skillOk && poolWeight > 0f;"),
    ("pool admits zero weight", "return memeOk && skillOk && hostileOk && poolWeight > 0f;", "return memeOk && skillOk && hostileOk && poolWeight >= 0f;"),
    ("pick lands on a leading zero weight", "if (weights[i] <= 0f) continue;          // a zero or negative weight can never be picked (roll 0 would otherwise land on a leading zero)", ""),
    ("pick strict comparison", "if (roll <= cursor) return i;", "if (roll < cursor) return i;"),
    ("pick has no last-entry fallback", "            return last;\n        }\n\n        /// <summary>Sum of", "            return -1;\n        }\n\n        /// <summary>Sum of"),
    ("pick ignores weights", "cursor += weights[i];\n                last = i;", "cursor += 1f;\n                last = i;"),
    ("total counts negative weights", "for (int i = 0; i < weights.Count; i++) if (weights[i] > 0f) t += weights[i];", "for (int i = 0; i < weights.Count; i++) t += weights[i];"),
    ("subject beats nothing", "if (hasSubjectThought && viewerIsSubject) return RM_ReactionSlot.Subject;", ""),
    ("own faction before subject", "if (hasSubjectThought && viewerIsSubject) return RM_ReactionSlot.Subject;\n                if (hasOwnFactionThought && makerFactionIsViewerFaction) return RM_ReactionSlot.OwnFaction;", "if (hasOwnFactionThought && makerFactionIsViewerFaction) return RM_ReactionSlot.OwnFaction;\n                if (hasSubjectThought && viewerIsSubject) return RM_ReactionSlot.Subject;"),
    ("hostile before same ideo", "if (hasSameIdeoThought && makerIdeoIsViewerIdeo) return RM_ReactionSlot.SameIdeo;\n                if (hasHostileThought && makerFactionHostileToViewer) return RM_ReactionSlot.HostileMaker;", "if (hasHostileThought && makerFactionHostileToViewer) return RM_ReactionSlot.HostileMaker;\n                if (hasSameIdeoThought && makerIdeoIsViewerIdeo) return RM_ReactionSlot.SameIdeo;"),
    ("slot taken without its thought", "if (hasOtherIdeoThought && makerIdeoDiffersFromViewer) return RM_ReactionSlot.OtherIdeo;", "if (makerIdeoDiffersFromViewer) return RM_ReactionSlot.OtherIdeo;"),
    ("reaction without provenance", "if (hasProvenance)\n            {", "if (true)\n            {"),
    ("clan-only blocks the player", "return clanOnly && !viewerIsPlayerFaction;", "return clanOnly && viewerIsPlayerFaction;"),
    ("clan-only blocks nobody", "return clanOnly && !viewerIsPlayerFaction;", "return false;"),
    ("room rule requires both rooms", "return !(viewerRoomKnown && cellRoomKnown && !sameRoom);", "return sameRoom;"),
    ("thought without a spawned viewer", "return settingOn && onMap && spawned && markFound;", "return settingOn && onMap && markFound;"),
    ("scrub protection beats a forced clean", "if (forced || !settingOn) return false;", "if (!settingOn) return false;"),
    ("scrub protection ignores the setting", "if (forced || !settingOn) return false;", "if (forced) return false;"),
    ("scrub protection needs all three", "return flagged || ownFaction || devotional;", "return flagged && ownFaction && devotional;"),
    ("scrub protection drops Devotional", "return flagged || ownFaction || devotional;", "return flagged || ownFaction;"),
    ("scrub protection of non-marks", "if (!isMark || !hasExt) return false;", "if (!hasExt) return false;"),
    ("raid exit tags the player", "return factionKnown && !factionIsPlayer && hostileToPlayer;", "return factionKnown && hostileToPlayer;"),
    ("raid exit tags neutral factions", "return factionKnown && !factionIsPlayer && hostileToPlayer;", "return factionKnown && !factionIsPlayer;"),
    ("raid exit ignores the setting", "if (!paintingOn || !exitTaggingOn) return false;", "if (!paintingOn) return false;"),
    ("going over destroys the same def", "return isMark && !sameDef;", "return isMark;"),
    ("going over never", "return isMark && !sameDef;", "return false;"),
    ("gather offers marked cells first", "return bare.Count > 0 ? bare : any;", "return any.Count > 0 ? any : bare;"),
    ("gather ignores the cap", "if (bare.Count >= MaxCandidates) break;", ""),
    ("gather fallback uncapped", "else if (any.Count < MaxCandidates)", "else"),
    ("gather keeps unusable cells", "if (!cells[i].usable) continue;", ""),
    ("gather cap 13", "public const int MaxCandidates = 12;", "public const int MaxCandidates = 13;"),
    ("lure takes the farthest", "distSqToFallback[i] < distSqToFallback[best]", "distSqToFallback[i] > distSqToFallback[best]"),
    ("lure ties by the highest key", "tieKey[i] < tieKey[best]", "tieKey[i] > tieKey[best]"),
    ("lure takes the first", "if (best < 0 || distSqToFallback[i] < distSqToFallback[best] || (distSqToFallback[i] == distSqToFallback[best] && tieKey[i] < tieKey[best])) best = i;", "if (best < 0) best = i;"),
]

if __name__ == "__main__":
    sys.exit(run_mutations("src/RimMandrake/Graffiti/Source/Kernel/RM_GraffitiKernel.cs",
                           "selftest_graffiti_fuzz.py", MUTATIONS, sys.argv[1] if len(sys.argv) > 1 else None))
