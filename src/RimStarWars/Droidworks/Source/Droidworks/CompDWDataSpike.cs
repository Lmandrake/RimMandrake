using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.StarWars.Droidworks
{
    /// <summary>
    /// DROIDWORKS_WIPE_AND_SPIKE_1; per-faction keys added
    /// DROIDWORKS_HEADS_BRAINS_SPIKES_1 (packet B3). Data-driven faction key
    /// for a data spike - see JobDriver_DWDataSpike.cs and
    /// CompTargetable_DWDataSpike.cs for how it is read. Each keyed faction
    /// is its own ThingDef of this same shape with a different spikeFaction
    /// value (or factionless=true) - never a C# change. v0's single generic
    /// RSW_DW_DataSpike (design/Jawa/droid_ruling.md's KotOR ruling, "THE
    /// capture target") is untouched by B3; RSW_DW_DataSpike_Empire/Hutt/
    /// Junker/Wild are the new siblings.
    /// </summary>
    public class CompProperties_DWDataSpike : CompProperties
    {
        /// <summary>FactionDef defName this spike is keyed to.</summary>
        public string spikeFaction;

        /// <summary>
        /// RSW_DW_DataSpike_Wild (packet B3): targets a FACTIONLESS droid -
        /// the crashed/gone-wild units of DROIDWORKS_WILD_DROIDS_1 (E4,
        /// unbuilt), which per that item's own design carry Faction == null,
        /// never a real FactionDef. When true, spikeFaction is ignored.
        /// </summary>
        public bool factionless;

        /// <summary>
        /// DROIDWORKS_WILD_DROIDS_1 (packet E4). When true the spike refuses a
        /// merely-DOWNED target and only works on a pawn already taken
        /// prisoner. Set on RSW_DW_DataSpike_Wild because that spike runs on
        /// recruitment resistance (below), and Pawn_GuestTracker.resistance is
        /// only initialised by CapturedBy -> SetGuestStatus(Prisoner); before
        /// capture it is the -1 sentinel, i.e. "no resistance value exists
        /// yet". The faction-keyed spikes leave this false and stay usable in
        /// the field on a downed droid, exactly as before.
        /// </summary>
        public bool requiresPrisoner;

        /// <summary>
        /// DROIDWORKS_WILD_DROIDS_1 (packet E4). 0 (the default, and what every
        /// faction-keyed spike leaves it at) = the original behaviour: one use,
        /// instant faction flip. Above 0 = "reprogram-as-recruit with
        /// resistance": each use chews this much (times a spiker-skill factor)
        /// off the target's vanilla recruitment resistance, and the flip only
        /// happens on the use that takes it to zero. The spike is consumed
        /// either way, so a stubborn droid costs several.
        /// </summary>
        public float resistancePerUse;

        public CompProperties_DWDataSpike()
        {
            compClass = typeof(CompDWDataSpike);
        }
    }

    public class CompDWDataSpike : ThingComp
    {
        public CompProperties_DWDataSpike Props => (CompProperties_DWDataSpike)props;

        /// <summary>
        /// True only when the target's ACTUAL faction (read live, not cached)
        /// matches this spike's key - a spike keyed to the wrong faction
        /// refuses rather than silently working on anyone.
        /// </summary>
        public bool MatchesFaction(Pawn target)
        {
            if (target == null) return false;
            if (Props.factionless) return target.Faction == null;
            if (target.Faction?.def == null || Props.spikeFaction.NullOrEmpty()) return false;
            return target.Faction.def.defName == Props.spikeFaction;
        }

        /// <summary>
        /// The whole legality test for a spike target, in one place so the
        /// targeting UI (CompTargetable_DWDataSpike) and the job's own re-check
        /// at completion (JobDriver_DWDataSpike) cannot drift apart.
        /// </summary>
        public bool ValidTarget(Pawn target)
        {
            if (target == null || target.Dead) return false;
            if (!(target.Downed || target.IsPrisoner)) return false;
            if (Props.requiresPrisoner && !target.IsPrisoner) return false;
            return MatchesFaction(target);
        }

        /// <summary>
        /// DROIDWORKS_WILD_DROIDS_1 (packet E4). Applies one spike to a legal
        /// target. Returns true only if the droid actually changed hands.
        ///
        /// With resistancePerUse == 0 this is the original single-use flip.
        /// Above 0 it is the resistance loop: the vanilla prisoner recruitment
        /// resistance the engine already rolled on capture (from the kind's
        /// initialResistanceRange - Patches/PawnKind_HumanoidDroidResistanceWill
        /// .xml gives every RSW_DW_ kind 10~20) is the thing being worn down,
        /// so the prisoner tab's existing "recruitment resistance" readout is
        /// the progress bar and nothing new has to be scribed or drawn.
        /// Faction change goes through Pawn.SetFaction, which itself calls
        /// guest.SetGuestStatus(null) first - so the droid stops being a
        /// prisoner and becomes a colonist in one call, and that call is
        /// null-Faction-safe (FactionUtility.HostileTo is an extension method
        /// that returns false for a null 'this').
        /// </summary>
        public bool TryReprogram(Pawn target, Pawn spiker)
        {
            if (target == null || target.Dead) return false;

            if (Props.resistancePerUse > 0f && target.guest != null)
            {
                if (target.guest.resistance < 0f)
                {
                    // Sentinel: never captured, so no resistance was ever rolled.
                    // requiresPrisoner should have stopped us getting here; roll
                    // one rather than silently treating "unset" as "zero left".
                    target.guest.resistance =
                        target.kindDef?.initialResistanceRange?.RandomInRange ?? 10f;
                }

                target.guest.resistance =
                    Mathf.Max(0f, target.guest.resistance - Props.resistancePerUse * SkillFactor(spiker));

                if (target.guest.resistance > 0f)
                {
                    Messages.Message(
                        "The spike is rejected. " + target.LabelShortCap +
                        " fights the overwrite - " + target.guest.resistance.ToString("F0") +
                        " resistance left.",
                        target, MessageTypeDefOf.NeutralEvent, historical: false);
                    return false;
                }
            }

            if (target.Faction == Faction.OfPlayer) return false;
            target.SetFaction(Faction.OfPlayer, spiker);
            Messages.Message(
                target.LabelShortCap + " has been reprogrammed and now answers to you.",
                target, MessageTypeDefOf.PositiveEvent, historical: false);
            return true;
        }

        /// <summary>
        /// How hard the spiker bites: 0.5x at Intellectual 0, 1.0x at 10,
        /// 1.5x at 20. Intellectual rather than Social because nobody is
        /// talking the droid round - Patches/PawnKind_HumanoidDroidResistance
        /// Will.xml's own header already rules that droids are not talked down
        /// like a human prisoner.
        /// </summary>
        private static float SkillFactor(Pawn spiker)
        {
            int level = spiker?.skills?.GetSkill(SkillDefOf.Intellectual)?.Level ?? 0;
            return 0.5f + 0.05f * level;
        }
    }
}
